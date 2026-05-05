from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class CDRProductCategory(str, Enum):
    TRANS_AND_SAVINGS_ACCOUNTS = "TRANS_AND_SAVINGS_ACCOUNTS"
    TERM_DEPOSITS = "TERM_DEPOSITS"
    TRAVEL_CARDS = "TRAVEL_CARDS"
    REGULATED_TRUST_ACCOUNTS = "REGULATED_TRUST_ACCOUNTS"
    RESIDENTIAL_MORTGAGES = "RESIDENTIAL_MORTGAGES"
    CRED_AND_CHRG_CARDS = "CRED_AND_CHRG_CARDS"
    PERS_LOANS = "PERS_LOANS"
    MARGIN_LOANS = "MARGIN_LOANS"
    LEASES = "LEASES"
    TRADE_FINANCE = "TRADE_FINANCE"
    OVERDRAFTS = "OVERDRAFTS"
    BUSINESS_LOANS = "BUSINESS_LOANS"


class ProductFeatureSchema(BaseModel):
    feature_type: str
    additional_value: Optional[str] = None
    additional_info: Optional[str] = None
    additional_info_uri: Optional[str] = None


class ProductRateSchema(BaseModel):
    rate_type: str
    rate: Optional[str] = None
    comparison_rate: Optional[str] = None
    calculation_frequency: Optional[str] = None
    application_frequency: Optional[str] = None
    tiers: Optional[List[Any]] = None
    additional_value: Optional[str] = None
    additional_info: Optional[str] = None


class ProductFeeSchema(BaseModel):
    fee_type: str
    name: str
    amount: Optional[str] = None
    balance_rate: Optional[str] = None
    transaction_rate: Optional[str] = None
    currency: Optional[str] = "AUD"
    additional_info: Optional[str] = None
    discounts: Optional[List[Any]] = None


class EligibilityRuleSchema(BaseModel):
    eligibility_type: str
    additional_value: Optional[str] = None
    additional_info: Optional[str] = None
    additional_info_uri: Optional[str] = None


class ProductBase(BaseModel):
    provider_id: str
    external_product_id: Optional[str] = None
    name: str
    category: CDRProductCategory
    description: Optional[str] = None
    brand: Optional[str] = None
    brand_name: Optional[str] = None
    application_uri: Optional[str] = None
    is_tailored: bool = False
    is_active: bool = True


class ProductCreate(ProductBase):
    features: Optional[List[ProductFeatureSchema]] = None
    rates: Optional[List[ProductRateSchema]] = None
    fees: Optional[List[ProductFeeSchema]] = None
    eligibility: Optional[List[EligibilityRuleSchema]] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    features: Optional[List[ProductFeatureSchema]] = None
    rates: Optional[List[ProductRateSchema]] = None
    fees: Optional[List[ProductFeeSchema]] = None
    eligibility: Optional[List[EligibilityRuleSchema]] = None


class ProductResponse(ProductBase):
    id: str
    features: List[ProductFeatureSchema] = []
    rates: List[ProductRateSchema] = []
    fees: List[ProductFeeSchema] = []
    eligibility: List[EligibilityRuleSchema] = []
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductSummary(BaseModel):
    id: str
    provider_id: str
    name: str
    category: str
    description: Optional[str] = None
    brand_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
