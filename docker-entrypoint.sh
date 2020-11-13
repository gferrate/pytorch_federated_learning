#!/bin/bash

if [ "$TYPE" = "CLIENT" ]; then
    echo "Starting client"
    python client/app.py -p $PORT -n $N_CLIENT 
elif [[ "$TYPE" = "MAIN_SERVER" ]]; then
    echo "Starting main server"
    python main_server/app.py -p $PORT 
elif [[ "$TYPE" = "SECURE_AGGREGATOR" ]]; then
    echo "Starting secure aggregator"
    python secure_aggregator/app.py -p $PORT 
else
    echo "Type not recognized"
fi

