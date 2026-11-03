#!/usr/bin/env python3
"""Keeps data/garmin.json, the bike rides Garmin detects on its own (Move IQ), up to date.

    python garmin_activity.py

These are not recorded activities: the watch notices you're cycling and logs it in
the day's timeline. Garmin has no public API for that, so this uses the Garmin
Connect mobile API. The first run (or --backfill) fetches the last year, one request
per day; later runs refetch the last week. The file only changes when the rides do.

Needs GARMIN_TOKENS: {"oauth_token": ..., "oauth_token_secret": ...}, the long-lived
OAuth1 token from a Garmin Connect login (valid for about a year). It is exchanged
for a short-lived access token on every run.
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data" / "garmin.json"
API = "https://connectapi.garmin.com"
CONSUMER_URL = "https://thegarth.s3.amazonaws.com/oauth_consumer.json"
USER_AGENT = "com.garmin.android.apps.connectmobile"
BACKFILL_DAYS = 371
REFRESH_DAYS = 7
KEEP_DAYS = 400


def quote(value):
    return urllib.parse.quote(str(value), safe="~")


def signed_url(method, url, consumer, token):
    params = {
        "oauth_consumer_key": consumer["consumer_key"],
        "oauth_nonce": secrets.token_hex(16),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_token": token["oauth_token"],
        "oauth_version": "1.0",
    }
    normalized = "&".join(f"{quote(key)}={quote(value)}" for key, value in sorted(params.items()))
    base = "&".join([method, quote(url), quote(normalized)])
    key = f"{quote(consumer['consumer_secret'])}&{quote(token['oauth_token_secret'])}"
    params["oauth_signature"] = base64.b64encode(hmac.new(key.encode(), base.encode(), hashlib.sha1).digest()).decode()
    return f"{url}?{urllib.parse.urlencode(params)}"


def access_token():
    token = json.loads(os.environ["GARMIN_TOKENS"])
    with urllib.request.urlopen(CONSUMER_URL, timeout=30) as response:
        consumer = json.load(response)
    url = signed_url("POST", f"{API}/oauth-service/oauth/exchange/user/2.0", consumer, token)
    request = urllib.request.Request(url, data=b"", method="POST", headers={
        "User-Agent": USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)["access_token"]


def client(token):
    def get(path, **params):
        request = urllib.request.Request(f"{API}{path}?{urllib.parse.urlencode(params)}", headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": USER_AGENT,
        })
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    return get


def recorded(get, start, end):
    """Recorded activities as (start, end) local datetimes, to tell them apart from detected rides."""
    spans, offset = [], 0
    while True:
        page = get("/activitylist-service/activities/search/activities",
                   startDate=start.isoformat(), endDate=end.isoformat(), start=offset, limit=100)
        for activity in page:
            begin = datetime.fromisoformat(activity["startTimeLocal"])
            spans.append((begin, begin + timedelta(seconds=activity.get("duration") or 0)))
        offset += len(page)
        if len(page) < 100:
            return spans


def rides(get, day, spans):
    result = []
    for event in get("/wellness-service/wellness/dailyEvents", calendarDate=day.isoformat()) or []:
        if event.get("activityType") != "cycling":
            continue
        begin = datetime.fromisoformat(event["startTimestampLocal"])
        end = datetime.fromisoformat(event["endTimestampLocal"])
        if any(begin < span_end and span_begin < end for span_begin, span_end in spans):
            continue
        result.append({"start": f"{begin:%H:%M}", "minutes": event["duration"]})
    return result


def main():
    if not os.environ.get("GARMIN_TOKENS"):
        print("GARMIN_TOKENS not set, skipping Garmin activity")
        return

    today = date.today()
    stored = json.loads(DATA.read_text()) if DATA.exists() else None
    backfill = stored is None or "--backfill" in sys.argv

    get = client(access_token())
    first = today - timedelta(days=BACKFILL_DAYS if backfill else REFRESH_DAYS)
    spans = recorded(get, first - timedelta(days=1), today)
    days = dict(stored["days"]) if stored else {}
    day = first
    while day <= today:
        found = rides(get, day, spans)
        if found:
            days[day.isoformat()] = found
        else:
            days.pop(day.isoformat(), None)
        day += timedelta(days=1)
        time.sleep(0.2)

    cutoff = (today - timedelta(days=KEEP_DAYS)).isoformat()
    days = {key: value for key, value in sorted(days.items()) if key >= cutoff}
    minutes = sum(ride["minutes"] for value in days.values() for ride in value)
    print(f"Garmin activity: {sum(map(len, days.values()))} rides, {minutes} minutes across {len(days)} days")
    if stored and stored["days"] == days:
        return
    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps({"updated": datetime.now().isoformat(timespec="minutes"), "days": days}, indent=1) + "\n")


if __name__ == "__main__":
    main()
