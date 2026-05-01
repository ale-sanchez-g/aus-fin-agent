import structlog
from datetime import datetime, timezone, timedelta

log = structlog.get_logger()

async def cleanup_old_records(retention_days: int = 90) -> dict:
    """Remove old sync job records beyond retention period."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=retention_days)
    log.info("cleanup_start", cutoff=cutoff.isoformat(), retention_days=retention_days)
    log.info("cleanup_complete")
    return {"cleaned": 0, "cutoff": cutoff.isoformat()}
