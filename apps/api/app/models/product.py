import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Product(Base):
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    provider_id: Mapped[str] = mapped_column(String(36), ForeignKey("providers.id"), nullable=False)
    external_product_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    brand: Mapped[str | None] = mapped_column(String(255), nullable=True)
    brand_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    application_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_tailored: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    effective_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_updated: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    additional_info: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    provider: Mapped["Provider"] = relationship("Provider", back_populates="products")  # noqa: F821
    features: Mapped[list["ProductFeature"]] = relationship(
        "ProductFeature", back_populates="product", cascade="all, delete-orphan"
    )
    rates: Mapped[list["ProductRate"]] = relationship(
        "ProductRate", back_populates="product", cascade="all, delete-orphan"
    )
    fees: Mapped[list["ProductFee"]] = relationship(
        "ProductFee", back_populates="product", cascade="all, delete-orphan"
    )
    eligibility_rules: Mapped[list["EligibilityRule"]] = relationship(
        "EligibilityRule", back_populates="product", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "provider_id": self.provider_id,
            "external_product_id": self.external_product_id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "brand": self.brand,
            "brand_name": self.brand_name,
            "application_uri": self.application_uri,
            "is_tailored": self.is_tailored,
            "is_active": self.is_active,
            "features": [
                {
                    "feature_type": f.feature_type,
                    "additional_value": f.additional_value,
                    "additional_info": f.additional_info,
                }
                for f in self.features
            ],
            "rates": [
                {
                    "rate_type": r.rate_type,
                    "rate": r.rate,
                    "comparison_rate": r.comparison_rate,
                    "tiers": r.tiers,
                }
                for r in self.rates
            ],
            "fees": [
                {
                    "fee_type": f.fee_type,
                    "name": f.name,
                    "amount": f.amount,
                    "balance_rate": f.balance_rate,
                    "transaction_rate": f.transaction_rate,
                    "currency": f.currency,
                }
                for f in self.fees
            ],
            "eligibility": [
                {
                    "eligibility_type": e.eligibility_type,
                    "additional_value": e.additional_value,
                }
                for e in self.eligibility_rules
            ],
        }


class ProductFeature(Base):
    __tablename__ = "product_features"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    feature_type: Mapped[str] = mapped_column(String(100), nullable=False)
    additional_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
    additional_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    additional_info_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)

    product: Mapped["Product"] = relationship("Product", back_populates="features")


class ProductRate(Base):
    __tablename__ = "product_rates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    rate_type: Mapped[str] = mapped_column(String(100), nullable=False)
    rate: Mapped[str | None] = mapped_column(String(50), nullable=True)
    comparison_rate: Mapped[str | None] = mapped_column(String(50), nullable=True)
    calculation_frequency: Mapped[str | None] = mapped_column(String(50), nullable=True)
    application_frequency: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tiers: Mapped[list | None] = mapped_column(JSON, nullable=True)
    additional_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
    additional_info: Mapped[str | None] = mapped_column(Text, nullable=True)

    product: Mapped["Product"] = relationship("Product", back_populates="rates")


class ProductFee(Base):
    __tablename__ = "product_fees"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    fee_type: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[str | None] = mapped_column(String(50), nullable=True)
    balance_rate: Mapped[str | None] = mapped_column(String(50), nullable=True)
    transaction_rate: Mapped[str | None] = mapped_column(String(50), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True, default="AUD")
    additional_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    discounts: Mapped[list | None] = mapped_column(JSON, nullable=True)

    product: Mapped["Product"] = relationship("Product", back_populates="fees")


class EligibilityRule(Base):
    __tablename__ = "eligibility_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    product_id: Mapped[str] = mapped_column(String(36), ForeignKey("products.id"), nullable=False)
    eligibility_type: Mapped[str] = mapped_column(String(100), nullable=False)
    additional_value: Mapped[str | None] = mapped_column(String(500), nullable=True)
    additional_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    additional_info_uri: Mapped[str | None] = mapped_column(String(500), nullable=True)

    product: Mapped["Product"] = relationship("Product", back_populates="eligibility_rules")
