import pytest
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_sync_products_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": [{"productId": "p1"}, {"productId": "p2"}, {"productId": "p3"}]}
    mock_response.raise_for_status = MagicMock()
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)
    with patch("app.tasks.sync_products.httpx.AsyncClient", return_value=mock_client):
        from app.tasks.sync_products import sync_all_products
        result = await sync_all_products("http://localhost:4000")
        assert result["synced"] == 3
        assert result["errors"] == []

@pytest.mark.asyncio
async def test_sync_products_failure():
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(side_effect=ConnectionError("Adapter unavailable"))
    with patch("app.tasks.sync_products.httpx.AsyncClient", return_value=mock_client):
        from app.tasks.sync_products import sync_all_products
        result = await sync_all_products("http://localhost:4000")
        assert result["synced"] == 0
        assert len(result["errors"]) > 0

@pytest.mark.asyncio
async def test_cleanup():
    from app.tasks.cleanup import cleanup_old_records
    result = await cleanup_old_records(retention_days=30)
    assert "cutoff" in result
    assert "cleaned" in result
