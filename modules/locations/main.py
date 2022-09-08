from fastapi import FastAPI
from pydantic import BaseModel

import grpc
import location_pb2
import location_pb2_grpc


# Simple Health Endpoint for debugging
class Health_Response(BaseModel):
    kafka_connection = 'OK'
    status = 'OK'

app = FastAPI()

@app.get('/health', response_model=Health_Response)
def get_health() -> Health_Response:
    """
    check if service is healthy and the connection to the database is established
    """
    return Health_Response()


# gRPC Server
class LocationServicer(location_pb2_grpc.LocationServiceServicer):
    def __init__(self):
        pass # init connection to Kafka

    def PushLocation(self, request: location_pb2.Location, context):
        print(f'{request.user=} | {request.latitude=} | {request.longitude=} | {request.utc=}')
        return location_pb2.Empty()

