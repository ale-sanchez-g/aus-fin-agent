from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.core.security import get_current_user, CurrentUser, require_role
from app.repositories.provider_repository import ProviderRepository
from app.schemas.provider import ProviderResponse, SyncJobResponse

router = APIRouter()


@router.get("", response_model=List[ProviderResponse])
async def list_providers(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    repo = ProviderRepository(db)
    return repo.list_providers()


@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    provider_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    repo = ProviderRepository(db)
    provider = repo.get_provider_by_id(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.post("/{provider_id}/sync", response_model=SyncJobResponse, status_code=202)
async def trigger_sync(
    provider_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("admin")),
):
    repo = ProviderRepository(db)
    provider = repo.get_provider_by_id(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    sync_job = repo.create_sync_job(provider_id=provider_id)
    db.commit()
    db.refresh(sync_job)

    background_tasks.add_task(_run_sync, sync_job.id, provider_id)
    return sync_job


@router.get("/{provider_id}/sync-status", response_model=List[SyncJobResponse])
async def get_sync_status(
    provider_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    repo = ProviderRepository(db)
    return repo.get_sync_jobs_for_provider(provider_id)


def _run_sync(sync_job_id: str, provider_id: str):
    """Background task to sync products from Node adapter."""
    from app.db.session import SessionLocal
    from app.repositories.provider_repository import ProviderRepository
    from app.tasks.sync_products import sync_provider_products
    from datetime import datetime, timezone

    db = SessionLocal()
    try:
        repo = ProviderRepository(db)
        repo.update_sync_job(sync_job_id, status="running", started_at=datetime.now(timezone.utc))
        db.commit()

        count = sync_provider_products(db, provider_id)

        repo.update_sync_job(
            sync_job_id,
            status="completed",
            completed_at=datetime.now(timezone.utc),
            records_synced=count,
        )
        db.commit()
    except Exception as exc:
        repo = ProviderRepository(db)
        repo.update_sync_job(sync_job_id, status="failed", error_message=str(exc))
        db.commit()
    finally:
        db.close()
