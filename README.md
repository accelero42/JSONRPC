# JSONRPC

This repository contains a simple Python client for the Snapcast JSON-RPC control API and a minimal Flask-based web interface.

## Requirements

- Python 3.11+
- `websocket-client` (`pip install websocket-client`)
- `Flask` (`pip install Flask`)

## Command Line Usage

The script `snapcast_client.py` connects to the Snapcast server (defaults to
`192.168.1.70:1780`) and calls `Server.GetStatus` using WebSocket JSON-RPC.  Host,
port and request timeout can be changed with the environment variables
`SNAPCAST_HOST`, `SNAPCAST_PORT` and `SNAPCAST_TIMEOUT` respectively.
The resulting JSON is printed to the console.

```bash
python3 snapcast_client.py
```

If the server is unreachable or returns an error, an error message will be printed instead.

## Web Interface

Run the Flask application to view connected clients and change their streams.
The same environment variables used by ``snapcast_client.py`` can be set to
point the web interface at a different Snapcast server or to adjust the
request timeout. Example:

```bash
SNAPCAST_HOST=192.168.1.50 SNAPCAST_TIMEOUT=15 python3 web_app.py
```

Or simply:

```bash
python3 web_app.py
```

Visit `http://localhost:5000` in your browser. The page lists all clients with inline name editing and buttons to switch streams for each client.

The interface, now titled **AudioBrane**, features a simple illustration of a brain with musical notes. A checkbox lets you hide clients that are not connected. The streams table lists each stream with its current status and the song that is playing.

The API reference is available at <https://github.com/badaix/snapcast/blob/develop/doc/json_rpc_api/control.md>.

## Hardware Controller

`controller.py` listens for a rotary encoder on GPIO 23/24 and a push button on GPIO 25 using `gpiozero`. On each detent the volume of the configured client is adjusted by 5%. Pressing the button cycles the client's group through the available streams.

The controller reads the client ID from `selected_client.json` by default. This
file is written by the web interface when you save a client selection. You can
override the path with `SNAPCAST_CLIENT_ID_FILE` or provide the ID directly via
`SNAPCAST_CLIENT_ID`.

To run this controller automatically with systemd, install `controller.service` and update the paths:

```bash
sudo cp controller.service /etc/systemd/system/controller.service
sudo systemctl enable controller.service
sudo systemctl start controller.service
```
