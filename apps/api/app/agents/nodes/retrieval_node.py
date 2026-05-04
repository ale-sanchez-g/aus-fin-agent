import structlog
import asyncio
from app.agents.state import AgentState
from app.services.openbanking_adapter_client import adapter_client

log = structlog.get_logger()


def retrieval_node(state: AgentState) -> dict:
    log.info("retrieval_node", session_id=state.get("session_id"))
    try:
        products = _fetch_products(
            category=state.get("product_category"),
            session_id=state.get("session_id"),
        )
        log.info("retrieval_complete", count=len(products), session_id=state.get("session_id"))
        return {**state, "products": products, "status": "retrieval_complete"}
    except Exception as exc:
        log.error("retrieval_node_error", error=str(exc))
        return {**state, "error": f"Retrieval failed: {exc}", "status": "failed"}


def _fetch_products(category: str | None, session_id: str | None) -> list[dict]:
    """Fetch products from DB, falling back to adapter."""
    try:
        from app.db.session import SessionLocal
        from app.repositories.product_repository import ProductRepository

        db = SessionLocal()
        try:
            repo = ProductRepository(db)
            items, total = repo.list_products(
                page=1,
                page_size=200,
                category=category,
                is_active=True,
            )
            if items:
                return [_product_summary_to_dict(p) for p in items]
        finally:
            db.close()
    except Exception as exc:
        log.warning("db_fetch_failed", error=str(exc))

    return _fetch_products_from_adapter(category, session_id)


def _fetch_products_from_adapter(category: str | None, session_id: str | None) -> list[dict]:
    """Fetch products from MCP adapter when DB has no product inventory."""
    categories = _category_candidates(category)
    try:
        products: list[dict] = []
        for c in categories:
            raw = asyncio.run(adapter_client.get_products(category=c))
            if raw:
                products.extend(_normalize_adapter_product(p) for p in raw)

        deduped = _dedupe_products(products)
        log.info(
            "mcp_retrieval_complete",
            category=category,
            attempted_categories=categories,
            count=len(deduped),
            session_id=session_id,
        )
        return deduped
    except Exception as exc:
        log.warning("mcp_retrieval_failed", error=str(exc), session_id=session_id)
        return []


def _category_candidates(category: str | None) -> list[str | None]:
    if not category:
        return [None]
    # Some CDR catalogs classify travel cards under credit cards and vice versa.
    if category == "TRAVEL_CARDS":
        return ["TRAVEL_CARDS", "CRED_AND_CHRG_CARDS"]
    if category == "CRED_AND_CHRG_CARDS":
        return ["CRED_AND_CHRG_CARDS", "TRAVEL_CARDS"]
    return [category]


def _normalize_adapter_product(raw: dict) -> dict:
    rates_source = (
        raw.get("depositRates")
        or raw.get("lendingRates")
        or raw.get("rates")
        or []
    )

    features = [
        {
            "feature_type": f.get("featureType", f.get("feature_type", "")),
            "additional_value": f.get("additionalValue", f.get("additional_value")),
            "additional_info": f.get("additionalInfo", f.get("additional_info")),
        }
        for f in (raw.get("features") or [])
    ]

    rates = [
        {
            "rate_type": r.get(
                "depositRateType",
                r.get("lendingRateType", r.get("rateType", r.get("rate_type", ""))),
            ),
            "rate": r.get("rate"),
            "comparison_rate": r.get("comparisonRate", r.get("comparison_rate")),
            "tiers": r.get("tiers"),
            "additional_value": r.get("additionalValue", r.get("additional_value")),
        }
        for r in rates_source
    ]

    fees = [
        {
            "fee_type": f.get("feeType", f.get("fee_type", "")),
            "name": f.get("name", "Fee"),
            "amount": f.get("amount"),
            "balance_rate": f.get("balanceRate", f.get("balance_rate")),
            "transaction_rate": f.get("transactionRate", f.get("transaction_rate")),
            "currency": f.get("currency", "AUD"),
            "additional_info": f.get("additionalInfo", f.get("additional_info")),
        }
        for f in (raw.get("fees") or [])
    ]

    eligibility = [
        {
            "eligibility_type": e.get("eligibilityType", e.get("eligibility_type", "")),
            "additional_value": e.get("additionalValue", e.get("additional_value")),
            "additional_info": e.get("additionalInfo", e.get("additional_info")),
        }
        for e in (raw.get("eligibility") or [])
    ]

    external_id = raw.get("productId") or raw.get("id")
    return {
        "id": external_id or raw.get("name") or "unknown-product",
        "external_product_id": external_id,
        "provider_id": raw.get("providerId") or raw.get("provider_id"),
        "name": raw.get("name", raw.get("productName", "Unknown")),
        "category": raw.get("productCategory", raw.get("category")),
        "description": raw.get("description"),
        "brand": raw.get("brand"),
        "brand_name": raw.get("brandName", raw.get("brand_name")),
        "application_uri": raw.get("applicationUri", raw.get("application_uri")),
        "is_tailored": raw.get("isTailored", raw.get("is_tailored", False)),
        "is_active": bool(raw.get("isActive", True)),
        "features": features,
        "rates": rates,
        "fees": fees,
        "eligibility": eligibility,
    }


def _dedupe_products(products: list[dict]) -> list[dict]:
    seen: set[str] = set()
    deduped: list[dict] = []
    for product in products:
        key = (
            str(product.get("external_product_id") or "")
            or str(product.get("id") or "")
            or str(product.get("name") or "")
        )
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(product)
    return deduped


def _product_summary_to_dict(product) -> dict:
    """Convert ProductSummary schema or ORM object to dict for agent processing."""
    if hasattr(product, "model_dump"):
        return product.model_dump()
    if hasattr(product, "__dict__"):
        return {k: v for k, v in product.__dict__.items() if not k.startswith("_")}
    return dict(product)
