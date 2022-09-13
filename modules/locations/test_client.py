"""
Used to simulate location entries sent by user mobile phones
"""
import grpc
import location_pb2
import location_pb2_grpc
from datetime import datetime

def send_location(stub: location_pb2_grpc.LocationServiceStub, usr: float, lat: float, long: float, timestamp: datetime):
    print(f'{usr=} | {lat=} | {long=} | utc={timestamp.timestamp()} | datetime={timestamp}')
    # create message
    loc = location_pb2.Location(
        user = usr,
        latitude = lat,
        longitude = long,
        utc = timestamp.timestamp()
    )
    # send message
    stub.PushLocation(loc)


if __name__ == '__main__':
    with grpc.insecure_channel('localhost:30051') as channel:
        stub = location_pb2_grpc.LocationServiceStub(channel)
        send_location(stub, 1, 47, 11, datetime.now())
