import pytest
from unittest.mock import AsyncMock, patch
import httpx # Added import for httpx
import json # Added import for json
from core.services.xui_client import XUIClient, XUIClientError, get_client
from core.database.models import Server
# from core.utils.security import decrypt_password # Removed direct import, will patch where it's used

@pytest.fixture
def mock_httpx_client():
    """Fixture to mock httpx.AsyncClient."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client_instance = mock_client_class.return_value
        # Ensure post and get methods are AsyncMocks and their return values are also AsyncMocks
        mock_client_instance.post = AsyncMock()
        mock_client_instance.get = AsyncMock()

        # Mock the return value of .json() to be an AsyncMock that returns a dictionary
        mock_client_instance.post.return_value.json.return_value = {}
        mock_client_instance.get.return_value.json.return_value = {}

        # Mock the return value of .raise_for_status() to be an AsyncMock
        mock_client_instance.post.return_value.raise_for_status = AsyncMock()
        mock_client_instance.get.return_value.raise_for_status = AsyncMock()

        yield mock_client_instance

@pytest.fixture
def xui_client(mock_httpx_client):
    """Fixture for an XUIClient instance with a mocked httpx client."""
    client = XUIClient(api_url="http://test.xui.com", username="test_user", password="test_password")
    client.client = mock_httpx_client  # Inject the mocked client
    return client

@pytest.fixture
def mock_server():
    """Fixture for a mocked Server object."""
    server = AsyncMock(spec=Server)
    server.api_url = "http://mock.server.com"
    server.api_user = "mock_user"
    server.api_password = "encrypted_password" # This will be decrypted by get_client
    server.inbound_id = 1
    return server

# Mock the decrypt_password function globally for these tests
@pytest.fixture(autouse=True)
def mock_decrypt_password():
    # Patch decrypt_password where it's used in xui_client.py
    with patch('core.services.xui_client.decrypt_password', return_value="decrypted_password") as mock_decrypt:
        yield mock_decrypt

class TestXUIClient:

    @pytest.mark.asyncio
    async def test_login_success(self, xui_client, mock_httpx_client):
        mock_httpx_client.post.return_value = AsyncMock() # Ensure return value is awaitable
        mock_httpx_client.post.return_value.json.return_value = {"success": True}
        mock_httpx_client.post.return_value.cookies = {"session": "test_session_cookie"}
        
        await xui_client._login()
        assert xui_client.session_cookie == "test_session_cookie"
        mock_httpx_client.post.assert_called_once_with("/login", data={'username': 'test_user', 'password': 'test_password'})

    @pytest.mark.asyncio
    async def test_login_failure(self, xui_client, mock_httpx_client):
        mock_httpx_client.post.return_value = AsyncMock() # Ensure return value is awaitable
        mock_httpx_client.post.return_value.json.return_value = {"success": False, "msg": "Invalid credentials"}
        
        with pytest.raises(XUIClientError, match="Login failed. Response: Invalid credentials"):
            await xui_client._login()

    @pytest.mark.asyncio
    async def test_login_http_error(self, xui_client, mock_httpx_client):
        mock_httpx_client.post.return_value.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Bad Request", request=httpx.Request("POST", "/login"), response=httpx.Response(400)
        )
        with pytest.raises(XUIClientError, match="HTTP error during XUI login: 400"):
            await xui_client._login()

    @pytest.mark.asyncio
    async def test_ensure_authenticated_already_authenticated(self, xui_client):
        xui_client.session_cookie = "existing_session"
        with patch.object(xui_client, '_login') as mock_login:
            await xui_client._ensure_authenticated()
            mock_login.assert_not_called()

    @pytest.mark.asyncio
    async def test_ensure_authenticated_not_authenticated(self, xui_client):
        xui_client.session_cookie = None
        with patch.object(xui_client, '_login', new_callable=AsyncMock) as mock_login:
            await xui_client._ensure_authenticated()
            mock_login.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_inbound_success(self, xui_client, mock_httpx_client):
        xui_client.session_cookie = "test_session"
        mock_httpx_client.get.return_value = AsyncMock() # Ensure return value is awaitable
        mock_httpx_client.get.return_value.json.return_value = {
            "success": True,
            "obj": {"id": 1, "settings": "{\"clients\": []}"}
        }
        inbound = await xui_client.get_inbound(1)
        assert inbound["id"] == 1
        assert isinstance(inbound["settings"], dict)
        mock_httpx_client.get.assert_called_once_with("/panel/api/inbounds/get/1", cookies={"session": "test_session"})

    @pytest.mark.asyncio
    async def test_get_inbound_failure(self, xui_client, mock_httpx_client):
        xui_client.session_cookie = "test_session"
        mock_httpx_client.get.return_value = AsyncMock() # Ensure return value is awaitable
        mock_httpx_client.get.return_value.json.return_value = {"success": False, "msg": "Inbound not found"}
        with pytest.raises(XUIClientError, match="Failed to get inbound 1: Inbound not found"):
            await xui_client.get_inbound(1)

    @pytest.mark.asyncio
    async def test_create_user_success(self, xui_client, mock_httpx_client):
        xui_client.session_cookie = "test_session"
        mock_httpx_client.post.return_value.json.return_value = {"success": True}
        
        result = await xui_client.create_user(1, "test_uuid", "test@example.com", 1234567890, 123)
        assert result["success"] is True
        assert result["uuid"] == "test_uuid"
        mock_httpx_client.post.assert_called_once()
        args, kwargs = mock_httpx_client.post.call_args
        assert args[0] == "/panel/api/inbounds/addClient"
        
        # Parse the 'settings' JSON string from kwargs['data']
        payload_data = kwargs["data"]
        settings_json = json.loads(payload_data["settings"])
        clients = settings_json["clients"]
        
        assert len(clients) == 1
        assert clients[0]["id"] == "test_uuid"
        assert clients[0]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_create_user_failure(self, xui_client, mock_httpx_client):
        xui_client.session_cookie = "test_session"
        mock_httpx_client.post.return_value.json.return_value = {"success": False, "msg": "User exists"}
        with pytest.raises(XUIClientError, match="Failed to create user test@example.com: User exists"):
            await xui_client.create_user(1, "test_uuid", "test@example.com", 1234567890)

    @pytest.mark.asyncio
    async def test_update_client_success(self, xui_client, mock_httpx_client):
        xui_client.session_cookie = "test_session"
        # Mock get_inbound first
        mock_httpx_client.get.return_value.json.return_value = {
            "success": True,
            "obj": {"id": 1, "settings": "{\"clients\": [{\"id\": \"test_uuid\", \"expiryTime\": 0}]}"}
        }
        mock_httpx_client.post.return_value.json.return_value = {"success": True}

        result = await xui_client.update_client(1, "test_uuid", 9876543210)
        assert result["success"] is True
        mock_httpx_client.get.assert_called_once() # Called by update_client
        mock_httpx_client.post.assert_called_once()
        args, kwargs = mock_httpx_client.post.call_args
        assert args[0] == "/panel/api/inbounds/updateClient"
        
        # Parse the 'settings' JSON string from kwargs['data']
        payload_data = kwargs["data"]
        settings_json = json.loads(payload_data["settings"])
        clients = settings_json["clients"]

        assert len(clients) == 1
        assert clients[0]["id"] == "test_uuid"
        assert clients[0]["expiryTime"] == 9876543210

    @pytest.mark.asyncio
    async def test_update_client_not_found(self, xui_client, mock_httpx_client):
        xui_client.session_cookie = "test_session"
        mock_httpx_client.get.return_value = AsyncMock() # Ensure return value is awaitable
        mock_httpx_client.get.return_value.json.return_value = {
            "success": True,
            "obj": {"id": 1, "settings": "{\"clients\": []}"} # No clients
        }
        with pytest.raises(XUIClientError, match="Client test_uuid not found in inbound 1"):
            await xui_client.update_client(1, "test_uuid", 9876543210)

    @pytest.mark.asyncio
    async def test_delete_user_success(self, xui_client, mock_httpx_client):
        xui_client.session_cookie = "test_session"
        mock_httpx_client.post.return_value = AsyncMock() # Ensure return value is awaitable
        mock_httpx_client.post.return_value.json.return_value = {"success": True}
        
        result = await xui_client.delete_user(1, "test_uuid")
        assert result["success"] is True
        mock_httpx_client.post.assert_called_once_with("/panel/api/inbounds/1/delClient/test_uuid", cookies={"session": "test_session"})

    @pytest.mark.asyncio
    async def test_delete_user_failure(self, xui_client, mock_httpx_client):
        xui_client.session_cookie = "test_session"
        mock_httpx_client.post.return_value = AsyncMock() # Ensure return value is awaitable
        mock_httpx_client.post.return_value.json.return_value = {"success": False, "msg": "Client not found"}
        with pytest.raises(XUIClientError, match="Failed to delete client test_uuid: Client not found"):
            await xui_client.delete_user(1, "test_uuid")

    @pytest.mark.asyncio
    async def test_get_client(self, mock_server, mock_decrypt_password):
        client = get_client(mock_server)
        assert isinstance(client, XUIClient)
        assert client.api_url == "http://mock.server.com"
        assert client.username == "mock_user"
        assert client.password == "decrypted_password"
        mock_decrypt_password.assert_called_once_with("encrypted_password")
