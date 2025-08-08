import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request
from yookassa.domain.notification import WebhookNotification
from core.config import settings
import json

# Import main here, after all patching is set up
# This is a workaround for how Python imports and patching work.
# In a real application, you might refactor main.py to make it more testable.
# For now, we'll import it inside the test functions to ensure mocks are applied.

@pytest.mark.asyncio
async def test_yookassa_webhook_valid_signature(mocker):
    """
    Test that yookassa_webhook processes a valid webhook with correct signature.
    """
    # Patch verify_yookassa_signature before importing main
    mock_verify_signature = mocker.patch('main.verify_yookassa_signature', return_value=True)
    
    # Now import main
    from main import yookassa_webhook, process_successful_payment, async_session_maker, bot

    mock_payload = {"event": "payment.succeeded", "object": {"id": "test_payment_id"}}
    mock_raw_body = json.dumps(mock_payload).encode('utf-8')
    mock_signature = "valid_signature"

    mock_request = AsyncMock(spec=Request)
    mock_request.json.return_value = mock_payload
    mock_request.body.return_value = mock_raw_body
    mock_request.headers.get.return_value = mock_signature

    mocker.patch('main.WebhookNotification', return_value=MagicMock(object=MagicMock(id="test_payment_id"), event="payment.succeeded"))
    
    mock_session = AsyncMock()
    mock_session.get.return_value = MagicMock(status='pending', id="test_payment_id")
    
    # Correctly mock async_session_maker as an async context manager
    mock_async_session_maker = AsyncMock()
    mock_async_session_maker.return_value.__aenter__.return_value = mock_session
    mocker.patch('main.async_session_maker', new=mock_async_session_maker)

    mocker.patch('main.bot', new=AsyncMock())
    mocker.patch('main.process_successful_payment', new_callable=AsyncMock)

    response = await yookassa_webhook(mock_request)

    mock_verify_signature.assert_called_once_with(mock_raw_body, mock_signature)
    assert response == {"status": "ok"}

@pytest.mark.asyncio
async def test_yookassa_webhook_invalid_signature(mocker):
    """
    Test that yookassa_webhook returns 400 for invalid signature.
    """
    mock_verify_signature = mocker.patch('main.verify_yookassa_signature', return_value=False)
    from main import yookassa_webhook, process_successful_payment, async_session_maker, bot

    mock_payload = {"event": "payment.succeeded", "object": {"id": "test_payment_id"}}
    mock_raw_body = json.dumps(mock_payload).encode('utf-8')
    mock_signature = "invalid_signature"

    mock_request = AsyncMock(spec=Request)
    mock_request.json.return_value = mock_payload
    mock_request.body.return_value = mock_raw_body
    mock_request.headers.get.return_value = mock_signature

    mock_logger_error = mocker.patch('loguru.logger.error')

    response, status_code = await yookassa_webhook(mock_request)

    mock_verify_signature.assert_called_once_with(mock_raw_body, mock_signature)
    assert response == {"status": "error", "message": "Invalid signature"}
    assert status_code == 400
    mock_logger_error.assert_called_once()

@pytest.mark.asyncio
async def test_yookassa_webhook_transaction_not_found(mocker):
    """
    Test that yookassa_webhook returns 'ok' and logs a warning if transaction is not found.
    """
    mock_verify_signature = mocker.patch('main.verify_yookassa_signature', return_value=True)
    from main import yookassa_webhook, process_successful_payment, async_session_maker, bot

    mock_payload = {"event": "payment.succeeded", "object": {"id": "non_existent_id"}}
    mock_raw_body = json.dumps(mock_payload).encode('utf-8')
    mock_signature = "valid_signature"

    mock_request = AsyncMock(spec=Request)
    mock_request.json.return_value = mock_payload
    mock_request.body.return_value = mock_raw_body
    mock_request.headers.get.return_value = mock_signature

    mocker.patch('main.WebhookNotification', return_value=MagicMock(object=MagicMock(id="non_existent_id"), event="payment.succeeded"))
    
    mock_session = AsyncMock()
    mock_session.get.return_value = None
    mock_async_session_maker = AsyncMock()
    mock_async_session_maker.return_value.__aenter__.return_value = mock_session
    mocker.patch('main.async_session_maker', new=mock_async_session_maker)

    mocker.patch('main.bot', new=AsyncMock())
    mocker.patch('main.process_successful_payment', new_callable=AsyncMock)
    
    mock_logger_warning = mocker.patch('loguru.logger.warning')

    response = await yookassa_webhook(mock_request)

    assert response == {"status": "ok"}
    mock_logger_warning.assert_called_once_with("Transaction with id non_existent_id not found in DB.")

