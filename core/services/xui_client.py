import httpx
import json
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from loguru import logger
from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import Optional, List, Dict, Any

from core.database.models import Server
from core.utils.security import decrypt_password

class XUIClientError(Exception):
    """Custom exception for XUI client errors."""
    pass

# --- Pydantic Models for API Requests and Responses ---

class XUIBaseResponse(BaseModel):
    success: bool
    msg: Optional[str] = None

class LoginResponse(XUIBaseResponse):
    obj: Optional[Any] = None

class ClientConfig(BaseModel):
    id: str
    email: str
    flow: str = ""
    limitIp: int = 0
    totalGB: int = 0
    expiryTime: int = 0
    enable: bool = True
    tgId: str = ""
    subId: str = ""

class InboundSettings(BaseModel):
    clients: List[ClientConfig] = []
    decryption: str = 'none'
    fallbacks: List[Any] = []

class RealitySettings(BaseModel):
    show: bool
    xver: int
    dest: str
    serverNames: List[str]
    privateKey: str
    minClient: str
    maxClient: str
    maxTimediff: int
    shortIds: List[str]
    settings: Dict[str, Any]

class StreamSettings(BaseModel):
    network: str
    security: str
    externalProxy: List[Any] = []
    realitySettings: Optional[RealitySettings] = None
    tcpSettings: Optional[Dict[str, Any]] = None
    wsSettings: Optional[Dict[str, Any]] = None

class SniffingSettings(BaseModel):
    enabled: bool
    destOverride: List[str]
    metadataOnly: bool = False
    routeOnly: bool = False

class Inbound(BaseModel):
    id: Optional[int] = None
    up: Optional[int] = None
    down: Optional[int] = None
    total: Optional[int] = None
    remark: Optional[str] = None
    enable: Optional[bool] = None
    expiryTime: Optional[int] = None
    clientStats: Optional[Any] = None
    listen: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = None
    settings: InboundSettings
    streamSettings: StreamSettings
    tag: Optional[str] = None
    sniffing: SniffingSettings
    allocate: Optional[Dict[str, Any]] = None

    @model_validator(mode='before')
    def parse_json_strings(cls, values):
        for field in ['settings', 'streamSettings', 'sniffing', 'allocate']:
            if field in values and isinstance(values[field], str):
                try:
                    values[field] = json.loads(values[field])
                except json.JSONDecodeError:
                    pass
        return values

class GetInboundResponse(XUIBaseResponse):
    obj: Optional[Inbound] = None

class AddClientResponse(XUIBaseResponse):
    obj: Optional[Any] = None

class UpdateClientResponse(XUIBaseResponse):
    obj: Optional[Any] = None

class DeleteClientResponse(XUIBaseResponse):
    obj: Optional[Any] = None

