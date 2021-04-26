FINISHED=false

waitfortest()
{
    while [ $FINISHED != "true" ]
    do
        FINISHED=$(curl -s http://209.250.231.139:8002/ | jq '. | {finished_training}.finished_training')
        echo "Still not finished..."
        sleep 30
    done
    echo "Finished training"
    echo "Waiting 3 mins"
    sleep 3m
}

#################################################################################
#echo "Doing non-iid 1 frame 5 clients 200 CR"
#DELETE_OLD_LOGS=1 RESTART_SCREEN=1 SPLIT_TYPE=non-iid N_FRAMES=1 COMM_ROUNDS=200 ./initialize.sh
#waitfortest
#echo "Compressing results"
#tar -czvf 5_clients_non-iid_1_frame_200_cr.tar.gz logs/*.log
#################################################################################

################################################################################
echo "Doing iid 7 frame 5 clients 200 CR"
DELETE_OLD_LOGS=1 RESTART_SCREEN=1 SPLIT_TYPE=iid N_FRAMES=7 COMM_ROUNDS=200 ./initialize.sh
waitfortest
echo "Compressing results"
tar -czvf 5_clients_iid_7_frames_200_cr.tar.gz logs/*.log
################################################################################

###############################################################################
echo "Doing iid 1 frame 5 clients 200 CR"
DELETE_OLD_LOGS=1 RESTART_SCREEN=1 SPLIT_TYPE=iid N_FRAMES=1 COMM_ROUNDS=200 ./initialize.sh
waitfortest
echo "Compressing results"
tar -czvf 5_clients_iid_1_frame_200_cr.tar.gz logs/*.log
###############################################################################

###############################################################################
#echo "Doing iid 7 frame 1 clients"
##DELETE_OLD_LOGS=1 RESTART_SCREEN=1 SPLIT_TYPE=iid N_FRAMES=7 ./initialize.sh
#waitfortest
#echo "Compressing results"
#tar -czvf 1_clients_iid_7_frames.tar.gz logs/*.log
################################################################################

################################################################################
#echo "Doing non-iid 7 frame 1 clients"
#DELETE_OLD_LOGS=1 RESTART_SCREEN=1 SPLIT_TYPE=non-iid N_FRAMES=7 ./initialize.sh
#waitfortest
#echo "Compressing results"
#tar -czvf 1_clients_non-iid_7_frames.tar.gz logs/*.log
################################################################################
#
################################################################################
#echo "Doing no split 7 frame 1 clients"
#DELETE_OLD_LOGS=1 RESTART_SCREEN=1 SPLIT_TYPE=no_split N_FRAMES=7 ./initialize.sh
#waitfortest
#echo "Compressing results"
#tar -czvf 1_clients_no_split_7_frames.tar.gz logs/*.log
################################################################################
#
################################################################################
#echo "Doing no split 1 frame 1 clients"
#DELETE_OLD_LOGS=1 RESTART_SCREEN=1 SPLIT_TYPE=no_split N_FRAMES=1 ./initialize.sh
#waitfortest
#echo "Compressing results"
#tar -czvf 1_clients_no_split_1_frames.tar.gz logs/*.log
################################################################################

echo "DONE"
