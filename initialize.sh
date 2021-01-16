#!/bin/bash

# Python path. Change to match yours.
PYTHON_PATH="/Users/Gabrieljr./.virtualenvs/pytorch_fl/bin/python"

# Close current screens if env variable enabled.
[[ ! -z "$RESTART_SCREEN" && "$RESTART_SCREEN" != 0 ]] && echo "Closing current screens" && killall screen || echo "Not closing current screens"

# Delete all logs if env variable enabled.
[[ ! -z "$DELETE_OLD_LOGS" && "$DELETE_OLD_LOGS" != 0  ]] && echo "Deleting old logs" && rm logs/*.log || echo "Not deleting old logs"

# Restart the frontend
curl http://104.197.103.25:8002/restart

# Start main server in a new screen.
screen -dmS main_server bash -c "$PYTHON_PATH main_server/app.py -p 8000"

# Start secure aggregator in a new screen.
screen -dmS secure_aggregator bash -c "$PYTHON_PATH secure_aggregator/app.py -p 8001"

# Split type
if [[ "$SPLIT_TYPE" == "no_split" ]]
then
    echo "No split type"
    TO_APPEND="-s no_split"
elif [[ "$SPLIT_TYPE" == "iid" ]]
else
    echo "Split type: iid"
    TO_APPEND="-s iid"
elif [[ "$SPLIT_TYPE" == "iid" ]]
else
    echo "Split type: non-iid"
    TO_APPEND="-s non-iid-a"
else
    echo "No split type"
    TO_APPEND="-s no_split"
fi

# Start N clients in new screens. Add or comment lines as wanted.
screen -dmS client_0 bash -c "$PYTHON_PATH client/app.py -p 8003 -n 0 $TO_APPEND"
screen -dmS client_1 bash -c "$PYTHON_PATH client/app.py -p 8004 -n 1 $TO_APPEND"
screen -dmS client_2 bash -c "$PYTHON_PATH client/app.py -p 8005 -n 2 $TO_APPEND"
screen -dmS client_3 bash -c "$PYTHON_PATH client/app.py -p 8006 -n 3 $TO_APPEND"
screen -dmS client_4 bash -c "$PYTHON_PATH client/app.py -p 8007 -n 4 $TO_APPEND"

echo "Waiting 3 minutes so all clients start"
sleep 3m
echo "Starting run"
# Start the orchestrator (will start the training).
screen -dmS orchestrator bash -c "$PYTHON_PATH orchestrator/orchestrator.py"
