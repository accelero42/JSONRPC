# JSONRPC

This repository contains a simple Python client for the Snapcast JSON-RPC control API and a minimal Flask-based web interface.

## Requirements

- Python 3.11+
- `requests` library (`pip install requests`)
- `Flask` (`pip install Flask`)

## Command Line Usage

The script `snapcast_client.py` connects to the Snapcast server at `192.168.1.70` on port `1780` and calls `Server.GetStatus` via HTTP JSON-RPC. The resulting JSON is printed to the console.

```bash
python3 snapcast_client.py
```

If the server is unreachable or returns an error, an error message will be printed instead.

## Web Interface

Run the Flask application to view connected clients and change their streams:

```bash
python3 web_app.py
```

Visit `http://localhost:5000` in your browser. The page lists all clients with the stream they are currently connected to. A drop-down allows selecting a different stream for each client.

The API reference is available at <https://github.com/badaix/snapcast/blob/develop/doc/json_rpc_api/control.md>.
