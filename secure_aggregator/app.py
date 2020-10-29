import sys; sys.path.insert(0, '.')
from flask import Flask, request, jsonify

import requests, json, os
import argparse
import ntpath

from shared import utils
from sec_agg import SecAgg


parser = argparse.ArgumentParser(description='PyTorch FL MNIST Example')
parser.add_argument('-p', '--port', type=str, required=True,
                    help='Client port. Example: 8001')

args = parser.parse_args()
hosts = utils.read_hosts()

use_cuda = True
sec_agg = SecAgg(args.port, use_cuda)


app = Flask(__name__)


@app.route('/')
def hello():
    return jsonify({'running': 1})


@app.route('/client_model', methods=['POST'])
def get_client_model():
    if request.method == 'POST':
        file = request.files['model'].read()
        data = request.files['json'].read()
        data = json.loads(data.decode('utf-8'))
        client_id = data['client_id']
        fname = '{}_{}'.format(client_id, 'model.tar')
        fname = 'secure_aggregator/client_models/{}'.format(fname)
        if not os.path.exists(os.path.dirname(fname)):
            os.makedirs(os.path.dirname(fname))
        with open(fname, 'wb') as f:
            f.write(file)
        return jsonify({'msg': 'Model received', 'location': fname})

    else:
        return jsonify({'msg': 'No file received', 'location': None})


@app.route('/aggregate_models')
def perform_model_aggregation():
    # Test: Init model in each model aggregation to restart the epoch numbers
    sec_agg.init_model()
    sec_agg.aggregate_models()
    # TODO: Maybe we could save the model and continue the process before
    # doing the test so the clients can do more work in less time
    test_result = sec_agg.test()
    sec_agg.save_model()
    # This is only to make sure that no aggregation is repeated
    sec_agg.delete_client_models()

    return jsonify({
        'msg': ('Model aggregation done!\n'
                'Global model written to persistent storage.'),
        'test_result': test_result
    })


@app.route('/send_model_to_main_server')
def send_agg_to_mainserver():
    path = sec_agg.get_model_filename()
    with open(path, 'rb') as f:
        data = {'fname': path, 'id': 'sec_agg'}
        files = {
            'json': ('json_data', json.dumps(data), 'application/json'),
            'model': (path, f, 'application/octet-stream')
        }
        endpoint = 'http://{}:{}/secagg_model'.format(
            hosts['main_server']['host'],
            hosts['main_server']['port'])
        req = requests.post(url=endpoint, files=files)
    if req.status_code == 200:
        return jsonify({'msg': 'Aggregated model sent to main server'})
    return jsonify({'msg': 'Something went wrong'})


app.run(host='0.0.0.0', port=sec_agg.port, debug=False, use_reloader=True)

