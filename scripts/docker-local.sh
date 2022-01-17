#!/usr/bin/bash

docker run --name conductor -d --network host -v data:/app/data broadcaststorm/maestro-conductor-service:latest
