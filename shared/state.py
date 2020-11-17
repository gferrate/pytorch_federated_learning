from shared import utils
import requests
import logging
import socket
from time import sleep
import multiprocessing


IDLE = 0

CLIENT_TRAIN_MODEL = 1
CLIENT_GET_AGG_MODEL = 2
CLIENT_SEND_MODEL = 3

SEC_AGG_GET_CLIENT_MODEL = 4
SEC_AGG_AGGREGATE_MODELS = 5
SEC_AGG_SEND_TO_MAIN_SERVER = 6

MAIN_SERVER_SEND_MODEL_TO_CLIENTS = 7
MAIN_SERVER_GET_SECAGG_MODEL = 8

PING_CADENCE = 20  # Seconds

hosts = utils.read_hosts()


class State:
    def __init__(self, client_type, _id, port):
        assert client_type in ('client', 'secure_aggregator', 'main_server')
        self.client_type = client_type
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = port
        self._id = _id
        self._current_state = IDLE
        self.current_state = IDLE
        p = multiprocessing.Process(target=self.send_ping_continuously)
        p.start()

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, state):
        payload = {
            'client_type': self.client_type,
            '_id': self._id,
            'state': self.get_state_string(self.current_state),
            'port': self.port,
            'host': self.host
        }
        try:
            requests.post(
                url='http://{}:{}/send_state'.format(
                    hosts['frontend']['host'],
                    hosts['frontend']['port']
                ),
                json=payload
            )
        except Exception as e:
            logging.warning('Frontend not reachable.\n{}'.format(e))

        self._current_state = state

    def idle(self):
        self.current_state = IDLE

    def is_idle(self):
        return self.current_state == IDLE

    def send_ping_continuously(self):
        while True:
            self.send_ping()
            sleep(PING_CADENCE)

    def send_ping(self):
        payload = {
            'client_type': self.client_type,
            '_id': self._id,
            'state': self.get_state_string(self.current_state),
            'port': self.port,
            'host': self.host
        }
        try:
            requests.post(
                url='http://{}:{}/ping'.format(
                    hosts['frontend']['host'],
                    hosts['frontend']['port']
                ),
                json=payload
            )
        except Exception as e:
            logging.warning('Frontend not reachable.\n{}'.format(e))

    @staticmethod
    def get_state_string(state):
        strings = {
            IDLE: 'IDLE',
            CLIENT_TRAIN_MODEL: 'Training model',
            CLIENT_GET_AGG_MODEL: 'Getting aggregated model',
            CLIENT_SEND_MODEL: 'Sending model to secure aggregator',
            SEC_AGG_GET_CLIENT_MODEL: 'Getting getting client models',
            SEC_AGG_SEND_TO_MAIN_SERVER: 'Sending model to main server',
            SEC_AGG_AGGREGATE_MODELS: 'Aggregating models',
            MAIN_SERVER_GET_SECAGG_MODEL: 'Getting model from sec agg',
            MAIN_SERVER_SEND_MODEL_TO_CLIENTS: 'Sending model to clients',
        }
        if state not in strings:
            raise Exception('State not recognized')
        return strings[state]

