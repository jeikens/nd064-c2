from concurrent import futures
import grpc
import location_pb2
import location_pb2_grpc
from datetime import datetime
import logging

# configure logging
logging.basicConfig(format='[%(levelname)s:%(asctime)s:%(name)s] %(message)s', level=logging.DEBUG)
log = logging.get_logger(__name__)

# gRPC Server
class LocationServicer(location_pb2_grpc.LocationServiceServicer):
    def __init__(self):
        pass # init connection to Kafka

    def PushLocation(self, request: location_pb2.Location, context):
        log.debug(f'{request.user=};{request.latitude=};{request.longitude=};{request.utc=};datetime={datetime.fromtimestamp(request.utc)}')
        return location_pb2.Empty()


def start_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    location_pb2_grpc.add_LocationServiceServicer_to_server(LocationServicer(), server)
    server.add_insecure_port(f'[::]:50051')
    server.start()
    log.debug('starting gRPC server')
    server.wait_for_termination()

if __name__ == '__main__':
    start_server()