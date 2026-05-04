import asyncio

from app.core.config import settings
from app.services.openbanking_adapter_client import MCPAdapterClient


async def _noop():
    return None


async def _fake_call_credit_cards(tool_name: str, args: dict):
    if tool_name != "find_credit_cards":
        return ""
    return """
| # | Card Image | Bank | Product | Annual Fee | Key Feature | Link |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | [![Card](https://img)](https://bank/img) | ANZ | [ANZ Rewards](https://anz/rewards) | $99 | Travel insurance | [Read more](https://anz/rewards) |
"""


async def _fake_call_list_banks(tool_name: str, args: dict):
    if tool_name != "list_banks":
        return ""
    return """
**Australian Banks**

- `anz` — ANZ
- `commbank` — Commonwealth Bank
"""


def test_get_products_credit_cards_parses_markdown(monkeypatch):
    client = MCPAdapterClient()
    monkeypatch.setattr(settings, "CDR_MOCK_MODE", False)
    monkeypatch.setattr(client, "_dismiss_disclaimer", _noop)
    monkeypatch.setattr(client, "_call_mcp_tool", _fake_call_credit_cards)

    products = asyncio.run(client.get_products(category="CRED_AND_CHRG_CARDS"))

    assert len(products) == 1
    assert products[0]["name"] == "ANZ Rewards"
    assert products[0]["fees"][0]["amount"] == "99"


def test_list_providers_parses_bank_list(monkeypatch):
    client = MCPAdapterClient()
    monkeypatch.setattr(settings, "CDR_MOCK_MODE", False)
    monkeypatch.setattr(client, "_call_mcp_tool", _fake_call_list_banks)

    providers = asyncio.run(client.list_providers())

    assert len(providers) == 2
    assert providers[0]["providerId"] == "anz"
    assert providers[1]["name"] == "Commonwealth Bank"
