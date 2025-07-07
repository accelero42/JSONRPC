from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json
from snapcast_client import SnapcastRPCClient

app = Flask(__name__)
app.secret_key = os.urandom(24)

client = SnapcastRPCClient()

@app.route('/')
def index():
    show_disconnected = request.args.get('show_disconnected') == '1'
    try:
        status = client.call('Server.GetStatus')
    except Exception as exc:
        return f'Error fetching status: {exc}', 500

    streams = status.get('server', {}).get('streams', [])
    groups = status.get('server', {}).get('groups', [])

    # Flatten clients with group, stream and volume info
    clients = []
    for group in groups:
        stream_id = group.get('stream_id')
        group_id = group.get('id')
        for c in group.get('clients', []):
            connected = c.get('connected', True)
            if not show_disconnected and not connected:
                continue
            name = c.get('config', {}).get('name') or c.get('host', {}).get('name') or c.get('id')
            volume_cfg = c.get('config', {}).get('volume', {})
        client_info = {
            'id': c.get('id'),
            'name': name,
            'group_id': group_id,
            'stream_id': stream_id,
            'volume_percent': volume_cfg.get('percent'),
            'volume_muted': volume_cfg.get('muted'),
        }
        clients.append(client_info)
    return render_template('index.html', clients=clients, streams=streams, show_disconnected=show_disconnected)

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


@app.route('/change_name', methods=['POST'])
def change_name():
    client_id = request.form.get('client_id')
    name = request.form.get('name')
    if not client_id or name is None:
        flash('Invalid request')
        return redirect(url_for('index'))
    try:
        client.call('Client.SetName', {'id': client_id, 'name': name})
        flash(f'Name changed to {name} for {client_id}')
    except Exception as exc:
        flash(f'Error setting name: {exc}')
    return redirect(url_for('index'))


@app.route('/set_volume', methods=['POST'])
def set_volume():
    client_id = request.form.get('client_id')
    volume = request.form.get('volume')
    if client_id is None or volume is None:
        flash('Invalid request')
        return redirect(url_for('index'))

    try:
        volume_val = int(volume)
    except ValueError:
        flash('Invalid volume value')
        return redirect(url_for('index'))

    params = {
        'id': client_id,
        'volume': {
            'muted': volume_val == 0,
            'percent': volume_val,
        },
    }
    try:
        client.call('Client.SetVolume', params)
        flash(f'Volume set to {volume_val}% for {client_id}')
    except Exception as exc:
        flash(f'Error setting volume: {exc}')
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
