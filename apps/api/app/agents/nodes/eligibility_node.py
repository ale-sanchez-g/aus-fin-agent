import structlog
from app.agents.state import AgentState

log = structlog.get_logger()

VEHICLE_KEYWORDS = {"car", "auto", "vehicle", "motor", "ute", "truck"}


def _contains_keyword(text: str, keywords: set[str]) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)


def _matches_intent(product: dict, user_intent: str) -> bool:
    if not user_intent:
        return True

    searchable = " ".join(
        str(value)
        for value in [
            product.get("name"),
            product.get("description"),
            product.get("category"),
        ]
        if value
    )

    product_is_vehicle_specific = _contains_keyword(searchable, VEHICLE_KEYWORDS)
    intent_mentions_vehicle = _contains_keyword(user_intent, VEHICLE_KEYWORDS)

    if product_is_vehicle_specific and not intent_mentions_vehicle:
        return False

    return True


def _get_periodic_fee(product: dict) -> float:
    fees: list[dict] = product.get("fees", []) or []
    total = 0.0
    for fee in fees:
        if fee.get("fee_type", "").upper() in ("PERIODIC", "MONTHLY"):
            try:
                total += float(str(fee.get("amount", 0) or 0).replace(",", ""))
            except (ValueError, TypeError):
                pass
    return total


def _get_best_rate(product: dict, rate_types: set[str]) -> float | None:
    rates: list[dict] = product.get("rates", []) or []
    candidates = [
        r for r in rates if r.get("rate_type", "").upper() in rate_types and r.get("rate")
    ]
    if not candidates:
        return None
    parsed = []
    for r in candidates:
        try:
            parsed.append(float(str(r["rate"]).strip()))
        except (ValueError, TypeError):
            pass
    return max(parsed) if parsed else None


def eligibility_node(state: AgentState) -> dict:
    log.info("eligibility_node", session_id=state.get("session_id"))
    try:
        products: list[dict] = state.get("products") or []
        constraints: dict = state.get("constraints") or {}
        user_intent = state.get("user_intent", "")

        max_monthly_fee = constraints.get("max_monthly_fee")
        min_rate = constraints.get("min_rate")
        max_rate = constraints.get("max_rate")
        min_deposit = constraints.get("min_deposit")
        residency = constraints.get("residency_status")

        eligible = []
        for product in products:
            if not _matches_intent(product, user_intent):
                continue

            # Fee constraint
            if max_monthly_fee is not None:
                fee = _get_periodic_fee(product)
                if fee > float(max_monthly_fee):
                    continue

            # Rate constraints (deposit rate)
            deposit_rate = _get_best_rate(
                product, {"DEPOSIT", "SAVINGS", "VARIABLE", "FIXED", "INTRODUCTORY"}
            )
            if min_rate is not None and deposit_rate is not None:
                if deposit_rate < float(min_rate):
                    continue
            if max_rate is not None and deposit_rate is not None:
                if deposit_rate > float(max_rate):
                    continue

            # Eligibility rules check
            rules: list[dict] = product.get("eligibility", []) or []
            failed = False
            for rule in rules:
                rule_type = rule.get("eligibility_type", "").upper()
                value = rule.get("additional_value", "")
                if rule_type == "RESIDENCY_STATUS" and residency:
                    if value and value.upper() != residency.upper():
                        failed = True
                        break
                elif rule_type == "MIN_AGE":
                    client_age = constraints.get("age")
                    if client_age:
                        try:
                            if client_age < int(value or 0):
                                failed = True
                                break
                        except (ValueError, TypeError):
                            pass

            if failed:
                continue

            eligible.append(product)

        log.info(
            "eligibility_complete",
            total=len(products),
            eligible=len(eligible),
            session_id=state.get("session_id"),
        )
        return {**state, "eligible_products": eligible, "status": "eligibility_complete"}

    except Exception as exc:
        log.error("eligibility_node_error", error=str(exc))
        return {**state, "error": f"Eligibility filtering failed: {exc}", "status": "failed"}
