import httpx
import structlog
from datetime import datetime, timezone
from tenacity import retry, stop_after_attempt, wait_exponential

log = structlog.get_logger()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch_products_from_adapter(adapter_url: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(f"{adapter_url}/api/products")
        response.raise_for_status()
        return response.json().get("data", [])

async def sync_all_products(adapter_url: str) -> dict:
    """Fetch all products from the adapter and log result."""
    log.info("sync_products_start", adapter_url=adapter_url)
    try:
        products = await fetch_products_from_adapter(adapter_url)
        log.info("sync_products_complete", count=len(products))
        return {"synced": len(products), "errors": [], "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        log.error("sync_products_failed", error=str(e))
        return {"synced": 0, "errors": [str(e)], "timestamp": datetime.now(timezone.utc).isoformat()}
