# Import module
import requests
import xml.etree.ElementTree as ET
import logging
from config import Config

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load API key
API_KEY = Config.BUS_API_KEY

# Find station info by station name(type:str)
def get_station_by_name(stSrch: str = None) -> list[dict[str, str]]:
    API_URL = "http://ws.bus.go.kr/api/rest/stationinfo/getStationByName"
    params = {
        "serviceKey": API_KEY,
        "stSrch": stSrch
    }
    results = []

    try:
        response = requests.get(API_URL, params=params, timeout=5)
    except requests.exceptions.RequestException as e:
        logger.error(f"[get_station_by_name] HTTP error: {e}")
        return []

    if response.status_code == 200:
        root = ET.fromstring(response.content)
        header_cd = root.findtext(".//headerCd")
        header_msg = root.findtext(".//headerMsg")

        if header_cd == "0":
            for item in root.iter("itemList"):
                station_name = item.findtext("stNm")
                ars_id = item.findtext("arsId")
                tm_x = item.findtext("tmX")
                tm_y = item.findtext("tmY")

                results.append({
                    "stationName": station_name,
                    "arsId": ars_id,
                    "tmX": tm_x,
                    "tmY": tm_y
                })
        else:
            logger.warning(f"[get_station_by_name] API error: {header_cd}, message: {header_msg}")
    else:
        logger.warning(f"[get_station_by_name] HTTP response code: {response.status_code}")

    return results

# Find bus info by station number(type:str)
def get_station_by_uid(arsId: str = None) -> list[dict[str, str]]:
    API_URL = "http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid"
    params = {
        "serviceKey": API_KEY,
        "arsId": arsId
    }
    results = []

    try:
        response = requests.get(API_URL, params=params, timeout=5)
    except requests.exceptions.RequestException as e:
        logger.error(f"[get_station_by_uid] HTTP error: {e}")
        return []

    if response.status_code == 200:
        root = ET.fromstring(response.content)
        header_cd = root.findtext(".//headerCd")
        header_msg = root.findtext(".//headerMsg")

        if header_cd == "0":
            for item in root.iter("itemList"):
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
            logger.warning(f"[get_station_by_uid] API error: {header_cd}, message: {header_msg}")
    else:
        logger.warning(f"[get_station_by_uid] HTTP response code: {response.status_code}")

    return results
