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
    start = time.time()
    for i in range(num_iterations):
        logging.info('Iteration {}...'.format(i))

        logging.info('Sending /train_model request to client...')
        url = 'http://{}:{}/train_model'.format('localhost', 8003)
        res = requests.get(url)
        check_response_ok(res)
        logging.info('Done')
        log_elapsed_time(start)

        logging.info('Sending /model_test command to client...')
        url = 'http://{}:{}/model_test'.format('localhost', 8003)
        res = requests.get(url)
        check_response_ok(res)
        test_result = res.json()
        end = time.time()
        elapsed_time = end - start
        test_result['elapsed_time'] = elapsed_time
        all_results.append(test_result)
        logging.info('Done')

        logging.info('Test result: {}'.format(test_result))
        log_elapsed_time(start)

    logging.info('All results:')
    logging.info(all_results)


if __name__ == '__main__':
    main()
