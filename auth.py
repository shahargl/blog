#!/usr/bin/env python3
"""One-time OAuth authorization for the heatmaps.

    python auth.py strava
    python auth.py linkedin

Opens the service's consent page, captures the redirect on localhost, then
stores the credentials in .env and as GitHub Actions secrets on this repository.

Strava: client ID and secret from https://www.strava.com/settings/api. Strava
always allows localhost callbacks.

LinkedIn: client ID and secret from https://www.linkedin.com/developers/apps.
The app needs the Community Management API product (for r_member_postAnalytics)
and http://localhost:8722/ under Auth > Authorized redirect URLs.
"""

import getpass
import json
import os
import subprocess
import sys
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parent / ".env"

SERVICES = {
    "strava": {
        "port": 8721,
        "authorize": "https://www.strava.com/oauth/authorize",
        "token": "https://www.strava.com/oauth/token",
        "scope": "read,activity:read_all",
        "extra": {"approval_prompt": "auto"},
    },
    "linkedin": {
        "port": 8722,
        "authorize": "https://www.linkedin.com/oauth/v2/authorization",
        "token": "https://www.linkedin.com/oauth/v2/accessToken",
        "scope": "r_member_postAnalytics",
        "extra": {},
    },
}


def ask(name, secret=False):
    value = os.environ.get(name)
    if value:
        return value
    prompt = f"{name}: "
    return (getpass.getpass(prompt) if secret else input(prompt)).strip()


def wait_for_code(port):
    result = {}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            result.update({key: values[0] for key, values in query.items()})
            ok = "code" in result
            self.send_response(200 if ok else 400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"Connected, you can close this tab." if ok else b"Authorization failed.")

        def log_message(self, *args):
            pass

    with HTTPServer(("localhost", port), Handler) as server:
        while not result:
            server.handle_request()
    if "code" not in result:
        raise SystemExit(f"Authorization failed: {result.get('error_description') or result.get('error') or result}")
    return result


def exchange(service, client_id, client_secret, code, redirect_uri):
    body = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }).encode()
    request = urllib.request.Request(service["token"], data=body, headers={
        "Content-Type": "application/x-www-form-urlencoded",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def save_env(values):
    lines = ENV_FILE.read_text().splitlines() if ENV_FILE.exists() else []
    lines = [line for line in lines if line.partition("=")[0] not in values]
    lines += [f"{key}={value}" for key, value in values.items()]
    ENV_FILE.write_text("\n".join(lines) + "\n")
    ENV_FILE.chmod(0o600)


def main():
    name = sys.argv[1] if len(sys.argv) > 1 else ""
    if name not in SERVICES:
        raise SystemExit(f"usage: python auth.py {{{'|'.join(SERVICES)}}}")
    service, prefix = SERVICES[name], name.upper()
    redirect_uri = f"http://localhost:{service['port']}/"

    client_id = ask(f"{prefix}_CLIENT_ID")
    client_secret = ask(f"{prefix}_CLIENT_SECRET", secret=True)
    url = service["authorize"] + "?" + urllib.parse.urlencode({
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": service["scope"],
        **service["extra"],
    })
    print(f"Opening {name}. If nothing happens, visit:\n{url}")
    webbrowser.open(url)

    callback = wait_for_code(service["port"])
    if name == "strava" and "activity:read" not in callback.get("scope", ""):
        raise SystemExit("Please approve access to your activities and try again.")
    token = exchange(service, client_id, client_secret, callback["code"], redirect_uri)

    values = {f"{prefix}_CLIENT_ID": client_id, f"{prefix}_CLIENT_SECRET": client_secret}
    if token.get("refresh_token"):
        values[f"{prefix}_REFRESH_TOKEN"] = token["refresh_token"]
    else:
        values[f"{prefix}_ACCESS_TOKEN"] = token["access_token"]
        days = token.get("expires_in", 0) // 86400
        print(f"No refresh token was issued. The access token expires in {days} days; run this again before then.")

    save_env(values)
    print(f"Saved to {ENV_FILE.name}")
    for key, value in values.items():
        subprocess.run(["gh", "secret", "set", key], input=value, text=True, check=True)
    print(f"Saved as GitHub Actions secrets. The next deploy will include the {name} heatmap.")


if __name__ == "__main__":
    main()
