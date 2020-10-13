import sys; sys.path.insert(0, '.')
import argparse
from flask import Flask, request
import json
import requests

from shared import utils
from client import Client


parser = argparse.ArgumentParser(description='PyTorch FedLearn')
parser.add_argument('-p', '--port', type=str, required=True,
                    help='Client port. Example: 8001')
parser.add_argument('-n', '--client-number', type=int, required=True,
                    help='Client number. Example: 1')

args = parser.parse_args()
hosts = utils.read_hosts()
num_clients = len(hosts['clients'])
client = Client(args.client_number, args.port, num_clients)

app = Flask(__name__)


@app.route('/')
def hello():
    return '{} Running'.format(client.client_id)


@app.route('/sendstatus', methods=['GET'])
def send_status():
    api_url = 'http://{}:{}/clientstatus'.format(hosts['main_server']['host'],
                                                 hosts['main_server']['port'])
    data = {'client_id': client.client_id}
    print(data)
    r = requests.post(url=api_url, json=data)
    print(r, r.status_code, r.reason, r.text)
    if r.status_code == 200:
        print('Yeah')
    return 'Status OK sent!'


@app.route('/sendmodel')
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
            url='http://{}:{}/cmodel'.format(
                hosts['secure_aggregator']['host'],
                hosts['secure_aggregator']['port']
            ),
            files=files
        )
    return 'Model sent!'


@app.route('/aggmodel', methods=['POST'])
def get_agg_model():
    if request.method == 'POST':
        file = request.files['model'].read()
        fname = request.files['json'].read()
        fname = json.loads(fname.decode('utf-8'))['fname']

        path = 'client/model_update/{}'.format(fname)
        with open(path, 'wb') as wfile:
            wfile.write(file)
        print('Agg model saved to {}'.format(path))
        # Update the client model
        client.update_model(path)
        return 'Model received!'
    else:
        return 'No file received!'


@app.route('/modeltrain')
def model_train():
    client.train()
    # client.test()
    # client.save_model()
    return 'Model trained and saved successfully!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=client.port, debug=False, use_reloader=True)
