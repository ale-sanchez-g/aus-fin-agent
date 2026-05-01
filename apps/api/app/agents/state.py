from typing import TypedDict, Optional


class AgentState(TypedDict):
    session_id: str
    user_intent: str
    product_category: str
    preferences: dict
    constraints: dict
    weight_profile: str
    products: list[dict]
    eligible_products: list[dict]
    scored_products: list[dict]
    narrative: str
    compliance_notes: list[str]
    report: dict
    error: Optional[str]
    status: str
