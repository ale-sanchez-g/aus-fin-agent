from app.services.scoring import ScoringEngine, WeightProfile


def test_score_balanced_profile():
    engine = ScoringEngine()
    product = {
        "fees": [{"fee_type": "PERIODIC", "amount": "5.00"}],
        "rates": [{"rate_type": "DEPOSIT", "rate": "0.0475"}],
        "features": [{"feature_type": "DIGITAL_BANKING"}, {"feature_type": "NPP_PAYID"}],
    }
    preferences = {"max_monthly_fee": 10.0, "target_rate": 0.04}
    score = engine.score_product(product, preferences, WeightProfile.BALANCED)
    assert 0 <= score.total <= 100
    assert score.weight_profile == WeightProfile.BALANCED


def test_fee_conscious_weights_fees_higher():
    engine = ScoringEngine()
    product_low_fee = {
        "fees": [{"fee_type": "PERIODIC", "amount": "0.00"}],
        "rates": [{"rate_type": "DEPOSIT", "rate": "0.03"}],
        "features": [],
    }
    product_high_fee = {
        "fees": [{"fee_type": "PERIODIC", "amount": "20.00"}],
        "rates": [{"rate_type": "DEPOSIT", "rate": "0.05"}],
        "features": [{"feature_type": "DIGITAL_BANKING"}],
    }
    preferences = {}
    s1 = engine.score_product(product_low_fee, preferences, WeightProfile.FEE_CONSCIOUS)
    s2 = engine.score_product(product_high_fee, preferences, WeightProfile.FEE_CONSCIOUS)
    assert s1.total > s2.total  # low fee should win with fee_conscious profile


def test_score_no_fees_max_score_on_fee_dimension():
    engine = ScoringEngine()
    product = {"fees": [], "rates": [], "features": []}
    score = engine.score_monthly_fees(product)
    assert score == 100.0


def test_score_high_fee_above_cap():
    engine = ScoringEngine()
    product = {"fees": [{"fee_type": "PERIODIC", "amount": "50.00"}]}
    score = engine.score_monthly_fees(product, max_acceptable_fee=5.0)
    assert score < 50.0


def test_score_rate_competitive():
    engine = ScoringEngine()
    product = {"rates": [{"rate_type": "DEPOSIT", "rate": "0.055"}]}
    score = engine.score_rate(product, target_rate=0.04)
    assert score > 80.0


def test_score_rate_no_rates():
    engine = ScoringEngine()
    product = {"rates": []}
    score = engine.score_rate(product)
    assert score == 50.0  # neutral


def test_score_digital_capability_full():
    engine = ScoringEngine()
    product = {
        "features": [
            {"feature_type": "DIGITAL_BANKING"},
            {"feature_type": "NPP_PAYID"},
            {"feature_type": "NPP_ENABLED"},
            {"feature_type": "DIGITAL_WALLET"},
            {"feature_type": "NOTIFICATIONS"},
            {"feature_type": "ALERTS"},
        ]
    }
    score = engine.score_digital_capability(product)
    assert score == 100.0


def test_score_digital_capability_none():
    engine = ScoringEngine()
    product = {"features": []}
    score = engine.score_digital_capability(product)
    assert score == 0.0


def test_rate_focused_profile_weights_rate():
    engine = ScoringEngine()
    product_high_rate = {
        "fees": [{"fee_type": "PERIODIC", "amount": "10.00"}],
        "rates": [{"rate_type": "DEPOSIT", "rate": "0.055"}],
        "features": [],
    }
    product_low_rate = {
        "fees": [{"fee_type": "PERIODIC", "amount": "0.00"}],
        "rates": [{"rate_type": "DEPOSIT", "rate": "0.01"}],
        "features": [],
    }
    preferences = {}
    s1 = engine.score_product(product_high_rate, preferences, WeightProfile.RATE_FOCUSED)
    s2 = engine.score_product(product_low_rate, preferences, WeightProfile.RATE_FOCUSED)
    assert s1.total > s2.total