class XUIClient:
    """A robust asynchronous client for X-UI panel API."""

    def __init__(self, api_url: str, username: str, password: str):
        self.api_url = api_url.rstrip('/')
        self.username = username
        self.password = password
        self.client = httpx.AsyncClient(base_url=self.api_url, timeout=30, verify=False)
        self._is_authenticated = False

    async def _login(self):
        """Authenticates with the X-UI panel."""
        if self._is_authenticated:
            return

        logger.info(f"Attempting to log in to X-UI at {self.api_url}")
        try:
            response = await self.client.post(
                "/login",
                data={"username": self.username, "password": self.password}
            )
            response.raise_for_status()
            result = response.json()
            login_response = LoginResponse.model_validate(result)

            if login_response.success:
                self._is_authenticated = True
                logger.success(f"Successfully logged in to {self.api_url}")
            else:
                raise XUIClientError(f"Login failed: {login_response.msg or 'Unknown error'}")

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during XUI login to {self.api_url}: {e.response.status_code} - {e.response.text}")
            raise XUIClientError(f"HTTP error during XUI login: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error(f"Network error during XUI login to {self.api_url}: {e}")
            raise XUIClientError(f"Network error during XUI login: {e}") from e
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error during XUI login to {self.api_url}: {e}")
            raise XUIClientError(f"JSON decode error during XUI login: {e}") from e
        except ValidationError as e:
            logger.error(f"Pydantic validation error during XUI login: {e} - Response: {result}")
            raise XUIClientError(f"Pydantic validation error during XUI login: {e}") from e

    async def _ensure_authenticated(self):
        """Ensures that the client has an active session, logging in if necessary."""
        if not self._is_authenticated:
            await self._login()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(httpx.RequestError))
    async def get_inbound(self, inbound_id: int) -> Optional[Inbound]:
        """Retrieves details for a specific inbound configuration."""
        await self._ensure_authenticated()
        logger.info(f"Getting inbound {inbound_id} details...")
        try:
            response = await self.client.get(f"/panel/api/inbounds/get/{inbound_id}")
            response.raise_for_status()
            if not response.text:
                raise XUIClientError("Empty response from server")
            result = response.json()
            get_inbound_response = GetInboundResponse.model_validate(result)
            if get_inbound_response.success and get_inbound_response.obj:
                logger.info(f"Inbound {inbound_id} details retrieved successfully.")
                return get_inbound_response.obj
            else:
                raise XUIClientError(f"Failed to get inbound {inbound_id}: {get_inbound_response.msg or 'Unknown error'}")
        except (httpx.HTTPStatusError, httpx.RequestError, json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Error getting inbound {inbound_id}: {e}")
            raise XUIClientError(f"Error getting inbound: {e}") from e

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(httpx.RequestError))
    async def add_client(self, inbound_id: int, client_config: ClientConfig) -> dict:
        """Adds a new client to a specific inbound configuration."""
        await self._ensure_authenticated()
        logger.info(f"Adding client {client_config.email} to inbound {inbound_id}...")
        payload = {
            "id": inbound_id,
            "settings": json.dumps({"clients": [client_config.model_dump(by_alias=True)]})
        }
        logger.info(f"Отправка данных: {payload}")
        try:
            response = await self.client.post("/panel/api/inbounds/addClient", data=payload)
            response.raise_for_status()
            if not response.text:
                raise XUIClientError("Empty response from server")
            result = response.json()
            add_client_response = AddClientResponse.model_validate(result)
            if add_client_response.success:
                logger.info(f"User {client_config.email} created successfully.")
                return {"success": True, "uuid": client_config.id}
            else:
                raise XUIClientError(f"Failed to create user {client_config.email}: {add_client_response.msg or 'Unknown error'}")
        except (httpx.HTTPStatusError, httpx.RequestError, json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Error creating user {client_config.email}: {e}")
            raise XUIClientError(f"Error creating user: {e}") from e

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(httpx.RequestError))
    async def update_client(self, inbound_id: int, uuid: str, new_expiry_time_ms: int, new_total_gb: Optional[int] = None) -> dict:
        """Updates an existing client's settings by sending a payload similar to add_client."""
        await self._ensure_authenticated()
        logger.info(f"Attempting to update client {uuid} in inbound {inbound_id} (v3 logic)...")

        # First, we need the original client details to ensure we only change what's necessary.
        inbound = await self.get_inbound(inbound_id)
        if not inbound:
            raise XUIClientError(f"Inbound {inbound_id} not found, cannot update client.")

        client_to_update_model = None
        for client in inbound.settings.clients:
            if client.id == uuid:
                # Create a copy to modify, preserving the original model's other fields
                client_to_update_model = client.model_copy(deep=True)
                break

        if not client_to_update_model:
            raise XUIClientError(f"Client {uuid} not found in inbound {inbound_id}")

        # Apply the updates to our copy
        client_to_update_model.expiryTime = new_expiry_time_ms
        if new_total_gb is not None:
            client_to_update_model.totalGB = new_total_gb
        else: # Ensure we send the original value if not changing
            client_to_update_model.totalGB = client_to_update_model.totalGB or 0

        # Mimic the structure of addClient: `{"clients": [...]}`
        update_payload_obj = {"clients": [client_to_update_model.model_dump(by_alias=True)]}
        settings_json_string = json.dumps(update_payload_obj)

        payload = {
            "id": inbound_id,
            "settings": settings_json_string
        }
        logger.info(f"Sending update payload for client {uuid}: {payload}")

        try:
            response = await self.client.post(f"/panel/api/inbounds/updateClient/{uuid}", data=payload)
            response.raise_for_status()
            if not response.text:
                raise XUIClientError("Empty response from server on client update")

            result = response.json()
            update_response = UpdateClientResponse.model_validate(result)

            if update_response.success:
                logger.success(f"Client {uuid} updated successfully in inbound {inbound_id}.")
                return {"success": True}
            else:
                logger.error(f"Failed to update client {uuid}. Panel msg: {update_response.msg}. Full response: {response.text}")
                raise XUIClientError(f"Failed to update client {uuid}: {update_response.msg or 'Unknown error'}")

        except (httpx.HTTPStatusError, httpx.RequestError, json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Error updating client {uuid}: {e}")
            if hasattr(e, 'response'):
                logger.error(f"Response body: {e.response.text}")
            raise XUIClientError(f"Error updating client: {e}") from e

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(httpx.RequestError))
    async def delete_client(self, inbound_id: int, uuid: str) -> dict:
        """Deletes a client from a specific inbound configuration."""
        await self._ensure_authenticated()
        logger.info(f"Deleting client {uuid} from inbound {inbound_id}...")
        try:
            # Note: The delete endpoint requires the UUID in the URL path
            response = await self.client.post(f"/panel/api/inbounds/{inbound_id}/delClient/{uuid}")
            response.raise_for_status()
            if not response.text:
                raise XUIClientError("Empty response from server")
            result = response.json()
            delete_client_response = DeleteClientResponse.model_validate(result)
            if delete_client_response.success:
                logger.info(f"Client {uuid} deleted successfully.")
                return {"success": True}
            else:
                raise XUIClientError(f"Failed to delete client {uuid}: {delete_client_response.msg or 'Unknown error'}")
        except (httpx.HTTPStatusError, httpx.RequestError, json.JSONDecodeError, ValidationError) as e:
            logger.error(f"Error deleting client {uuid}: {e}")
            raise XUIClientError(f"Error deleting client: {e}") from e

    async def close(self):
        """Closes the underlying HTTP client session."""
        if not self.client.is_closed:
            await self.client.aclose()

async def get_client(server: Server) -> XUIClient:
    """Returns an authenticated XUIClient instance for a specific server."""
    decrypted_password = decrypt_password(server.api_password)
    return XUIClient(
        api_url=server.api_url,
        username=server.api_user,
        password=decrypted_password
    )