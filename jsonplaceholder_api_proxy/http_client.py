from typing import AsyncGenerator

from httpx import URL, AsyncClient, Headers

BASE_URL = "http://jsonplaceholder.typicode.com"


async def get_http_client() -> AsyncGenerator[AsyncClient, None]:
    url = URL(BASE_URL)
    headers = Headers({"accept": "application/json"})
    async with AsyncClient(base_url=url, headers=headers) as client:
        yield client
