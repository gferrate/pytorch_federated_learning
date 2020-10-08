import argparse
from flask import Flask, request
import json
import requests
from client import Client

parser = argparse.ArgumentParser(description='PyTorch FL MNIST Example')
parser.add_argument('-n', '--num-clients', type=int, metavar='N', required=True,
                    help='Total number of clients')
parser.add_argument('-p', '--port', type=str, required=True,
                    help='Client port. Example: 8001')
parser.add_argument('--batch-size', type=int, default=32, metavar='N',
                    help='input batch size for training (default: 32)')
parser.add_argument('-s', '--secure-agg-port', type=int, metavar='N',
                    required=True,
                    help='Secure aggregator port. Example: 8003')
parser.add_argument('-m', '--main-server-port', type=int, metavar='N',
                    help='Main server port. Example: 8000')

use_cuda = True
args = parser.parse_args()
secure_agg_port = args.secure_agg_port
main_server_port = args.main_server_port
client = Client(args.port, args.num_clients, use_cuda)

app = Flask(__name__)


@app.route('/')
def hello():
    return '{} Running'.format(client.client_id)


@app.route('/sendstatus', methods=['GET'])
def send_status():
    api_url = 'http://localhost:{}/clientstatus'.format(main_server_port)
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
            'id': 'http://localhost:{}/'.format(client.port)
        }
        files = {
            'json': ('json_data', json.dumps(data), 'application/json'),
            'model': (model_fn, file, 'application/octet-stream')
        }
        req = requests.post(
            url='http://localhost:{}/cmodel'.format(secure_agg_port),
            files=files
        )
    return 'Model sent!'


@app.route('/aggmodel', methods=['POST'])
def get_agg_model():
    if request.method == 'POST':
        file = request.files['model'].read()
        fname = request.files['json'].read()
        fname = json.loads(fname.decode('utf-8'))['fname']

        path = 'model_update/{}'.format(fname)
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
    client.save_model()
    return 'Model trained and saved successfully!'


app.run(host='localhost', port=client.port, debug=False, use_reloader=True)
