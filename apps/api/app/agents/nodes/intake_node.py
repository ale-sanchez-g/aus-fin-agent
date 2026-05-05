import re
import structlog
from app.agents.state import AgentState

log = structlog.get_logger()

CDR_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "TRANS_AND_SAVINGS_ACCOUNTS": [
        "savings", "transaction", "everyday", "account", "deposit", "high interest",
    ],
    "TERM_DEPOSITS": ["term deposit", "fixed term", "td", "fixed deposit"],
    "RESIDENTIAL_MORTGAGES": [
        "mortgage", "home loan", "property", "house", "refinance", "investment property",
    ],
    "CRED_AND_CHRG_CARDS": ["credit card", "charge card", "card", "rewards card"],
    "PERS_LOANS": ["personal loan", "car loan", "auto loan", "vehicle loan"],
    "BUSINESS_LOANS": ["business loan", "sme", "commercial loan"],
    "OVERDRAFTS": ["overdraft", "line of credit"],
    "LEASES": ["lease", "equipment finance"],
}

WEIGHT_PROFILE_KEYWORDS: dict[str, list[str]] = {
    "fee_conscious": ["no fee", "low fee", "cheap", "free", "cost", "affordable"],
    "rate_focused": ["best rate", "high rate", "interest", "return", "yield"],
    "feature_rich": ["features", "rewards", "perks", "benefits", "cashback"],
    "balanced": [],
}


def _infer_category(intent: str, explicit_category: str | None) -> str:
    if explicit_category:
        return explicit_category
    lower = intent.lower()
    for category, keywords in CDR_CATEGORY_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return category
    return "TRANS_AND_SAVINGS_ACCOUNTS"


def _infer_weight_profile(intent: str, explicit_profile: str | None) -> str:
    if explicit_profile and explicit_profile != "balanced":
        return explicit_profile
    lower = intent.lower()
    for profile, keywords in WEIGHT_PROFILE_KEYWORDS.items():
        if keywords and any(kw in lower for kw in keywords):
            return profile
    return "balanced"


def _extract_fee_constraint(intent: str) -> float | None:
    patterns = [
        r"(?:no more than|under|less than|max|maximum)\s*\$?(\d+(?:\.\d+)?)\s*(?:per month|monthly|/month)?",
        r"\$(\d+(?:\.\d+)?)\s*(?:or less|max|maximum)?\s*(?:per month|monthly|/month)",
    ]
    for pattern in patterns:
        match = re.search(pattern, intent.lower())
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
    return None


def intake_node(state: AgentState) -> dict:
    log.info("intake_node", session_id=state.get("session_id"))
    try:
        user_intent = state.get("user_intent", "")
        preferences = dict(state.get("preferences") or {})
        constraints = dict(state.get("constraints") or {})

        # Infer category if not set
        product_category = _infer_category(user_intent, state.get("product_category"))

        # Infer weight profile from intent
        weight_profile = _infer_weight_profile(user_intent, state.get("weight_profile"))

        # Extract fee constraints from natural language
        fee_constraint = _extract_fee_constraint(user_intent)
        if fee_constraint is not None and "max_monthly_fee" not in constraints:
            constraints["max_monthly_fee"] = fee_constraint

        return {
            **state,
            "product_category": product_category,
            "weight_profile": weight_profile,
            "preferences": preferences,
            "constraints": constraints,
            "status": "intake_complete",
        }
    except Exception as exc:
        log.error("intake_node_error", error=str(exc))
        return {**state, "error": f"Intake failed: {exc}", "status": "failed"}
