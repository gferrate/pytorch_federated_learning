ITERATIONS=49

waitfortest()
{
    ITERATION=-1
    while [ $ITERATION != $ITERATIONS ]
    do
        ITERATION=$(curl -s http://95.179.192.253:8002/ | jq '. | {iteration}.iteration')
        echo "$ITERATION of $ITERATIONS"
        sleep 10
    done
    echo "Reached $ITERATIONS iterations"
    echo "Waiting 3 mins"
    sleep 3m
}

###############################################################################
waitfortest
echo "Compressing results"
tar -czvf 5_clients_non-iid_1_frame.tar.gz logs/*.log
###############################################################################

###############################################################################
echo "Doing iid 1 frame 5 clients"
DELETE_OLD_LOGS=1 RESTART_SCREEN=1 SPLIT_TYPE=iid N_FRAMES=1 ./initialize.sh
waitfortest
echo "Compressing results"
tar -czvf 5_clients_iid_1_frame.tar.gz logs/*.log
###############################################################################

###############################################################################
echo "Doing iid 7 frame 5 clients"
DELETE_OLD_LOGS=1 RESTART_SCREEN=1 SPLIT_TYPE=iid N_FRAMES=7 ./initialize.sh
waitfortest
echo "Compressing results"
tar -czvf 5_clients_iid_7_frames.tar.gz logs/*.log
###############################################################################

###############################################################################
echo "Doing non-iid 7 frame 5 clients"
DELETE_OLD_LOGS=1 RESTART_SCREEN=1 SPLIT_TYPE=non-iid N_FRAMES=7 ./initialize.sh
waitfortest
echo "Compressing results"
tar -czvf 5_clients_non-iid_7_frames.tar.gz logs/*.log
###############################################################################
