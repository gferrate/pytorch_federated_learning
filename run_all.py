import sys; sys.path.insert(0, '.')

import grequests
import requests
import time

from shared import utils

hosts = utils.read_hosts()


def get_client_urls(endpoint):
    hp = []
    for cl in hosts['clients']:
        host = cl[list(cl.keys())[0]]['host']
        port = cl[list(cl.keys())[0]]['port']
        url = 'http://{}:{}/{}'.format(host, port, endpoint)
        hp.append(url)
    return hp


def main():
    # TODO: Configure epochs and everything from here
    num_iterations = 50
    start = time.now()
    for i in range(num_iterations):
        print('\n\n')
        print('-'*30)
        print('\n\n')
        print('Iteration {}...'.format(i))

        print('Sending /modeltrain request to clients...')
        client_urls = get_client_urls('modeltrain')
        rs = (grequests.get(u) for u in client_urls)
        grequests.map(rs)
        print('Done')

        print('Sending /sendmodel command to clients...')
        client_urls = get_client_urls('sendmodel')
        rs = (grequests.get(u) for u in client_urls)
        grequests.map(rs)
        print('Done')

        print('Sending /aggregate_models command to secure aggregator...')
        url = 'http://{}:{}/aggregate_models'.format(
            hosts['secure_aggregator']['host'],
            hosts['secure_aggregator']['port']
        )
        res = requests.get(url)
        test_result = res.json()
        print('Done')

        print('Sending /send_model_to_main_server command to secure aggregator...')
        url = 'http://{}:{}/send_model_to_main_server'.format(
            hosts['secure_aggregator']['host'],
            hosts['secure_aggregator']['port']
        )
        requests.get(url)
        print('Done')

        print('Sending /send_model_clients command to main server...')
        url = 'http://{}:{}/aggregate_models'.format(
            hosts['main_server']['host'],
            hosts['main_server']['port']
        )
        requests.get(url)
        print('Done')

        print('\n')
        print('Test result:')
        print(test_result)

        print('\n')
        print('Time elapsed:')
        print(time.now() - start)

        print('\n\n')
        print('-'*30)
        print('\n\n')


if __name__ == '__main__':
    main()
