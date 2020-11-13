from shared import utils
import requests
import logging


IDLE = 0

CLIENT_TRAIN_MODEL = 1
CLIENT_GET_AGG_MODEL = 2
CLIENT_SEND_MODEL = 3

SEC_AGG_GET_CLIENT_MODEL = 4
SEC_AGG_AGGREGATE_MODELS = 5
SEC_AGG_SEND_TO_MAIN_SERVER = 6

MAIN_SERVER_SEND_MODEL_TO_CLIENTS = 7
MAIN_SERVER_GET_SECAGG_MODEL = 8

hosts = utils.read_hosts()


class State:
    def __init__(self, client_type, _id):
        assert client_type in ('client', 'secure_aggregator', 'main_server')
        self.client_type = client_type
        self._id = _id
        self._current_state = IDLE
        self.current_state = IDLE

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, state):
        payload = {
            'client_type': self.client_type,
            '_id': self._id,
            'state': self.get_state_string(self.current_state)
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
