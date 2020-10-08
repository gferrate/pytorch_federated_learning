import argparse
from flask import Flask, request
import requests, json


parser = argparse.ArgumentParser(description='PyTorch FL MNIST Example')
parser.add_argument('-p', '--port', type=str, required=True,
                    help='Client port. Example: 8001')
parser.add_argument('-s', '--secure-agg-port', type=int, metavar='N',
                    required=True,
                    help='Secure aggregator port. Example: 8003')
parser.add_argument('-l', '--client-ports', nargs='+', type=int, required=True,
                    help='List of the clients\'s ports. Example: -l 8001 8002')

args = parser.parse_args()
secure_agg_port = args.secure_agg_port
client_ports = args.client_ports

app = Flask(__name__)


@app.route('/')
def hello():
    return (
        'Server running!</br>'
        'Clients: {}'.format(', '.join(map(str, client_ports)))
    )


@app.route('/clientstatus', methods=['GET','POST'])
def client_status():
    url = 'http://localhost:8001/serverack'

    if request.method == 'POST':
        client_port = request.json['client_id']

        with open('clients.txt', 'a+') as f:
            f.write('http://localhost:' + client_port + '/\n')

        print(client_port)

        if client_port:
            serverack = {'server_ack': '1'}
            # response = requests.post( url, data=json.dumps(serverack), headers={'Content-Type': 'application/json'} )
            return str(serverack)
        else:
            return 'Client status not OK!'
    else:
        return 'Client GET request received!'


@app.route('/secagg_model', methods=['POST'])
def get_secagg_model():
    if request.method == 'POST':
        file = request.files['model'].read()
        fname = request.files['json'].read()
        # cli = request.files['id'].read()

        # fname = json.loads(fname.decode('utf-8'))
        # path = 'agg_model/{}'.format(fname['fname'])
        path = 'agg_model/agg_model.tar'
        with open(path, 'wb') as f:
            f.write(file)
        return 'Model received and saved to {}'.format(path)
    else:
        return 'No file received!'


@app.route('/send_model_clients')
def send_agg_to_clients():
    for port in client_ports:
        url = 'http://localhost:{}/aggmodel'.format(port)
        print('Sending agg model to {}'.format(url))
        path = 'agg_model/agg_model.tar'
        with open(path, 'rb') as file:
            data = {'fname': 'agg_model.tar'}
            files = {
                'json': ('json_data', json.dumps(data), 'application/json'),
                'model': ('agg_model.tar', file, 'application/octet-stream')
            }
            req = requests.post(url=url, files=files)
        if req.status_code != 200:
            msg = 'Something went wrong'
            print(msg)
            return msg
    return 'Aggregated model sent!'


if __name__ == '__main__':
    app.run(host='localhost', port=args.port, debug=False, use_reloader=True)

