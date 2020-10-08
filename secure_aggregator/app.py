from flask import Flask, request
import requests, json
import argparse
from sec_agg import SecAgg


parser = argparse.ArgumentParser(description='PyTorch FL MNIST Example')
parser.add_argument('-p', '--port', type=str,
                    help='Client port. Example: 8001')
parser.add_argument('-m', '--main-server-port', type=int, metavar='N',
                    help='Main server port. Example: 8000')

args = parser.parse_args()
main_server_port = args.main_server_port

use_cuda = True
sec_agg = SecAgg(args.port, use_cuda)


app = Flask(__name__)


@app.route('/')
def hello():
    return 'Secure Aggregator running!'


@app.route('/cmodel', methods=['POST'])
def get_model():
    if request.method == 'POST':
        file = request.files['model'].read()
        fname = request.files['json'].read()

        fname = json.loads(fname.decode("utf-8"))
        fname = fname['fname']
        fname = 'client_models/{}'.format(fname)
        with open(fname, 'wb') as f:
            f.write(file)
        return "Model received! And saved to {}".format(fname)
    else:
        return "No file received!"


@app.route('/aggregate_models')
def perform_model_aggregation():
    sec_agg.aggregate_models()
    sec_agg.save_model()
    return (
        'Model aggregation done!\n'
        'Global model written to persistent storage.'
    )


@app.route('/send_model_secagg')
def send_agg_to_mainserver():
    model_fn = sec_agg.get_model_filename()
    path = 'persistent_storage/{}'.format(model_fn)
    with open(path, 'rb') as f:
        data = {'fname': model_fn, 'id': 'sec_agg'}
        files = {
            'json': ('json_data', json.dumps(data), 'application/json'),
            'model': (model_fn, f, 'application/octet-stream')
        }
        endpoint = 'http://localhost:{}/secagg_model'.format(main_server_port)
        req = requests.post(url=endpoint, files=files)
    if req.status_code == 200:
        return "Aggregated model sent to main server!"
    return "Something went wrong"


app.run(host='localhost', port=sec_agg.port, debug=False, use_reloader=True)

