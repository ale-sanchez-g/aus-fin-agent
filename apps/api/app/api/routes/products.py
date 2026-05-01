from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.db.session import get_db
from app.core.security import get_current_user, CurrentUser
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductResponse, ProductSummary
from app.schemas.common import PaginatedResponse

router = APIRouter()


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
