"""MCP client for open-banking-mcp sidecar.

Connects to the `open-banking-mcp` process over stdio using
langchain-mcp-adapters.  When CDR_MOCK_MODE is true the client reads
from the bundled JSON fixture instead of spawning the MCP process.
"""
import json
import time
import structlog
from app.core.config import settings

log = structlog.get_logger()

_CIRCUIT_FAILURE_THRESHOLD = 5
_CIRCUIT_RESET_TIMEOUT = 60.0

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
    async def _call_mcp_tool(self, tool_name: str, args: dict) -> dict | list:
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
                return json.loads(call_result.content[0].text)
        except Exception as exc:
            self._record_failure()
            log.error("mcp_tool_call_failed", tool=tool_name, error=str(exc))
            raise

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    async def list_providers(self) -> list[dict]:
        if settings.CDR_MOCK_MODE:
            return _load_mock_fixture().get("providers", [])
        try:
            result = await self._call_mcp_tool("list-providers", {})
            return result if isinstance(result, list) else result.get("data", [])
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
            result = await self._call_mcp_tool("list-products", args)
            return result if isinstance(result, list) else result.get("data", [])
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
