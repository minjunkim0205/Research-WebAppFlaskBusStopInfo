# For test
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import module
import app.services.bus_api as bus_api

# Test run
def test_get_station_by_name():
    result = bus_api.get_station_by_name("고덕역")
    print("정류장 검색 결과:")
    for item in result:
        print(item)

def test_get_station_by_uid():
    result = bus_api.get_station_by_uid(25139)
    print("정류장 버스 검색 결과:")
    for item in result:
        print(item)

# Main
if __name__ == "__main__":
    test_get_station_by_uid()
