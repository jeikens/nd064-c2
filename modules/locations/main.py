from concurrent import futures
import grpc
import location_pb2
import location_pb2_grpc
from datetime import datetime
import logging
from kafka import KafkaProducer
import json
import os

# configure logging
logging.basicConfig(
    format='[%(levelname)s:%(asctime)s:%(name)s] %(message)s', level=logging.DEBUG)


# gRPC Server

class LocationServicer(location_pb2_grpc.LocationServiceServicer):
    def __init__(self):
        # get kafka connection details
        kafka_host = os.environ.get('KAFKA_HOST','kafka')
        kafka_port = os.environ.get('KAFKA_PORT', '9092')
        # setup kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=f'{kafka_host}:{kafka_port}',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def PushLocation(self, request: location_pb2.Location, context):
        logging.debug(f'{request.user=};{request.latitude=};{request.longitude=};' +
                  f'datetime={datetime.fromtimestamp(request.utc)}')
        future = self.producer.send(
            os.environ.get('KAFKA_TOPIC', 'udaconnectlocations'),
            {
                'person_id': request.user,
                'latitude': request.latitude,
                'longitude': request.longitude,
                'utc': request.utc,
            }
        )
        self.producer.flush()
        result = future.get(timeout=30)
        logging.debug(f'Producer Result: {result}')
        return location_pb2.Empty()


def start_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    location_pb2_grpc.add_LocationServiceServicer_to_server(
        LocationServicer(), server)
    server.add_insecure_port(f'[::]:50051')
    server.start()
    logging.debug('starting gRPC server')
    server.wait_for_termination()


if __name__ == '__main__':
    # setup gRPC server
    start_server()
