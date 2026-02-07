from jsonplaceholder_api_proxy.http_client import BASE_URL, get_http_client
import pytest


@pytest.mark.asyncio
async def test_get_http_client():
    client = await anext(get_http_client())
    assert client.base_url == BASE_URL
    assert client.headers["accept"] == "application/json"
