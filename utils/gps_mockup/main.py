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

"""
create a new person
"""
def register_person() -> Union[int, None]:
    host = os.environ.get("API_HOST", "localhost")
    person = {
        'first_name':names.get_first_name(),
        'last_name':names.get_last_name(),
        'company_name':f'{names.get_last_name()} {random.choice(["GmbH", "Inc.", "LLC", "AG"])}'
    }
    result = requests.post(f'http://{host}:30001/api/persons', json=person)
    if result.status_code == 200:
        return result.json()['id']
    else:
        logging.error(f'Server returned {result.status_code}:{result.text}, Unable to add user {person}')


def run_gps_mockup():
    person_id = register_person()
    if person_id is not None:
        print(f'Created new user {person_id} - {running}')
        with grpc.insecure_channel('localhost:30051') as channel:
            stub = location_pb2_grpc.LocationServiceStub(channel)
            while (running):
                loc = random.choice(locations[:10])
                print(f'{person_id}: pushing {loc}')
                stub.PushLocation(location_pb2.Location(
                    user=person_id,
                    latitude=loc[0],
                    longitude=loc[1],
                    utc=loc[2]
                ))
                sleep(random.uniform(0,2))


if __name__ == "__main__":
    numberOfWorkers = 2 # defines how many gps mockups to be created
    running = True # status variable to shut down the threads
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
    running=False
    for t in thrds:
        t.join()