@pytest.mark.asyncio
async def test_yookassa_webhook_transaction_already_processed(mocker):
    """
    Test that yookassa_webhook logs info if transaction is already succeeded.
    """
    mock_verify_signature = mocker.patch('main.verify_yookassa_signature', return_value=True)
    from main import yookassa_webhook, process_successful_payment, async_session_maker, bot

    mock_payload = {"event": "payment.succeeded", "object": {"id": "already_succeeded_id"}}
    mock_raw_body = json.dumps(mock_payload).encode('utf-8')
    mock_signature = "valid_signature"

    mock_request = AsyncMock(spec=Request)
    mock_request.json.return_value = mock_payload
    mock_request.body.return_value = mock_raw_body
    mock_request.headers.get.return_value = mock_signature

    mocker.patch('main.WebhookNotification', return_value=MagicMock(object=MagicMock(id="already_succeeded_id"), event="payment.succeeded"))
    
    mock_session = AsyncMock()
    mock_session.get.return_value = MagicMock(status='succeeded', id="already_succeeded_id")
    mock_async_session_maker = AsyncMock()
    mock_async_session_maker.return_value.__aenter__.return_value = mock_session
    mocker.patch('main.async_session_maker', new=mock_async_session_maker)

    mocker.patch('main.bot', new=AsyncMock())
    mocker.patch('main.process_successful_payment', new_callable=AsyncMock)
    
    mock_logger_info = mocker.patch('loguru.logger.info')

    response = await yookassa_webhook(mock_request)

    assert response == {"status": "ok"}
    mock_logger_info.assert_called_once_with("Transaction already_succeeded_id already processed.")

@pytest.mark.asyncio
async def test_yookassa_webhook_payment_canceled(mocker):
    """
    Test that yookassa_webhook correctly handles payment.canceled event.
    """
    mock_verify_signature = mocker.patch('main.verify_yookassa_signature', return_value=True)
    from main import yookassa_webhook, process_successful_payment, async_session_maker, bot

    mock_payload = {"event": "payment.canceled", "object": {"id": "canceled_id"}}
    mock_raw_body = json.dumps(mock_payload).encode('utf-8')
    mock_signature = "valid_signature"

    mock_request = AsyncMock(spec=Request)
    mock_request.json.return_value = mock_payload
    mock_request.body.return_value = mock_raw_body
    mock_request.headers.get.return_value = mock_signature

    mocker.patch('main.WebhookNotification', return_value=MagicMock(object=MagicMock(id="canceled_id"), event="payment.canceled"))
    
    mock_transaction = MagicMock(status='pending', id="canceled_id")
    mock_session = AsyncMock()
    mock_session.get.return_value = mock_transaction
    mock_async_session_maker = AsyncMock()
    mock_async_session_maker.return_value.__aenter__.return_value = mock_session
    mocker.patch('main.async_session_maker', new=mock_async_session_maker)

    mocker.patch('main.bot', new=AsyncMock())
    mocker.patch('main.process_successful_payment', new_callable=AsyncMock)
    
    mock_logger_info = mocker.patch('loguru.logger.info')

    response = await yookassa_webhook(mock_request)

    assert response == {"status": "ok"}
    assert mock_transaction.status == 'canceled'
    mock_session.commit.assert_called_once()
    mock_logger_info.assert_called_once_with("Transaction canceled_id was canceled.")

@pytest.mark.asyncio
async def test_yookassa_webhook_exception_handling(mocker):
    """
    Test that yookassa_webhook handles exceptions gracefully and returns 'error'.
    """
    mock_verify_signature = mocker.patch('main.verify_yookassa_signature', return_value=True)
    from main import yookassa_webhook, process_successful_payment, async_session_maker, bot

    mock_payload = {"event": "payment.succeeded", "object": {"id": "test_payment_id"}}
    mock_raw_body = json.dumps(mock_payload).encode('utf-8')
    mock_signature = "valid_signature"

    mock_request = AsyncMock(spec=Request)
    mock_request.json.return_value = mock_payload
    mock_request.body.return_value = mock_raw_body
    mock_request.headers.get.return_value = mock_signature

    mocker.patch('main.WebhookNotification', side_effect=Exception("Test exception"))
    
    mock_logger_error = mocker.patch('loguru.logger.error')

    response = await yookassa_webhook(mock_request)

    assert response == {"status": "error"}
    mock_logger_error.assert_called_once() # Check that error was logged
    assert "Error processing YooKassa webhook: Test exception" in mock_logger_error.call_args[0][0]
