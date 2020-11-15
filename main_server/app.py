import sys; sys.path.insert(0, '.')
import os
import argparse
from flask import Flask, request, jsonify, abort
import requests
import json
import logging

from shared import utils
from shared.state import (
    MAIN_SERVER_SEND_MODEL_TO_CLIENTS,
    MAIN_SERVER_GET_SECAGG_MODEL,
    State
)


l_filename = 'logs/main_server.log'
logging.basicConfig(
    format='%(asctime)s %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(l_filename),
        logging.StreamHandler()
    ]
)


parser = argparse.ArgumentParser(description='PyTorch FedLearn')
parser.add_argument('-p', '--port', type=str, required=True,
                    help='Client port. Example: 8001')

args = parser.parse_args()
hosts = utils.read_hosts()
state = State('main_server', 'client_{}'.format(args.port), args.port)

app = Flask(__name__)


def assert_idle_state(func):
    def wrapper():
        if not state.is_idle():
            msg = (
                'Application not in IDLE state. '
                'Current state: {}'.format(state.current_state)
            )
            abort(404, description=msg)
        return func()
    return wrapper


@app.route('/')
def index():
    return jsonify({'msg': 'Server running', 'clients': hosts['clients']})


@assert_idle_state
@app.route('/secagg_model', methods=['POST'])
def get_secagg_model():
    state.current_state = MAIN_SERVER_GET_SECAGG_MODEL
    file = request.files['model'].read()
    path = 'main_server/agg_model/agg_model.tar'
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'wb') as f:
        f.write(file)
    state.idle()
    return jsonify({'msg': 'Model received', 'location': path})


@assert_idle_state
@app.route('/send_model_clients')
def send_agg_to_clients():
    state.current_state = MAIN_SERVER_SEND_MODEL_TO_CLIENTS
    for cl in hosts['clients']:
        host = cl[list(cl.keys())[0]]['host']
        port = cl[list(cl.keys())[0]]['port']
        url = 'http://{}:{}/aggmodel'.format(host, port)
        logging.info('Sending agg model to {}'.format(url))
        path = 'main_server/agg_model/agg_model.tar'
        with open(path, 'rb') as file:
            data = {'fname': 'agg_model.tar'}
            files = {
                'json': ('json_data', json.dumps(data), 'application/json'),
                'model': ('agg_model.tar', file, 'application/octet-stream')
            }
            req = requests.post(url=url, files=files)
        if req.status_code != 200:
            msg = 'Something went wrong'
            logging.info(msg)
            return msg
    state.idle()
    return jsonify({'msg': 'Aggregated model sent'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=args.port, debug=False, use_reloader=True)

