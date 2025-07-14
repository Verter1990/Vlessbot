import httpx
import json
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from loguru import logger

# We need the Server model for type hinting and the decryption utility
from core.database.models import Server
from core.utils.security import decrypt_password


class XUIClientError(Exception):
    """Custom exception for XUI client errors."""
    pass

class XUIClient:
    def __init__(self, api_url: str, username: str, password: str):
        self.api_url = api_url.rstrip('/')
        self.username = username
        self.password = password
        self.client = httpx.AsyncClient(base_url=self.api_url, timeout=30)
        self.session_cookie = None

    async def _login(self):
        logger.info("Attempting to log in to XUI panel...")
        try:
            response = await self.client.post(
                "/login",
                data={'username': self.username, 'password': self.password}
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("success"):
                self.session_cookie = response.cookies.get('session') # Get session cookie if available
                logger.info("Successfully logged in to XUI panel.")
            else:
                raise XUIClientError(f"Login failed. Response: {result.get('msg', response.text)}")

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during XUI login: {e.response.status_code} - {e.response.text}")
            raise XUIClientError(f"HTTP error during XUI login: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error(f"Network error during XUI login: {e}")
            raise XUIClientError(f"Network error during XUI login: {e}") from e

    async def _ensure_authenticated(self):
        if not self.session_cookie:
            await self._login()

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(httpx.RequestError))
    async def get_inbound(self, inbound_id: int) -> dict:
        await self._ensure_authenticated()
        logger.info(f"Getting inbound {inbound_id} details...")
        try:
            response = await self.client.get(
                f"/panel/api/inbounds/get/{inbound_id}",
                cookies={"session": self.session_cookie}
            )
            response.raise_for_status()
            result = response.json()
            if result.get("success"):
                logger.info(f"Inbound {inbound_id} details retrieved successfully.")
                inbound = result.get("obj", {})
                if "settings" in inbound and isinstance(inbound["settings"], str):
                    inbound["settings"] = json.loads(inbound["settings"])
                return inbound
            else:
                raise XUIClientError(f"Failed to get inbound {inbound_id}: {result.get('msg', response.text)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error getting inbound {inbound_id}: {e.response.status_code} - {e.response.text}")
            raise XUIClientError(f"HTTP error getting inbound: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error(f"Network error getting inbound {inbound_id}: {e}")
            raise XUIClientError(f"Network error getting inbound: {e}") from e

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(httpx.RequestError))
    async def create_user(self, inbound_id: int, uuid: str, email: str, expire_time_ms: int, telegram_id: str = "") -> dict:
        await self._ensure_authenticated()
        logger.info(f"Creating user {email} for inbound {inbound_id}...")
        
        client_settings = {
            "id": uuid,
            "email": email,
            "flow": "",
            "limitIp": 0,
            "totalGB": 0,
            "expiryTime": expire_time_ms,
            "enable": True,
            "tgId": str(telegram_id),
            "subId": ""
        }
        
        payload = {
            "id": inbound_id,
            "settings": json.dumps({"clients": [client_settings]})
        }

        try:
            response = await self.client.post(
                "/panel/api/inbounds/addClient",
                data=payload,
                cookies={"session": self.session_cookie}
            )
            response.raise_for_status()
            result = response.json()

            if result.get("success"):
                logger.info(f"User {email} created successfully.")
                return {"success": True, "uuid": uuid}
            else:
                raise XUIClientError(f"Failed to create user {email}: {result.get('msg', response.text)}")

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error creating user {email}: {e.response.status_code} - {e.response.text}")
            raise XUIClientError(f"HTTP error creating user: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error(f"Network error creating user {email}: {e}")
            raise XUIClientError(f"Network error creating user: {e}") from e

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(httpx.RequestError))
    async def update_client(self, inbound_id: int, uuid: str, expire_time_ms: int) -> dict:
        await self._ensure_authenticated()
        logger.info(f"Updating client {uuid} for inbound {inbound_id}...")

        inbound = await self.get_inbound(inbound_id)
        if not inbound:
            raise XUIClientError(f"Inbound {inbound_id} not found")

        clients = inbound.get("settings", {}).get("clients", [])
        client_found = False
        for client in clients:
            if client.get("id") == uuid:
                client["expiryTime"] = expire_time_ms
                client_found = True
                break

        if not client_found:
            raise XUIClientError(f"Client {uuid} not found in inbound {inbound_id}")

        payload = {
            "id": inbound_id,
            "settings": json.dumps({"clients": clients})
        }

        try:
            response = await self.client.post(
                "/panel/api/inbounds/updateClient",
                data=payload,
                cookies={"session": self.session_cookie}
            )
            response.raise_for_status()
            result = response.json()

            if result.get("success"):
                logger.info(f"Client {uuid} updated successfully.")
                return {"success": True}
            else:
                raise XUIClientError(f"Failed to update client {uuid}: {result.get('msg', response.text)}")

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error updating client {uuid}: {e.response.status_code} - {e.response.text}")
            raise XUIClientError(f"HTTP error updating client: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error(f"Network error updating client {uuid}: {e}")
            raise XUIClientError(f"Network error updating client: {e}") from e

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(httpx.RequestError))
    async def delete_user(self, inbound_id: int, uuid: str) -> dict:
        await self._ensure_authenticated()
        logger.info(f"Deleting client {uuid} from inbound {inbound_id}...")

        try:
            response = await self.client.post(
                f"/panel/api/inbounds/{inbound_id}/delClient/{uuid}",
                cookies={"session": self.session_cookie}
            )
            response.raise_for_status()
            result = response.json()

            if result.get("success"):
                logger.info(f"Client {uuid} deleted successfully.")
                return {"success": True}
            else:
                raise XUIClientError(f"Failed to delete client {uuid}: {result.get('msg', response.text)}")

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error deleting client {uuid}: {e.response.status_code} - {e.response.text}")
            raise XUIClientError(f"HTTP error deleting client: {e.response.status_code}") from e
        except httpx.RequestError as e:
            logger.error(f"Network error deleting client {uuid}: {e}")
            raise XUIClientError(f"Network error deleting client: {e}") from e

def get_client(server: Server) -> XUIClient:
    """
    Returns an authenticated XUIClient instance for a specific server.
    """
    decrypted_password = decrypt_password(server.api_password)
    return XUIClient(
        api_url=server.api_url,
        username=server.api_user,
        password=decrypted_password
    )
