import logging
from kafka import KafkaConsumer
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from geoalchemy2.functions import ST_Point
from models import Person, Location, Base
from datetime import datetime

# configure logging
logging.basicConfig(
    format='[%(levelname)s:%(asctime)s:%(name)s] %(message)s', level=logging.DEBUG)


# init kafka consumer with json deserializer
def init_consumer() -> KafkaConsumer:
    kafka_host = os.environ.get('KAFKA_HOST', 'kafka')
    kafka_port = os.environ.get('KAFKA_PORT', '9092')
    return KafkaConsumer(
        os.environ.get('KAFKA_TOPIC', 'udaconnectlocations'),
        bootstrap_servers=f'{kafka_host}:{kafka_port}',
        value_deserializer=lambda v: json.loads(v.decode('utf-8')))

# init database session
def init_database() -> sessionmaker:
    DB_USERNAME = os.environ.get('DB_USERNAME', 'ct_admin')
    DB_PASSWORD = os.environ.get('DB_PASSWORD') # never ever do this in real life...
    DB_HOST = os.environ.get('DB_HOST', 'postgres')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    DB_NAME = os.environ.get('DB_NAME', 'geoconnections')
    engine = create_engine(f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}')
    Base.metadata.bind = engine
    Session = sessionmaker(bind=engine)
    return Session()


# parse received message and push it to the database
def handle_message(message):
    logging.debug(f'Message received: {message.value}')
    # check if person exists - exit if not
    person_id = message.value['person_id']
    if session.query(Person.id).filter(Person.id==person_id).count() == 0:
        logging.warning(f'location data from missing person id {person_id} received')
        return
    # add location to database
    location = Location(
        person_id = person_id,
        coordinate = ST_Point(message.value['latitude'], message.value['longitude']),
        creation_time = datetime.fromtimestamp(message.value['utc'])
    )
    session.add(location)
    session.commit()



if __name__ == '__main__':
    # init kafka consumer
    consumer = init_consumer()
    # init db connection
    session: sessionmaker = init_database()
    # message receiver loop
    for message in consumer:
        handle_message(message)
