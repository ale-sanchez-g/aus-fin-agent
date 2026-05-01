import structlog
from app.agents.state import AgentState

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

    return []


def _product_summary_to_dict(product) -> dict:
    """Convert ProductSummary schema or ORM object to dict for agent processing."""
    if hasattr(product, "model_dump"):
        return product.model_dump()
    if hasattr(product, "__dict__"):
        return {k: v for k, v in product.__dict__.items() if not k.startswith("_")}
    return dict(product)
