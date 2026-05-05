import structlog
import json
import re
from collections import defaultdict, deque
from app.agents.state import AgentState
from app.services.scoring import ScoringEngine, WeightProfile
from app.core.config import settings

log = structlog.get_logger()
_scoring_engine = ScoringEngine()

GOAL_KEYWORDS = {
    "save",
    "saving",
    "holiday",
    "trip",
    "travel",
    "goal",
    "short",
    "term",
}

SAVINGS_PRODUCT_KEYWORDS = {
    "savings",
    "term deposit",
    "deposit",
    "notice saver",
    "account",
}

SEGMENT_KEYWORDS: dict[str, set[str]] = {
    "agriculture": {"farm", "farming", "farmer", "primary producer", "agribusiness", "rural"},
    "business": {"business", "commercial", "merchant", "enterprise", "sme"},
    "retirement": {"retirement", "retiree", "pension", "super", "smsf"},
    "student": {"student", "youth", "apprentice"},
}


def _contains_any(text: str, keywords: set[str]) -> bool:
    lowered = (text or "").lower()
    return any(keyword in lowered for keyword in keywords)


def _extract_month_horizon(user_intent: str) -> int | None:
    match = re.search(r"\b(\d{1,2})\s*(?:month|months|mo)\b", (user_intent or "").lower())
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def _heuristic_intent_relevance(product: dict, user_intent: str, product_category: str | None) -> float:
    intent = (user_intent or "").lower()
    text = " ".join(
        str(v)
        for v in [
            product.get("name"),
            product.get("description"),
            product.get("category"),
            product.get("brand"),
            product.get("brand_name"),
        ]
        if v
    ).lower()

    score = 55.0

    product_category_value = str(product.get("category") or "")
    if product_category and product_category_value:
        if product_category_value.upper() == str(product_category).upper():
            score += 10.0
        else:
            score -= 15.0

    for keywords in SEGMENT_KEYWORDS.values():
        if _contains_any(text, keywords) and not _contains_any(intent, keywords):
            score -= 40.0

    if _contains_any(intent, GOAL_KEYWORDS):
        if _contains_any(text, SAVINGS_PRODUCT_KEYWORDS):
            score += 15.0
        if _contains_any(text, {"loan", "credit card", "mortgage", "lease"}):
            score -= 20.0

    months = _extract_month_horizon(intent)
    if months is not None and months <= 6:
        if _contains_any(text, {"notice", "31 day", "90 day"}):
            score -= 10.0
        if _contains_any(text, {"3 month", "90 days", "short term", "term"}):
            score += 8.0

    return round(min(max(score, 0.0), 100.0), 2)


def _llm_relevance_scores(scored: list[dict], user_intent: str, product_category: str | None) -> dict[str, float]:
    if not settings.FEATURE_FLAG_LLM_RERANK:
        return {}
    if not settings.AWS_REGION or not settings.AWS_BEDROCK_MODEL_ID:
        return {}

    try:
        import boto3

        subset = scored[:20]
        payload_products = [
            {
                "id": str(product.get("id") or product.get("external_product_id") or product.get("name") or "unknown"),
                "name": product.get("name"),
                "description": product.get("description"),
                "category": product.get("category"),
                "provider": product.get("brand_name") or product.get("brand"),
                "eligibility": product.get("eligibility", []),
            }
            for product in subset
        ]

        prompt = (
            "You are ranking relevance of Australian banking products to a user request. "
            "Return ONLY valid JSON object mapping product id to relevance score 0-100. "
            "Penalize products targeted to niche segments not requested (e.g., farm/primary producer products for generic holiday savings).\n\n"
            f"User intent: {user_intent}\n"
            f"Requested category: {product_category}\n"
            f"Products: {json.dumps(payload_products, ensure_ascii=True)}"
        )

        bedrock = boto3.client("bedrock-runtime", region_name=settings.AWS_REGION)
        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 800,
                "messages": [{"role": "user", "content": prompt}],
            }
        )
        response = bedrock.invoke_model(modelId=settings.AWS_BEDROCK_MODEL_ID, body=body)
        response_body = json.loads(response["body"].read())
        raw_text = response_body["content"][0]["text"]
        json_match = re.search(r"\{[\s\S]*\}", raw_text)
        if not json_match:
            return {}

        parsed = json.loads(json_match.group(0))
        relevance_scores: dict[str, float] = {}
        for product_id, value in parsed.items():
            try:
                relevance_scores[str(product_id)] = float(value)
            except (ValueError, TypeError):
                continue

        return relevance_scores
    except Exception as exc:
        log.warning("llm_rerank_failed", error=str(exc))
        return {}


def _apply_intent_relevance(scored: list[dict], user_intent: str, product_category: str | None) -> tuple[list[dict], dict]:
    if not scored:
        return scored, {"intent_relevance_applied": False, "llm_rerank_applied": False}

    llm_scores = _llm_relevance_scores(scored, user_intent, product_category)
    llm_applied = bool(llm_scores)

    for product in scored:
        product_id = str(product.get("id") or product.get("external_product_id") or product.get("name") or "unknown")
        relevance = llm_scores.get(
            product_id,
            _heuristic_intent_relevance(product, user_intent, product_category),
        )
        base_total = float(product.get("total_score", 0.0))
        adjusted_total = round(min(max((base_total * 0.75) + (relevance * 0.25), 0.0), 100.0), 2)
        product["total_score"] = adjusted_total
        breakdown = product.get("score_breakdown")
        if isinstance(breakdown, dict):
            breakdown["intent_relevance"] = round(relevance, 2)
            breakdown["total"] = adjusted_total

    return scored, {"intent_relevance_applied": True, "llm_rerank_applied": llm_applied}


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
        scored, relevance_metadata = _apply_intent_relevance(
            scored,
            state.get("user_intent", ""),
            state.get("product_category"),
        )
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
            **relevance_metadata,
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
