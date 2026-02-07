from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, Path, Request, Response, status
from httpx import AsyncClient, Headers

from ..endpoint_tags import EndpointTag
from ..http_client import get_http_client
from ..models import HTTPError
from ..posts.models import PostRead
from ..utils import confirm_resource_existence
from .models import UserCreate, UserRead

users_router = APIRouter(tags=[EndpointTag.USERS])


@users_router.get("", response_model=list[UserRead])
async def read_users(
    client: Annotated[AsyncClient, Depends(get_http_client, scope="function")],
) -> Any:
    """Get an array with all existing users"""
    ext_response = await client.get("/users")
    ext_response.raise_for_status()
    return ext_response.json()


@users_router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    client: Annotated[AsyncClient, Depends(get_http_client, scope="function")],
    user: Annotated[UserCreate, Body()],
    request: Request,
    partial_response: Response,
) -> Any:
    """Create a new user"""
    user_serialized = user.model_dump_json(by_alias=True)
    ext_request_headers = Headers({"content-type": "application/json"})
    ext_response = await client.post(
        "/users", headers=ext_request_headers, content=user_serialized
    )
    ext_response.raise_for_status()
    request_url = request.url
    created_user_id = ext_response.json()["id"]
    location_url = f"{request_url}/{created_user_id}"
    partial_response.headers["location"] = location_url
    return ext_response.json()


@users_router.get(
    "/{userId}",
    response_model=UserRead,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def read_user_by_id(
    client: Annotated[AsyncClient, Depends(get_http_client, scope="function")],
    user_id: Annotated[
        int,
        Path(alias="userId", gt=0, description="The ID of the user to be retrieved"),
    ],
) -> Any:
    """Read a user by providing a valid user ID"""
    await confirm_resource_existence(
        client=client,
        url=f"/users/{user_id}",
        error_message="User {user_id} does not exist.",
        user_id=user_id,
    )
    ext_response = await client.get(f"/users/{user_id}")
    ext_response.raise_for_status()
    return ext_response.json()


@users_router.put(
    "/{userId}",
    response_model=UserRead,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_user(
    client: Annotated[AsyncClient, Depends(get_http_client, scope="function")],
    user_id: Annotated[
        int, Path(alias="userId", gt=0, description="The ID of the user to be replaced")
    ],
    user: Annotated[UserCreate, Body()],
) -> Any:
    """Replace an existing user"""
    await confirm_resource_existence(
        client=client,
        url=f"/users/{user_id}",
        error_message="User {user_id} does not exist and cannot be replaced.",
        user_id=user_id,
    )
    user_serialized = user.model_dump_json(by_alias=True)
    ext_request_headers = Headers({"content-type": "application/json"})
    ext_response = await client.put(
        f"/users/{user_id}", headers=ext_request_headers, content=user_serialized
    )
    ext_response.raise_for_status()
    return ext_response.json()


@users_router.delete("/{userId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    client: Annotated[AsyncClient, Depends(get_http_client, scope="function")],
    user_id: Annotated[
        int, Path(alias="userId", gt=0, description="The ID of the user to be deleted")
    ],
) -> None:
    """Delete an existing user by providing a user ID"""
    ext_response = await client.delete(f"/users/{user_id}")
    ext_response.raise_for_status()


@users_router.get(
    "/{userId}/posts",
    tags=[EndpointTag.POSTS],
    response_model=list[PostRead],
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def read_user_posts(
    client: Annotated[AsyncClient, Depends(get_http_client, scope="function")],
    user_id: Annotated[
        int,
        Path(
            alias="userId",
            gt=0,
            description="The ID of the user whose posts will be retrieved",
        ),
    ],
) -> Any:
    """Get an array with all the posts of a user"""
    await confirm_resource_existence(
        client=client,
        url=f"/users/{user_id}",
        error_message="User {user_id} does not exist and cannot have any posts",
        user_id=user_id,
    )
    ext_response = await client.get(f"/users/{user_id}/posts")
    ext_response.raise_for_status()
    return ext_response.json()
