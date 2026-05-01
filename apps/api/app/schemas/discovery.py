from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class ClientProfileBase(BaseModel):
    name: Optional[str] = None
    product_category: Optional[str] = None
    preferences: Optional[dict] = None
    constraints: Optional[dict] = None


class ClientProfileCreate(ClientProfileBase):
    pass


class ClientProfileResponse(ClientProfileBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CreateDiscoveryRequest(BaseModel):
    user_intent: str
    product_category: Optional[str] = None
    preferences: Optional[dict] = None
    constraints: Optional[dict] = None
    weight_profile: Optional[str] = "balanced"
    client_profile_id: Optional[str] = None


class DiscoverySessionResponse(BaseModel):
    id: str
    user_id: str
    user_intent: Optional[str] = None
    product_category: Optional[str] = None
    preferences: Optional[dict] = None
    constraints: Optional[dict] = None
    weight_profile: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ScoreBreakdownSchema(BaseModel):
    monthly_fees: float
    rate_competitiveness: float
    feature_fit: float
    eligibility_fit: float
    digital_capability: float
    suitability: float
    total: float
    weight_profile: str


class RecommendationResultResponse(BaseModel):
    id: str
    session_id: str
    product_id: Optional[str] = None
    external_product_id: Optional[str] = None
    rank: int
    total_score: float
    score_breakdown: Optional[dict] = None
    narrative: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
