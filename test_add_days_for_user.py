
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

# Temporarily add the project root to the path to allow imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.database.models import User, Server, Subscription
from core.handlers.user_handlers import _create_or_update_vpn_key
from core.services.xui_client import XUIClient, XUIClientError

async def run_test():
    """
    Performs a dry run of the subscription extension logic for a specific user.
    """
    USER_ID_TO_TEST = 218265585
    DAYS_TO_ADD = 30

    print("--- Starting Test: Extend Subscription for a Specific User ---")
    print(f"[*] User ID: {USER_ID_TO_TEST}")
    print(f"[*] Days to Add: {DAYS_TO_ADD}")
    print("-" * 20)

    # --- 1. Setup Mock Objects ---
    # We don't have a real DB connection, so we create mock objects to simulate the data.
    mock_user = User(
        telegram_id=USER_ID_TO_TEST,
        username='real_user_test',
        language_code='ru'
    )

    mock_server = Server(
        id=1,
        name='Netherlands Server',
        api_url='http://mock.server:54321',
        api_user='admin',
        api_password='password',
        inbound_id=10
    )

    # Simulate an existing subscription that expires in 5 days
    existing_uuid = str(uuid.uuid4())
    initial_expiry = datetime.utcnow() + timedelta(days=5)
    mock_subscription = Subscription(
        user_id=mock_user.telegram_id,
        server_id=mock_server.id,
        xui_user_uuid=existing_uuid,
        expires_at=initial_expiry,
        is_active=True
    )
    
    print(f"[1] Mocks created. Initial expiry date: {initial_expiry.strftime('%Y-%m-%d %H:%M:%S')}")

    # --- 2. Mock the Database Session ---
    # This fake session will return our mock_subscription when queried.
    mock_session = MagicMock()
    
    # This complex part ensures that the `(await session.execute(...)).scalars().first()` call chain works
    scalars_obj = MagicMock()
    scalars_obj.first.return_value = mock_subscription
    execute_obj = MagicMock()
    execute_obj.scalars.return_value = scalars_obj
    mock_session.execute = AsyncMock(return_value=execute_obj)
    mock_session.commit = AsyncMock() # Mock the commit method

    print("[2] Mock database session configured to return the existing subscription.")

    # --- 3. Mock the X-UI Client ---
    # We don't want to call the real X-UI API.
    mock_xui_client_instance = MagicMock(spec=XUIClient)
    mock_xui_client_instance.update_client = AsyncMock(return_value={"success": True})
    mock_xui_client_instance.add_client = AsyncMock() # Should not be called

    # --- 4. Patch the necessary functions ---
    # We intercept the calls to `get_client` and `_generate_vless_link`
    with patch('core.handlers.user_handlers.get_client', new_callable=AsyncMock) as mock_get_client:
        mock_get_client.return_value = mock_xui_client_instance
        
        with patch('core.handlers.user_handlers._generate_vless_link', new_callable=AsyncMock) as mock_generate_link:
            mock_generate_link.return_value = "vless://this_is_a_mock_link"
            
            print("[3] X-UI client and helper functions are now mocked.")
            print("-" * 20)
            print("[*] Calling the function _create_or_update_vpn_key...")

            # --- 5. Execute the actual function ---
            try:
                vless_link, new_expiry_date = await _create_or_update_vpn_key(
                    session=mock_session,
                    user=mock_user,
                    server=mock_server,
                    days=DAYS_TO_ADD,
                    lang='ru'
                )
                print("[+] Function executed successfully!")
                print("-" * 20)

                # --- 6. Verify the results ---
                print("[4] Verifying results...")

                # Check that the update function was called on the X-UI client
                try:
                    mock_xui_client_instance.update_client.assert_called_once()
                    print("  - SUCCESS: `update_client` was called on the X-UI client.")
                except AssertionError:
                    print("  - FAILURE: `update_client` was NOT called.")

                # Check that the add function was NOT called
                try:
                    mock_xui_client_instance.add_client.assert_not_called()
                    print("  - SUCCESS: `add_client` was not called.")
                except AssertionError:
                    print("  - FAILURE: `add_client` was called, which is incorrect for an extension.")

                # Check the arguments sent to the update function
                expected_new_expiry = initial_expiry + timedelta(days=DAYS_TO_ADD)
                expected_new_expiry_ms = int(expected_new_expiry.timestamp() * 1000)
                
                call_args = mock_xui_client_instance.update_client.call_args[1]
                print(f"  - INFO: `update_client` was called with:")
                print(f"    - inbound_id: {call_args['inbound_id']}")
                print(f"    - uuid: {call_args['uuid']}")
                print(f"    - new_expiry_time_ms: {call_args['new_expiry_time_ms']}")

                # Check if the calculated expiry time is correct
                if call_args['new_expiry_time_ms'] == expected_new_expiry_ms:
                    print("  - SUCCESS: The new expiry timestamp is correct.")
                else:
                    print(f"  - FAILURE: Expiry timestamp is INCORRECT. Expected {expected_new_expiry_ms}, got {call_args['new_expiry_time_ms']}")

                # Check that the database commit was called
                try:
                    mock_session.commit.assert_called_once()
                    print("  - SUCCESS: `session.commit()` was called to save changes in the database.")
                except AssertionError:
                    print("  - FAILURE: `session.commit()` was not called.")

                print("-" * 20)
                print(f"[*] Final Result: The new subscription would expire on: {new_expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
                print("--- Test Finished ---")

            except Exception as e:
                print(f"\n[!!!] AN ERROR OCCURRED DURING THE TEST: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
