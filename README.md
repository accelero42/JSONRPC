# JSONRPC

This repository contains a simple Python client for the Snapcast JSON-RPC control API.

## Requirements

- Python 3.11+
- `requests` library (`pip install requests`)

## Usage

The provided script `snapcast_client.py` connects to the Snapcast server at `192.168.1.70` on port `1780` and calls `Server.GetStatus` via HTTP JSON-RPC. The resulting JSON is printed to the console.

```bash
python3 snapcast_client.py
```

If the server is unreachable or returns an error, an error message will be printed instead.

The API reference is available at <https://github.com/badaix/snapcast/blob/develop/doc/json_rpc_api/control.md>.
