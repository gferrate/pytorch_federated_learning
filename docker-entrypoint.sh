#!/bin/bash

if [ "$TYPE" = "CLIENT" ]; then
    echo "Starting client"
    echo /code/logs/client_$PORT.log
    python client/app.py -p $PORT -n $N_CLIENT &> /code/logs/client_$PORT.log
elif [[ "$TYPE" = "MAIN_SERVER" ]]; then
    echo "Starting main server"
    python main_server/app.py -p $PORT &> /code/logs/main_server.log
elif [[ "$TYPE" = "SECURE_AGGREGATOR" ]]; then
    echo "Starting secure aggregator"
    python secure_aggregator/app.py -p $PORT &> /code/logs/secure_aggregator.log
else
    echo "Type not recognized"
fi

