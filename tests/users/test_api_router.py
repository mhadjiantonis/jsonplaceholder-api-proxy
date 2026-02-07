from typing import Any, Generator

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from httpx import HTTPStatusError
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


def _create_test_user(user_id: int = 1) -> dict[str, Any]:
    """Helper to create test user data"""
    return {
        "id": user_id,
        "name": "John Doe",
        "username": "johndoe",
        "email": "john@example.com",
        "phone": "1-770-736-8031",
        "address": {
            "street": "Kulas Light",
            "suite": "Apt. 556",
            "city": "Gwenborough",
            "zipcode": "92998-3874",
            "geo": {"lat": 37.7749, "lng": -122.4194},
        },
        "company": {
            "name": "Romaguera-Crona",
            "catchPhrase": "Multi-layered client-server neural-net",
            "bs": "harness real-time e-markets",
        },
    }


@pytest.mark.asyncio
async def test_read_all_users(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test GET /users returns all users"""
    test_client, mock_http_client = client

    users_data = [_create_test_user(1), _create_test_user(2)]
    mock_response = mocker.Mock()
    mock_response.json.return_value = users_data
    mock_http_client.get.return_value = mock_response

    response = test_client.get("/users")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == users_data
    mock_http_client.get.assert_called_once_with("/users")


@pytest.mark.asyncio
async def test_read_all_users_upstream_error(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test GET /users when upstream returns an error"""
    test_client, mock_http_client = client

    mock_response = mocker.Mock()
    mock_response.status_code = 500
    request = mocker.MagicMock()
    http_error = HTTPStatusError(
        "500 Server Error", request=request, response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_http_client.get.return_value = mock_response

    response = test_client.get("/users")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_create_user_success(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test POST /users creates a user and returns location header"""
    test_client, mock_http_client = client

    created_user = _create_test_user(101)
    mock_response = mocker.Mock()
    mock_response.json.return_value = created_user
    mock_http_client.post.return_value = mock_response

    payload: dict[str, Any] = {
        "name": "John Doe",
        "username": "johndoe",
        "email": "john@example.com",
        "phone": "1-770-736-8031",
        "address": {
            "street": "Kulas Light",
            "suite": "Apt. 556",
            "city": "Gwenborough",
            "zipcode": "92998-3874",
            "geo": {"lat": 37.7749, "lng": -122.4194},
        },
        "company": {
            "name": "Romaguera-Crona",
            "catchPhrase": "Multi-layered client-server neural-net",
            "bs": "harness real-time e-markets",
        },
    }

    response = test_client.post("/users", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == created_user
    assert "location" in response.headers
    assert "/users/101" in response.headers["location"]


@pytest.mark.asyncio
async def test_create_user_invalid_email(client: tuple[TestClient, AsyncMockType]):
    """Test POST /users with invalid email"""
    test_client, _ = client

    payload: dict[str, Any] = {
        "name": "John Doe",
        "username": "johndoe",
        "email": "not-an-email",
        "phone": "1-770-736-8031",
        "address": {
            "street": "Kulas Light",
            "suite": "Apt. 556",
            "city": "Gwenborough",
            "zipcode": "92998-3874",
            "geo": {"lat": 37.7749, "lng": -122.4194},
        },
        "company": {
            "name": "Romaguera-Crona",
            "catchPhrase": "Multi-layered client-server neural-net",
            "bs": "harness real-time e-markets",
        },
    }

    response = test_client.post("/users", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_create_user_missing_required_field(
    client: tuple[TestClient, AsyncMockType],
):
    """Test POST /users with missing required field"""
    test_client, _ = client

    payload: dict[str, Any] = {
        "name": "John Doe",
        # missing username
        "email": "john@example.com",
        "phone": "1-770-736-8031",
        "address": {
            "street": "Kulas Light",
            "suite": "Apt. 556",
            "city": "Gwenborough",
            "zipcode": "92998-3874",
            "geo": {"lat": 37.7749, "lng": -122.4194},
        },
        "company": {
            "name": "Romaguera-Crona",
            "catchPhrase": "Multi-layered client-server neural-net",
            "bs": "harness real-time e-markets",
        },
    }

    response = test_client.post("/users", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_read_user_by_id_success(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test GET /users/{userId} returns user when exists"""
    test_client, mock_http_client = client

    user_data = _create_test_user(1)
    mock_response = mocker.Mock()
    mock_response.json.return_value = user_data
    mock_http_client.head.return_value = mock_response
    mock_http_client.get.return_value = mock_response

    response = test_client.get("/users/1")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == user_data
    mock_http_client.head.assert_called_once_with("/users/1")
    mock_http_client.get.assert_called_once_with("/users/1")


@pytest.mark.asyncio
async def test_read_user_by_id_not_found(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test GET /users/{userId} returns 404 when user not found"""
    test_client, mock_http_client = client

    mock_response = mocker.Mock()
    mock_response.status_code = 404
    request = mocker.MagicMock()
    http_error = HTTPStatusError(
        "404 Not Found", request=request, response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_http_client.head.return_value = mock_response

    response = test_client.get("/users/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "does not exist" in response.json()["detail"]


@pytest.mark.asyncio
async def test_read_user_by_id_invalid_id_zero(
    client: tuple[TestClient, AsyncMockType],
):
    """Test GET /users/{userId} with userId=0 (invalid)"""
    test_client, _ = client

    response = test_client.get("/users/0")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_update_user_success(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test PUT /users/{userId} updates user successfully"""
    test_client, mock_http_client = client

    updated_user = _create_test_user(1)
    updated_user["name"] = "Jane Doe"
    mock_response = mocker.Mock()
    mock_response.json.return_value = updated_user
    mock_http_client.head.return_value = mock_response
    mock_http_client.put.return_value = mock_response

    payload: dict[str, Any] = {
        "name": "Jane Doe",
        "username": "janedoe",
        "email": "jane@example.com",
        "phone": "1-770-736-8031",
        "address": {
            "street": "Kulas Light",
            "suite": "Apt. 556",
            "city": "Gwenborough",
            "zipcode": "92998-3874",
            "geo": {"lat": 37.7749, "lng": -122.4194},
        },
        "company": {
            "name": "Romaguera-Crona",
            "catchPhrase": "Multi-layered client-server neural-net",
            "bs": "harness real-time e-markets",
        },
    }

    response = test_client.put("/users/1", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == updated_user
    mock_http_client.head.assert_called_once_with("/users/1")


@pytest.mark.asyncio
async def test_update_user_not_found(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test PUT /users/{userId} returns 404 when user not found"""
    test_client, mock_http_client = client

    mock_response = mocker.Mock()
    mock_response.status_code = 404
    request = mocker.MagicMock()
    http_error = HTTPStatusError(
        "404 Not Found", request=request, response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_http_client.head.return_value = mock_response

    payload: dict[str, Any] = {
        "name": "Jane Doe",
        "username": "janedoe",
        "email": "jane@example.com",
        "phone": "1-770-736-8031",
        "address": {
            "street": "Kulas Light",
            "suite": "Apt. 556",
            "city": "Gwenborough",
            "zipcode": "92998-3874",
            "geo": {"lat": 37.7749, "lng": -122.4194},
        },
        "company": {
            "name": "Romaguera-Crona",
            "catchPhrase": "Multi-layered client-server neural-net",
            "bs": "harness real-time e-markets",
        },
    }

    response = test_client.put("/users/999", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "does not exist" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_user_invalid_payload(client: tuple[TestClient, AsyncMockType]):
    """Test PUT /users/{userId} with invalid payload"""
    test_client, _ = client

    payload = {"name": "Jane Doe"}  # Missing required fields

    response = test_client.put("/users/1", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_delete_user_success(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test DELETE /users/{userId} deletes user successfully"""
    test_client, mock_http_client = client

    mock_response = mocker.Mock()
    mock_http_client.delete.return_value = mock_response

    response = test_client.delete("/users/1")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_http_client.delete.assert_called_once_with("/users/1")


@pytest.mark.asyncio
async def test_delete_user_upstream_error(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test DELETE /users/{userId} when upstream returns error"""
    test_client, mock_http_client = client

    mock_response = mocker.Mock()
    mock_response.status_code = 500
    request = mocker.MagicMock()
    http_error = HTTPStatusError(
        "500 Server Error", request=request, response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_http_client.delete.return_value = mock_response

    response = test_client.delete("/users/1")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_delete_user_invalid_id_zero(client: tuple[TestClient, AsyncMockType]):
    """Test DELETE /users/{userId} with userId=0 (invalid)"""
    test_client, _ = client

    response = test_client.delete("/users/0")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


@pytest.mark.asyncio
async def test_read_user_posts_success(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test GET /users/{userId}/posts returns posts"""
    test_client, mock_http_client = client

    posts_data: list[dict[str, Any]] = [
        {"id": 1, "userId": 1, "title": "Post 1", "body": "Body 1"},
        {"id": 2, "userId": 1, "title": "Post 2", "body": "Body 2"},
    ]
    mock_response = mocker.Mock()
    mock_response.json.return_value = posts_data
    mock_http_client.head.return_value = mock_response
    mock_http_client.get.return_value = mock_response

    response = test_client.get("/users/1/posts")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == posts_data
    mock_http_client.head.assert_called_once_with("/users/1")
    mock_http_client.get.assert_called_once_with("/users/1/posts")


@pytest.mark.asyncio
async def test_read_user_posts_user_not_found(
    client: tuple[TestClient, AsyncMockType], mocker: MockerFixture
):
    """Test GET /users/{userId}/posts returns 404 when user not found"""
    test_client, mock_http_client = client

    mock_response = mocker.Mock()
    mock_response.status_code = 404
    request = mocker.MagicMock()
    http_error = HTTPStatusError(
        "404 Not Found", request=request, response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_http_client.head.return_value = mock_response

    response = test_client.get("/users/999/posts")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "does not exist" in response.json()["detail"]


@pytest.mark.asyncio
async def test_read_user_posts_invalid_id_zero(
    client: tuple[TestClient, AsyncMockType],
):
    """Test GET /users/{userId}/posts with userId=0 (invalid)"""
    test_client, _ = client

    response = test_client.get("/users/0/posts")

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
