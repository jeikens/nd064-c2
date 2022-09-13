import json
import logging
import os
import grpc
from time import sleep
from typing import Union
import requests
import names
import random
import location_pb2
import location_pb2_grpc
from threading import Thread


# configure logging
logging.basicConfig(
    format='[%(levelname)s:%(asctime)s:%(name)s] %(message)s', level=logging.DEBUG)


# randomly create a new person and push it to the API
def register_person() -> Union[int, None]:
    person = {
        'first_name': names.get_first_name(),
        'last_name': names.get_last_name(),
        'company_name': f'{names.get_last_name()} {random.choice(["GmbH", "Inc.", "LLC", "AG"])}'
    }
    result = requests.post(
        f'http://{api_host}:{api_port}/api/persons', json=person)
    if result.status_code == 200:
        return result.json()['id']
    else:
        logging.error(
            f'Server returned {result.status_code}:{result.text}, Unable to add user {person}')


# Frequently pushes new location data.
# The location and time is randomly chosen from a predefined set. To make sure there will a connection at some point.
def run_gps_mockup():
    person_id = register_person()
    if person_id is not None:
        logging.debug(f'Created new user {person_id} - {running}')
        # open new gRPC channel
        with grpc.insecure_channel(f'{grpc_host}:{grpc_port}') as channel:
            stub = location_pb2_grpc.LocationServiceStub(channel)
            while (running):
                # get random location data
                loc = random.choice(locations)
                logging.debug(f'{person_id}: pushing {loc}')
                # push data to gRPC
                stub.PushLocation(location_pb2.Location(
                    user=person_id,
                    latitude=loc[0],
                    longitude=loc[1],
                    utc=loc[2]
                ))
                # random sleep time
                sleep(random.uniform(0, 2))


if __name__ == "__main__":
    # get connection info
    api_host = os.environ.get("API_HOST", "localhost")
    api_port = os.environ.get("API_PORT", "30001")
    grpc_host = os.environ.get("GRPC_HOST", "localhost")
    grpc_port = os.environ.get("GRPC_PORT", "30051")

    # defines how many gps mockups to be created
    numberOfWorkers = int(os.environ.get("MOCKUP_COUNT", "2"))
    running = True  # status variable to shut down the threads
    # load a set of location/timestamps
    locations = json.load(open('locations.json', 'r'))
    # create multiple threads pushing data to the gRPC server
    thrds = []
    for i in range(numberOfWorkers):
        t = Thread(target=run_gps_mockup)
        t.start()
        thrds.append(t)
    # wait for user input to shutdown
    print('press enter to stop')
    try:
        input()
    except KeyboardInterrupt:
        running = False
    running = False
    for t in thrds:
        t.join()
