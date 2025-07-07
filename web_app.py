from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json
import urllib.parse
import urllib.request
import logging
from snapcast_client import SnapcastRPCClient

app = Flask(__name__)
app.secret_key = os.urandom(24)
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s %(levelname)s: %(message)s')

client = SnapcastRPCClient()

album_art_cache = {}


def fetch_album_art(artist, album):
    key = (artist, album)
    if key in album_art_cache:
        return album_art_cache[key]
    try:
        search_url = (
            "https://musicbrainz.org/ws/2/release/?query=artist:%s%%20AND%%20release:%s&fmt=json&limit=1"
            % (urllib.parse.quote(artist), urllib.parse.quote(album))
        )
        req = urllib.request.Request(
            search_url,
            headers={"User-Agent": "AudioBrane/1.0 (contact@example.com)"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.load(resp)
        if not data.get("releases"):
            album_art_cache[key] = None
            return None
        release_id = data["releases"][0]["id"]
        cover_url = f"https://coverartarchive.org/release/{release_id}/front-250"
        album_art_cache[key] = cover_url
        return cover_url
    except Exception:
        album_art_cache[key] = None
        return None

@app.route('/')
def index():
    show_disconnected = request.args.get('show_disconnected') == '1'
    try:
        status = client.call('Server.GetStatus')
    except Exception as exc:
        return f'Error fetching status: {exc}', 500

    streams = status.get('server', {}).get('streams', [])
    for stream in streams:
        metadata = stream.get('metadata', {})
        title = metadata.get('title') or metadata.get('name') or metadata.get('file', '')
        artist = metadata.get('artist')
        if isinstance(artist, list):
            artist = ", ".join(artist)
        album = metadata.get('album')
        stream['title'] = title
        stream['artist'] = artist
        stream['album'] = album
        stream['current_song'] = title
        if artist and album:
            stream['album_art'] = fetch_album_art(artist, album)
        else:
            stream['album_art'] = None
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
            clients.append({
                'id': c.get('id'),
                'name': name,
                'group_id': group_id,
                'stream_id': stream_id,
                'volume_percent': volume_cfg.get('percent'),
                'volume_muted': volume_cfg.get('muted'),
            })
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
