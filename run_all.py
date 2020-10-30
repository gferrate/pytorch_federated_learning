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


def print_elapsed_time(start):
    print('\n')
    print('Elapsed time:')
    end = time.time()
    elapsed_time = end - start
    print(time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))


def check_response_ok(res):
    if res.status_code != 200:
        raise Exception('The response was not successful')


def main():
    # TODO: Configure epochs and everything from here
    num_iterations = 50
    all_results = []
    #train_accs = {}
    start = time.time()
    for i in range(num_iterations):
        print('\n\n')
        print('-'*30)
        print('\n\n')
        print('Iteration {}...'.format(i))

        print('Sending /train_model request to clients...')
        client_urls = get_client_urls('train_model')
        rs = (grequests.get(u) for u in client_urls)
        responses = grequests.map(rs)
        print('\nTrain acc:')
        for res in responses:
            check_response_ok(res)
            #res_json = res.json()
            #print(res_json)
            #print('\n')
            #train_accs.setdefault(res_json['client_id'], []).append(
            #    res_json['results'])
        print('Done')
        print_elapsed_time(start)

        print('Sending /send_model command to clients...')
        client_urls = get_client_urls('send_model')
        rs = (grequests.get(u) for u in client_urls)
        responses = grequests.map(rs)
        for res in responses:
            check_response_ok(res)
        print('Done')
        print_elapsed_time(start)

        print('Sending /aggregate_models command to secure aggregator...')
        url = 'http://{}:{}/aggregate_models'.format(
            hosts['secure_aggregator']['host'],
            hosts['secure_aggregator']['port']
        )
        res = requests.get(url)
        check_response_ok(res)
        test_result = res.json()
        all_results.append(test_result)
        print('Done')
        print_elapsed_time(start)

        print('Sending /send_model_to_main_server command to secure aggregator...')
        url = 'http://{}:{}/send_model_to_main_server'.format(
            hosts['secure_aggregator']['host'],
            hosts['secure_aggregator']['port']
        )
        res = requests.get(url)
        check_response_ok(res)
        print('Done')
        print_elapsed_time(start)

        print('Sending /send_model_clients command to main server...')
        url = 'http://{}:{}/send_model_clients'.format(
            hosts['main_server']['host'],
            hosts['main_server']['port']
        )
        res = requests.get(url)
        check_response_ok(res)
        print('Done')

        print('\n')
        print('Test result:')
        print(test_result)

        print_elapsed_time(start)

        print('\n\n')
        print('-'*30)
        print('\n\n')
    print('\n\n')
    print('-'*30)
    print('\n\n')
    print('All train accuracies:')
    #print(train_accs)
    print('\n\n')
    print('-'*30)
    print('\n\n')
    print('All results:')
    print(all_results)


if __name__ == '__main__':
    main()
