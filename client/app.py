import sys; sys.path.insert(0, '.')
import argparse
from flask import Flask, request, jsonify
import json
import requests
import logging

from shared import utils
from client import Client


parser = argparse.ArgumentParser(description='PyTorch FedLearn')
parser.add_argument('-p', '--port', type=str, required=True,
                    help='Client port. Example: 8001')
parser.add_argument('-n', '--client-number', type=int, required=True,
                    help='Client number. Example: 1')
parser.add_argument('-s', '--split-type', type=str, required=False,
                    default='no_split',
                    help='Metadata split type. Example: no_split, iid')

args = parser.parse_args()
hosts = utils.read_hosts()
num_clients = len(hosts['clients'])
port = args.port
logging.basicConfig(
    format='%(asctime)s %(message)s',
    filename='logs/client_{}.log'.format(port),
    level=logging.INFO
)
client = Client(args.client_number, port, num_clients)

app = Flask(__name__)


@app.route('/')
def hello():
    return jsonify({'msg': '{} Running'.format(client.client_id)})


@app.route('/send_status', methods=['GET'])
def send_status():
    api_url = 'http://{}:{}/clientstatus'.format(hosts['main_server']['host'],
                                                 hosts['main_server']['port'])
    data = {'client_id': client.client_id}
    logging.info(data)
    r = requests.post(url=api_url, json=data)
    logging.info(r, r.status_code, r.reason, r.text)
    if r.status_code == 200:
        logging.info('Yeah')
    return jsonify({'msg': 'Status OK sent'})


@app.route('/send_model')
def send_model():
    model_fn = client.get_model_filename()
    with open(model_fn, 'rb') as file:
        data = {
            'fname': model_fn,
            'host': 'http://client:{}/'.format(client.port),
            'client_id': client.client_id
        }
        files = {
            'json': ('json_data', json.dumps(data), 'application/json'),
            'model': (model_fn, file, 'application/octet-stream')
        }
        req = requests.post(
            url='http://{}:{}/client_model'.format(
                hosts['secure_aggregator']['host'],
                hosts['secure_aggregator']['port']
            ),
            files=files
        )
    return jsonify({'msg': 'Model sent'})


@app.route('/aggmodel', methods=['POST'])
def get_agg_model():
    if request.method == 'POST':
        file = request.files['model'].read()
        fname = request.files['json'].read()
        fname = json.loads(fname.decode('utf-8'))['fname']

        path = 'client/model_update/{}'.format(fname)
        with open(path, 'wb') as wfile:
            wfile.write(file)
        logging.info('Agg model saved to {}'.format(path))
        # Update the client model
        client.update_model(path)
        return jsonify({'msg': 'Model received'})
    else:
        return jsonify({'msg': 'No file received'})


@app.route('/train_model')
def model_train():
    train_accuracies = client.train()
    # client.test()
    client.save_model()
    return jsonify({
        'msg': 'Model trained and saved successfully',
        'results': train_accuracies,
        'client_id': client.client_id
    })


@app.route('/experimental_test')
def model_test():
    res = client.test()
    # client.test()
    # client.save_model()
    return jsonify(res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=client.port, debug=False, use_reloader=True)
