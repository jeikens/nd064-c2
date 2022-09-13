from datetime import datetime

from app.udaconnect.models import Connection, Location, Person
from app.udaconnect.schemas import (
    ConnectionSchema,
    LocationSchema,
    PersonSchema,
)
from app.udaconnect.services import ConnectionService, LocationService, PersonService
from flask import request, abort
from flask_accepts import accepts, responds
from flask_restx import Namespace, Resource, fields
from typing import Optional, List
import logging

DATE_FORMAT = "%Y-%m-%d"

api = Namespace("UdaConnect", description="Connections via geolocation.")  # noqa


person_model = api.schema_model('Person', {
    'required': ['first_name', 'last_name', 'company_name'],
    'type': 'object',
    'properties': {
        'first_name': {'type': 'string'},
        'last_name': {'type': 'string'},
        'company_name': {'type': 'string'}
    }
})


@api.route("/locations", doc={"description": "Get all stored locations"})
class LocationsResource(Resource):
    @responds(schema=LocationSchema, many=True)
    @api.response(200, 'Success')
    def get(self) -> List[Location]:
        location: List[Location] = LocationService.retrieve_all()
        return location


@api.route("/locations/<location_id>", doc={"description": "Get a specific location by id"})
@api.param("location_id", "Unique ID for a given Location", _in="query")
class LocationResource(Resource):
    @responds(schema=LocationSchema)
    @api.response(200, 'Success')
    @api.response(404, 'Unknown ID')
    def get(self, location_id) -> Location:
        location: Location = LocationService.retrieve(location_id)
        if location is None:
            abort(404, f'Location {location_id} does not exist')
        return location


@api.route("/persons", doc={"description": "Get all registered persons or post a new one"})
class PersonsResource(Resource):
    @accepts(schema=PersonSchema)
    @responds(schema=PersonSchema)
    @api.expect(person_model)
    def post(self) -> Person:
        payload = request.get_json()
        new_person: Person = PersonService.create(payload)
        return new_person

    @responds(schema=PersonSchema, many=True)
    def get(self) -> List[Person]:
        persons: List[Person] = PersonService.retrieve_all()
        return persons


@api.route("/persons/<person_id>", doc={"description": "Get information about one specific person"})
@api.param("person_id", "Unique ID for a given Person", _in="query")
class PersonResource(Resource):
    @responds(schema=PersonSchema)
    def get(self, person_id) -> Person:
        person: Person = PersonService.retrieve(person_id)
        return person

    def delete(self, person_id) -> dict:
        if not PersonService.exists(person_id):
            abort(404, f'User {person_id} does not exist')
        deleted = PersonService.delete(person_id)
        if not deleted:
            logging.error(f'Unable to delete User {person_id}')
            abort(500, f'Unable to delete User {person_id}')
        return {'status': "OK"}


@api.route("/persons/<person_id>/locations", doc={"description": "Get the location history of a person"})
@api.param("person_id", "Unique ID for a given Person", _in="query")
class PersonLocationResource(Resource):
    @responds(schema=LocationSchema, many=True)
    def get(self, person_id) -> List[Location]:
        location: List[Location] = LocationService.retrieve_by_person(
            person_id)
        return location


@api.route("/persons/<person_id>/connection", doc={"description": "Get the detected connections of a person within a given timeframe"})
@api.param("person_id", "Unique ID for a given Person", _in="query")
@api.param("start_date", "Lower bound of date range", _in="query")
@api.param("end_date", "Upper bound of date range", _in="query")
@api.param("distance", "Proximity to a given user in meters", _in="query")
class ConnectionDataResource(Resource):
    @responds(schema=ConnectionSchema, many=True)
    def get(self, person_id) -> ConnectionSchema:
        start_date: datetime = datetime.strptime(
            request.args["start_date"], DATE_FORMAT
        )
        end_date: datetime = datetime.strptime(
            request.args["end_date"], DATE_FORMAT)
        distance: Optional[int] = request.args.get("distance", 5)

        results = ConnectionService.find_contacts(
            person_id=person_id,
            start_date=start_date,
            end_date=end_date,
            meters=distance,
        )
        return results
