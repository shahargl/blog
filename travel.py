#!/usr/bin/env python3
"""Keeps data/travel.json, the countries I was in each day, up to date.

    python travel.py

Sources, most trusted first:
1. data/timeline.json, imported from a Google Maps Timeline export (timeline_import.py).
2. GPS start points of Strava and Garmin activities.
3. The watch's time zone each day (Garmin): a day away from home time borrows the
   country of the nearest known day of the same trip, or stays "abroad" if there is none.

Needs STRAVA_* and GARMIN_TOKENS for the live sources; without them only the
Timeline import is used. Also downloads the flag of every country it finds.
"""

import json
import os
import sys
import time
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from functools import cache
from zoneinfo import TZPATH, ZoneInfo

import garmin_activity
import heatmaps
from countries import country

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "travel.json"
TIMELINE = ROOT / "data" / "timeline.json"
FLAGS = ROOT / "static" / "flags"
FLAG_URL = "https://cdn.jsdelivr.net/gh/lipis/flag-icons@7/flags/1x1/{}.svg"
HOME = heatmaps.HOME_COUNTRIES
HOME_ZONE = ZoneInfo("Asia/Jerusalem")
WINDOW_DAYS = 372
KEEP_DAYS = 400
SEARCH_DAYS = 10
REFRESH_DAYS = 2


def strava_points(since):
    token = heatmaps.strava_access_token()
    after = int(datetime.combine(since, datetime.min.time()).timestamp())
    points, page = [], 1
    while True:
        batch = heatmaps.request_json(
            f"https://www.strava.com/api/v3/athlete/activities?after={after}&per_page=200&page={page}",
            headers={"Authorization": f"Bearer {token}"},
        )
        points += [(a["start_date_local"][:19], *a["start_latlng"]) for a in batch if a.get("start_latlng")]
        if len(batch) < 200:
            return points
        page += 1


def garmin_points(get, since, today):
    points, offset = [], 0
    while True:
        page = get("/activitylist-service/activities/search/activities",
                   startDate=since.isoformat(), endDate=today.isoformat(), start=offset, limit=100)
        points += [(a["startTimeLocal"].replace(" ", "T"), a["startLatitude"], a["startLongitude"])
                   for a in page if a.get("startLatitude") is not None]
        offset += len(page)
        if len(page) < 100:
            return points


def garmin_offsets(get, days, known):
    """Minutes ahead of UTC the watch was on each day, None when it wasn't worn."""
    name = get("/userprofile-service/socialProfile")["displayName"]
    offsets = dict(known)
    for day in days:
        if day in offsets and day < days[-REFRESH_DAYS]:
            continue
        summary = get(f"/usersummary-service/usersummary/daily/{name}", calendarDate=day)
        start_gmt, start_local = summary.get("wellnessStartTimeGmt"), summary.get("wellnessStartTimeLocal")
        offsets[day] = (
            round((datetime.fromisoformat(start_local) - datetime.fromisoformat(start_gmt)).total_seconds() / 60)
            if start_gmt and start_local else None
        )
        time.sleep(0.2)
    return offsets


def offset_in(zone, day):
    noon = datetime.combine(date.fromisoformat(day), datetime.min.time().replace(hour=12), zone)
    return round(noon.utcoffset().total_seconds() / 60)


def home_offset(day):
    return offset_in(HOME_ZONE, day)


@cache
def country_zones():
    for directory in TZPATH:
        table = Path(directory) / "zone.tab"
        if table.exists():
            zones = {}
            for line in table.read_text().splitlines():
                if line and not line.startswith("#"):
                    code, _, name = line.split("\t")[:3]
                    zones.setdefault(code, []).append(ZoneInfo(name))
            return zones
    return {}


def plausible(code, day, offset):
    """Timeline stays sometimes run on for days after leaving, so a country has to match the watch's time zone."""
    zones = country_zones().get(code)
    return offset is None or not zones or code in HOME or any(offset_in(zone, day) == offset for zone in zones)


