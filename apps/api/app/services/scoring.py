from dataclasses import dataclass, asdict
from typing import Any
from enum import Enum
import re

DIGITAL_FEATURE_TYPES = {
    "DIGITAL_BANKING",
    "NPP_PAYID",
    "NPP_ENABLED",
    "DIGITAL_WALLET",
    "NOTIFICATIONS",
    "ALERTS",
}

VALUABLE_FEATURE_TYPES = {
    "FREE_TXNS",
    "FREE_TXNS_ALLOWANCE",
    "CASHBACK_OFFER",
    "BONUS_REWARDS",
    "INSURANCE",
    "TRAVEL_INSURANCE",
    "BALANCE_TRANSFERS",
}

_STOP_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}


class WeightProfile(str, Enum):
    BALANCED = "balanced"
    FEE_CONSCIOUS = "fee_conscious"
    RATE_FOCUSED = "rate_focused"
    FEATURE_RICH = "feature_rich"


WEIGHT_PROFILES: dict[WeightProfile, dict[str, float]] = {
    WeightProfile.BALANCED: {
        "monthly_fees": 0.20,
        "rate_competitiveness": 0.20,
        "feature_fit": 0.20,
        "eligibility_fit": 0.20,
        "digital_capability": 0.10,
        "suitability": 0.10,
    },
    WeightProfile.FEE_CONSCIOUS: {
        "monthly_fees": 0.40,
        "rate_competitiveness": 0.20,
        "feature_fit": 0.15,
        "eligibility_fit": 0.15,
        "digital_capability": 0.05,
        "suitability": 0.05,
    },
    WeightProfile.RATE_FOCUSED: {
        "monthly_fees": 0.10,
        "rate_competitiveness": 0.45,
        "feature_fit": 0.15,
        "eligibility_fit": 0.15,
        "digital_capability": 0.05,
        "suitability": 0.10,
    },
    WeightProfile.FEATURE_RICH: {
        "monthly_fees": 0.10,
        "rate_competitiveness": 0.15,
        "feature_fit": 0.35,
        "eligibility_fit": 0.15,
        "digital_capability": 0.15,
        "suitability": 0.10,
    },
}


@dataclass
class ScoreBreakdown:
    monthly_fees: float
    rate_competitiveness: float
    feature_fit: float
    eligibility_fit: float
    digital_capability: float
    suitability: float
    total: float
    weight_profile: str

    def to_dict(self) -> dict:
        return asdict(self)


