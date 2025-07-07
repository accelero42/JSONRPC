import json
import os
import requests

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

        self.url = f"http://{host}:{port}/jsonrpc"
        self.session = requests.Session()
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
        try:
            response = self.session.post(
                self.url,
                json=payload,
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(f"RPC request failed: {exc}") from exc
        try:
            data = response.json()
        except json.JSONDecodeError as exc:
            raise RuntimeError("Invalid JSON response") from exc
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
