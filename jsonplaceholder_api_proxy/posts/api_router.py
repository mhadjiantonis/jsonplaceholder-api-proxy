from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, Path, Query, Request, Response, status
from httpx2 import AsyncClient, Headers

from ..endpoint_tags import EndpointTag
from ..http_client import get_http_client
from ..models import HTTPError
from ..utils import confirm_resource_existence
from .models import PostCreate, PostRead, PostUpdate

type HTTPClientDep = Annotated[AsyncClient, Depends(get_http_client, scope="function")]

posts_router = APIRouter(tags=[EndpointTag.POSTS])


@posts_router.get(
    "",
    response_model=list[PostRead],
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def read_posts(
    client: HTTPClientDep,
    user_id: Annotated[
        int | None,
        Query(
            alias="userId",
            description="The ID for the user whose posts will be retrieved",
            gt=0,
        ),
    ] = None,
) -> Any:
    """Get an array with all posts optionally filtered by user ID"""
    if user_id:
        await confirm_resource_existence(
            client=client,
            url=f"/users/{user_id}",
            error_message="User {user_id} does not exist and cannot have any posts",
            user_id=user_id,
        )
    ext_response = await client.get(
        "/posts", params=({"userId": user_id} if user_id else None)
    )
    ext_response.raise_for_status()
    return ext_response.json()


@posts_router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    client: HTTPClientDep,
    post: Annotated[PostCreate, Body()],
    request: Request,
    partial_response: Response,
):
    """Create a new post"""
    post_serialized = post.model_dump_json(by_alias=True)
    ext_request_headers = Headers({"content-type": "application/json"})
    ext_response = await client.post(
        "/posts", headers=ext_request_headers, content=post_serialized
    )
    ext_response.raise_for_status()
    request_url = request.url
    created_post_id = ext_response.json()["id"]
    location_url = f"{request_url}/{created_post_id}"
    partial_response.headers["location"] = location_url
    return ext_response.json()


@posts_router.get(
    "/{postId}",
    response_model=PostRead,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def read_post_by_id(
    client: HTTPClientDep,
    post_id: Annotated[
        int,
        Path(alias="postId", gt=0, description="The ID of the post to be retrieved"),
    ],
) -> Any:
    """Read a post by providing a valid post ID"""
    await confirm_resource_existence(
        client=client,
        url=f"/posts/{post_id}",
        error_message="Post {post_id} does not exist.",
        post_id=post_id,
    )
    ext_response = await client.get(f"/posts/{post_id}")
    ext_response.raise_for_status()
    return ext_response.json()


@posts_router.patch(
    "/{postId}",
    response_model=PostRead,
    responses={status.HTTP_404_NOT_FOUND: {"model": HTTPError}},
)
async def update_post(
    client: HTTPClientDep,
    post_id: Annotated[
        int, Path(alias="postId", gt=0, description="The ID of the post to be replaced")
    ],
    post: Annotated[PostUpdate, Body()],
) -> Any:
    """Replace an existing post"""
    await confirm_resource_existence(
        client=client,
        url=f"/posts/{post_id}",
        error_message="Post {post_id} does not exist and cannot be replaced.",
        post_id=post_id,
    )
    post_serialized = post.model_dump_json(by_alias=True)
    ext_request_headers = Headers({"content-type": "application/json"})
    ext_response = await client.patch(
        f"/posts/{post_id}", headers=ext_request_headers, content=post_serialized
    )
    ext_response.raise_for_status()
    return ext_response.json()


@posts_router.delete("/{postId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    client: HTTPClientDep,
    post_id: Annotated[
        int, Path(alias="postId", gt=0, description="The ID of the post to be deleted")
    ],
) -> None:
    """Delete an existing post by providing a post ID"""
    ext_response = await client.delete(f"/posts/{post_id}")
    ext_response.raise_for_status()
