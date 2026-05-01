from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.provider import Provider, DataSource, SyncJob


class ProviderRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_providers(self, active_only: bool = False) -> list[Provider]:
        query = self.db.query(Provider)
        if active_only:
            query = query.filter(Provider.is_active == True)  # noqa: E712
        return query.order_by(Provider.name).all()

    def get_provider_by_id(self, provider_id: str) -> Optional[Provider]:
        return self.db.query(Provider).filter(Provider.id == provider_id).first()

    def create_provider(self, data: dict) -> Provider:
        provider = Provider(**data)
        self.db.add(provider)
        return provider

    def update_provider(self, provider_id: str, data: dict) -> Optional[Provider]:
        provider = self.get_provider_by_id(provider_id)
        if provider:
            for key, value in data.items():
                if hasattr(provider, key) and value is not None:
                    setattr(provider, key, value)
        return provider

    def create_sync_job(self, provider_id: str) -> SyncJob:
        job = SyncJob(provider_id=provider_id, status="pending")
        self.db.add(job)
        return job

    def update_sync_job(
        self,
        job_id: str,
        status: str,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
        records_synced: int = 0,
        error_message: Optional[str] = None,
    ):
        job = self.db.query(SyncJob).filter(SyncJob.id == job_id).first()
        if job:
            job.status = status
            if started_at:
                job.started_at = started_at
            if completed_at:
                job.completed_at = completed_at
            if records_synced:
                job.records_synced = records_synced
            if error_message:
                job.error_message = error_message

    def get_sync_jobs_for_provider(self, provider_id: str) -> list[SyncJob]:
        return (
            self.db.query(SyncJob)
            .filter(SyncJob.provider_id == provider_id)
            .order_by(SyncJob.created_at.desc())
            .limit(10)
            .all()
        )
