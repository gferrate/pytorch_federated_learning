import sys; sys.path.insert(0, '.')
import argparse
from flask import Flask, request, jsonify, abort
import json
import requests
import logging

from shared import utils
from client import Client
from shared.state import (
    CLIENT_TRAIN_MODEL,
    CLIENT_GET_AGG_MODEL,
    CLIENT_SEND_MODEL,
    State
)
from shared import rsa_utils


parser = argparse.ArgumentParser(description='PyTorch FedLearn')
parser.add_argument('-p', '--port', type=str, required=True,
                    help='Client port. Example: 8001')
parser.add_argument('-n', '--client-number', type=int, required=True,
                    help='Client number. Example: 1')
parser.add_argument('-s', '--split-type', type=str, required=False,
                    default='no_split',
                    help=('Metadata split type. '
                          'Example: no_split, iid, non-iid-a')

rsa = rsa_utils.RSAUtils()
args = parser.parse_args()
hosts = utils.read_hosts()
num_clients = len(hosts['clients'])
port = args.port
l_filename = 'logs/client_{}.log'.format(port)
logging.basicConfig(
    format='%(asctime)s %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(l_filename),
        logging.StreamHandler()
    ]
)

client = Client(args.client_number, port, num_clients, args.split_type)
state = State('client', client.client_id, port)

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
def hello():
    return jsonify({'msg': '{} Running'.format(client.client_id)})


@app.route('/pub_key')
def get_pub_key():
    return jsonify({'pub_key': rsa.export_public_key()})


@assert_idle_state
@app.route('/send_model')
def send_model():
    state.current_state = CLIENT_SEND_MODEL
    model_fn = client.get_model_filename()
    host = hosts['secure_aggregator']['host']
    port = hosts['secure_aggregator']['port']
    model_byte_array = open(model_fn, "rb").read()
    enc_session_key, nonce, tag, ciphertext = \
        rsa.encrypt_bytes(model_byte_array, host=host, port=port)
    data = {'client_id': client.client_id}
    files = {
        'json': ('json_data', json.dumps(data), 'application/json'),
        'enc_session_key': ('sk', enc_session_key, 'application/octet-stream'),
        'nonce': ('nonce', nonce, 'application/octet-stream'),
        'tag': ('tag', tag, 'application/octet-stream'),
        'ciphertext': ('ciphertext', ciphertext, 'application/octet-stream'),
    }
    requests.post(url='http://{}:{}/client_model'.format(host, port),
                  files=files)
    state.idle()
    return jsonify({'msg': 'Model sent'})


@assert_idle_state
@app.route('/aggmodel', methods=['POST'])
def get_agg_model():
    state.current_state = CLIENT_GET_AGG_MODEL
    enc_data = rsa.get_crypt_files_from_req(request)
    file = rsa.decrypt_bytes(enc_data)
    fname = request.files['json'].read()
    fname = json.loads(fname.decode('utf-8'))['fname']
    path = 'client/model_update/{}'.format(fname)
    with open(path, 'wb') as wfile:
        wfile.write(file)
    logging.info('Agg model saved to {}'.format(path))
    # Update the client model
    client.update_model(path)
    state.idle()
    return jsonify({'msg': 'Model received'})


@assert_idle_state
@app.route('/train_model')
def model_train():
    state.current_state = CLIENT_TRAIN_MODEL
    client.train()
    # client.test()
    client.save_model()
    state.idle()
    return jsonify({'msg': 'Model trained and saved successfully'})


@app.route('/state')
def get_state():
    return jsonify({'state': state.current_state})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=client.port, debug=False, use_reloader=False)
