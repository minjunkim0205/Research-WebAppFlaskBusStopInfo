from config import setting
import requests

API_KEY = setting.DATABASE_CONFIG["api_decoded_key"]
ars_id = "25139"  # 고덕역 ARS ID 예시

url = "http://ws.bus.go.kr/api/rest/arrive/getLowArrInfoByStId"
params = {
    "ServiceKey": API_KEY,
    "arsId": ars_id,
    "_type": "xml"
}

resp = requests.get(url, params=params)
print(resp.status_code)
print(resp.text)
