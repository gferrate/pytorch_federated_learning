import sys; sys.path.insert(0, '.')

import grequests
import requests
import time
import logging
import argparse

from shared import utils
import client_handler

logging.basicConfig(
    format='%(asctime)s %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/orchestrator.log'),
        logging.StreamHandler()
    ]
)


hosts = utils.read_hosts(override_localhost=False)


def log_elapsed_time(start):
    end = time.time()
    elapsed_time = end - start
    elapsed_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
    msg = 'Elapsed time: {}'.format(elapsed_time)
    logging.info(msg)


def check_response_ok(res):
    if res.status_code != 200:
        raise Exception(
            'The response was not successful. Code: {}, Msg: {}'.format(
                res.status_code, res.text))


def send_iteration_to_frontend(i):
    logging.info('Sending iteration number to frontend')
    try:
        requests.post(
            url='http://{}:{}/iteration'.format(
                hosts['frontend']['host'],
                hosts['frontend']['port']
            ),
            json={'iteration': i}
        )
    except:
        logging.warning('Frontend may be down')


def end_frontend():
    logging.info('Sending end signal to frontend')
    try:
        requests.post(
            url='http://{}:{}/finish'.format(hosts['frontend']['host'],
                                             hosts['frontend']['port']))
    except:
        logging.warning('Frontend may be down')


def restart_frontend():
    logging.info('Restarting frontend')
    try:
        requests.post(
            url='http://{}:{}/restart'.format(
                hosts['frontend']['host'],
                hosts['frontend']['port']
            )
        )
    except:
        logging.warning('Frontend may be down')


def main(op_mode, communication_rounds):
    all_results = []
    ch = client_handler.ClientHandler(clients=hosts['clients'],
                                      OPERATION_MODE=op_mode)
    #train_accs = {}
    start = time.time()
    # restart_frontend()
    for i in range(communication_rounds):
        logging.info('Iteration {}...'.format(i))
        send_iteration_to_frontend(i)

        logging.info('Deleting client models...')
        url = 'http://{}:{}/del_client_models'.format(
            hosts['secure_aggregator']['host'],
            hosts['secure_aggregator']['port']
        )
        res = requests.post(url)
        check_response_ok(res)
        logging.info('Done')

        logging.info('Sending /train_model request to clients...')
        ch.perform_requests_and_wait('train_model')
        #logging.info('Performed clients: {}'.format(performed_clients))
        logging.info('Done')
        log_elapsed_time(start)

        logging.info('Sending /send_model command to clients...')
        ch.perform_requests_and_wait('send_model')
        #logging.info('Performed clients: {}'.format(performed_clients))
        logging.info('Done')
        log_elapsed_time(start)

        logging.info('Sending /aggregate_models '
                     'command to secure aggregator...')
        url = 'http://{}:{}/aggregate_models'.format(
            hosts['secure_aggregator']['host'],
            hosts['secure_aggregator']['port']
        )
        res = requests.get(url)
        check_response_ok(res)
        test_result = res.json()
        end = time.time()
        elapsed_time = end - start
        test_result['elapsed_time'] = elapsed_time
        all_results.append(test_result)
        logging.info('Done')
        log_elapsed_time(start)

        logging.info(
            'Sending /send_model_to_main_server '
            'command to secure aggregator...')
        url = 'http://{}:{}/send_model_to_main_server'.format(
            hosts['secure_aggregator']['host'],
            hosts['secure_aggregator']['port']
        )
        res = requests.get(url)
        check_response_ok(res)
        logging.info('Done')
        log_elapsed_time(start)

        logging.info('Sending /send_model_clients command to main server...')
        url = 'http://{}:{}/send_model_clients'.format(
            hosts['main_server']['host'],
            hosts['main_server']['port']
        )
        res = requests.get(url)
        check_response_ok(res)
        logging.info('Done')

        logging.info('Test result: {}'.format(test_result))
        log_elapsed_time(start)

    logging.info('All results:')
    logging.info(all_results)
    end_frontend()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Orchestrator')
    # TODO: Add configuration for Client handlers in other modes (timeout, etc)
    parser.add_argument('-o', '--operation-mode', type=str, required=False,
                        default='wait_all',
                        help=(
                            'Operation mode. '
                            'Options: wait_all (default), n_firsts, timeout'
                        ))
    parser.add_argument('-c',
                        '--communication-rounds',
                        type=int,
                        required=False,
                        default=50,
                        help='Number of communication rounds. Default: 50')
    args = parser.parse_args()
    try:
        main(args.operation_mode, args.communication_rounds)
    except Exception:
        logging.error("Fatal error in main loop", exc_info=True)

