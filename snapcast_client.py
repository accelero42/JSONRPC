import json
import os
import logging
import websocket

class SnapcastRPCClient:
    def __init__(self, host=None, port=None, timeout=None):
        """Create a new RPC client.

        Parameters can be provided explicitly or via the environment
        variables ``SNAPCAST_HOST``, ``SNAPCAST_PORT`` and
        ``SNAPCAST_TIMEOUT``. If not specified, reasonable defaults are
        used. ``timeout`` controls the total request timeout in seconds.
        """

        host = host or os.environ.get("SNAPCAST_HOST", "192.168.1.70")
        port = int(port or os.environ.get("SNAPCAST_PORT", 1780))
        self.timeout = float(timeout or os.environ.get("SNAPCAST_TIMEOUT", 10))

        self.url = f"ws://{host}:{port}/jsonrpc"
        self.request_id = 0

    def call(self, method, params=None):
        self.request_id += 1
        payload = {
            "id": self.request_id,
            "jsonrpc": "2.0",
            "method": method,
        }
        if params is not None:
            payload["params"] = params
        logging.info("Sending RPC payload: %s", payload)
        try:
            ws = websocket.create_connection(self.url, timeout=self.timeout)
            ws.send(json.dumps(payload))
            ws.settimeout(self.timeout)
            response = ws.recv()
        except websocket.WebSocketException as exc:
            raise RuntimeError(f"RPC request failed: {exc}") from exc
        finally:
            try:
                ws.close()
            except Exception:
                pass
        try:
            data = json.loads(response)
        except json.JSONDecodeError as exc:
            raise RuntimeError("Invalid JSON response") from exc
        logging.info("RPC response: %s", data)
        if "error" in data:
            raise RuntimeError(f"RPC error: {data['error']}")
        return data.get("result")

def main():
    client = SnapcastRPCClient()
    try:
        status = client.call("Server.GetStatus")
    except Exception as exc:
        print(f"Failed to get server status: {exc}")
    else:
        print(json.dumps(status, indent=2))

if __name__ == "__main__":
    main()
