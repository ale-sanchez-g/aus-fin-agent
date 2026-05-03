import json
import structlog
from datetime import datetime, timezone
from app.core.config import settings

log = structlog.get_logger()

_MOCK_FIXTURE_PATH = "/app/mock-cdr-data.json"


def _load_mock_fixture() -> dict:
    try:
        with open(_MOCK_FIXTURE_PATH) as fh:
            return json.load(fh)
    except Exception as exc:
        log.warning("mock_fixture_load_failed", error=str(exc))
        return {"providers": [], "products": []}


async def fetch_providers_via_mcp() -> list[dict]:
    if settings.CDR_MOCK_MODE:
        return _load_mock_fixture().get("providers", [])
    from langchain_mcp_adapters.client import MultiServerMCPClient  # type: ignore

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
        call_result = await session.call_tool("list-providers", arguments={})
        if not call_result.content:
            return []
        raw = json.loads(call_result.content[0].text)
        return raw if isinstance(raw, list) else raw.get("data", [])


async def sync_all_providers() -> dict:
    """Fetch providers via MCP stdio and log result."""
    log.info("sync_providers_start")
    try:
        providers = await fetch_providers_via_mcp()
        log.info("sync_providers_complete", count=len(providers))
        return {"synced": len(providers), "errors": [], "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        log.error("sync_providers_failed", error=str(e))
        return {"synced": 0, "errors": [str(e)], "timestamp": datetime.now(timezone.utc).isoformat()}
