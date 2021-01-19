from multiprocessing.dummy import Pool
import requests
from time import time, sleep
import logging


class ClientHandler:
    """Performs concurrent requests with timeout

    :OPERATION_MODE n_firsts, timeout or wait_all.
    :clients list of clients' (host, port) tuples
    """

    def __init__(self, clients, OPERATION_MODE='wait_all', **kwargs):
        self.clients = self.parse_clients(clients)
        self.n_clients = len(clients)
        self.OPERATION_MODE = OPERATION_MODE
        # Set the pool as None, later on will be created
        self.pool = None
        logging.info(
            '[Client Handler] Operation mode: {}'.format(self.OPERATION_MODE))
        default_n_firsts = max(1, self.n_clients - 2)
        if self.OPERATION_MODE == 'n_firsts':
            self.N_FIRSTS = kwargs.get('n_firsts', default_n_firsts)
            assert self.N_FIRSTS <= self.n_clients, \
                'n_firsts must be <= than num clients'
            logging.info(
                '[Client Handler] n_firsts: {}'.format(self.N_FIRSTS))
        elif self.OPERATION_MODE == 'timeout':
            self.WAIT_FROM_N_FIRSTS = kwargs.get('wait_from_n_firsts',
                                                 default_n_firsts)
            self.TIMEOUT = kwargs.get('timoeut', 60)  # Seconds
        elif self.OPERATION_MODE == 'wait_all':
            self.N_FIRSTS = self.n_clients
            logging.info('[Client Handler] Will wait '
                         'until {} clients'.format(self.N_FIRSTS))
        else:
            raise Exception('Operation mode not accepted')
        self.operations_history = {}
        self.init_operations_history()

    def perform_requests_and_wait(self, endpoint):
        self.perform_parallel_requests(endpoint)
        if self.OPERATION_MODE == 'n_firsts':
            if endpoint == 'send_model':
                # TODO: Do this part with redundancy
                return self.wait_until_n_responses(wait_all=True)
            return self.wait_until_n_responses()
        elif self.OPERATION_MODE == 'timeout':
            self.started = time()
            return self.wait_until_timeout()
        elif self.OPERATION_MODE == 'wait_all':
            return self.wait_until_n_responses(wait_all=True)

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

    def wait_until_timeout(self):
        ended_clients = set()
        completed = False
        while not completed:
            for key in self.clients:
                try:
                    last_operation = self.operations_history[key][-1]
                except IndexError:
                    # Last operation still not computed
                    continue
                if key in ended_clients:
                    continue
                elif last_operation['ended']:
                    # TODO: Handle exception when status code != 200
                    assert last_operation['response'].status_code == 200
                    logging.info(
                        '[Client Handler] client {} '
                        'finished performing operation {}'.format(
                            key, last_operation['op']
                        )
                    )
                    ended_clients.add(key)
            elapsed = time() - self.started
            if ((len(ended_clients) >= self.WAIT_FROM_N_FIRSTS) and
                    elapsed > self.TIMEOUT):
                self.pool.terminate()
                completed = True
            sleep(0.1)
        return list(ended_clients)

    def wait_until_n_responses(self, wait_all=False):
        # TODO: What to do in send model?
        ended_clients = set()
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
                    assert last_operation['response'].status_code == 200
                    logging.info(
                        '[Client Handler] client {} '
                        'finished performing operation {}'.format(
                            key, last_operation['op']
                        )
                    )
                    ended_clients.add(key)
                if ((not wait_all and (len(ended_clients) >= self.N_FIRSTS))
                        or (wait_all and len(ended_clients) == self.N_FIRSTS)):
                    self.pool.terminate()
                    completed = True
            sleep(0.1)
        return list(ended_clients)

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

