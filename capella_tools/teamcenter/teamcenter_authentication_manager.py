import os
from getpass import getpass
from pathlib import Path

class TeamcenterAuthManager:
    """
    A class to securely store and retrieve Teamcenter authentication credentials.
    """

    def __init__(self):
        self.home_dir = Path.home()
        self.secrets_dir = self.home_dir / ".secrets"
        self.secrets_dir.mkdir(exist_ok=True)  # Create the directory if it doesn't exist
        self.credential_file = self.secrets_dir / "teamcenter_credentials.txt"

    def set_credentials(self):
        """Prompt the user to enter Teamcenter credentials and securely store them."""
        username = input("Enter your Teamcenter Username: ")
        password = getpass("Enter your Teamcenter Password: ")

        if not username or not password:
            print("Error: Username and password cannot be empty.")
            return

        with self.credential_file.open("w") as f:
            f.write(f"{username}\n{password}")

        print(f"Teamcenter credentials saved securely to {self.credential_file}.")

    def get_credentials(self):
        """Retrieve stored Teamcenter credentials."""
        if not self.credential_file.exists():
            raise FileNotFoundError(
                f"Teamcenter credentials not found at {self.credential_file}. "
                "Please set them using set_credentials() first."
            )

        with self.credential_file.open("r") as f:
            credentials = f.read().strip().split("\n")

        if len(credentials) != 2:
            raise ValueError("Stored Teamcenter credentials are invalid or corrupted.")

        return {"username": credentials[0], "password": credentials[1]}
