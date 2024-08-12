
from fyers_utils import get_access_token, initialize_fyers
access_token = get_access_token()
fyers = initialize_fyers(access_token)
data = {
    "symbol": "NSE:SBIN-EQ",
    "resolution": "5",
    "date_format": "0",
    "range_from": "1690895316",
    "range_to": "1691068173",
    "cont_flag": "1"
    
historical_data = fyers.history(data)

# use normally like the original fyers api
