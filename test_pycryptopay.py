import sys
import os

print("sys.path before import:", sys.path)

try:
    from pycryptopay import AioCryptoPay
    print("Successfully imported AioCryptoPay")
    # You might need a dummy token for instantiation, or just skip it if import works
    # crypto = AioCryptoPay("YOUR_DUMMY_TOKEN")
    # print("Successfully instantiated AioCryptoPay")
except ModuleNotFoundError as e:
    print(f"ModuleNotFoundError: {e}")
    print("Current working directory:", os.getcwd())
    print("PYTHONPATH environment variable:", os.environ.get('PYTHONPATH'))
except Exception as e:
    print(f"An unexpected error occurred: {e}")

print("Script finished.")