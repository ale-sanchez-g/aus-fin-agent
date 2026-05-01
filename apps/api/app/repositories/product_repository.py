from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from app.models.product import Product, ProductFeature, ProductRate, ProductFee, EligibilityRule
from app.schemas.product import ProductSummary, ProductResponse, ProductFeatureSchema, ProductRateSchema, ProductFeeSchema, EligibilityRuleSchema


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_products(
        self,
        page: int = 1,
        page_size: int = 20,
        category: Optional[str] = None,
        provider_id: Optional[str] = None,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[list[ProductSummary], int]:
        query = self.db.query(Product)

        if is_active is not None:
            query = query.filter(Product.is_active == is_active)
        elif category is None and provider_id is None and search is None:
            query = query.filter(Product.is_active == True)  # noqa: E712

        if category:
            query = query.filter(Product.category == category)
        if provider_id:
            query = query.filter(Product.provider_id == provider_id)
        if search:
            term = f"%{search}%"
            query = query.filter(
                or_(
                    Product.name.ilike(term),
                    Product.description.ilike(term),
                    Product.brand_name.ilike(term),
                )
            )

        total = query.count()
        offset = (page - 1) * page_size
        products = query.offset(offset).limit(page_size).all()

        items = [
            ProductSummary(
                id=p.id,
                provider_id=p.provider_id,
                name=p.name,
                category=p.category,
                description=p.description,
                brand_name=p.brand_name,
                is_active=p.is_active,
                created_at=p.created_at,
            )
            for p in products
        ]
        return items, total

    def get_product_by_id(self, product_id: str) -> Optional[ProductResponse]:
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        return self._to_response(product)

    def get_products_by_ids(self, product_ids: list[str]) -> list[ProductResponse]:
        products = self.db.query(Product).filter(Product.id.in_(product_ids)).all()
        return [self._to_response(p) for p in products]

    def get_products_for_category(self, category: str, limit: int = 200) -> list[dict]:
        products = (
            self.db.query(Product)
            .filter(Product.category == category, Product.is_active == True)  # noqa: E712
            .limit(limit)
            .all()
        )
        return [p.to_dict() for p in products]

    def _to_response(self, product: Product) -> ProductResponse:
        return ProductResponse(
            id=product.id,
            provider_id=product.provider_id,
            external_product_id=product.external_product_id,
            name=product.name,
            category=product.category,
            description=product.description,
            brand=product.brand,
            brand_name=product.brand_name,
            application_uri=product.application_uri,
            is_tailored=product.is_tailored,
            is_active=product.is_active,
            effective_from=product.effective_from,
            effective_to=product.effective_to,
            last_updated=product.last_updated,
            created_at=product.created_at,
            updated_at=product.updated_at,
            features=[
                ProductFeatureSchema(
                    feature_type=f.feature_type,
                    additional_value=f.additional_value,
                    additional_info=f.additional_info,
                    additional_info_uri=f.additional_info_uri,
                )
                for f in product.features
            ],
            rates=[
                ProductRateSchema(
                    rate_type=r.rate_type,
                    rate=r.rate,
                    comparison_rate=r.comparison_rate,
                    calculation_frequency=r.calculation_frequency,
                    application_frequency=r.application_frequency,
                    tiers=r.tiers,
                    additional_value=r.additional_value,
                    additional_info=r.additional_info,
                )
                for r in product.rates
            ],
            fees=[
                ProductFeeSchema(
                    fee_type=f.fee_type,
                    name=f.name,
                    amount=f.amount,
                    balance_rate=f.balance_rate,
                    transaction_rate=f.transaction_rate,
                    currency=f.currency,
                    additional_info=f.additional_info,
                    discounts=f.discounts,
                )
                for f in product.fees
            ],
            eligibility=[
                EligibilityRuleSchema(
                    eligibility_type=e.eligibility_type,
                    additional_value=e.additional_value,
                    additional_info=e.additional_info,
                    additional_info_uri=e.additional_info_uri,
                )
                for e in product.eligibility_rules
            ],
        )

    def create_product(self, data: dict) -> Product:
        product = Product(
            provider_id=data["provider_id"],
            external_product_id=data.get("external_product_id"),
            name=data["name"],
            category=data["category"],
            description=data.get("description"),
            brand=data.get("brand"),
            brand_name=data.get("brand_name"),
            application_uri=data.get("application_uri"),
            is_tailored=data.get("is_tailored", False),
            is_active=data.get("is_active", True),
        )
        self.db.add(product)
        self.db.flush()

        for feat in data.get("features", []) or []:
            self.db.add(ProductFeature(product_id=product.id, **feat))
        for rate in data.get("rates", []) or []:
            self.db.add(ProductRate(product_id=product.id, **rate))
        for fee in data.get("fees", []) or []:
            self.db.add(ProductFee(product_id=product.id, **fee))
        for rule in data.get("eligibility", []) or []:
            self.db.add(EligibilityRule(product_id=product.id, **rule))

        return product
