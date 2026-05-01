import pytest
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_sync_providers_success():
    mock_response = MagicMock()
    mock_response.json.return_value = {"data": [{"id": "harbour-bank"}, {"id": "scb"}]}
    mock_response.raise_for_status = MagicMock()
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=mock_response)
    with patch("app.tasks.sync_providers.httpx.AsyncClient", return_value=mock_client):
        from app.tasks.sync_providers import sync_all_providers
        result = await sync_all_providers("http://localhost:4000")
        assert result["synced"] == 2
        assert result["errors"] == []
        assert "timestamp" in result

@pytest.mark.asyncio
async def test_sync_providers_failure():
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(side_effect=Exception("Connection refused"))
    with patch("app.tasks.sync_providers.httpx.AsyncClient", return_value=mock_client):
        from app.tasks.sync_providers import sync_all_providers
        result = await sync_all_providers("http://localhost:4000")
        assert result["synced"] == 0
        assert len(result["errors"]) > 0
