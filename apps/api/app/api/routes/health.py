from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import httpx

from app.db.session import get_db
from app.core.config import settings
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    # Check database
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    # Check node adapter
    adapter_status = "unconfigured"
    if settings.NODE_ADAPTER_URL:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.get(f"{settings.NODE_ADAPTER_URL}/health")
                adapter_status = "ok" if resp.status_code == 200 else "degraded"
        except Exception:
            adapter_status = "unreachable"

    return HealthResponse(
        status="ok",
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        database=db_status,
        node_adapter=adapter_status,
    )
