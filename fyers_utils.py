import pandas as pd
from fyers_apiv3 import fyersModel
from cred import client_id
from Auth import FyersAuth
import os



def create_log_directory(log_path: str = "logs/") -> None:
    """
    Creates the log directory if it doesn't exist.

    Args:
    log_path (str): The path to the log directory.
    """
    try:
        if not os.path.exists(log_path):
            os.makedirs(log_path)
    except OSError as e:
        print(f"Error creating log directory: {e}")

def get_access_token(file_path: str = 'AccessToken.txt') -> str:
    """
    Reads access token from a file.

    Args:
    file_path (str): Path to the file containing the access token.

    Returns:
    str: The access token, or None if the file does not exist.
    """
    try:
        with open(file_path) as file:
            return file.read().strip()
    except FileNotFoundError:
        return None


def refresh_access_token() -> str:
    """
    Refreshes access token using FyersAuth.

    Returns:
    str: The new access token.

    Raises:
    Exception: If an error occurs during authentication.
    """
    try:
        fy = FyersAuth.main()
        with open('AccessToken.txt', 'w') as file:
            file.write(fy)
        return fy
    except Exception as e:
        print(f"Error refreshing access token: {e}")
        # Consider handling specific exceptions here
        raise


def initialize_fyers(access_token: str) -> fyersModel.FyersModel:
    """
    Initializes the FyersModel with given access token.

    Args:
    access_token (str): The access token.

    Returns:
    fyersModel.FyersModel: The initialized Fyers API client.
    """
    create_log_directory()
    fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="logs/")
    try:
        profile = fyers.get_profile()['data']
        print(profile.get('name', 'Name not found'))
    except KeyError:
        print("Initial access token failed. Fetching new access token...")
        new_access_token = refresh_access_token()
        print("New access token obtained. Re-initializing Fyers API client...")
        return initialize_fyers(new_access_token)
    return fyers

    