"""GitHub, Strava and X activity heatmaps, rendered as SVG at build time.

GitHub and Strava are fetched on every build (cached locally for an hour).
X comes from data/x.json, which x_activity.py keeps up to date.
"""

import json
import os
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / ".cache" / "heatmaps.json"
X_DATA = ROOT / "data" / "x.json"
CACHE_TTL = 3600
WEEKS = 53
RUN_TYPES = {"Run", "TrailRun", "VirtualRun"}


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
    for activity in sorted(activities, key=lambda activity: activity["start_date_local"]):
        sport = activity.get("sport_type") or activity.get("type")
        if sport not in RUN_TYPES or not activity.get("distance"):
            continue
        day = days.setdefault(activity["start_date_local"][:10], {"runs": []})
        day["runs"].append({
            "type": sport,
            "km": round(activity["distance"] / 1000, 2),
            "seconds": activity.get("moving_time", 0),
            "climb": round(activity.get("total_elevation_gain") or 0),
        })
    for day in days.values():
        day["km"] = round(sum(run["km"] for run in day["runs"]), 2)
        day["seconds"] = sum(run["seconds"] for run in day["runs"])
    return {"athlete": athlete["id"], "days": days}


def quartile_levels(days, key):
    values = sorted(day[key] for day in days.values() if day[key] > 0)
    if not values:
        return
    thresholds = [values[int(len(values) * q)] for q in (0.25, 0.5, 0.75)]
    for day in days.values():
        day["level"] = 1 + sum(day[key] >= threshold for threshold in thresholds) if day[key] > 0 else 0


def load(github_login, timezone_name):
    """Fetch errors raise in CI so a flaky API never ships a missing section."""
    if CACHE.exists() and time.time() - CACHE.stat().st_mtime < CACHE_TTL:
        data = json.loads(CACHE.read_text())
    else:
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
            quartile_levels(data["strava"]["days"], "km")
        CACHE.parent.mkdir(exist_ok=True)
        CACHE.write_text(json.dumps(data))

    if X_DATA.exists():
        x = json.loads(X_DATA.read_text())
        x["days"] = {day: {"count": count} for day, count in x["days"].items()}
        quartile_levels(x["days"], "count")
        data["x"] = x
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
            level, lines = describe(day)
            tip = escape("\n".join([f"{day:%a}, {pretty(day)}", *lines]))
            x, y = LEFT + column * STEP, TOP + row * STEP
            parts.append(f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" class="l{level}" data-tip="{tip}"/>')
    parts.append("</svg>")
    return "".join(parts)


def pretty(day):
    return f"{day:%b} {day.day}, {day.year}"


def duration(seconds):
    hours, rest = divmod(round(seconds), 3600)
    minutes, seconds = divmod(rest, 60)
    return f"{hours}:{minutes:02}:{seconds:02}" if hours else f"{minutes}:{seconds:02}"


def pace(seconds, km):
    return f"{duration(seconds / km)} /km" if km else "-"


def plural(count, noun):
    return f"{count:,} {noun}" if count == 1 else f"{count:,} {noun}s"


def legend():
    cells = "".join(f'<span class="cell l{level}"></span>' for level in range(5))
    return f'<span class="legend">less {cells} more</span>'


def figure(kind, title, link, svg_markup, summary, subtitle=None):
    caption = f'<a href="{link}">{title}</a>'
    if subtitle:
        caption += f' <span class="heatmap-subtitle">{subtitle}</span>'
    return (
        f'<figure class="heatmap {kind}"><figcaption>{caption}</figcaption>'
        f'<div class="heatmap-scroll">{svg_markup}</div>'
        f'<p class="meta heatmap-meta"><span>{summary}</span>{legend()}</p></figure>'
    )


def render(data, github_login):
    if not data or not ({"github", "strava", "x"} & data.keys()):
        return ""
    weeks = calendar_weeks(date.fromisoformat(data["today"]))
    in_range = {day.isoformat() for week in weeks for day in week if day}
    sections = []

    if "github" in data:
        days = data["github"]["days"]

        def describe_github(day):
            entry = days.get(day.isoformat(), {"count": 0, "level": 0})
            return entry["level"], [plural(entry["count"], "contribution") if entry["count"] else "No contributions"]

        sections.append(figure(
            "github",
            "GitHub",
            f"https://github.com/{github_login}",
            svg(weeks, describe_github, "GitHub contributions over the last year"),
            f"{data['github']['total']:,} contributions in the last year",
        ))

    if "strava" in data:
        days = data["strava"]["days"]

        def describe_strava(day):
            entry = days.get(day.isoformat())
            if not entry:
                return 0, ["Rest day"]
            def row(label, km, seconds, run_pace="", climb=0):
                line = f"{label:<6}{km:>5.1f} km  {run_pace:>8}  {duration(seconds):>7}"
                return line + (f"  +{climb} m" if climb >= 50 else "")

            lines = [
                row("Trail" if run["type"] == "TrailRun" else "Run", run["km"], run["seconds"],
                    pace(run["seconds"], run["km"]), run["climb"])
                for run in entry["runs"]
            ]
            if len(entry["runs"]) > 1:
                lines.append(row("Total", entry["km"], entry["seconds"], pace(entry["seconds"], entry["km"])))
            return entry["level"], lines

        recent = [days[key] for key in in_range if key in days]
        runs = sum(len(day["runs"]) for day in recent)
        km = sum(day["km"] for day in recent)
        seconds = sum(day["seconds"] for day in recent)
        sections.append(figure(
            "strava",
            "Strava",
            f"https://www.strava.com/athletes/{data['strava']['athlete']}",
            svg(weeks, describe_strava, "Runs over the last year"),
            f"{plural(runs, 'run')}, {km:,.0f} km, avg {pace(seconds, km)} in the last year",
            subtitle="running",
        ))

    if "x" in data:
        days = data["x"]["days"]

        def describe_x(day):
            entry = days.get(day.isoformat(), {"count": 0, "level": 0})
            return entry["level"], [plural(entry["count"], "post") if entry["count"] else "No posts"]

        posts = sum(days[key]["count"] for key in in_range if key in days)
        sections.append(figure(
            "x",
            "X",
            f"https://x.com/{data['x']['username']}",
            svg(weeks, describe_x, "Posts on X over the last year"),
            f"{plural(posts, 'post')} in the last year",
        ))

    updated = datetime.fromisoformat(data["updated"])
    stamp = f"{updated:%b} {updated.day}, {updated.year} {updated:%H:%M} UTC"
    return "".join(sections) + f'<p class="meta">Updated automatically. Last refresh: {stamp}.</p>'
