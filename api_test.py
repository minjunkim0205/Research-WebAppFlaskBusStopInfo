from config import setting

import requests

API_ENCODED_KEY = setting.DATABASE_CONFIG["api_encoded_key"]
API_DECODED_KEY = setting.DATABASE_CONFIG["api_decoded_key"]
API_URL = "http://ws.bus.go.kr/api/rest/stationinfo/getStationByName"

params ={"serviceKey" : API_DECODED_KEY, "stSrch" : "고덕역" }

response = requests.get(API_URL, params=params)

print(response.content)