import json
import requests

class SnapcastRPCClient:
    def __init__(self, host="192.168.1.70", port=1780):
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
                timeout=5,
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
