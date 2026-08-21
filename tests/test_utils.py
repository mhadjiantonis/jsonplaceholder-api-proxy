import pytest
from pytest_mock import MockerFixture
from fastapi import HTTPException, status
from httpx2 import HTTPStatusError, Request

from jsonplaceholder_api_proxy.utils import confirm_resource_existence


@pytest.mark.asyncio
async def test_resource_exists_success(mocker: MockerFixture):
    """Test when resource exists (200 response, no error)"""
    mock_client = mocker.AsyncMock()
    mock_response = mocker.Mock()
    mock_response.raise_for_status.return_value = None
    mock_client.head.return_value = mock_response

    # Should not raise any exception
    await confirm_resource_existence(
        client=mock_client, url="/users/1", error_message="User not found"
    )

    mock_client.head.assert_called_once_with("/users/1")
    mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_resource_not_found_404_raises_http_exception(mocker: MockerFixture):
    """Test when resource returns 404 (should raise HTTPException)"""
    mock_client = mocker.AsyncMock()
    mock_response = mocker.Mock()
    mock_response.status_code = 404

    # Create HTTPStatusError for 404
    request = mocker.MagicMock(spec=Request)
    request.method = "HEAD"
    request.url = "http://example.com/users/999"
    http_error = HTTPStatusError(
        "404 Not Found", request=request, response=mock_response
    )
    mock_response.raise_for_status.return_value = None
    mock_response.raise_for_status.side_effect = http_error
    mock_client.head.return_value = mock_response

    with pytest.raises(HTTPException) as exc_info:
        await confirm_resource_existence(
            client=mock_client, url="/users/999", error_message="User does not exist"
        )

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User does not exist"


@pytest.mark.asyncio
async def test_resource_not_found_with_formatted_message(mocker: MockerFixture):
    """Test 404 error message formatting with kwargs"""
    mock_client = mocker.AsyncMock()
    mock_response = mocker.Mock()
    mock_response.status_code = 404

    request = mocker.MagicMock(spec=Request)
    http_error = HTTPStatusError(
        "404 Not Found", request=request, response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_client.head.return_value = mock_response

    with pytest.raises(HTTPException) as exc_info:
        await confirm_resource_existence(
            client=mock_client,
            url="/posts/42",
            error_message="Post {post_id} not found",
            post_id=42,
        )

    assert exc_info.value.detail == "Post 42 not found"


@pytest.mark.asyncio
async def test_upstream_error_500_re_raises_http_status_error(mocker: MockerFixture):
    """Test that non-404 HTTP errors are re-raised"""
    mock_client = mocker.AsyncMock()
    mock_response = mocker.Mock()
    mock_response.status_code = 500

    request = mocker.MagicMock(spec=Request)
    http_error = HTTPStatusError(
        "500 Server Error", request=request, response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_client.head.return_value = mock_response

    with pytest.raises(HTTPStatusError) as exc_info:
        await confirm_resource_existence(
            client=mock_client, url="/users/1", error_message="User not found"
        )

    assert exc_info.value.response.status_code == 500


@pytest.mark.asyncio
async def test_upstream_error_503_re_raises_http_status_error(mocker: MockerFixture):
    """Test that 503 errors are re-raised (not converted to HTTPException)"""
    mock_client = mocker.AsyncMock()
    mock_response = mocker.Mock()
    mock_response.status_code = 503

    request = mocker.MagicMock(spec=Request)
    http_error = HTTPStatusError(
        "503 Service Unavailable", request=request, response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_client.head.return_value = mock_response

    with pytest.raises(HTTPStatusError):
        await confirm_resource_existence(
            client=mock_client, url="/users/1", error_message="User not found"
        )


@pytest.mark.asyncio
async def test_multiple_format_parameters(mocker: MockerFixture):
    """Test error message with multiple format parameters"""
    mock_client = mocker.AsyncMock()
    mock_response = mocker.Mock()
    mock_response.status_code = 404

    request = mocker.MagicMock(spec=Request)
    http_error = HTTPStatusError(
        "404 Not Found", request=request, response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_client.head.return_value = mock_response

    with pytest.raises(HTTPException) as exc_info:
        await confirm_resource_existence(
            client=mock_client,
            url="/users/1/posts/5",
            error_message="Post {post_id} by user {user_id} not found",
            post_id=5,
            user_id=1,
        )

    assert exc_info.value.detail == "Post 5 by user 1 not found"
