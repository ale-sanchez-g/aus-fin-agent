import structlog
from app.agents.state import AgentState
from app.services.scoring import ScoringEngine, WeightProfile

log = structlog.get_logger()
_scoring_engine = ScoringEngine()


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
