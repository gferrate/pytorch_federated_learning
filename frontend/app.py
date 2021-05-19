import sys; sys.path.insert(0, '.')
from time import sleep, time
from datetime import datetime, timedelta
import json
import random
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)


KEEP_ALIVE_TIMEOUT = 120  # Seconds

global_state = {
    'clients': {},
    'iteration': -1,
    'started_training': False,
    'finished_training': False
}

def check_clients_ok():
    global global_state
    for client_id, client in global_state['clients'].items():
        td = timedelta(seconds=KEEP_ALIVE_TIMEOUT)
        if datetime.now() - client['last_ping'] > td:
            client['check_ok'] = False
        else:
            client['check_ok'] = True


@app.route('/')
def index():
    check_clients_ok()
    return jsonify(global_state)


@app.route('/restart')
def restart():
    global global_state
    global_state = {
        'clients': {},
        'iteration': -1,
        'started_training': False,
        'finished_training': False
    }
    return jsonify(global_state)


@app.route('/finish', methods=['POST'])
def finish():
    global global_state
    global_state['finished_training'] = True
    return jsonify(global_state)


@app.route('/fake')
def fake_data():
    global global_state
    client_types = ['main_server', 'secure_aggregator', 'client']
    statuses = [
        'IDLE', 'Training model', 'Getting aggregated model',
        'Sending model to secure aggregator', 'Getting getting client models',
        'Sending model to main server', 'Aggregating models',
        'Getting model from sec agg', 'Sending model to clients'
    ]
    for port in range(8000, 8009):
        client = random.choice(client_types)
        status = random.choice(statuses)
        check_ok = random.choice([True, False])
        _id = 'fake_client_{}'.format(port)
        data = {
            'client_type': client,
            '_id': _id,
            'state': status,
            'port': port,
            'joined_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'check_ok': check_ok,
            'host': '127.0.0.1',
            'last_ping': datetime.now()
        }
        global_state['clients'].setdefault(_id, {}).update(data)
    return jsonify(global_state)


@app.route('/frontend')
def index_fe():
    check_clients_ok()
    return render_template('index.html', state=global_state)


@app.route('/ping', methods=['POST'])
def keep_alive():
    global global_state
    data = json.loads(request.data)
    host = request.remote_addr
    port = data['port']
    _id = data['_id']
    if _id not in global_state['clients']:
        global_state['clients'][_id] = {
            'joined_at': datetime.now().strftime('%Y-%m-%d %H:%m'),
            'client_type': data['client_type'],
            'port': port,
            'check_ok': True,
            'host': host,
            'last_ping': datetime.now()
        }
    global_state['clients'][_id].update({'state': data['state']})
    global_state['clients'][_id]['last_ping'] = datetime.now()
    return jsonify({'msg': 'OK'})


@app.route('/iteration', methods=['POST'])
def iteration():
    global global_state
    data = json.loads(request.data)
    global_state['iteration'] = data['iteration']
    if not global_state['started_training'] and global_state['iteration'] > -1:
        global_state['started_training'] = True
    return jsonify({'msg': 'OK'})


@app.route('/send_state', methods=['POST'])
def get_state():
    global global_state
    host = request.remote_addr
    data = json.loads(request.data)
    port = data['port']
    _id = data['_id']
    if _id not in global_state['clients']:
        global_state['clients'][_id] = {
            'joined_at': datetime.now().strftime('%Y-%m-%d %H:%m'),
            'client_type': data['client_type'],
            'port': port,
            'check_ok': True,
            'host': host,
            'last_ping': datetime.now()
        }
    global_state['clients'][_id].update({'state': data['state']})
    return jsonify({'msg': 'OK'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=False, use_reloader=False)

