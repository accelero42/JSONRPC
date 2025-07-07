from flask import Flask, render_template, request, redirect, url_for, flash
import os
from snapcast_client import SnapcastRPCClient

app = Flask(__name__)
app.secret_key = os.urandom(24)

client = SnapcastRPCClient()

@app.route('/')
def index():
    try:
        status = client.call('Server.GetStatus')
    except Exception as exc:
        return f'Error fetching status: {exc}', 500

    streams = status.get('server', {}).get('streams', [])
    groups = status.get('server', {}).get('groups', [])

    # Flatten clients with group and stream info
    clients = []
    for group in groups:
        stream_id = group.get('stream_id')
        group_id = group.get('id')
        for c in group.get('clients', []):
            name = c.get('config', {}).get('name') or c.get('host', {}).get('name') or c.get('id')
            clients.append({'id': c.get('id'), 'name': name, 'group_id': group_id, 'stream_id': stream_id})
    return render_template('index.html', clients=clients, streams=streams)

@app.route('/change_stream', methods=['POST'])
def change_stream():
    group_id = request.form.get('group_id')
    stream_id = request.form.get('stream_id')
    if not group_id or not stream_id:
        flash('Invalid request')
        return redirect(url_for('index'))
    try:
        client.call('Group.SetStream', {'id': group_id, 'stream_id': stream_id})
        flash(f'Stream changed to {stream_id} for group {group_id}')
    except Exception as exc:
        flash(f'Error setting stream: {exc}')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
