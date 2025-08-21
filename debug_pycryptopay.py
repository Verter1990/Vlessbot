
import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("Starting debug_pycryptopay.py script...")

logger.info(f"Python executable: {sys.executable}")
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"PYTHONPATH environment variable: {os.environ.get('PYTHONPATH')}")
logger.info(f"sys.path before import: {sys.path}")

try:
    logger.info("Attempting to import pycryptopay...")
    import pycryptopay
    logger.info("Successfully imported pycryptopay module.")

    logger.info("Attempting to import AioCryptoPay from pycryptopay...")
    from pycryptopay import AioCryptoPay
    logger.info("Successfully imported AioCryptoPay class.")

    # Try to list contents of pycryptopay installation directory
    pycryptopay_path = os.path.dirname(pycryptopay.__file__)
    logger.info(f"pycryptopay installed at: {pycryptopay_path}")
    logger.info(f"Contents of pycryptopay directory: {os.listdir(pycryptopay_path)}")

    # Attempt to instantiate AioCryptoPay (requires a token, even a dummy one)
    # Replace "YOUR_DUMMY_TOKEN" with an actual token if you want to test instantiation further
    # For now, we'll just try to instantiate without making actual API calls
    try:
        logger.info("Attempting to instantiate AioCryptoPay...")
        # AioCryptoPay requires a token, even if it's invalid for this test
        # This might still raise an error if the token format is strictly validated
        crypto_client = AioCryptoPay("YOUR_DUMMY_TOKEN") 
        logger.info("Successfully instantiated AioCryptoPay.")
        # Close the client if it was successfully instantiated
        # if hasattr(crypto_client, 'close') and callable(crypto_client.close):
        #     import asyncio
        #     asyncio.run(crypto_client.close())
        #     logger.info("AioCryptoPay client closed.")
    except Exception as e:
        logger.error(f"Error during AioCryptoPay instantiation: {e}", exc_info=True)

except ModuleNotFoundError as e:
    logger.error(f"ModuleNotFoundError: {e}", exc_info=True)
    logger.error("pycryptopay module was not found. This is the primary issue.")
except ImportError as e:
    logger.error(f"ImportError: {e}", exc_info=True)
    logger.error("An issue occurred during import, possibly a missing sub-module or dependency.")
except Exception as e:
    logger.error(f"An unexpected error occurred during import or initial checks: {e}", exc_info=True)

logger.info("Script finished.")
