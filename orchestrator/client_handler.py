from multiprocessing import Process, Manager, Lock
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
        self.manager = Manager()
        self.lock = Lock()
        self.last_operation = self.manager.dict()
        self.reset_last_operation()
        self.processes = []

    def perform_requests_and_wait(self, endpoint):
        self.perform_parallel_requests(endpoint)
        if self.OPERATION_MODE == 'n_firsts':
            if endpoint == 'send_model':
                # TODO: Do this part with redundancy
                return self.wait_until('n_responses', wait_all=True)
            return self.wait_until('n_responses')
        elif self.OPERATION_MODE == 'timeout':
            self.started = time()
            return self.wait_until('timeout')
        elif self.OPERATION_MODE == 'wait_all':
            return self.wait_until('n_responses', wait_all=True)

    def reset_last_operation(self):
        self.lock.acquire()
        for key in self.clients:
            self.last_operation[key] = None
        self.lock.release()

    @staticmethod
    def parse_clients(clients):
        p_clients = []
        for cl in clients:
            host = cl[list(cl.keys())[0]]['host']
            port = cl[list(cl.keys())[0]]['port']
            p_clients.append((host, port))
        return p_clients

    def perform_parallel_requests(self, endpoint):
        self.reset_last_operation()
        for host, port in self.clients:
            p = Process(target=self.perform_request,
                        args=(host, port, endpoint))
            p.start()
            self.processes.append(p)

    def wait_until(self, until_cond, wait_all=False):
        # TODO: What to do in send model?
        ended_clients = set()
        completed = False
        while not completed:
            # Periodically check if the requests are ending
            for key in self.clients:
                last_operation = self.last_operation[key]
                if not last_operation or key in ended_clients:
                    # Last operation still not computed or already finished
                    continue
                elif last_operation['ended']:
                    # TODO: Handle exception when status code != 200
                    if last_operation['response'].status_code != 200:
                        raise Exception(
                            'Error in response. Error code: {}'.format(
                                last_operation['response'].text))
                    logging.info(
                        '[Client Handler] client {} '
                        'finished performing operation {}'.format(
                            key, last_operation['op']
                        )
                    )
                    ended_clients.add(key)
            if until_cond == 'n_responses':
                if ((not wait_all and (len(ended_clients) >= self.N_FIRSTS))
                        or (wait_all and len(ended_clients) == self.N_FIRSTS)):
                    completed = True
            elif until_cond == 'timeout':
                elapsed = time() - self.started
                if ((len(ended_clients) >= self.WAIT_FROM_N_FIRSTS) and
                        elapsed > self.TIMEOUT):
                    completed = True
            else:
                raise Exception('Not implemented')
            sleep(0.2)
        self.terminate_processes()
        return list(ended_clients)

    def terminate_processes(self):
        for p in self.processes:
            p.terminate()
        self.processes = []

    @staticmethod
    def get_client_key(host, port):
        return (host, port)

    def perform_request(self, host, port, endpoint):
        client_key = self.get_client_key(host, port)
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
        self.lock.acquire()
        self.last_operation[client_key] = last_operation
        self.lock.release()

