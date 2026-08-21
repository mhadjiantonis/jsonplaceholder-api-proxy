from typing import Any, Generator

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx2 import HTTPStatusError
from pytest_mock import AsyncMockType, MockerFixture

from jsonplaceholder_api_proxy.api import app
from jsonplaceholder_api_proxy.http_client import get_http_client


@pytest.fixture
def client(
    mocker: MockerFixture,
) -> Generator[tuple[TestClient, AsyncMockType], None, None]:
    """Provide TestClient with mocked HTTP client"""
    mock_http_client = mocker.AsyncMock()

    async def override_get_http_client():
        yield mock_http_client

    app.dependency_overrides[get_http_client] = override_get_http_client

    test_client = TestClient(app, raise_server_exceptions=False)
    yield test_client, mock_http_client

    app.dependency_overrides.clear()


def _create_test_post(post_id: int = 1, user_id: int = 1) -> dict[str, Any]:
    """Helper to create test post data"""
    return {
        "id": post_id,
        "userId": user_id,
        "title": f"Post {post_id} Title",
        "body": f"Post {post_id} body content",
    }


@pytest.mark.asyncio
async def test_read_all_posts(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test GET /posts returns all posts"""
    test_client, mock_http_client = client

    posts_data = [_create_test_post(1, 1), _create_test_post(2, 1)]
    mock_response = mocker.Mock()
    mock_response.json.return_value = posts_data
    mock_http_client.get.return_value = mock_response

    response = test_client.get("/posts")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == posts_data
    mock_http_client.get.assert_called_once_with("/posts", params=None)


@pytest.mark.asyncio
async def test_read_posts_filtered_by_user_id(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test GET /posts?userId=1 returns posts filtered by user"""
    test_client, mock_http_client = client

    posts_data = [_create_test_post(1, 1), _create_test_post(2, 1)]
    mock_response = mocker.Mock()
    mock_response.json.return_value = posts_data
    mock_response.status_code = 200
    mock_http_client.head.return_value = mock_response
    mock_http_client.get.return_value = mock_response

    response = test_client.get("/posts?userId=1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == posts_data
    mock_http_client.head.assert_called_once_with("/users/1")
    mock_http_client.get.assert_called_once_with("/posts", params={"userId": 1})


@pytest.mark.asyncio
async def test_read_posts_by_invalid_user_id(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test GET /posts?userId=999 returns 404 when user not found"""
    test_client, mock_http_client = client

    mock_response = mocker.Mock()
    mock_response.status_code = 404
    request = mocker.MagicMock()
    http_error = HTTPStatusError(
        "404 Not Found", request=request, response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_http_client.head.return_value = mock_response

    response = test_client.get("/posts?userId=999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "does not exist" in response.json()["detail"]


@pytest.mark.asyncio
async def test_read_posts_by_user_id_zero(client: tuple[TestClient, AsyncMockType]):
    """Test GET /posts?userId=0 returns validation error"""
    test_client, _ = client

    response = test_client.get("/posts?userId=0")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_read_posts_upstream_error(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test GET /posts when upstream returns an error"""
    test_client, mock_http_client = client

    mock_response = mocker.Mock()
    mock_response.status_code = 500
    request = mocker.MagicMock()
    http_error = HTTPStatusError(
        "500 Server Error", request=request, response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_http_client.get.return_value = mock_response

    response = test_client.get("/posts")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_create_post_success(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test POST /posts creates a post and returns location header"""
    test_client, mock_http_client = client

    created_post = _create_test_post(101, 1)
    mock_response = mocker.Mock()
    mock_response.json.return_value = created_post
    mock_http_client.post.return_value = mock_response

    payload: dict[str, Any] = {
        "userId": 1,
        "title": "New Post",
        "body": "Post body content",
    }

    response = test_client.post("/posts", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == created_post
    assert "location" in response.headers
    assert "/posts/101" in response.headers["location"]


@pytest.mark.asyncio
async def test_create_post_missing_title(client: tuple[TestClient, AsyncMockType]):
    """Test POST /posts with missing title field"""
    test_client, _ = client

    payload: dict[str, Any] = {"userId": 1, "body": "Post body content"}

    response = test_client.post("/posts", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_create_post_missing_body(client: tuple[TestClient, AsyncMockType]):
    """Test POST /posts with missing body field"""
    test_client, _ = client

    payload: dict[str, Any] = {"userId": 1, "title": "New Post"}

    response = test_client.post("/posts", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_create_post_invalid_user_id_zero(
    client: tuple[TestClient, AsyncMockType],
):
    """Test POST /posts with userId=0 (invalid)"""
    test_client, _ = client

    payload: dict[str, Any] = {
        "userId": 0,
        "title": "New Post",
        "body": "Post body content",
    }

    response = test_client.post("/posts", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_create_post_upstream_error(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test POST /posts when upstream returns an error"""
    test_client, mock_http_client = client

    mock_response = mocker.Mock()
    mock_response.status_code = 500
    request = mocker.MagicMock()
    http_error = HTTPStatusError(
        "500 Server Error", request=request, response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_http_client.post.return_value = mock_response

    payload: dict[str, Any] = {
        "userId": 1,
        "title": "New Post",
        "body": "Post body content",
    }

    response = test_client.post("/posts", json=payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_read_post_by_id_success(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test GET /posts/{postId} returns post when exists"""
    test_client, mock_http_client = client

    post_data = _create_test_post(1, 1)
    mock_response = mocker.Mock()
    mock_response.json.return_value = post_data
    mock_http_client.head.return_value = mock_response
    mock_http_client.get.return_value = mock_response

    response = test_client.get("/posts/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == post_data
    mock_http_client.head.assert_called_once_with("/posts/1")
    mock_http_client.get.assert_called_once_with("/posts/1")


@pytest.mark.asyncio
async def test_read_post_by_id_not_found(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test GET /posts/{postId} returns 404 when post not found"""
    test_client, mock_http_client = client

    mock_response = mocker.Mock()
    mock_response.status_code = 404
    request = mocker.MagicMock()
    http_error = HTTPStatusError(
        "404 Not Found", request=request, response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_http_client.head.return_value = mock_response

    response = test_client.get("/posts/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "does not exist" in response.json()["detail"]


@pytest.mark.asyncio
async def test_read_post_by_id_invalid_id_zero(
    client: tuple[TestClient, AsyncMockType],
):
    """Test GET /posts/{postId} with postId=0 (invalid)"""
    test_client, _ = client

    response = test_client.get("/posts/0")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_update_post_success(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test PATCH /posts/{postId} updates post successfully"""
    test_client, mock_http_client = client

    updated_post = _create_test_post(1, 1)
    updated_post["title"] = "Updated Title"
    updated_post["body"] = "Updated body"
    mock_response = mocker.Mock()
    mock_response.json.return_value = updated_post
    mock_http_client.head.return_value = mock_response
    mock_http_client.patch.return_value = mock_response

    payload = {"title": "Updated Title", "body": "Updated body"}

    response = test_client.patch("/posts/1", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == updated_post
    mock_http_client.head.assert_called_once_with("/posts/1")


@pytest.mark.asyncio
async def test_update_post_not_found(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test PATCH /posts/{postId} returns 404 when post not found"""
    test_client, mock_http_client = client

    mock_response = mocker.Mock()
    mock_response.status_code = 404
    request = mocker.MagicMock()
    http_error = HTTPStatusError(
        "404 Not Found", request=request, response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_http_client.head.return_value = mock_response

    payload = {"title": "Updated Title", "body": "Updated body"}

    response = test_client.patch("/posts/999", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "does not exist" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_post_missing_title(client: tuple[TestClient, AsyncMockType]):
    """Test PATCH /posts/{postId} with missing title"""
    test_client, _ = client

    payload = {"body": "Updated body"}

    response = test_client.patch("/posts/1", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_update_post_missing_body(client: tuple[TestClient, AsyncMockType]):
    """Test PATCH /posts/{postId} with missing body"""
    test_client, _ = client

    payload = {"title": "Updated Title"}

    response = test_client.patch("/posts/1", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_update_post_upstream_error(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test PATCH /posts/{postId} when upstream returns error"""
    test_client, mock_http_client = client

    mock_head_response = mocker.Mock()
    mock_head_response.status_code = 200
    mock_http_client.head.return_value = mock_head_response

    mock_patch_response = mocker.Mock()
    mock_patch_response.status_code = 500
    request = mocker.MagicMock()
    http_error = HTTPStatusError(
        "500 Server Error", request=request, response=mock_patch_response
    )
    mock_patch_response.raise_for_status.side_effect = http_error
    mock_http_client.patch.return_value = mock_patch_response

    payload = {"title": "Updated Title", "body": "Updated body"}

    response = test_client.patch("/posts/1", json=payload)

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_delete_post_success(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test DELETE /posts/{postId} deletes post successfully"""
    test_client, mock_http_client = client

    mock_response = mocker.Mock()
    mock_http_client.delete.return_value = mock_response

    response = test_client.delete("/posts/1")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_http_client.delete.assert_called_once_with("/posts/1")


@pytest.mark.asyncio
async def test_delete_post_upstream_error(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test DELETE /posts/{postId} when upstream returns error"""
    test_client, mock_http_client = client

    mock_response = mocker.Mock()
    mock_response.status_code = 500
    request = mocker.MagicMock()
    http_error = HTTPStatusError(
        "500 Server Error", request=request, response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_http_client.delete.return_value = mock_response

    response = test_client.delete("/posts/1")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_delete_post_invalid_id_zero(client: tuple[TestClient, AsyncMockType]):
    """Test DELETE /posts/{postId} with postId=0 (invalid)"""
    test_client, _ = client

    response = test_client.delete("/posts/0")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
