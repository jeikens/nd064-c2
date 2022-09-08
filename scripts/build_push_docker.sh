#!/bin/sh
docker login

# API
docker build -t udaconnect-api ./modules/api
docker tag udaconnect-api:latest jeikens/udaconnect-api:latest
docker push jeikens/udaconnect-api:latest 

# frontend
# docker build -t udaconnect-frontend ./modules/frontend
# docker tag udaconnect-frontend:latest jeikens/udaconnect-frontend:latest
# docker push jeikens/udaconnect-frontend:latest 
