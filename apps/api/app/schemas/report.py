from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class ReportSection(BaseModel):
    title: str
    content: Any
    section_type: str = "text"


class DiscoveryReport(BaseModel):
    session_id: str
    generated_at: datetime
    product_category: Optional[str] = None
    user_intent: Optional[str] = None
    total_products_evaluated: int = 0
    total_eligible_products: int = 0
    top_recommendations: List[dict] = []
    narrative: Optional[str] = None
    sections: List[ReportSection] = []
    compliance_notes: List[str] = []
    disclaimer: str = ""
    weight_profile: Optional[str] = None


class ReportArtifactBase(BaseModel):
    session_id: str
    report_type: str = "discovery"
    format: str = "json"


class ReportArtifactCreate(ReportArtifactBase):
    content: Optional[dict] = None
    s3_key: Optional[str] = None
    local_path: Optional[str] = None


class ReportArtifactResponse(ReportArtifactBase):
    id: str
    s3_key: Optional[str] = None
    local_path: Optional[str] = None
    created_at: datetime
    expires_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DownloadUrlResponse(BaseModel):
    url: str
    expires_in_seconds: int = 3600
    report_id: str
