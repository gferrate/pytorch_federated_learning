from multiprocessing.dummy import Pool
import requests
from time import time, sleep
import logging

CLIENT_OPERATIONS = ('client_train', 'send_model')


class ClientHandler:
    """Performs concurrent requests with timeout"""

    def __init__(self, clients, operation_mode='n_firsts', **kwargs):
        self.clients = self.parse_clients(clients)
        self.n_clients = len(clients)
        self.operation_mode = operation_mode
        # Creates a pool with N_CLIENTS threads
        self.pool = None
        logging.info(
            '[Client Handler] Operation mode: {}'.format(self.operation_mode))
        if self.operation_mode == 'n_firsts':
            self.N_FIRSTS = kwargs.get('n_firsts', max(1, self.n_clients - 2))
            assert self.N_FIRSTS <= self.n_clients, \
                'n_firsts must be <= than num clients'
            logging.info(
                '[Client Handler] n_firsts: {}'.format(self.N_FIRSTS))
        elif self.operation_mode == 'timeout':
            pass
        else:
            raise Exception('Operation mode not accepted')
        self.operations_history = {}
        self.init_operations_history()

    def perform_requests_and_wait(self, endpoint):
        self.perform_parallel_requests(endpoint)
        if self.operation_mode == 'n_firsts':
            if endpoint == 'send_model':
                return self.wait_until_n_responses(wait_all=True)
            return self.wait_until_n_responses()
        elif self.operation_mode == 'timeout':
            # TODO
            return

    def init_operations_history(self):
        for host, port in self.clients:
            key = self.get_client_key(host, port)
            self.operations_history[key] = []

    @staticmethod
    def parse_clients(clients):
        p_clients = []
        for cl in clients:
            host = cl[list(cl.keys())[0]]['host']
            port = cl[list(cl.keys())[0]]['port']
            p_clients.append((host, port))
        return p_clients

    def perform_parallel_requests(self, endpoint):
        futures = []
        self.pool = Pool(self.n_clients)
        for host, port in self.clients:
            futures.append(
                self.pool.apply_async(self.perform_request,
                                      [host, port, endpoint]))
        self.pool.close()

    def wait_until_n_responses(self, wait_all=False):
        # TODO: What to do in send model?
        ended_clients = []
        completed = False
        while not completed:
            # Periodically check if the requests are ending
            for key in self.clients:
                try:
                    last_operation = self.operations_history[key][-1]
                except IndexError:
                    # Last operation still not computed
                    continue
                if last_operation['ended']:
                    # TODO: Handle exception when status code != 200
                    assert last_operation['res'].status_code == 200
                    logging.info(
                        '[Client Handler] client {} '
                        'finished performing operation {}'.format(
                            key, last_operation['op']
                        )
                    )
                    ended_clients.append(key)
                if ((not wait_all and (len(ended_clients) >= self.N_FIRSTS))
                        or (wait_all and len(ended_clients) == self.N_FIRSTS)):
                    self.pool.terminate()
                    completed = True
            sleep(0.1)
        return ended_clients

    @staticmethod
    def get_client_key(host, port):
        return (host, port)

    def perform_request(self, host, port, endpoint):
        key = self.get_client_key(host, port)
        last_operation = {
            'started': time(),
            'op': endpoint,
            'status': 'started',
            'ended': None
        }
        url = 'http://{}:{}/{}'.format(host, port, endpoint)
        res = requests.get(url)
        last_operation.update({'status': 'ended',
                               'ended': time(),
                               'response': res})
        self.operations_history.setdefault(key, []).append(last_operation)

