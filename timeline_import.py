#!/usr/bin/env python3
"""Imports a Google Maps Timeline export into data/timeline.json, one list of countries per day.

    python timeline_import.py [Timeline.json]

Export it on the phone: Google Maps, Settings, Personal content, Export Timeline data.
Without a path, ~/Downloads/Timeline.json is used. Only country codes are kept, never
coordinates. Days from the new export replace overlapping days, older ones are kept.
"""

import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from countries import country

DATA = Path(__file__).resolve().parent / "data" / "timeline.json"
KEEP_DAYS = 400
# A day's country needs this much weight (hours of visits, or ten path points per hour).
MIN_WEIGHT = 0.3


def coordinates(text):
    lat, lng = text.removeprefix("geo:").replace("°", "").split(",")
    return float(lat), float(lng)


def samples(segment):
    """(local time, weight, coordinate) for each location in a Timeline segment."""
    start, end = datetime.fromisoformat(segment["startTime"]), datetime.fromisoformat(segment["endTime"])
    if "visit" in segment:
        location = segment["visit"]["topCandidate"].get("placeLocation")
        if location:
            # Multi-day stays count towards every day they cover.
            moment = start
            while moment < end:
                midnight = datetime.combine(moment.date() + timedelta(days=1), datetime.min.time(), moment.tzinfo)
                until = min(end, midnight)
                yield moment, (until - moment).total_seconds() / 3600, location
                moment = until
    elif "activity" in segment:
        for key, moment in (("start", start), ("end", end)):
            if segment["activity"].get(key):
                yield moment, 0.5, segment["activity"][key]
    elif "timelinePath" in segment:
        for point in segment["timelinePath"]:
            yield start + timedelta(minutes=int(point["durationMinutesOffsetFromStartTime"])), 0.1, point["point"]


def main():
    path = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.home() / "Downloads" / "Timeline.json"
    segments = json.loads(path.read_text())
    if isinstance(segments, dict):
        segments = segments.get("semanticSegments", [])
    cutoff = date.today() - timedelta(days=KEEP_DAYS)

    weights, first_seen = {}, {}
    for segment in segments:
        if datetime.fromisoformat(segment["endTime"]).date() < cutoff:
            continue
        for moment, weight, location in samples(segment):
            code = country(*coordinates(location))
            if not code:
                continue
            day = moment.date().isoformat()
            weights.setdefault(day, {}).setdefault(code, 0)
            weights[day][code] += weight
            first_seen.setdefault((day, code), moment)

    imported = {}
    for day, by_country in weights.items():
        kept = [code for code, weight in by_country.items() if weight >= MIN_WEIGHT] or [max(by_country, key=by_country.get)]
        imported[day] = sorted(kept, key=lambda code: first_seen[(day, code)])

    stored = json.loads(DATA.read_text()) if DATA.exists() else {"days": {}}
    days = {day: value for day, value in sorted((stored["days"] | imported).items()) if day >= cutoff.isoformat()}
    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps({"updated": max(imported), "days": days}, indent=1) + "\n")
    abroad = {code for value in days.values() for code in value} - {"IL", "PS"}
    print(f"Timeline: {len(days)} days through {max(imported)}, countries outside home: {', '.join(sorted(abroad))}")


if __name__ == "__main__":
    main()
