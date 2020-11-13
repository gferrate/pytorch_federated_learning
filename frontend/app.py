import sys; sys.path.insert(0, '.')
from time import sleep, time
from datetime import datetime
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

global_state = {
    'clients': {},
    'iteration': -1,
    'started_training': False
}


@app.route('/')
def index():
    return jsonify(global_state)


@app.route('/iteration', methods=['POST'])
def iteration():
    data = json.loads(request.data)
    global_state['iteration'] = data['iteration']
    if not global_state['started_training'] and global_state['iteration'] > -1:
        global_state['started_training'] = True
    return jsonify({'msg': 'OK'})


@app.route('/send_state', methods=['POST'])
def get_state():
    data = json.loads(request.data)
    _id = data['_id']
    if _id not in global_state['clients']:
        global_state['clients'][_id] = {
            'joined_at': datetime.now(),
            'client_type': data['client_type']
        }
    global_state['clients'][_id].update({'state': data['state']})
    return jsonify({'msg': 'OK'})


if __name__ == '__main__':
    app.run(host='localhost', port=8002, debug=False, use_reloader=True)

