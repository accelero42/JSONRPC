from flask import Flask, render_template, request, redirect, url_for, flash
import os
import json
from snapcast_client import SnapcastRPCClient

app = Flask(__name__)
app.secret_key = os.urandom(24)

client = SnapcastRPCClient()

SELECTED_FILE = "selected_client.json"


def load_selected_id() -> str | None:
    """Return the saved client id if the file exists."""
    if os.path.exists(SELECTED_FILE):
        try:
            with open(SELECTED_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("id")
        except Exception:
            return None
    return None


@app.route("/")
def index():
    """Show available clients and the current selection."""
    try:
        status = client.call("Server.GetStatus")
    except Exception as exc:
        return f"Error fetching status: {exc}", 500

    clients = []
    for group in status.get("server", {}).get("groups", []):
        for c in group.get("clients", []):
            name = (
                c.get("config", {}).get("name")
                or c.get("host", {}).get("name")
                or c.get("id")
            )
            clients.append({"id": c.get("id"), "name": name})

    selected = load_selected_id()
    return render_template("index.html", clients=clients, selected=selected)


@app.route("/save_selection", methods=["POST"])
def save_selection():
    """Persist the chosen client id."""
    client_id = request.form.get("client_id")
    if not client_id:
        flash("No client selected")
        return redirect(url_for("index"))

    try:
        with open(SELECTED_FILE, "w", encoding="utf-8") as f:
            json.dump({"id": client_id}, f)
        flash(f"Saved client {client_id}")
    except Exception as exc:
        flash(f"Failed to save: {exc}")

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
