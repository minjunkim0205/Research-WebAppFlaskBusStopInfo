import requests
import json

key = "44KvNd6mVM05o9F/+imFyMLx3XV/BzVdbnH2ht7qSWnZkvLIsJu5LpumzAtsA3msMojs6iS+Vjlw+vTpvCcimA=="
bus_stop_id = "100000001"	# 종로2가사거리 정류장
bus_id = "123000010"		# 741번 버스
ord_number = '77'		# 741번 버스 순번

url = f'http://ws.bus.go.kr/api/rest/arrive/getArrInfoByRoute?ServiceKey={key}&stId={bus_stop_id}&busRouteId={bus_id}&ord={ord_number}&resultType=json'

response = requests.get(url)

if response.status_code == 200:
	json_ob = json.loads(response.text)
	data = json_ob['msgBody']['itemList']
	print(data)
'''
	df = json_normalize(data)
	print(f"1번째 버스 현재 위치: {df['stationNm1'].iloc[0]}, 남은 시간: {df['arrmsg1'].iloc[0]}")
	print(f"2번째 버스 현재 위치: {df['stationNm2'].iloc[0]}, 남은 시간: {df['arrmsg2'].iloc[0]}")
'''
