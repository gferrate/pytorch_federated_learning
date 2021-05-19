#!/bin/bash

# Python path. Change to match yours.
PYTHON_PATH="/home/gabriel/pytorch_federated_learning/venv/bin/python"

# Close current screens if env variable enabled.
[[ ! -z "$RESTART_SCREEN" && "$RESTART_SCREEN" != 0 ]] && echo "Closing current screens" && killall screen || echo "Not closing current screens"

# Delete all logs if env variable enabled.
[[ ! -z "$DELETE_OLD_LOGS" && "$DELETE_OLD_LOGS" != 0  ]] && echo "Deleting old logs" && rm logs/*.log || echo "Not deleting old logs"

# Split type
if [[ "$SPLIT_TYPE" == "no_split" ]]
then
    echo "No split type"
    TO_APPEND="-s no_split"
elif [[ "$SPLIT_TYPE" == "iid" ]]
then
    echo "Split type: iid"
    TO_APPEND="-s iid"
elif [[ "$SPLIT_TYPE" == "non-iid" ]]
then
    echo "Split type: non-iid"
    TO_APPEND="-s non-iid-a"
else
    echo "No split type"
    TO_APPEND="-s no_split"
fi

# N frames
if [[ -z "$N_FRAMES" ]]
then
    echo "No N_FRAMES DEFINED. DEFAULT = 1"
    N_FRAMES_APPEND=""
else
    echo "N_FRAMES DEFINED: $N_FRAMES"
    N_FRAMES_APPEND=" -f $N_FRAMES"
fi

# Start N clients in new screens. Add or comment lines as wanted.
screen -dmS client_0 bash -c "$PYTHON_PATH client/app.py -p 8003 -n 5 $TO_APPEND $N_FRAMES_APPEND"
screen -dmS client_1 bash -c "$PYTHON_PATH client/app.py -p 8004 -n 6 $TO_APPEND $N_FRAMES_APPEND"
screen -dmS client_2 bash -c "$PYTHON_PATH client/app.py -p 8005 -n 7 $TO_APPEND $N_FRAMES_APPEND"
#screen -dmS client_3 bash -c "$PYTHON_PATH client/app.py -p 8006 -n 8 $TO_APPEND $N_FRAMES_APPEND"
#screen -dmS client_3 bash -c "$PYTHON_PATH client/app.py -p 8006 -n 3 $TO_APPEND"
#screen -dmS client_4 bash -c "$PYTHON_PATH client/app.py -p 8007 -n 4 $TO_APPEND"