def _parse_amount(value: Any) -> float:
    """Safely parse a monetary amount to float."""
    if value is None:
        return 0.0
    try:
        return float(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return 0.0


def _parse_rate(value: Any) -> float:
    """Safely parse a rate (decimal form, e.g. 0.0475) to float."""
    if value is None:
        return 0.0
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return 0.0


def _tokenize_text(value: str) -> set[str]:
    tokens = set(re.findall(r"[a-z0-9]{3,}", (value or "").lower()))
    return {token for token in tokens if token not in _STOP_WORDS}


class ScoringEngine:
    def score_product(
        self,
        product: dict,
        preferences: dict,
        profile: WeightProfile,
    ) -> ScoreBreakdown:
        weights = WEIGHT_PROFILES.get(profile, WEIGHT_PROFILES[WeightProfile.BALANCED])

        max_fee = preferences.get("max_monthly_fee") or preferences.get("max_fee")
        target_rate = preferences.get("target_rate")
        desired_features: list[str] = preferences.get("desired_features", [])

        fee_score = self.score_monthly_fees(product, max_fee)
        rate_score = self.score_rate(product, target_rate)
        feature_score = self.score_features(product, desired_features)
        eligibility_score = self.score_eligibility(product, preferences)
        digital_score = self.score_digital_capability(product)
        suitability_score = self.score_suitability(product, preferences)

        total = (
            weights["monthly_fees"] * fee_score
            + weights["rate_competitiveness"] * rate_score
            + weights["feature_fit"] * feature_score
            + weights["eligibility_fit"] * eligibility_score
            + weights["digital_capability"] * digital_score
            + weights["suitability"] * suitability_score
        )

        return ScoreBreakdown(
            monthly_fees=round(fee_score, 2),
            rate_competitiveness=round(rate_score, 2),
            feature_fit=round(feature_score, 2),
            eligibility_fit=round(eligibility_score, 2),
            digital_capability=round(digital_score, 2),
            suitability=round(suitability_score, 2),
            total=round(min(max(total, 0.0), 100.0), 2),
            weight_profile=profile,
        )

    def score_monthly_fees(
        self, product: dict, max_acceptable_fee: float = None
    ) -> float:
        """Score 0-100: higher is better (lower fees)."""
        fees: list[dict] = product.get("fees", []) or []
        periodic_fees = [
            f for f in fees if f.get("fee_type", "").upper() in ("PERIODIC", "MONTHLY")
        ]

        if not periodic_fees:
            # No periodic fee — perfect score
            return 100.0

        total_periodic = sum(_parse_amount(f.get("amount", 0)) for f in periodic_fees)

        if total_periodic == 0.0:
            return 100.0

        if max_acceptable_fee is not None and max_acceptable_fee > 0:
            if total_periodic > max_acceptable_fee:
                # Over cap — score drops proportionally
                excess_ratio = total_periodic / max_acceptable_fee
                return max(0.0, 100.0 - (excess_ratio - 1) * 50)
            ratio = total_periodic / max_acceptable_fee
            return round(100.0 - ratio * 40, 2)

        # No preference — use absolute scale: $0=100, $30+=0
        score = max(0.0, 100.0 - (total_periodic / 30.0) * 100.0)
        return round(score, 2)

    def score_rate(self, product: dict, target_rate: float = None) -> float:
        """Score 0-100 for rate competitiveness."""
        rates: list[dict] = product.get("rates", []) or []
        if not rates:
            return 50.0  # Neutral when no rate info

        # Look for deposit or lending rate
        deposit_rates = [
            r for r in rates if r.get("rate_type", "").upper() in ("DEPOSIT", "SAVINGS", "VARIABLE")
        ]
        lending_rates = [
            r for r in rates if r.get("rate_type", "").upper() in ("FIXED", "VARIABLE", "INTRODUCTORY")
        ]

        candidate_rates = deposit_rates or lending_rates or rates
        parsed = [_parse_rate(r.get("rate")) for r in candidate_rates if r.get("rate")]
        if not parsed:
            return 50.0

        best_rate = max(parsed)

        if target_rate is not None and target_rate > 0:
            ratio = best_rate / target_rate
            if ratio >= 1.0:
                return min(100.0, 80.0 + (ratio - 1.0) * 100)
            return round(ratio * 80.0, 2)

        # Benchmark: 0% = 0, 6%+ = 100 for deposits
        score = min(100.0, (best_rate / 0.06) * 100.0)
        return round(score, 2)

    def score_features(self, product: dict, desired_features: list[str] = None) -> float:
        """Score 0-100 based on feature richness and fit."""
        features: list[dict] = product.get("features", []) or []
        if not features:
            return 20.0

        feature_types = {f.get("feature_type", "").upper() for f in features}

        if desired_features:
            desired_upper = {d.upper() for d in desired_features}
            matched = len(desired_upper & feature_types)
            fit_score = (matched / len(desired_upper)) * 100.0 if desired_upper else 50.0
        else:
            # Score by breadth — cap at 20 features
            fit_score = min(100.0, (len(features) / 20.0) * 100.0)

        # Bonus for valuable features
        valuable_present = len(VALUABLE_FEATURE_TYPES & feature_types)
        bonus = min(20.0, valuable_present * 5.0)
        return round(min(100.0, fit_score + bonus), 2)

    def score_eligibility(self, product: dict, preferences: dict) -> float:
        """Score 0-100 based on eligibility rule compatibility."""
        rules: list[dict] = product.get("eligibility", []) or []
        if not rules:
            return 80.0  # Open product — good for most

        score = 80.0
        for rule in rules:
            rule_type = rule.get("eligibility_type", "").upper()
            value = rule.get("additional_value", "")

            if rule_type == "MIN_AGE":
                try:
                    min_age = int(value or 0)
                    client_age = preferences.get("age")
                    if client_age and client_age < min_age:
                        return 0.0
                except (ValueError, TypeError):
                    pass
            elif rule_type == "EMPLOYMENT_STATUS":
                client_employment = preferences.get("employment_status", "")
                if client_employment and value and client_employment.upper() != value.upper():
                    score -= 20.0
            elif rule_type == "RESIDENCY_STATUS":
                if value and value.upper() == "CITIZEN":
                    score -= 5.0  # Slight penalty for citizenship requirement

        return max(0.0, round(score, 2))

    def score_digital_capability(self, product: dict) -> float:
        """Score 0-100 based on digital banking features."""
        features: list[dict] = product.get("features", []) or []
        feature_types = {f.get("feature_type", "").upper() for f in features}
        digital_count = len(DIGITAL_FEATURE_TYPES & feature_types)
        return round(min(100.0, (digital_count / len(DIGITAL_FEATURE_TYPES)) * 100.0), 2)

    def score_suitability(self, product: dict, preferences: dict) -> float:
        """Score 0-100 based on overall suitability signals."""
        score = 60.0  # Base suitability

        # Active and not tailored products score higher for general discovery
        if product.get("is_active", True):
            score += 10.0
        if not product.get("is_tailored", False):
            score += 10.0

        # Products with full info score higher
        if product.get("description"):
            score += 5.0
        if product.get("application_uri"):
            score += 5.0
        rates = product.get("rates") or []
        fees = product.get("fees") or []
        if rates:
            score += 5.0
        if fees:
            score += 5.0

        # When product metadata is sparse, use lexical intent matching to
        # differentiate similarly structured products.
        user_intent = str(preferences.get("user_intent") or "")
        if user_intent:
            intent_tokens = _tokenize_text(user_intent)
            product_text = " ".join(
                str(v)
                for v in [
                    product.get("name"),
                    product.get("description"),
                    product.get("category"),
                    product.get("brand"),
                    product.get("brand_name"),
                ]
                if v
            )
            product_tokens = _tokenize_text(product_text)
            if intent_tokens and product_tokens:
                overlap_ratio = len(intent_tokens & product_tokens) / len(intent_tokens)
                score += min(15.0, overlap_ratio * 15.0)

        return round(min(100.0, score), 2)


scoring_engine = ScoringEngine()