def foreign(codes):
    return [code for code in codes if code not in HOME]


def resolve(days, known, offsets):
    resolved, abroad = {}, {}
    for index, day in enumerate(days):
        if day in known:
            resolved[day] = known[day]
            continue
        offset = offsets.get(day)
        away = offset is not None and offset != home_offset(day)

        def nearest(direction):
            for step in range(1, SEARCH_DAYS + 1):
                other = index + direction * step
                if not 0 <= other < len(days):
                    return None
                other_day = days[other]
                if other_day in known:
                    found = foreign(known[other_day])
                    if not found:
                        return None
                    return found[-1] if direction < 0 else found[0]
                if away and offsets.get(other_day) == home_offset(other_day):
                    return None
            return None

        before, after = nearest(-1), nearest(1)
        if away:
            guess = before or after
            if guess:
                resolved[day] = [guess]
            else:
                abroad[day] = offset
        elif before and before == after:
            # Same time zone as home (Cyprus, Jordan...) but between two days of the same trip.
            resolved[day] = [before]

    for index, day in enumerate(days):
        codes = resolved.get(day)
        if not codes or not foreign(codes) or len(foreign(codes)) == len(codes):
            continue
        away = foreign(codes)
        previous = resolved.get(days[index - 1], []) if index else []
        returning = away[0] in previous
        resolved[day] = away + ["IL"] if returning else ["IL"] + away
    return resolved, abroad


def download_flags(codes):
    FLAGS.mkdir(parents=True, exist_ok=True)
    for code in codes:
        path = FLAGS / f"{code.lower()}.svg"
        if not path.exists():
            with urllib.request.urlopen(FLAG_URL.format(code.lower()), timeout=30) as response:
                path.write_bytes(response.read())


def main():
    today = date.today()
    first = today - timedelta(days=WINDOW_DAYS)
    days = [(first + timedelta(days=step)).isoformat() for step in range(WINDOW_DAYS + 1)]
    stored = json.loads(DATA.read_text()) if DATA.exists() else {"offsets": {}}
    timeline = json.loads(TIMELINE.read_text())["days"] if TIMELINE.exists() else {}

    points, offsets = [], stored["offsets"]
    if os.environ.get("STRAVA_REFRESH_TOKEN"):
        points += strava_points(first)
    if os.environ.get("GARMIN_TOKENS"):
        get = garmin_activity.client(garmin_activity.access_token())
        points += garmin_points(get, first, today)
        offsets = garmin_offsets(get, days, offsets)
    known = {}
    for day, codes in timeline.items():
        if day >= days[0]:
            # An emptied day still counts as known (home), so trips don't spill into it.
            kept = ["IL" if code in HOME else code for code in codes if plausible(code, day, offsets.get(day))]
            known[day] = list(dict.fromkeys(kept))
    for moment, lat, lng in sorted(points):
        code = country(lat, lng)
        code = "IL" if code in HOME else code
        if code and code not in known.setdefault(moment[:10], []):
            known[moment[:10]].append(code)

    resolved, abroad = resolve(days, known, offsets)
    visited = sorted({code for codes in resolved.values() for code in foreign(codes)})
    download_flags(visited)

    cutoff = (today - timedelta(days=KEEP_DAYS)).isoformat()
    result = {
        "days": {day: codes for day, codes in resolved.items() if foreign(codes)},
        "abroad": abroad,
        "offsets": {day: value for day, value in sorted(offsets.items()) if day >= cutoff},
    }
    if {key: stored.get(key) for key in result} != result:
        DATA.write_text(json.dumps({"updated": datetime.now().isoformat(timespec="minutes"), **result}, indent=1) + "\n")
    print(f"Travel: {len(result['days'])} days in {', '.join(visited) or 'no countries'}, "
          f"{len(abroad)} days abroad in an unknown country")


if __name__ == "__main__":
    sys.exit(main())
