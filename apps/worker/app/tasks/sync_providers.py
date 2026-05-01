import httpx
import structlog
from datetime import datetime, timezone
from tenacity import retry, stop_after_attempt, wait_exponential

log = structlog.get_logger()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def fetch_providers_from_adapter(adapter_url: str) -> list[dict]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{adapter_url}/api/providers")
        response.raise_for_status()
        return response.json().get("data", [])

async def sync_all_providers(adapter_url: str) -> dict:
    """Fetch providers from Node adapter and log result."""
    log.info("sync_providers_start", adapter_url=adapter_url)
    try:
        providers = await fetch_providers_from_adapter(adapter_url)
        log.info("sync_providers_complete", count=len(providers))
        return {"synced": len(providers), "errors": [], "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        log.error("sync_providers_failed", error=str(e))
        return {"synced": 0, "errors": [str(e)], "timestamp": datetime.now(timezone.utc).isoformat()}
