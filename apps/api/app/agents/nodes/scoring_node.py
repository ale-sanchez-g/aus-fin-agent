import structlog
from collections import defaultdict, deque
from app.agents.state import AgentState
from app.services.scoring import ScoringEngine, WeightProfile

log = structlog.get_logger()
_scoring_engine = ScoringEngine()


def _provider_key(product: dict) -> str:
    provider = product.get("provider_id") or product.get("brand_name") or product.get("brand")
    return str(provider or "unknown").strip().lower()


def _diversify_tied_scores(scored: list[dict]) -> tuple[list[dict], bool]:
    """Interleave providers within identical score buckets.

    This avoids one provider dominating top recommendations when many products
    are tied on score due to sparse upstream attributes.
    """
    if not scored:
        return scored, False

    score_groups: dict[float, list[dict]] = defaultdict(list)
    for product in scored:
        score_groups[float(product.get("total_score", 0.0))].append(product)

    diversified: list[dict] = []
    tie_diversification_applied = False
    for score in sorted(score_groups.keys(), reverse=True):
        bucket = score_groups[score]
        by_provider: dict[str, deque[dict]] = defaultdict(deque)
        provider_order: list[str] = []

        for product in bucket:
            key = _provider_key(product)
            if key not in by_provider:
                provider_order.append(key)
            by_provider[key].append(product)

        if len(bucket) > 1 and len(by_provider) > 1:
            tie_diversification_applied = True

        added = True
        while added:
            added = False
            for key in provider_order:
                queue = by_provider.get(key)
                if queue:
                    diversified.append(queue.popleft())
                    added = True

    return diversified, tie_diversification_applied


def _spread_tied_scores(scored: list[dict], step: float = 0.1) -> tuple[list[dict], bool]:
    """Apply small deterministic deltas to tied totals while preserving order.

    This keeps ranking stable but avoids rendering identical percentages when
    upstream data is too sparse to produce naturally distinct totals.
    """
    if not scored:
        return scored, False

    tie_spread_applied = False
    index = 0
    while index < len(scored):
        base_score = float(scored[index].get("total_score", 0.0))
        group_end = index + 1
        while group_end < len(scored) and float(scored[group_end].get("total_score", 0.0)) == base_score:
            group_end += 1

        group_size = group_end - index
        if group_size > 1:
            tie_spread_applied = True
            for offset in range(group_size):
                adjusted = round(max(0.0, base_score - (offset * step)), 2)
                scored[index + offset]["total_score"] = adjusted
                breakdown = scored[index + offset].get("score_breakdown")
                if isinstance(breakdown, dict):
                    breakdown["total"] = adjusted

        index = group_end

    return scored, tie_spread_applied


def scoring_node(state: AgentState) -> dict:
    log.info("scoring_node", session_id=state.get("session_id"))
    try:
        eligible: list[dict] = state.get("eligible_products") or []
        preferences: dict = state.get("preferences") or {}
        constraints: dict = state.get("constraints") or {}
        weight_profile_str = state.get("weight_profile") or "balanced"

        # Merge constraints into preferences for scoring
        merged_prefs = {
            **preferences,
            **constraints,
            "user_intent": state.get("user_intent", ""),
        }

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
        scored, tie_diversification_applied = _diversify_tied_scores(scored)
        scored, tie_spread_applied = _spread_tied_scores(scored)

        log.info(
            "scoring_complete",
            scored=len(scored),
            top_score=scored[0]["total_score"] if scored else 0,
            session_id=state.get("session_id"),
        )
        ranking_metadata = {
            "tie_diversification_applied": tie_diversification_applied,
            "tie_spread_applied": tie_spread_applied,
        }
        return {
            **state,
            "scored_products": scored,
            "ranking_metadata": ranking_metadata,
            "status": "scoring_complete",
        }

    except Exception as exc:
        log.error("scoring_node_error", error=str(exc))
        return {**state, "error": f"Scoring failed: {exc}", "status": "failed"}
