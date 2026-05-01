import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
import structlog

log = structlog.get_logger()

_CIRCUIT_FAILURE_THRESHOLD = 5
_CIRCUIT_RESET_TIMEOUT = 60.0


class CircuitOpenError(Exception):
    pass


class AdapterClient:
    def __init__(self):
        self._base_url = settings.NODE_ADAPTER_URL
        self._client = httpx.AsyncClient(timeout=30.0)
        self._failures = 0
        self._circuit_open = False
        self._last_failure_time: float = 0.0

    def _check_circuit(self):
        import time

        if self._circuit_open:
            if time.time() - self._last_failure_time > _CIRCUIT_RESET_TIMEOUT:
                self._circuit_open = False
                self._failures = 0
                log.info("circuit_reset")
            else:
                raise CircuitOpenError("Circuit breaker is open")

    def _record_failure(self):
        import time

        self._failures += 1
        self._last_failure_time = time.time()
        if self._failures >= _CIRCUIT_FAILURE_THRESHOLD:
            self._circuit_open = True
            log.warning("circuit_opened", failures=self._failures)

    def _record_success(self):
        self._failures = 0
        self._circuit_open = False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.TransportError),
        reraise=True,
    )
    async def _get(self, path: str, params: dict = None) -> dict | list:
        self._check_circuit()
        try:
            resp = await self._client.get(f"{self._base_url}{path}", params=params or {})
            resp.raise_for_status()
            self._record_success()
            return resp.json()
        except (httpx.TransportError, httpx.HTTPStatusError) as exc:
            self._record_failure()
            raise exc

    async def list_providers(self) -> list[dict]:
        try:
            result = await self._get("/api/providers")
            return result if isinstance(result, list) else result.get("data", [])
        except Exception as exc:
            log.error("adapter_list_providers_failed", error=str(exc))
            return []

    async def get_products(
        self, provider_id: str = None, category: str = None
    ) -> list[dict]:
        params = {}
        if category:
            params["category"] = category
        try:
            if provider_id:
                path = f"/api/providers/{provider_id}/products"
            else:
                path = "/api/products"
            result = await self._get(path, params=params)
            return result if isinstance(result, list) else result.get("data", [])
        except Exception as exc:
            log.error("adapter_get_products_failed", error=str(exc))
            return []

    async def get_product_detail(self, product_id: str) -> dict:
        try:
            result = await self._get(f"/api/products/{product_id}")
            return result.get("data", {}) if isinstance(result, dict) else {}
        except Exception as exc:
            log.error("adapter_get_product_detail_failed", product_id=product_id, error=str(exc))
            return {}

    async def health(self) -> bool:
        try:
            resp = await self._client.get(f"{self._base_url}/health", timeout=5.0)
            return resp.status_code == 200
        except Exception:
            return False

    async def close(self):
        await self._client.aclose()


adapter_client = AdapterClient()
