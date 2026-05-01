from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime


class ProviderBase(BaseModel):
    name: str
    abn: Optional[str] = None
    cdr_holder_id: Optional[str] = None
    endpoint_url: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True


class ProviderCreate(ProviderBase):
    pass


class ProviderUpdate(BaseModel):
    name: Optional[str] = None
    abn: Optional[str] = None
    cdr_holder_id: Optional[str] = None
    endpoint_url: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None


class ProviderResponse(ProviderBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DataSourceBase(BaseModel):
    provider_id: str
    source_type: str
    url: Optional[str] = None
    is_active: bool = True


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceResponse(DataSourceBase):
    id: str
    last_synced_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class SyncJobBase(BaseModel):
    provider_id: Optional[str] = None
    status: str = "pending"


class SyncJobCreate(SyncJobBase):
    pass


class SyncJobResponse(SyncJobBase):
    id: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    records_synced: int = 0
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
