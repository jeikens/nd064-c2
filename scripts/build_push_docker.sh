#!/bin/sh
docker login

# API
# docker build -t udaconnect-api ./modules/api
# docker tag udaconnect-api:latest jeikens/udaconnect-api:latest
# docker push jeikens/udaconnect-api:latest 

# # Locations
# docker build -t udaconnect-locations ./modules/locations
# docker tag udaconnect-locations:latest jeikens/udaconnect-locations:latest
# docker push jeikens/udaconnect-locations:latest 

# Location Worker
docker build -t udaconnect-locationworker ./modules/locationWorker
docker tag udaconnect-locationworker:latest jeikens/udaconnect-locationworker:latest
docker push jeikens/udaconnect-locationworker:latest 

# frontend
# docker build -t udaconnect-frontend ./modules/frontend
# docker tag udaconnect-frontend:latest jeikens/udaconnect-frontend:latest
# docker push jeikens/udaconnect-frontend:latest 
