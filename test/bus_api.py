# Import module
from modules import seoulBusStopInformationApi as bus

# Main
if __name__ == "__main__":
    data_a = bus.get_station_by_name("고덕역")
    print(data_a[0]["arsId"], end="\n")

    data_b = bus.get_station_by_uid(data_a[0]["arsId"])
    print(data_b[0], end="\n")
