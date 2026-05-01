import pytest
from app.models.provider import Provider
from app.models.product import Product, ProductFee, ProductRate, ProductFeature
from app.repositories.product_repository import ProductRepository


@pytest.fixture
def sample_provider(db):
    provider = Provider(name="Test Bank", abn="12345678901", is_active=True)
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


@pytest.fixture
def sample_products(db, sample_provider):
    products = []
    for i in range(3):
        p = Product(
            provider_id=sample_provider.id,
            name=f"Savings Account {i + 1}",
            category="TRANS_AND_SAVINGS_ACCOUNTS",
            description=f"Test savings account {i + 1}",
            brand_name="Test Bank",
            is_active=True,
        )
        db.add(p)
        db.flush()

        fee = ProductFee(
            product_id=p.id,
            name="Monthly Fee",
            fee_type="PERIODIC",
            amount=str(i * 5),
            currency="AUD",
        )
        db.add(fee)

        rate = ProductRate(
            product_id=p.id,
            rate_type="DEPOSIT",
            rate=str(0.03 + i * 0.01),
        )
        db.add(rate)

        feature = ProductFeature(
            product_id=p.id,
            feature_type="DIGITAL_BANKING",
        )
        db.add(feature)

        products.append(p)

    db.commit()
    for p in products:
        db.refresh(p)
    return products


def test_list_products_empty(client):
    """List products endpoint returns paginated response."""
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data


def test_list_products_with_data(client, sample_products):
    response = client.get("/api/v1/products?category=TRANS_AND_SAVINGS_ACCOUNTS")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert len(data["items"]) >= 3


def test_list_products_pagination(client, sample_products):
    response = client.get("/api/v1/products?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert len(data["items"]) <= 2


def test_list_products_search(client, sample_products):
    response = client.get("/api/v1/products?search=Savings")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


def test_get_product_not_found(client):
    response = client.get("/api/v1/products/nonexistent-id")
    assert response.status_code == 404


def test_get_product_by_id(client, sample_products):
    product_id = sample_products[0].id
    response = client.get(f"/api/v1/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert "name" in data
    assert "fees" in data
    assert "rates" in data
    assert "features" in data


def test_compare_products(client, sample_products):
    ids = ",".join([p.id for p in sample_products[:2]])
    response = client.get(f"/api/v1/products/compare?ids={ids}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_compare_products_no_ids(client):
    response = client.get("/api/v1/products/compare?ids=")
    assert response.status_code == 400


def test_product_repository_list(db, sample_products):
    repo = ProductRepository(db)
    items, total = repo.list_products(page=1, page_size=10, category="TRANS_AND_SAVINGS_ACCOUNTS")
    assert total >= 3
    assert len(items) >= 3


def test_product_repository_get_by_id(db, sample_products):
    repo = ProductRepository(db)
    product = repo.get_product_by_id(sample_products[0].id)
    assert product is not None
    assert product.id == sample_products[0].id
    assert len(product.fees) >= 1
    assert len(product.rates) >= 1
    assert len(product.features) >= 1
