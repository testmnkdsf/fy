
from fyers_utils import get_access_token, initialize_fyers

# Fetch the access token
access_token = get_access_token()

# Initialize the Fyers API client
fyers = initialize_fyers(access_token)

# Define the data for fetching historical data
data = {
    "symbol": "NSE:SBIN-EQ",
    "resolution": "5",
    "date_format": "0",
    "range_from": "1690895316",
    "range_to": "1691068173",
    "cont_flag": "1"
}

# Fetch historical data
historical_data = fyers.history(data)
print(historical_data)
