from typing import Any

from fastapi import HTTPException, status
from httpx2 import AsyncClient, HTTPStatusError


async def confirm_resource_existence(
    client: AsyncClient, url: str, error_message: str, **kwargs: Any
) -> None:
    """
    Confirm a resourceexists in the remote API at the given URL

    :param client: The HTTP client to use for external requests
    :type client: AsyncClient
    :param url: The URL of the resource to be confirmed
    :type url: str
    :param error_message: The error message to show when the resource does not exist
    :type error_message: str
    :param kwargs: Keyword arguments to be passed to the string formatter for the error message
    :type kwargs: dict[str, Any]
    """
    ext_response = await client.head(url)
    try:
        ext_response.raise_for_status()
    except HTTPStatusError as http_error:
        if http_error.response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, error_message.format(**kwargs)
            ) from http_error
        raise http_error
