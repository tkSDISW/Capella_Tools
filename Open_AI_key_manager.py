
from pathlib import Path


def get_api_key():
    """Retrieve the OpenAI API key from a hidden file."""
    home_dir = Path.home()
    key_file = home_dir / ".secrets" / "openai_api_key.txt"

    if not key_file.exists():
        raise FileNotFoundError(
            f"API Key file not found at {key_file}. "
            "Please ensure the key is saved correctly."
        )

    with key_file.open("r") as f:
        api_key = f.read().strip()

    if not api_key:
        raise ValueError("API Key file is empty. Provide a valid API key.")

    return api_key

import os
from getpass import getpass
from pathlib import Path

# Get the user's home directory
home_dir = Path.home()

# Define a secure location for the file (e.g., ~/.secrets/openai_api_key.txt)
secrets_dir = home_dir / ".secrets"
secrets_dir.mkdir(exist_ok=True)  # Create the directory if it doesn't exist

key_file = secrets_dir / "openai_api_key.txt"

# Prompt for the API key
api_key = getpass("Enter your OpenAI API Key: ")

# Save the key securely to the file
with key_file.open("w") as f:
    f.write(api_key)

print(f"API Key saved to {key_file}.")