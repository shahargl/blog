#!/usr/bin/env python3
"""One-time Strava authorization for the heatmap.

Opens Strava's consent page, captures the redirect on localhost, then stores
STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET and STRAVA_REFRESH_TOKEN in .env and as
GitHub Actions secrets on this repository.

    python strava_auth.py

Client ID and secret come from https://www.strava.com/settings/api (any app works,
Strava always allows localhost as a callback).
"""

import getpass
import json
import os
import subprocess
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

PORT = 8721
REDIRECT_URI = f"http://localhost:{PORT}/"
ENV_FILE = Path(__file__).resolve().parent / ".env"


def ask(name, secret=False):
    value = os.environ.get(name)
    if value:
        return value
    prompt = f"{name}: "
    return (getpass.getpass(prompt) if secret else input(prompt)).strip()


def wait_for_code():
    result = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            result.update({key: values[0] for key, values in query.items()})
            ok = "code" in result
            self.send_response(200 if ok else 400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Strava connected, you can close this tab." if ok else b"Authorization failed.")

        def log_message(self, *args):
            pass

    with HTTPServer(("localhost", PORT), Handler) as server:
        while not result:
            server.handle_request()
    if "code" not in result:
        raise SystemExit(f"Strava returned an error: {result.get('error', result)}")
    if "activity:read" not in result.get("scope", ""):
        raise SystemExit("Please approve access to your activities and try again.")
    return result["code"]


def exchange(client_id, client_secret, code):
    body = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
    }).encode()
    with urllib.request.urlopen("https://www.strava.com/oauth/token", data=body, timeout=30) as response:
        return json.load(response)


def save_env(values):
    lines = ENV_FILE.read_text().splitlines() if ENV_FILE.exists() else []
    lines = [line for line in lines if line.partition("=")[0] not in values]
    lines += [f"{key}={value}" for key, value in values.items()]
    ENV_FILE.write_text("\n".join(lines) + "\n")
    ENV_FILE.chmod(0o600)


def main():
    client_id = ask("STRAVA_CLIENT_ID")
    client_secret = ask("STRAVA_CLIENT_SECRET", secret=True)
    url = "https://www.strava.com/oauth/authorize?" + urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "approval_prompt": "auto",
        "scope": "read,activity:read_all",
    })
    print(f"Opening Strava. If nothing happens, visit:\n{url}")
    webbrowser.open(url)

    token = exchange(client_id, client_secret, wait_for_code())
    athlete = token.get("athlete", {})
    print(f"Authorized as {athlete.get('firstname', '')} {athlete.get('lastname', '')}".rstrip())

    values = {
        "STRAVA_CLIENT_ID": client_id,
        "STRAVA_CLIENT_SECRET": client_secret,
        "STRAVA_REFRESH_TOKEN": token["refresh_token"],
    }
    save_env(values)
    print(f"Saved to {ENV_FILE.name}")
    for name, value in values.items():
        subprocess.run(["gh", "secret", "set", name], input=value, text=True, check=True)
    print("Saved as GitHub Actions secrets. The next deploy will include the Strava heatmap.")


if __name__ == "__main__":
    main()
