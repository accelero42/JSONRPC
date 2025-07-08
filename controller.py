import os
import time
import json
from gpiozero import RotaryEncoder, Button
from snapcast_client import SnapcastRPCClient

CLIENT_ID_FILE = os.environ.get("SNAPCAST_CLIENT_ID_FILE", "selected_client.json")
VOLUME_STEP = int(os.environ.get("VOLUME_STEP", 5))

class Controller:
    def __init__(self):
        self.client = SnapcastRPCClient()
        self.client_id = self.load_client_id()
        self.encoder = RotaryEncoder(23, 24)
        self.button = Button(25)
        self.encoder.when_rotated_clockwise = self.volume_up
        self.encoder.when_rotated_counter_clockwise = self.volume_down
        self.button.when_pressed = self.next_stream
        self.current_volume = self.get_current_volume()

    def load_client_id(self):
        env_id = os.environ.get("SNAPCAST_CLIENT_ID")
        if env_id:
            return env_id.strip()
        try:
            with open(CLIENT_ID_FILE, "r", encoding="utf-8") as f:
                if CLIENT_ID_FILE.endswith(".json"):
                    data = json.load(f)
                    cid = data.get("id")
                    if cid:
                        return str(cid).strip()
                    raise ValueError("Missing 'id' field")
                return f.read().strip()
        except FileNotFoundError:
            raise RuntimeError(
                f"Client ID not found. Set SNAPCAST_CLIENT_ID or create {CLIENT_ID_FILE}")
        except Exception as exc:
            raise RuntimeError(f"Failed to load client id from {CLIENT_ID_FILE}: {exc}") from exc

    def get_status(self):
        return self.client.call("Server.GetStatus")

    def get_current_volume(self):
        status = self.get_status()
        for group in status.get('server', {}).get('groups', []):
            for c in group.get('clients', []):
                if c.get('id') == self.client_id:
                    cfg = c.get('config', {}).get('volume', {})
                    return cfg.get('percent', 0)
        return 0

    def change_volume(self, delta):
        self.current_volume = max(0, min(100, self.current_volume + delta))
        params = {
            'id': self.client_id,
            'volume': {
                'percent': self.current_volume,
                'muted': self.current_volume == 0,
            },
        }
        try:
            self.client.call('Client.SetVolume', params)
            print(f"Volume set to {self.current_volume}%")
        except Exception as exc:
            print(f"Failed to set volume: {exc}")

    def volume_up(self):
        self.change_volume(VOLUME_STEP)

    def volume_down(self):
        self.change_volume(-VOLUME_STEP)

    def next_stream(self):
        try:
            status = self.get_status()
        except Exception as exc:
            print(f"Failed to get status: {exc}")
            return
        streams = status.get('server', {}).get('streams', [])
        groups = status.get('server', {}).get('groups', [])
        stream_ids = [s.get('id') for s in streams]
        group_id = None
        current_stream = None
        for g in groups:
            for c in g.get('clients', []):
                if c.get('id') == self.client_id:
                    group_id = g.get('id')
                    current_stream = g.get('stream_id')
                    break
            if group_id:
                break
        if not group_id or not stream_ids:
            print("Unable to determine group or streams")
            return
        if current_stream in stream_ids:
            idx = stream_ids.index(current_stream)
        else:
            idx = -1
        next_stream = stream_ids[(idx + 1) % len(stream_ids)]
        try:
            self.client.call('Group.SetStream', {'id': group_id, 'stream_id': next_stream})
            print(f"Stream changed to {next_stream}")
        except Exception as exc:
            print(f"Failed to set stream: {exc}")

    def run(self):
        print("Controller running. Press Ctrl+C to exit.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

if __name__ == '__main__':
    Controller().run()
