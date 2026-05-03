import structlog
from datetime import datetime, timezone
from app.core.config import settings

log = structlog.get_logger()


async def fetch_products_via_mcp() -> list[dict]:
    if settings.CDR_MOCK_MODE:
        from app.tasks.sync_providers import _load_mock_fixture
        return _load_mock_fixture().get("products", [])
    from langchain_mcp_adapters.client import MultiServerMCPClient  # type: ignore

    async with MultiServerMCPClient(
        {
            "open_banking": {
                "command": "npx",
                "args": ["open-banking-mcp"],
                "env": {"CDR_BASE_URL": settings.CDR_BASE_URL},
                "transport": "stdio",
            }
        }
    ) as client:
        result = await client.call_tool("open_banking", "list-products", {})
        return result if isinstance(result, list) else result.get("data", [])


async def sync_all_products() -> dict:
    """Fetch all products via MCP stdio and log result."""
    log.info("sync_products_start")
    try:
        products = await fetch_products_via_mcp()
        log.info("sync_products_complete", count=len(products))
        return {"synced": len(products), "errors": [], "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        log.error("sync_products_failed", error=str(e))
        return {"synced": 0, "errors": [str(e)], "timestamp": datetime.now(timezone.utc).isoformat()}
