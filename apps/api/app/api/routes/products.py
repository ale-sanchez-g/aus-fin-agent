from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Any
from pydantic import BaseModel

from app.db.session import get_db
from app.core.security import get_current_user, CurrentUser
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductResponse, ProductSummary
from app.schemas.common import PaginatedResponse

router = APIRouter()


class IntentSearchRequest(BaseModel):
    user_intent: str
    max_results: int = 6


def _to_frontend_product(product: dict, idx: int) -> dict:
    """Convert internal snake_case product dict to camelCase for the frontend."""
    rates = product.get("rates") or []
    category = (product.get("category") or "TRANS_AND_SAVINGS_ACCOUNTS").upper()
    is_lending = category in (
        "RESIDENTIAL_MORTGAGES", "PERS_LOANS", "BUSINESS_LOANS",
        "OVERDRAFTS", "LEASES", "CRED_AND_CHRG_CARDS",
    )

    deposit_rates: List[dict] = []
    lending_rates: List[dict] = []
    for r in rates:
        entry: dict[str, Any] = {
            "rateType": r.get("rate_type", "VARIABLE"),
            "rate": r.get("rate") or "0",
        }
        if r.get("comparison_rate"):
            entry["comparisonRate"] = r["comparison_rate"]
        if r.get("additional_value"):
            entry["additionalInfo"] = r["additional_value"]
        (lending_rates if is_lending else deposit_rates).append(entry)

    return {
        "id": product.get("id") or str(idx),
        "productId": product.get("external_product_id") or product.get("id") or str(idx),
        "productCategory": category,
        "name": product.get("name") or "Unknown Product",
        "description": product.get("description"),
        "brand": product.get("brand") or product.get("provider_id") or "",
        "brandName": product.get("brand_name") or product.get("brand") or "",
        "applicationUri": product.get("application_uri"),
        "isTailored": bool(product.get("is_tailored", False)),
        "features": [
            {
                "featureType": f.get("feature_type", ""),
                "additionalValue": f.get("additional_value"),
                "additionalInfo": f.get("additional_info"),
            }
            for f in (product.get("features") or [])
        ],
        "fees": [
            {
                "name": f.get("name") or "Fee",
                "feeType": f.get("fee_type", ""),
                "amount": f.get("amount"),
                "additionalInfo": f.get("additional_info"),
            }
            for f in (product.get("fees") or [])
        ],
        "depositRates": deposit_rates,
        "lendingRates": lending_rates,
        "eligibility": [
            {
                "eligibilityType": e.get("eligibility_type", ""),
                "additionalValue": e.get("additional_value"),
                "additionalInfo": e.get("additional_info"),
            }
            for e in (product.get("eligibility") or [])
        ],
    }


@router.get("", response_model=PaginatedResponse[ProductSummary])
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    provider_id: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    repo = ProductRepository(db)
    items, total = repo.list_products(
        page=page,
        page_size=page_size,
        category=category,
        provider_id=provider_id,
        search=search,
    )
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/compare", response_model=List[ProductResponse])
async def compare_products(
    ids: str = Query(..., description="Comma-separated product IDs"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    product_ids = [pid.strip() for pid in ids.split(",") if pid.strip()]
    if not product_ids:
        raise HTTPException(status_code=400, detail="No product IDs provided")
    if len(product_ids) > 10:
        raise HTTPException(status_code=400, detail="Cannot compare more than 10 products at once")

    repo = ProductRepository(db)
    products = repo.get_products_by_ids(product_ids)
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    repo = ProductRepository(db)
    product = repo.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/search-by-intent")
async def search_products_by_intent(
    request: IntentSearchRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Use an AI agent + OpenBanking MCP to discover real products matching a natural-language intent."""
    import structlog
    from app.agents.nodes.intake_node import _infer_category, _infer_weight_profile
    from app.agents.nodes.retrieval_node import _fetch_products

    log = structlog.get_logger()

    if not request.user_intent or not request.user_intent.strip():
        raise HTTPException(status_code=400, detail="user_intent must not be empty")

    intent = request.user_intent.strip()
    inferred_category = _infer_category(intent, None)
    inferred_profile = _infer_weight_profile(intent, None)

    log.info(
        "intent_search_started",
        intent=intent,
        category=inferred_category,
        profile=inferred_profile,
        user_id=current_user.user_id,
    )

    try:
        raw_products = _fetch_products(category=inferred_category, session_id=None)
    except Exception as exc:
        log.error("intent_search_failed", error=str(exc))
        raise HTTPException(status_code=502, detail=f"Product discovery failed: {exc}")

    max_r = max(1, min(request.max_results, 20))
    frontend_products = [
        _to_frontend_product(p, idx)
        for idx, p in enumerate(raw_products[:max_r])
    ]

    return {
        "products": frontend_products,
        "inferredCategory": inferred_category,
        "inferredProfile": inferred_profile,
        "userIntent": intent,
        "total": len(frontend_products),
    }
