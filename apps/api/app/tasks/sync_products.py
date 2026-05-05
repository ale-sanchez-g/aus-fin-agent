import structlog
from sqlalchemy.orm import Session

from app.services.openbanking_adapter_client import AdapterClient
from app.repositories.product_repository import ProductRepository
from app.repositories.provider_repository import ProviderRepository

log = structlog.get_logger()


def sync_provider_products(db: Session, provider_id: str) -> int:
    """
    Sync products from the Node adapter for the given provider.
    Returns the number of records synced.
    """
    import asyncio

    async def _fetch():
        client = AdapterClient()
        try:
            return await client.get_products(provider_id=provider_id)
        finally:
            await client.close()

    try:
        loop = asyncio.new_event_loop()
        raw_products: list[dict] = loop.run_until_complete(_fetch())
        loop.close()
    except Exception as exc:
        log.warning("adapter_fetch_failed_using_empty", provider_id=provider_id, error=str(exc))
        raw_products = []

    product_repo = ProductRepository(db)
    count = 0

    for raw in raw_products:
        try:
            _upsert_product(db, product_repo, provider_id, raw)
            count += 1
        except Exception as exc:
            log.error(
                "product_upsert_failed",
                provider_id=provider_id,
                product=raw.get("productId", "unknown"),
                error=str(exc),
            )

    db.flush()
    log.info("sync_complete", provider_id=provider_id, count=count)
    return count


def _upsert_product(db: Session, repo: ProductRepository, provider_id: str, raw: dict):
    """Create or update a product from raw CDR data."""
    from app.models.product import Product

    external_id = raw.get("productId") or raw.get("id")
    existing = (
        db.query(Product)
        .filter(Product.provider_id == provider_id, Product.external_product_id == external_id)
        .first()
    )

    features = [
        {"feature_type": f.get("featureType", f.get("feature_type", "")),
         "additional_value": f.get("additionalValue", f.get("additional_value")),
         "additional_info": f.get("additionalInfo", f.get("additional_info"))}
        for f in raw.get("features", []) or []
    ]
    rates = [
        {"rate_type": r.get("depositRateType", r.get("lendingRateType", r.get("rate_type", ""))),
         "rate": r.get("rate"),
         "tiers": r.get("tiers"),
         "additional_value": r.get("additionalValue", r.get("additional_value"))}
        for r in (raw.get("depositRates", []) or raw.get("lendingRates", []) or raw.get("rates", []) or [])
    ]
    fees = [
        {"fee_type": f.get("feeType", f.get("fee_type", "")),
         "name": f.get("name", "Fee"),
         "amount": f.get("amount"),
         "balance_rate": f.get("balanceRate", f.get("balance_rate")),
         "currency": f.get("currency", "AUD")}
        for f in raw.get("fees", []) or []
    ]

    product_data = {
        "provider_id": provider_id,
        "external_product_id": external_id,
        "name": raw.get("name", raw.get("productName", "Unknown")),
        "category": raw.get("productCategory", raw.get("category", "TRANS_AND_SAVINGS_ACCOUNTS")),
        "description": raw.get("description"),
        "brand": raw.get("brand"),
        "brand_name": raw.get("brandName", raw.get("brand_name")),
        "application_uri": raw.get("applicationUri", raw.get("application_uri")),
        "is_tailored": raw.get("isTailored", raw.get("is_tailored", False)),
        "is_active": True,
        "features": features,
        "rates": rates,
        "fees": fees,
        "eligibility": [],
    }

    if existing:
        existing.name = product_data["name"]
        existing.category = product_data["category"]
        existing.description = product_data["description"]
        existing.brand = product_data["brand"]
        existing.brand_name = product_data["brand_name"]
        existing.is_active = True
    else:
        repo.create_product(product_data)


def sync_all_providers(db: Session) -> dict[str, int]:
    """Sync products from all active providers."""
    provider_repo = ProviderRepository(db)
    providers = provider_repo.list_providers(active_only=True)
    results = {}
    for provider in providers:
        try:
            count = sync_provider_products(db, provider.id)
            results[provider.id] = count
        except Exception as exc:
            log.error("provider_sync_failed", provider_id=provider.id, error=str(exc))
            results[provider.id] = -1
    return results
