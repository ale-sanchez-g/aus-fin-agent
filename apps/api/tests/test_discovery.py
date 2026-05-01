import pytest
from app.schemas.discovery import CreateDiscoveryRequest


def test_create_discovery_session(client):
    payload = {
        "user_intent": "I want a savings account with no monthly fees",
        "product_category": "TRANS_AND_SAVINGS_ACCOUNTS",
        "preferences": {"target_rate": 0.04},
        "constraints": {"max_monthly_fee": 0.0},
        "weight_profile": "fee_conscious",
    }
    response = client.post("/api/v1/discovery/sessions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] in ("pending", "running", "completed", "failed")
    assert data["product_category"] == "TRANS_AND_SAVINGS_ACCOUNTS"


def test_get_discovery_session(client):
    # Create first
    payload = {
        "user_intent": "home loan",
        "product_category": "RESIDENTIAL_MORTGAGES",
        "weight_profile": "rate_focused",
    }
    create_resp = client.post("/api/v1/discovery/sessions", json=payload)
    assert create_resp.status_code == 201
    session_id = create_resp.json()["id"]

    # Get it
    get_resp = client.get(f"/api/v1/discovery/sessions/{session_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["id"] == session_id
    assert data["product_category"] == "RESIDENTIAL_MORTGAGES"


def test_get_discovery_session_not_found(client):
    response = client.get("/api/v1/discovery/sessions/nonexistent-session-id")
    assert response.status_code == 404


def test_list_discovery_sessions(client):
    # Create a session
    client.post(
        "/api/v1/discovery/sessions",
        json={"user_intent": "credit card with rewards", "weight_profile": "feature_rich"},
    )
    response = client.get("/api/v1/discovery/sessions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_session_results(client):
    payload = {"user_intent": "best savings account", "weight_profile": "balanced"}
    create_resp = client.post("/api/v1/discovery/sessions", json=payload)
    session_id = create_resp.json()["id"]

    results_resp = client.get(f"/api/v1/discovery/sessions/{session_id}/results")
    assert results_resp.status_code == 200
    assert isinstance(results_resp.json(), list)


def test_create_session_with_constraints(client):
    payload = {
        "user_intent": "term deposit for 12 months",
        "product_category": "TERM_DEPOSITS",
        "preferences": {"duration_months": 12},
        "constraints": {"min_rate": 0.04, "max_monthly_fee": 0},
        "weight_profile": "rate_focused",
    }
    response = client.post("/api/v1/discovery/sessions", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["constraints"]["min_rate"] == 0.04
