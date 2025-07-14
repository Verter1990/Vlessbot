import asyncio
import uuid
from datetime import datetime, timedelta
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database.database import async_session_maker, init_db
from core.database.models import User, Server, Subscription
from core.services.xui_client import get_client, XUIClientError
from loguru import logger

# --- Test Configuration ---
TEST_TELEGRAM_ID = 218265585
# We assume the default server has ID=1. If not, this needs to be adjusted.
TEST_SERVER_ID = 1 
# ---

async def generate_test_link():
    """
    Connects to the DB, finds the user and server,
    and generates a new VPN key.
    """
    logger.info("--- Starting Test Link Generation ---")
    
    # 1. Initialize DB Connection
    await init_db()
    async with async_session_maker() as session:
        
        # 2. Find or Create User
        stmt = select(User).where(User.telegram_id == TEST_TELEGRAM_ID)
        result = await session.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            logger.info(f"User {TEST_TELEGRAM_ID} not found. Creating a new one for the test.")
            user = User(telegram_id=TEST_TELEGRAM_ID, username="test_user")
            session.add(user)
            await session.commit()
            logger.info(f"User {TEST_TELEGRAM_ID} created.")
        else:
            logger.info(f"Found existing user {user.telegram_id}.")

        # 3. Find Server
        server = await session.get(Server, TEST_SERVER_ID)
        if not server:
            logger.error(f"Server with ID={TEST_SERVER_ID} not found in the database.")
            logger.error("Please run the db_check_and_seed.py script first to add the default server.")
            return
        logger.info(f"Found server: {server.name}")

        # 4. Clean up existing user in X-UI if any (to avoid duplicate email error)
        xui_client = get_client(server)
        logger.info(f"Attempting to delete existing user {TEST_TELEGRAM_ID}@test.com from X-UI...")
        try:
            # First, try to get the inbound to find existing clients
            inbound = await xui_client.get_inbound(server.inbound_id)
            if inbound and "settings" in inbound and "clients" in inbound["settings"]:
                clients = inbound["settings"]["clients"]
                for client in clients:
                    if client.get("email") == f"{TEST_TELEGRAM_ID}@test.com":
                        logger.info(f'Found existing client in X-UI with UUID: {client.get("id")}. Deleting...')
                        await xui_client.delete_user(server.inbound_id, client.get("id"))
                        logger.info("Existing client deleted from X-UI.")
                        break
        except XUIClientError as e:
            logger.warning(f"Could not delete existing user from X-UI (might not exist): {e}")
        except Exception as e:
            logger.warning(f"Unexpected error during X-UI cleanup: {e}")

        # 5. Generate Key using XUI Client
        logger.info("Attempting to create/update a VPN key via xui_client...")
        try:
            # Check if a subscription already exists for this user and server in our DB
            stmt = select(Subscription).where(
                Subscription.user_id == user.telegram_id,
                Subscription.server_id == server.id
            )
            result = await session.execute(stmt)
            existing_subscription = result.scalars().first()

            user_uuid = None
            if existing_subscription:
                user_uuid = existing_subscription.xui_user_uuid
                logger.info(f"Existing subscription found in DB. Updating expiry for UUID: {user_uuid}")
                # Generate a key for 7 days for this test
                expire_time = datetime.utcnow() + timedelta(days=7)
                expire_time_ms = int(expire_time.timestamp() * 1000)
                await xui_client.update_client(server.inbound_id, user_uuid, expire_time_ms)
                existing_subscription.expires_at = expire_time
                await session.commit()
            else:
                user_uuid = str(uuid.uuid4())
                logger.info(f"No existing subscription in DB. Creating new user with UUID: {user_uuid}")
                # Generate a key for 7 days for this test
                expire_time = datetime.utcnow() + timedelta(days=7)
                expire_time_ms = int(expire_time.timestamp() * 1000)

                create_response = await xui_client.create_user(
                    inbound_id=server.inbound_id,
                    uuid=user_uuid,
                    email=f"{user.telegram_id}@test.com",
                    expire_time_ms=expire_time_ms,
                    telegram_id=str(user.telegram_id)
                )
                
                if not create_response.get("success"):
                    logger.error(f"Failed to create user in X-UI: {create_response}")
                    return

                logger.info(f"Successfully created user in X-UI with UUID: {user_uuid}")

                new_subscription = Subscription(
                    user_id=user.telegram_id,
                    server_id=server.id,
                    xui_user_uuid=user_uuid,
                    expires_at=expire_time,
                    is_active=True
                )
                session.add(new_subscription)
                await session.commit()

            # 6. Construct the VLESS link
            inbound = await xui_client.get_inbound(server.inbound_id)
            if not inbound:
                logger.error("Could not retrieve inbound details to construct the link.")
                return

            settings_data = inbound.get("settings", {})
            params_list = []
            if "security" in settings_data:
                params_list.append(f"security={settings_data.get('security', 'tls')}")
            if "encryption" in settings_data:
                params_list.append(f"encryption={settings_data.get('encryption', 'none')}")
            if "type" in settings_data:
                params_list.append(f"type={settings_data.get('type', 'tcp')}")
            
            params = "&".join(params_list)
            
            parsed_url = urlparse(server.api_url)
            host = parsed_url.hostname
            port = parsed_url.port or 443
            
            vless_link = f"vless://{user_uuid}@{host}:{port}?{params}#Test_{server.name}"

            print("---" * 10)
            print("✅ TEST SUCCEEDED ✅")
            print("Generated VLESS Link:")
            print(vless_link)
            print("---" * 10)

        except XUIClientError as e:
            logger.error(f"An XUIClientError occurred: {e}")
            print("---" * 10)
            print("❌ TEST FAILED ❌")
            print(f"Could not generate link due to an API error: {e}")
            print("---" * 10)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            print("---" * 10)
            print("❌ TEST FAILED ❌")
            print(f"An unexpected error occurred: {e}")
            print("---" * 10)


if __name__ == "__main__":
    asyncio.run(generate_test_link())
