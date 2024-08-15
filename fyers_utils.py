from fyers_apiv3 import fyersModel
from cred import client_id
import os
from datetime import datetime
import time as tm , requests, pyotp, json
import datetime as dt
from urllib import parse
from urllib.parse import parse_qs, urlparse
from cred import *

class FyersAuth:
    SECRET_KEY = SECRET_KEY
    FY_ID = FY_ID
    APP_ID_TYPE = APP_ID_TYPE
    TOTP_KEY = TOTP_KEY
    PIN = PIN
    REDIRECT_URI = REDIRECT_URI
    client_id = client_id
    APP_ID = APP_ID
    APP_TYPE = APP_TYPE

    BASE_URL = "https://api-t2.fyers.in/vagator/v2"
    BASE_URL_2 = "https://api-t1.fyers.in/api/v3"
    URL_SEND_LOGIN_OTP = BASE_URL + "/send_login_otp"
    URL_VERIFY_TOTP = BASE_URL + "/verify_otp"
    URL_VERIFY_PIN = BASE_URL + "/verify_pin"
    URL_TOKEN = BASE_URL_2 + "/token"
    URL_VALIDATE_AUTH_CODE = BASE_URL_2 + "/validate-authcode"

    SUCCESS = 1
    ERROR = -1

    @staticmethod
    def send_login_otp(fy_id, app_id):
        try:
            result_string = requests.post(url=FyersAuth.URL_SEND_LOGIN_OTP, json={
                "fy_id": fy_id, "app_id": app_id})
            if result_string.status_code != 200:
                return [FyersAuth.ERROR, result_string.text]
            result = json.loads(result_string.text)
            request_key = result["request_key"]
            return [FyersAuth.SUCCESS, request_key]
        except Exception as e:
            return [FyersAuth.ERROR, e]

    @staticmethod
    def verify_totp(request_key, totp):
        print("6 digits>>>", totp)
        print("request key>>>", request_key)
        try:
            result_string = requests.post(url=FyersAuth.URL_VERIFY_TOTP, json={
                "request_key": request_key, "otp": totp})
            if result_string.status_code != 200:
                return [FyersAuth.ERROR, result_string.text]
            result = json.loads(result_string.text)
            request_key = result["request_key"]
            return [FyersAuth.SUCCESS, request_key]
        except Exception as e:
            return [FyersAuth.ERROR, e]

    @staticmethod
    def generate_totp(secret):
        try:
            generated_totp = pyotp.TOTP(secret).now()
            return [FyersAuth.SUCCESS, generated_totp]

        except Exception as e:
            return [FyersAuth.ERROR, e]

    @staticmethod
    def verify_PIN(request_key, pin):
        try:
            payload = {
                "request_key": request_key,
                "identity_type": "pin",
                "identifier": pin
            }

            result_string = requests.post(url=FyersAuth.URL_VERIFY_PIN, json=payload)
            if result_string.status_code != 200:
                return [FyersAuth.ERROR, result_string.text]

            result = json.loads(result_string.text)
            access_token = result["data"]["access_token"]

            return [FyersAuth.SUCCESS, access_token]

        except Exception as e:
            return [FyersAuth.ERROR, e]

    @staticmethod
    def token(fy_id, app_id, redirect_uri, app_type, access_token):
        try:
            payload = {
                "fyers_id": fy_id,
                "app_id": app_id,
                "redirect_uri": redirect_uri,
                "appType": app_type,
                "code_challenge": "",
                "state": "sample_state",
                "scope": "",
                "nonce": "",
                "response_type": "code",
                "create_cookie": True
            }
            headers = {'Authorization': f'Bearer {access_token}'}

            result_string = requests.post(
                url=FyersAuth.URL_TOKEN, json=payload, headers=headers
            )

            if result_string.status_code != 308:
                return [FyersAuth.ERROR, result_string.text]

            result = json.loads(result_string.text)
            url = result["Url"]
            auth_code = parse.parse_qs(parse.urlparse(url).query)['auth_code'][0]

            return [FyersAuth.SUCCESS, auth_code]

        except Exception as e:
            return [FyersAuth.ERROR, e]

    @staticmethod
    def main():

        # Step 1 - Retrieve request_key from send_login_otp API

        session = fyersModel.SessionModel(client_id=FyersAuth.client_id, secret_key=FyersAuth.SECRET_KEY, redirect_uri=FyersAuth.REDIRECT_URI,response_type='code', grant_type='authorization_code')

        urlToActivate = session.generate_authcode()
        print(f'URL to activate APP:  {urlToActivate}')

        send_otp_result = FyersAuth.send_login_otp(fy_id=FyersAuth.FY_ID, app_id=FyersAuth.APP_ID_TYPE)

        if send_otp_result[0] != FyersAuth.SUCCESS:
            print(f"send_login_otp msg failure - {send_otp_result[1]}")
            status=False
            sys.exit()
        else:
            print("send_login_otp msg SUCCESS")
            status=False


        # Step 2 - Generate totp
        generate_totp_result = FyersAuth.generate_totp(secret=FyersAuth.TOTP_KEY)

        if generate_totp_result[0] != FyersAuth.SUCCESS:
            print(f"generate_totp msg failure - {generate_totp_result[1]}")
            sys.exit()
        else:
            print("generate_totp msg success")


        # Step 3 - Verify totp and get request key from verify_otp API
        for i in range(1, 3):

            request_key = send_otp_result[1]
            totp = generate_totp_result[1]
            print("otp>>>", totp)
            verify_totp_result = FyersAuth.verify_totp(request_key=request_key, totp=totp)
            print("r==", verify_totp_result)

            if verify_totp_result[0] != FyersAuth.SUCCESS:
                print(f"verify_totp_result msg failure - {verify_totp_result[1]}")
                status=False

                tm.sleep(1)
            else:
                print(f"verify_totp_result msg SUCCESS {verify_totp_result}")
                status=False
                break

        if verify_totp_result[0] == FyersAuth.SUCCESS:

            request_key_2 = verify_totp_result[1]

            # Step 4 - Verify pin and send back access token
            ses = requests.Session()
            verify_pin_result = FyersAuth.verify_PIN(request_key=request_key_2, pin=FyersAuth.PIN)
            if verify_pin_result[0] != FyersAuth.SUCCESS:
                print(f"verify_pin_result got failure - {verify_pin_result[1]}")
                sys.exit()
            else:
                print("verify_pin_result got success")


            ses.headers.update({
                'authorization': f"Bearer {verify_pin_result[1]}"
            })

            # Step 5 - Get auth code for API V2 App from trade access token
            token_result = FyersAuth.token(
                fy_id=FyersAuth.FY_ID, app_id=FyersAuth.APP_ID, redirect_uri=FyersAuth.REDIRECT_URI, app_type=FyersAuth.APP_TYPE,
                access_token=verify_pin_result[1]
            )
            if token_result[0] != FyersAuth.SUCCESS:
                print(f"token_result msg failure - {token_result[1]}")
                sys.exit()
            else:
                print("Login Success")

            # Step 6 - Get API V2 access token from validating auth code
            auth_code = token_result[1]
            session.set_token(auth_code)
            response = session.generate_token()
            if response['s'] =='ERROR':
                print("\n Cannot Login. Check your credentials thoroughly!")
                status=False
                tm.sleep(10)
                sys.exit()

            access_token = response["access_token"]
        return access_token


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

    
