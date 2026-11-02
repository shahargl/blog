"""GitHub and Strava activity heatmaps, fetched at build time and rendered as SVG."""

import json
import os
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

CACHE = Path(__file__).resolve().parent / ".cache" / "heatmaps.json"
CACHE_TTL = 3600
WEEKS = 53


class NotConfigured(Exception):
    pass


GITHUB_LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def request_json(url, *, data=None, headers=None):
    body = json.dumps(data).encode() if data is not None else None
    request = urllib.request.Request(url, data=body, headers={"User-Agent": "shahar.blog", **(headers or {})})
    if body is not None:
        request.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def fetch_github(login):
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise NotConfigured("GITHUB_TOKEN is not set")
    query = """query($login: String!) { user(login: $login) { contributionsCollection { contributionCalendar {
        totalContributions weeks { contributionDays { date contributionCount contributionLevel } } } } } }"""
    result = request_json(
        "https://api.github.com/graphql",
        data={"query": query, "variables": {"login": login}},
        headers={"Authorization": f"Bearer {token}"},
    )
    if result.get("errors"):
        raise RuntimeError(result["errors"][0]["message"])
    calendar = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = {
        day["date"]: {"count": day["contributionCount"], "level": GITHUB_LEVELS[day["contributionLevel"]]}
        for week in calendar["weeks"]
        for day in week["contributionDays"]
    }
    return {"total": calendar["totalContributions"], "days": days}


def strava_access_token():
    names = ("STRAVA_CLIENT_ID", "STRAVA_CLIENT_SECRET", "STRAVA_REFRESH_TOKEN")
    missing = [name for name in names if not os.environ.get(name)]
    if missing:
        raise NotConfigured(f"{', '.join(missing)} not set")
    result = request_json(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": os.environ["STRAVA_CLIENT_ID"],
            "client_secret": os.environ["STRAVA_CLIENT_SECRET"],
            "grant_type": "refresh_token",
            "refresh_token": os.environ["STRAVA_REFRESH_TOKEN"],
        },
    )
    return result["access_token"]


def fetch_strava(today):
    headers = {"Authorization": f"Bearer {strava_access_token()}"}
    athlete = request_json("https://www.strava.com/api/v3/athlete", headers=headers)
    after = datetime.combine(today - timedelta(weeks=WEEKS, days=7), datetime.min.time(), timezone.utc)
    activities, page = [], 1
    while True:
        params = urllib.parse.urlencode({"after": int(after.timestamp()), "per_page": 200, "page": page})
        batch = request_json(f"https://www.strava.com/api/v3/athlete/activities?{params}", headers=headers)
        if not batch:
            break
        activities += batch
        page += 1

    days = {}
    for activity in activities:
        day = days.setdefault(activity["start_date_local"][:10], {"count": 0, "km": 0.0, "types": []})
        day["count"] += 1
        day["km"] += activity.get("distance", 0) / 1000
        sport = activity.get("sport_type") or activity.get("type") or "Workout"
        if sport not in day["types"]:
            day["types"].append(sport)
    return {"athlete": athlete["id"], "days": days}


def strava_levels(days):
    distances = sorted(day["km"] for day in days.values() if day["km"] > 0)
    if not distances:
        return
    thresholds = [distances[int(len(distances) * q)] for q in (0.25, 0.5, 0.75)]
    for day in days.values():
        if day["km"] <= 0:
            day["level"] = 1
        else:
            day["level"] = 1 + sum(day["km"] >= threshold for threshold in thresholds)


def load(github_login, timezone_name):
    """Returns cached or freshly fetched heatmap data. Fetch errors raise in CI so a flaky API never ships a missing section."""
    if CACHE.exists() and time.time() - CACHE.stat().st_mtime < CACHE_TTL:
        return json.loads(CACHE.read_text())

    today = datetime.now(ZoneInfo(timezone_name)).date()
    data = {"updated": datetime.now(timezone.utc).isoformat(timespec="minutes"), "today": today.isoformat()}
    for name, fetch in (("github", lambda: fetch_github(github_login)), ("strava", lambda: fetch_strava(today))):
        try:
            data[name] = fetch()
        except Exception as error:
            if os.environ.get("CI") and not isinstance(error, NotConfigured):
                raise
            print(f"skipping {name} heatmap: {error}")
    if "strava" in data:
        strava_levels(data["strava"]["days"])

    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(data))
    return data


