import os
from fastapi import FastAPI
import requests
import names
import random

def get_random_company():
    return f'{names.get_last_name()} {random.choice(["GmbH", "Inc.", "LLC", "AG"])}'

# check if connection environment 
grpc_host = f'{os.environ.get("GRPC_HOST", "localhost")}:{os.environ.get("GRPC_PORT", "50051")}'


app = FastAPI()

active_persons = []


@app.get("/")
def read_root():
    return {'Active Count': len(active_persons)}

@app.post("/add_new")
def add_new():
    host = os.environ.get("API_HOST", "localhost")
    person = {
        'first_name':names.get_first_name(),
        'last_name':names.get_last_name(),
        'company_name':get_random_company()
    }
    requests.post(f'http://{host}:30001/api/persons', json=person)
