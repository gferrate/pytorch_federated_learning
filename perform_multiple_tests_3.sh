FINISHED=false

waitfortest()
{
    while [ $FINISHED != "true" ]
    do
        FINISHED=$(curl -s http://95.179.192.253:8002/ | jq '. | {finished_training}.finished_training')
        echo "Still not finished..."
        sleep 15
    done
    echo "Finished training"
    echo "Waiting 3 mins"
    sleep 1m
}

#################################################################################
#echo "Doing iid 1 frame 9 clients 200 CR"
#DELETE_OLD_LOGS=1 RESTART_SCREEN=1 SPLIT_TYPE=iid N_FRAMES=1 COMM_ROUNDS=200 ./initialize_3.sh
#waitfortest
#echo "Compressing results"
#tar -czvf 9_clients_iid_1_frames_200_cr_kcl3.tar.gz logs/*.log
#################################################################################

################################################################################
echo "Doing non-iid 1 frame 9 clients 200 CR"
DELETE_OLD_LOGS=1 RESTART_SCREEN=1 SPLIT_TYPE=non-iid N_FRAMES=1 COMM_ROUNDS=200 ./initialize_3.sh
waitfortest
echo "Compressing results"
tar -czvf 9_clients_non_iid_1_frames_200_cr_kcl3.tar.gz logs/*.log
################################################################################

################################################################################
echo "Doing iid 7 frame 9 clients 200 CR"
DELETE_OLD_LOGS=1 RESTART_SCREEN=1 SPLIT_TYPE=iid N_FRAMES=7 COMM_ROUNDS=200 ./initialize_3.sh
waitfortest
echo "Compressing results"
tar -czvf 9_clients_iid_7_frames_200_cr_kcl3.tar.gz logs/*.log
################################################################################

################################################################################
echo "Doing non-iid 7 frame 9 clients 200 CR"
DELETE_OLD_LOGS=1 RESTART_SCREEN=1 SPLIT_TYPE=non-iid N_FRAMES=7 COMM_ROUNDS=200 ./initialize_3.sh
waitfortest
echo "Compressing results"
tar -czvf 9_clients_non_iid_7_frames_200_cr_kcl3.tar.gz logs/*.log
################################################################################
