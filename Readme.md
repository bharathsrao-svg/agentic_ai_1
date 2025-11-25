# API Key Generation process
#Step 1 : https://kite.trade/connect/login?api_key=API_KEY&v=3 : Get Request Token from teh response/redirect
# Step 2 python .\generate_access_token.py API_Key KITE_API_SECRET Request Token - Save the output of this (access_token) under Access Request_Token_Temp
# Run   python agent_with_holdings.py  --date 20251124 where Date is previous day
# At end of day run python scripts/save_eod_holdings.py to save EOD Prices
