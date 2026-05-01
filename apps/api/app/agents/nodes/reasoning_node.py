import json
import structlog
from app.agents.state import AgentState
from app.core.config import settings

log = structlog.get_logger()


def _bedrock_narrative(
    scored_products: list[dict],
    user_intent: str,
    product_category: str,
    weight_profile: str,
) -> str:
    """Generate narrative via AWS Bedrock Claude."""
    import boto3

    top_3 = scored_products[:3]
    products_summary = [
        {
            "name": p.get("name", "Unknown"),
            "score": p.get("total_score", 0),
            "breakdown": p.get("score_breakdown", {}),
        }
        for p in top_3
    ]

    prompt = (
        f"You are an Australian financial product discovery assistant. "
        f"A user is looking for: '{user_intent}' in category '{product_category}'. "
        f"Using a '{weight_profile}' scoring profile, the top products are:\n"
        f"{json.dumps(products_summary, indent=2)}\n\n"
        "Write a concise, objective 2-3 paragraph narrative explaining the top recommendations. "
        "Do NOT give personal financial advice. Use discovery/informational language only. "
        "Mention key differentiators like fees, rates, and features."
    )

    bedrock = boto3.client("bedrock-runtime", region_name=settings.AWS_REGION)
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}],
        }
    )
    response = bedrock.invoke_model(modelId=settings.AWS_BEDROCK_MODEL_ID, body=body)
    response_body = json.loads(response["body"].read())
    return response_body["content"][0]["text"]


def _template_narrative(
    scored_products: list[dict],
    user_intent: str,
    product_category: str,
    weight_profile: str,
) -> str:
    """Fallback template-based narrative when Bedrock is unavailable."""
    if not scored_products:
        return (
            f"No products were found matching your criteria for {product_category}. "
            "Consider broadening your search parameters."
        )

    top = scored_products[0]
    second = scored_products[1] if len(scored_products) > 1 else None
    third = scored_products[2] if len(scored_products) > 2 else None

    category_display = product_category.replace("_", " ").title()

    narrative = (
        f"Based on your interest in {category_display}, our discovery engine evaluated "
        f"{len(scored_products)} eligible products using the '{weight_profile}' scoring profile.\n\n"
        f"The highest-scoring product is **{top.get('name', 'Unknown')}** "
        f"(score: {top.get('total_score', 0):.1f}/100). "
    )

    breakdown = top.get("score_breakdown", {})
    if breakdown:
        narrative += (
            f"It performs well across fees ({breakdown.get('monthly_fees', 0):.0f}/100), "
            f"rates ({breakdown.get('rate_competitiveness', 0):.0f}/100), and "
            f"features ({breakdown.get('feature_fit', 0):.0f}/100). "
        )

    if second:
        narrative += (
            f"\n\n**{second.get('name', 'Unknown')}** ranks second "
            f"(score: {second.get('total_score', 0):.1f}/100)"
        )
        if third:
            narrative += (
                f", followed by **{third.get('name', 'Unknown')}** "
                f"(score: {third.get('total_score', 0):.1f}/100)"
            )
        narrative += "."

    narrative += (
        "\n\nAll products listed are available through the Australian Consumer Data Right (CDR) "
        "open banking ecosystem. Rates and fees are subject to change — always verify current "
        "terms with the provider before applying."
    )

    return narrative


def reasoning_node(state: AgentState) -> dict:
    log.info("reasoning_node", session_id=state.get("session_id"))
    try:
        scored_products = state.get("scored_products") or []
        user_intent = state.get("user_intent", "")
        product_category = state.get("product_category", "")
        weight_profile = state.get("weight_profile", "balanced")

        narrative = ""

        # Attempt Bedrock if configured
        if settings.AWS_REGION and settings.AWS_BEDROCK_MODEL_ID:
            try:
                narrative = _bedrock_narrative(
                    scored_products, user_intent, product_category, weight_profile
                )
                log.info("bedrock_narrative_generated", session_id=state.get("session_id"))
            except Exception as exc:
                log.warning("bedrock_failed_using_template", error=str(exc))

        if not narrative:
            narrative = _template_narrative(
                scored_products, user_intent, product_category, weight_profile
            )

        return {**state, "narrative": narrative, "status": "reasoning_complete"}

    except Exception as exc:
        log.error("reasoning_node_error", error=str(exc))
        # Non-fatal: use empty narrative
        return {**state, "narrative": "", "status": "reasoning_complete"}
