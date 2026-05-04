"""MCP client for open-banking-mcp sidecar.

Connects to the `open-banking-mcp` process over stdio using
langchain-mcp-adapters.  When CDR_MOCK_MODE is true the client reads
from the bundled JSON fixture instead of spawning the MCP process.
"""
import json
import re
import time
import structlog
from app.core.config import settings

log = structlog.get_logger()

_CIRCUIT_FAILURE_THRESHOLD = 5
_CIRCUIT_RESET_TIMEOUT = 60.0

_DISCOVERY_BANK_IDS = [
    "commbank",
    "anz",
    "nab",
    "westpac",
    "ing",
    "macquarie-bank",
]

# Path to the mock fixture bundled with this service
_MOCK_FIXTURE_PATH = "/app/mock-cdr-data.json"


def _load_mock_fixture() -> dict:
    try:
        with open(_MOCK_FIXTURE_PATH) as fh:
            return json.load(fh)
    except Exception as exc:
        log.warning("mock_fixture_load_failed", error=str(exc))
        return {"providers": [], "products": []}


class MCPAdapterClient:
    """Thin async wrapper around the open-banking-mcp MCP server.

    In CDR_MOCK_MODE the fixture is returned without spawning the
    subprocess.  In live mode MultiServerMCPClient is used to call the
    MCP tools over stdio transport.
    """

    def __init__(self):
        self._failures = 0
        self._circuit_open = False
        self._last_failure_time: float = 0.0

    # ------------------------------------------------------------------
    # Circuit-breaker helpers
    # ------------------------------------------------------------------
    def _check_circuit(self):
        if self._circuit_open:
            if time.time() - self._last_failure_time > _CIRCUIT_RESET_TIMEOUT:
                self._circuit_open = False
                self._failures = 0
                log.info("circuit_reset")
            else:
                raise RuntimeError("MCP circuit breaker is open")

    def _record_failure(self):
        self._failures += 1
        self._last_failure_time = time.time()
        if self._failures >= _CIRCUIT_FAILURE_THRESHOLD:
            self._circuit_open = True
            log.warning("circuit_opened", failures=self._failures)

    def _record_success(self):
        self._failures = 0
        self._circuit_open = False

    # ------------------------------------------------------------------
    # MCP call helpers
    # ------------------------------------------------------------------
    async def _call_mcp_tool(self, tool_name: str, args: dict) -> dict | list | str:
        """Spawn open-banking-mcp via stdio and call a single tool."""
        from langchain_mcp_adapters.client import MultiServerMCPClient  # type: ignore

        self._check_circuit()
        try:
            client = MultiServerMCPClient(
                {
                    "open_banking": {
                        "command": "npx",
                        "args": ["open-banking-mcp"],
                        "env": {"CDR_BASE_URL": settings.CDR_BASE_URL},
                        "transport": "stdio",
                    }
                }
            )
            async with client.session("open_banking") as session:
                call_result = await session.call_tool(tool_name, arguments=args)
                self._record_success()
                if not call_result.content:
                    return {}
                text = call_result.content[0].text
                try:
                    return json.loads(text)
                except Exception:
                    return text
        except Exception as exc:
            self._record_failure()
            log.error("mcp_tool_call_failed", tool=tool_name, error=str(exc))
            raise

    async def _dismiss_disclaimer(self):
        try:
            await self._call_mcp_tool("dismiss_disclaimer", {})
        except Exception:
            # Disclaimer acceptance is best effort; subsequent calls may still work.
            pass

    def _parse_markdown_table(self, markdown: str) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        headers: list[str] = []

        for raw_line in markdown.splitlines():
            line = raw_line.strip()
            if not line.startswith("|") or not line.endswith("|"):
                continue

            cols = [c.strip() for c in line.strip("|").split("|")]
            if not headers:
                headers = cols
                continue

            if all(re.fullmatch(r"-+", c.replace(" ", "")) for c in cols):
                continue

            if len(cols) != len(headers):
                continue

            rows.append(dict(zip(headers, cols)))

        return rows

    def _extract_markdown_link(self, value: str) -> tuple[str, str | None]:
        match = re.search(r"\[([^\]]+)\]\((https?://[^)]+)\)", value or "")
        if not match:
            return (value.strip(), None)
        return (match.group(1).strip(), match.group(2).strip())

    def _parse_fee_amount(self, value: str) -> str:
        match = re.search(r"\$\s*([0-9]+(?:\.[0-9]+)?)", value or "")
        if not match:
            return "0"
        return match.group(1)

    def _slug(self, value: str) -> str:
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", (value or "").strip().lower()).strip("-")
        return slug or "unknown"

    async def _fetch_credit_cards(self, category: str | None) -> list[dict]:
        query = "travel" if category == "TRAVEL_CARDS" else "all"
        result = await self._call_mcp_tool("find_credit_cards", {"query": query, "limit": 25})
        if not isinstance(result, str):
            return []

        products: list[dict] = []
        for row in self._parse_markdown_table(result):
            product_cell = row.get("Product", "")
            product_name, product_url = self._extract_markdown_link(product_cell)
            bank = row.get("Bank", "")
            annual_fee = self._parse_fee_amount(row.get("Annual Fee", ""))
            key_feature = row.get("Key Feature", "")

            feature_type = "TRAVEL_INSURANCE" if "travel" in key_feature.lower() else "BONUS_REWARDS"

            products.append(
                {
                    "productId": f"{self._slug(bank)}:{self._slug(product_name)}",
                    "providerId": self._slug(bank),
                    "name": product_name,
                    "productName": product_name,
                    "productCategory": "CRED_AND_CHRG_CARDS",
                    "brandName": bank,
                    "applicationUri": product_url,
                    "isTailored": False,
                    "fees": [{"feeType": "PERIODIC", "name": "Annual fee", "amount": annual_fee}],
                    "features": [{"featureType": feature_type, "additionalValue": key_feature}],
                    "depositRates": [],
                    "lendingRates": [],
                    "eligibility": [],
                }
            )

        return products

    async def _fetch_products_by_category(self, category: str | None) -> list[dict]:
        if not category:
            return []

        products: list[dict] = []
        for bank_id in _DISCOVERY_BANK_IDS:
            try:
                result = await self._call_mcp_tool(
                    "list_banking_products",
                    {"bankId": bank_id, "category": category, "pageSize": 25},
                )
                if not isinstance(result, str):
                    continue

                for row in self._parse_markdown_table(result):
                    product_cell = row.get("Product", "")
                    product_name, product_url = self._extract_markdown_link(product_cell)
                    products.append(
                        {
                            "productId": f"{bank_id}:{self._slug(product_name)}",
                            "providerId": bank_id,
                            "name": product_name,
                            "productName": product_name,
                            "productCategory": row.get("Category", category) or category,
                            "brandName": bank_id,
                            "applicationUri": product_url,
                            "isTailored": False,
                            "fees": [],
                            "features": [],
                            "depositRates": [],
                            "lendingRates": [],
                            "eligibility": [],
                        }
                    )
            except Exception as exc:
                log.warning("mcp_list_banking_products_failed", bank_id=bank_id, category=category, error=str(exc))

        return products

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def list_providers(self) -> list[dict]:
        if settings.CDR_MOCK_MODE:
            return _load_mock_fixture().get("providers", [])
        try:
            result = await self._call_mcp_tool("list_banks", {})
            if not isinstance(result, str):
                return []

            providers: list[dict] = []
            for line in result.splitlines():
                line = line.strip()
                match = re.match(r"^-\s*`([^`]+)`\s*[—-]\s*(.+)$", line)
                if not match:
                    continue
                providers.append(
                    {
                        "providerId": match.group(1).strip(),
                        "name": match.group(2).strip(),
                        "displayName": match.group(2).strip(),
                        "isActive": True,
                    }
                )
            return providers
        except Exception as exc:
            log.error("mcp_list_providers_failed", error=str(exc))
            return []

    async def get_products(
        self, provider_id: str = None, category: str = None
    ) -> list[dict]:
        if settings.CDR_MOCK_MODE:
            fixture = _load_mock_fixture()
            products = fixture.get("products", [])
            if category:
                products = [p for p in products if p.get("productCategory") == category]
            return products
        args: dict = {}
        if provider_id:
            args["providerId"] = provider_id
        if category:
            args["category"] = category
        try:
            await self._dismiss_disclaimer()

            # open-banking-mcp exposes credit-card discovery via find_credit_cards.
            if category in ("CRED_AND_CHRG_CARDS", "TRAVEL_CARDS"):
                return await self._fetch_credit_cards(category)

            # For other categories, query a representative bank set.
            return await self._fetch_products_by_category(category)
        except Exception as exc:
            log.error("mcp_get_products_failed", error=str(exc))
            return []

    async def get_product_detail(self, product_id: str) -> dict:
        if settings.CDR_MOCK_MODE:
            for p in _load_mock_fixture().get("products", []):
                if p.get("productId") == product_id:
                    return p
            return {}
        try:
            result = await self._call_mcp_tool("get-product-detail", {"productId": product_id})
            return result.get("data", {}) if isinstance(result, dict) else {}
        except Exception as exc:
            log.error("mcp_get_product_detail_failed", product_id=product_id, error=str(exc))
            return {}


adapter_client = MCPAdapterClient()
