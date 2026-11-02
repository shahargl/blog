#!/usr/bin/env python3
"""Keeps data/x.json, a daily count of everything posted on X, up to date.

    python x_activity.py

The first run backfills the last year from the user timeline (one paid read per
post). Later runs make a single counts request for the last 7 days and merge it
in, at most once per UTC day. Needs X_BEARER_TOKEN.
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

USERNAME = "shaharglazner"
DATA = Path(__file__).resolve().parent / "data" / "x.json"
API = "https://api.x.com/2"
KEEP_DAYS = 400


def api(path, **params):
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {os.environ['X_BEARER_TOKEN']}",
        "User-Agent": "shahar.blog",
    })
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def backfill(now):
    user_id = api(f"users/by/username/{USERNAME}")["data"]["id"]
    start = (now - timedelta(days=371)).strftime("%Y-%m-%dT%H:%M:%SZ")
    days, token = {}, None
    while True:
        params = {"max_results": 100, "start_time": start, "tweet.fields": "created_at"}
        if token:
            params["pagination_token"] = token
        page = api(f"users/{user_id}/tweets", **params)
        for post in page.get("data", []):
            day = post["created_at"][:10]
            days[day] = days.get(day, 0) + 1
        token = page.get("meta", {}).get("next_token")
        if not token:
            return days


def recent_counts():
    result = api("tweets/counts/recent", query=f"from:{USERNAME}", granularity="day")
    # The oldest bucket starts mid-day, so only whole days are trusted.
    return {
        bucket["start"][:10]: bucket["tweet_count"]
        for bucket in result.get("data", [])
        if bucket["start"].endswith("T00:00:00.000Z")
    }


def main():
    if not os.environ.get("X_BEARER_TOKEN"):
        print("X_BEARER_TOKEN not set, skipping X activity")
        return

    now = datetime.now(timezone.utc)
    stored = json.loads(DATA.read_text()) if DATA.exists() else None
    if stored and stored["updated"][:10] == now.date().isoformat() and "--force" not in sys.argv:
        print("X activity already updated today")
        return

    days = stored["days"] if stored else backfill(now)
    days.update(recent_counts())
    cutoff = (now - timedelta(days=KEEP_DAYS)).date().isoformat()
    days = {day: count for day, count in sorted(days.items()) if day >= cutoff and count}

    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps({
        "username": USERNAME,
        "updated": now.isoformat(timespec="minutes"),
        "days": days,
    }, indent=1) + "\n")
    print(f"X activity: {sum(days.values())} posts across {len(days)} days")


if __name__ == "__main__":
    main()