# Rendering

CELL, GAP, LEFT, TOP = 10, 3, 28, 16
STEP = CELL + GAP


def calendar_weeks(today):
    start = today - timedelta(days=(WEEKS - 1) * 7)
    start -= timedelta(days=(start.weekday() + 1) % 7)
    weeks, day = [], start
    while day <= today:
        week = []
        for _ in range(7):
            week.append(day if day <= today else None)
            day += timedelta(days=1)
        weeks.append(week)
    return weeks


def svg(weeks, describe, label):
    width = LEFT + len(weeks) * STEP
    height = TOP + 7 * STEP
    parts = [
        f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{escape(label)}">'
    ]

    starts = [c for c, week in enumerate(weeks) if c == 0 or week[0].month != weeks[c - 1][0].month]
    for column in starts:
        if column == 0 and len(starts) > 1 and starts[1] < 3 or column > len(weeks) - 3:
            continue
        parts.append(f'<text x="{LEFT + column * STEP}" y="{TOP - 6}">{weeks[column][0]:%b}</text>')

    for row, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(f'<text x="0" y="{TOP + row * STEP + CELL - 1}">{name}</text>')

    for column, week in enumerate(weeks):
        for row, day in enumerate(week):
            if day is None:
                continue
            level, title = describe(day)
            x, y = LEFT + column * STEP, TOP + row * STEP
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" class="l{level}">'
                f"<title>{escape(title)}</title></rect>"
            )
    parts.append("</svg>")
    return "".join(parts)


def pretty(day):
    return f"{day:%b} {day.day}, {day.year}"


def legend():
    cells = "".join(f'<span class="cell l{level}"></span>' for level in range(5))
    return f'<span class="legend">less {cells} more</span>'


def figure(title, link, svg_markup, summary):
    return (
        f'<figure class="heatmap"><figcaption><a href="{link}">{title}</a></figcaption>'
        f'<div class="heatmap-scroll">{svg_markup}</div>'
        f'<p class="meta heatmap-meta"><span>{summary}</span>{legend()}</p></figure>'
    )


def render(data, github_login):
    if not data or not ({"github", "strava"} & data.keys()):
        return ""
    weeks = calendar_weeks(date.fromisoformat(data["today"]))
    in_range = {day.isoformat() for week in weeks for day in week if day}
    sections = []

    if "github" in data:
        days = data["github"]["days"]

        def describe_github(day):
            entry = days.get(day.isoformat(), {"count": 0, "level": 0})
            noun = "contribution" if entry["count"] == 1 else "contributions"
            return entry["level"], f"{entry['count'] or 'No'} {noun} on {pretty(day)}"

        total = data["github"]["total"]
        sections.append(figure(
            "GitHub",
            f"https://github.com/{github_login}",
            svg(weeks, describe_github, "GitHub contributions over the last year"),
            f"{total:,} contributions in the last year",
        ))

    if "strava" in data:
        days = data["strava"]["days"]

        def describe_strava(day):
            entry = days.get(day.isoformat())
            if not entry:
                return 0, f"No activities on {pretty(day)}"
            noun = "activity" if entry["count"] == 1 else "activities"
            types = ", ".join(entry["types"])
            distance = f", {entry['km']:.1f} km" if entry["km"] > 0 else ""
            return entry["level"], f"{entry['count']} {noun} on {pretty(day)}: {types}{distance}"

        recent = [days[key] for key in in_range if key in days]
        count = sum(day["count"] for day in recent)
        km = sum(day["km"] for day in recent)
        sections.append(figure(
            "Strava",
            f"https://www.strava.com/athletes/{data['strava']['athlete']}",
            svg(weeks, describe_strava, "Strava activities over the last year"),
            f"{count:,} activities, {km:,.0f} km in the last year",
        ))

    updated = datetime.fromisoformat(data["updated"])
    stamp = f"{updated:%b} {updated.day}, {updated.year} {updated:%H:%M} UTC"
    return "".join(sections) + f'<p class="meta">Updated automatically. Last refresh: {stamp}.</p>'
