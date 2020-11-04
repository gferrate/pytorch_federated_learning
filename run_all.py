import sys; sys.path.insert(0, '.')

import grequests
import requests
import time
import logging

from shared import utils

logging.basicConfig(
    format='%(asctime)s %(message)s',
    # filename='logs/run.log',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/run.log'),
        logging.StreamHandler()
    ]
)


hosts = utils.read_hosts()


def get_client_urls(endpoint):
    hp = []
    for cl in hosts['clients']:
        host = cl[list(cl.keys())[0]]['host']
        port = cl[list(cl.keys())[0]]['port']
        url = 'http://{}:{}/{}'.format(host, port, endpoint)
        hp.append(url)
    return hp


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


def main():
    # TODO: Configure epochs and everything from here
    num_iterations = 50
    all_results = []
    #train_accs = {}
    start = time.time()
    for i in range(num_iterations):
        logging.info('Iteration {}...'.format(i))

        logging.info('Sending /train_model request to clients...')
        client_urls = get_client_urls('train_model')
        rs = (grequests.get(u) for u in client_urls)
        responses = grequests.map(rs)
        # print('\nTrain acc:')
        for res in responses:
            check_response_ok(res)
            #res_json = res.json()
            #print(res_json)
            #print('\n')
            #train_accs.setdefault(res_json['client_id'], []).append(
            #    res_json['results'])
        logging.info('Done')
        log_elapsed_time(start)

        logging.info('Sending /send_model command to clients...')
        client_urls = get_client_urls('send_model')
        rs = (grequests.get(u) for u in client_urls)
        responses = grequests.map(rs)
        for res in responses:
            check_response_ok(res)
        logging.info('Done')
        log_elapsed_time(start)

        logging.info('Sending /aggregate_models command to secure aggregator...')
        url = 'http://{}:{}/aggregate_models'.format(
            hosts['secure_aggregator']['host'],
            hosts['secure_aggregator']['port']
        )
        res = requests.get(url)
        check_response_ok(res)
        test_result = res.json()
        all_results.append(test_result)
        logging.info('Done')
        log_elapsed_time(start)

        logging.info('Sending /send_model_to_main_server command to secure aggregator...')
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

    # logging.info('All train accuracies:')
    # print(train_accs)
    logging.info('All results:')
    logging.info(all_results)


if __name__ == '__main__':
    main()
