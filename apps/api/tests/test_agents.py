import pytest
from app.agents.graph import build_discovery_graph
from app.agents.nodes.scoring_node import scoring_node
from app.agents.state import AgentState


def test_graph_builds():
    graph = build_discovery_graph()
    assert graph is not None


def test_scoring_node_empty_products():
    state = AgentState(
        session_id="test-123",
        user_intent="savings account",
        product_category="TRANS_AND_SAVINGS_ACCOUNTS",
        preferences={},
        constraints={},
        weight_profile="balanced",
        products=[],
        eligible_products=[],
        scored_products=[],
        narrative="",
        compliance_notes=[],
        report={},
        error=None,
        status="running",
    )
    result = scoring_node(state)
    assert result["scored_products"] == []


def test_eligibility_node_filters_correctly():
    from app.agents.nodes.eligibility_node import eligibility_node

    state = AgentState(
        session_id="test-456",
        user_intent="savings account",
        product_category="TRANS_AND_SAVINGS_ACCOUNTS",
        preferences={},
        constraints={"max_monthly_fee": 5.0},
        weight_profile="balanced",
        products=[
            {"id": "1", "name": "Free Account", "fees": [{"fee_type": "PERIODIC", "amount": "0.00"}]},
            {"id": "2", "name": "Premium Account", "fees": [{"fee_type": "PERIODIC", "amount": "15.00"}]},
        ],
        eligible_products=[],
        scored_products=[],
        narrative="",
        compliance_notes=[],
        report={},
        error=None,
        status="running",
    )
    result = eligibility_node(state)
    assert len(result["eligible_products"]) == 1
    assert result["eligible_products"][0]["id"] == "1"


def test_scoring_node_scores_and_sorts():
    state = AgentState(
        session_id="test-789",
        user_intent="best savings account",
        product_category="TRANS_AND_SAVINGS_ACCOUNTS",
        preferences={"target_rate": 0.04},
        constraints={},
        weight_profile="balanced",
        products=[],
        eligible_products=[
            {
                "id": "a",
                "name": "High Rate Account",
                "fees": [{"fee_type": "PERIODIC", "amount": "0.00"}],
                "rates": [{"rate_type": "DEPOSIT", "rate": "0.055"}],
                "features": [{"feature_type": "DIGITAL_BANKING"}],
            },
            {
                "id": "b",
                "name": "Low Rate Account",
                "fees": [{"fee_type": "PERIODIC", "amount": "15.00"}],
                "rates": [{"rate_type": "DEPOSIT", "rate": "0.01"}],
                "features": [],
            },
        ],
        scored_products=[],
        narrative="",
        compliance_notes=[],
        report={},
        error=None,
        status="running",
    )
    result = scoring_node(state)
    scored = result["scored_products"]
    assert len(scored) == 2
    # First product (high rate, no fee) should score higher
    assert scored[0]["total_score"] >= scored[1]["total_score"]
    assert scored[0]["id"] == "a"


def test_intake_node_infers_category():
    from app.agents.nodes.intake_node import intake_node

    state = AgentState(
        session_id="test-intake",
        user_intent="I want a credit card with cashback",
        product_category=None,
        preferences={},
        constraints={},
        weight_profile="balanced",
        products=[],
        eligible_products=[],
        scored_products=[],
        narrative="",
        compliance_notes=[],
        report={},
        error=None,
        status="pending",
    )
    result = intake_node(state)
    assert result["product_category"] == "CRED_AND_CHRG_CARDS"


def test_compliance_node_strips_prescriptive_language():
    from app.agents.nodes.compliance_node import compliance_node

    state = AgentState(
        session_id="test-compliance",
        user_intent="savings account",
        product_category="TRANS_AND_SAVINGS_ACCOUNTS",
        preferences={},
        constraints={},
        weight_profile="balanced",
        products=[],
        eligible_products=[],
        scored_products=[],
        narrative="You should open this account because we recommend it.",
        compliance_notes=[],
        report={},
        error=None,
        status="running",
    )
    result = compliance_node(state)
    assert "you should" not in result["narrative"].lower()
    assert "we recommend" not in result["narrative"].lower()
    assert len(result["compliance_notes"]) > 0


def test_retrieval_normalizes_adapter_product_shape():
    from app.agents.nodes.retrieval_node import _normalize_adapter_product

    raw = {
        "productId": "prod-123",
        "providerId": "provider-1",
        "productName": "Travel Rewards Card",
        "productCategory": "CRED_AND_CHRG_CARDS",
        "features": [{"featureType": "TRAVEL_INSURANCE"}],
        "depositRates": [{"depositRateType": "VARIABLE", "rate": "0.049"}],
        "fees": [{"feeType": "PERIODIC", "name": "Monthly fee", "amount": "10"}],
    }

    normalized = _normalize_adapter_product(raw)
    assert normalized["external_product_id"] == "prod-123"
    assert normalized["name"] == "Travel Rewards Card"
    assert normalized["features"][0]["feature_type"] == "TRAVEL_INSURANCE"
    assert normalized["rates"][0]["rate_type"] == "VARIABLE"
    assert normalized["fees"][0]["fee_type"] == "PERIODIC"


def test_retrieval_adapter_fallback_tries_credit_cards_for_travel(monkeypatch):
    from app.agents.nodes import retrieval_node as retrieval

    calls = []

    async def fake_get_products(provider_id=None, category=None):
        calls.append(category)
        if category == "TRAVEL_CARDS":
            return []
        return [{"productId": "prod-456", "name": "Fallback Card", "productCategory": "CRED_AND_CHRG_CARDS"}]

    monkeypatch.setattr(retrieval.adapter_client, "get_products", fake_get_products)

    products = retrieval._fetch_products_from_adapter("TRAVEL_CARDS", "session-1")
    assert calls == ["TRAVEL_CARDS", "CRED_AND_CHRG_CARDS"]
    assert len(products) == 1
    assert products[0]["name"] == "Fallback Card"
