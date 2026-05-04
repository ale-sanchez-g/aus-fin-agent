import structlog
from collections import defaultdict, deque
from app.agents.state import AgentState
from app.services.scoring import ScoringEngine, WeightProfile

log = structlog.get_logger()
_scoring_engine = ScoringEngine()


def _provider_key(product: dict) -> str:
    provider = product.get("provider_id") or product.get("brand_name") or product.get("brand")
    return str(provider or "unknown").strip().lower()


def _diversify_tied_scores(scored: list[dict]) -> list[dict]:
    """Interleave providers within identical score buckets.

    This avoids one provider dominating top recommendations when many products
    are tied on score due to sparse upstream attributes.
    """
    if not scored:
        return scored

    score_groups: dict[float, list[dict]] = defaultdict(list)
    for product in scored:
        score_groups[float(product.get("total_score", 0.0))].append(product)

    diversified: list[dict] = []
    for score in sorted(score_groups.keys(), reverse=True):
        bucket = score_groups[score]
        by_provider: dict[str, deque[dict]] = defaultdict(deque)
        provider_order: list[str] = []

        for product in bucket:
            key = _provider_key(product)
            if key not in by_provider:
                provider_order.append(key)
            by_provider[key].append(product)

        added = True
        while added:
            added = False
            for key in provider_order:
                queue = by_provider.get(key)
                if queue:
                    diversified.append(queue.popleft())
                    added = True

    return diversified


def scoring_node(state: AgentState) -> dict:
    log.info("scoring_node", session_id=state.get("session_id"))
    try:
        eligible: list[dict] = state.get("eligible_products") or []
        preferences: dict = state.get("preferences") or {}
        constraints: dict = state.get("constraints") or {}
        weight_profile_str = state.get("weight_profile") or "balanced"

        # Merge constraints into preferences for scoring
        merged_prefs = {**preferences, **constraints}

        try:
            profile = WeightProfile(weight_profile_str)
        except ValueError:
            profile = WeightProfile.BALANCED

        scored = []
        for product in eligible:
            breakdown = _scoring_engine.score_product(product, merged_prefs, profile)
            scored_product = {
                **product,
                "total_score": breakdown.total,
                "score_breakdown": breakdown.to_dict(),
            }
            scored.append(scored_product)

        scored.sort(key=lambda p: p["total_score"], reverse=True)
        scored = _diversify_tied_scores(scored)

        log.info(
            "scoring_complete",
            scored=len(scored),
            top_score=scored[0]["total_score"] if scored else 0,
            session_id=state.get("session_id"),
        )
        return {**state, "scored_products": scored, "status": "scoring_complete"}

    except Exception as exc:
        log.error("scoring_node_error", error=str(exc))
        return {**state, "error": f"Scoring failed: {exc}", "status": "failed"}
