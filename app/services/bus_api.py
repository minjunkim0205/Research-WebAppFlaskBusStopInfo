# Import module
import config
import xml.etree.ElementTree as ET
import requests
import os
from dotenv import load_dotenv

# Load .env API key
load_dotenv()
API_KEY = os.getenv("BUS_API_DECODE_KEY")

# Find station info by station name(type:str)
def get_station_by_name(stSrch: str = None) -> list[dict[str, str]]:
    # Constant value
    API_URL = "http://ws.bus.go.kr/api/rest/stationinfo/getStationByName"
    # Params
    params = {
        "serviceKey": API_KEY,
        "stSrch": stSrch
    }
    # Get raw xml data from API and convert it to list[dict]
    results = []

    try:
        response = requests.get(API_URL, params=params, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"[get_station_by_name()] Http error : {e}", end="\n")
        return []
    
    if (response.status_code == 200):
        root = ET.fromstring(response.content)

        header_cd = root.findtext(".//headerCd")
        header_msg = root.findtext(".//headerMsg")

        if header_cd == "0":
            '''[ Example raw xml data ]
            <itemList>
                <arsId>25139</arsId>
                <posX>213769.09133093522</posX>
                <posY>450666.54838451464</posY>
                <stId>124000039</stId>
                <stNm>고덕역</stNm>
                <tmX>127.15584924</tmX>
                <tmY>37.555373079</tmY>
            </itemList>
            '''
            for item in root.iter("itemList"):
                '''
                정류소 이름
                정류소 고유번호
                경도 좌표(WGS84 기반)
                위도 좌표(WGS84 기반)
                '''
                station_name = item.findtext("stNm")
                ars_id = item.findtext("arsId")
                tm_x = item.findtext("tmX") # WGS84 GPS coordinate system(Longitude)
                tm_y = item.findtext("tmY") # WGS84 GPS coordinate system(Latitude)

                results.append({"stationName": station_name, "arsId": ars_id, "tmX": tm_x, "tmY": tm_y})
        else:
            print(f"[get_station_by_name()] API error : {header_cd}, message: {header_msg}", end="\n")
    else:
        print(f"[get_station_by_name()] API response : {response.status_code}", end="\n")
    # Return(list[dict])
    return (results)

# Find bus info by station number(type:str)
def get_station_by_uid(arsId:str = None):
    # Constant value
    API_URL = "http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid"
    # Params
    params = {
        'serviceKey' : API_KEY,  
        'arsId' : arsId
    }
    # Get raw xml data from API and convert it to list[dict]
    results = []

    try:
        response = requests.get(API_URL, params=params, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"[get_station_by_name()] Http error : {e}", end="\n")
        return []
    
    if (response.status_code == 200):
        root = ET.fromstring(response.content)

        header_cd = root.findtext(".//headerCd")
        header_msg = root.findtext(".//headerMsg")

        if header_cd == "0":
            '''[ Example raw xml data ]
            <itemList>
                <adirection>인천공항</adirection>
                <arrmsg1>출발대기</arrmsg1>
                <arrmsg2>출발대기</arrmsg2>
                <arrmsgSec1>첫 번째 버스 출발대기</arrmsgSec1>
                <arrmsgSec2>두 번째 버스 출발대기</arrmsgSec2>
                <arsId>25139</arsId>
                <busRouteAbrv>6300</busRouteAbrv>
                <busRouteId>100100508</busRouteId>
                <busType1>0</busType1>
                <busType2>0</busType2>
                <congestion1>0</congestion1>
                <congestion2>0</congestion2>
                <deTourAt>00</deTourAt>
                <firstTm>0400 </firstTm>
                <gpsX>127.15584924</gpsX>
                <gpsY>37.555373079</gpsY>
                <isArrive1>0</isArrive1>
                <isArrive2>0</isArrive2>
                <isFullFlag1>0</isFullFlag1>
                <isFullFlag2>0</isFullFlag2>
                <isLast1>0</isLast1>
                <isLast2>0</isLast2>
                <lastTm>1940 </lastTm>
                <nextBus> </nextBus>
                <nxtStn>배재중고등학교</nxtStn>
                <posX>213769.09133093522</posX>
                <posY>450666.54838451464</posY>
                <rerdieDiv1>0</rerdieDiv1>
                <rerdieDiv2>0</rerdieDiv2>
                <rerideNum1>0</rerideNum1>
                <rerideNum2>0</rerideNum2>
                <routeType>1</routeType>
                <rtNm>6300</rtNm>
                <sectNm>상일동역1번출구~고덕역</sectNm>
                <sectOrd1>0</sectOrd1>
                <sectOrd2>0</sectOrd2>
                <stId>124000039</stId>
                <stNm>고덕역</stNm>
                <staOrd>4</staOrd>
                <stationTp>0</stationTp>
                <term>40</term>
                <traSpd1>0</traSpd1>
                <traSpd2>0</traSpd2>
                <traTime1>0</traTime1>
                <traTime2>0</traTime2>
                <vehId1>0</vehId1>
                <vehId2>0</vehId2>
            </itemList>
            '''
            for item in root.iter("itemList"):
                '''
                정류소 이름
                정류소 고유번호
                버스 번호
                첫 번째 도착 정보
                현재 버스가 위치한 정류소 이름
                행선지 방향
                다음 정류소
                구간 이름
                '''
                station_name = item.findtext("stNm")
                ars_id = item.findtext("arsId")
                route_name = item.findtext("rtNm")
                arrival_msg = item.findtext("arrmsg1")
                station_nm1 = item.findtext("stationNm1")
                adirection = item.findtext("adirection")
                next_station = item.findtext("nxtStn")
                section_name = item.findtext("sectNm")

                results.append({
                    "stationName": station_name,
                    "arsId": ars_id,
                    "rtNm": route_name,
                    "arrmsg1": arrival_msg,
                    "stationNm1": station_nm1,
                    "adirection": adirection,
                    "nxtStn": next_station,
                    "sectNm": section_name
                })
        else:
            print(f"[get_station_by_name()] API error : {header_cd}, message: {header_msg}", end="\n")
    else:
        print(f"[get_station_by_name()] API response : {response.status_code}", end="\n")
    # Return(list[dict])
    return (results)
