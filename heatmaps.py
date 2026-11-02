"""GitHub, Strava, X and LinkedIn activity heatmaps, rendered as SVG at build time.

GitHub, Strava and LinkedIn are fetched on every build (cached locally for an hour).
X comes from data/x.json, which x_activity.py keeps up to date.
"""

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

from icons import icon

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


LINKEDIN_API = "https://api.linkedin.com/rest"
LINKEDIN_VERSION = "202609"
LINKEDIN_METRICS = {"REACTION": "reactions", "COMMENT": "comments", "RESHARE": "reposts"}


class Expired(Exception):
    pass


def linkedin_access_token():
    if os.environ.get("LINKEDIN_REFRESH_TOKEN"):
        body = urllib.parse.urlencode({
            "grant_type": "refresh_token",
            "refresh_token": os.environ["LINKEDIN_REFRESH_TOKEN"],
            "client_id": os.environ.get("LINKEDIN_CLIENT_ID", ""),
            "client_secret": os.environ.get("LINKEDIN_CLIENT_SECRET", ""),
        }).encode()
        request = urllib.request.Request(
            "https://www.linkedin.com/oauth/v2/accessToken",
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "shahar.blog"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)["access_token"]
    if os.environ.get("LINKEDIN_ACCESS_TOKEN"):
        return os.environ["LINKEDIN_ACCESS_TOKEN"]
    raise NotConfigured("LINKEDIN_REFRESH_TOKEN or LINKEDIN_ACCESS_TOKEN not set")


def fetch_linkedin(today):
    headers = {
        "Authorization": f"Bearer {linkedin_access_token()}",
        "Linkedin-Version": LINKEDIN_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
    }
    start = today - timedelta(weeks=WEEKS, days=7)
    end = today + timedelta(days=1)
    date_range = (
        f"(start:(day:{start.day},month:{start.month},year:{start.year}),"
        f"end:(day:{end.day},month:{end.month},year:{end.year}))"
    )
    days = {}
    for metric, field in LINKEDIN_METRICS.items():
        offset = 0
        while True:
            url = (
                f"{LINKEDIN_API}/memberCreatorPostAnalytics?q=me&queryType={metric}&aggregation=DAILY"
                f"&dateRange={date_range}&start={offset}&count=100"
            )
            try:
                page = request_json(url, headers=headers)
            except urllib.error.HTTPError as error:
                if error.code == 401:
                    raise Expired("LinkedIn token expired, run `make linkedin-auth`") from error
                raise
            elements = page.get("elements", [])
            for element in elements:
                begin = element["dateRange"]["start"]
                key = f"{begin['year']}-{begin['month']:02}-{begin['day']:02}"
                day = days.setdefault(key, {"reactions": 0, "comments": 0, "reposts": 0})
                day[field] += element.get("count", 0)
            offset += len(elements)
            if len(elements) < 100:
                break
    for day in days.values():
        day["engagements"] = day["reactions"] + day["comments"] + day["reposts"]
    return {"days": {key: day for key, day in days.items() if day["engagements"]}}


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
        sources = {
            "github": lambda: fetch_github(github_login),
            "strava": lambda: fetch_strava(today),
            "linkedin": lambda: fetch_linkedin(today),
        }
        for name, fetch in sources.items():
            try:
                data[name] = fetch()
            except Expired as error:
                # A lapsed token hides the section instead of blocking every deploy.
                print(f"::warning::{error}" if os.environ.get("CI") else f"skipping {name} heatmap: {error}")
            except Exception as error:
                if os.environ.get("CI") and not isinstance(error, NotConfigured):
                    raise
                print(f"skipping {name} heatmap: {error}")
        if "strava" in data:
            quartile_levels(data["strava"]["days"], "km")
        if "linkedin" in data:
            quartile_levels(data["linkedin"]["days"], "engagements")
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


def profile(entry, heatmap=None):
    caption = f'<a class="profile-link" href="{entry["url"]}">{icon(entry["icon"])}<span>{entry["name"]}</span></a>'
    if heatmap is None:
        return f'<figure class="profile {entry["id"]}"><figcaption>{caption}</figcaption></figure>'
    svg_markup, summary, subtitle = heatmap
    if subtitle:
        caption += f' <span class="heatmap-subtitle">{subtitle}</span>'
    return (
        f'<figure class="profile heatmap {entry["id"]}"><figcaption>{caption}</figcaption>'
        f'<div class="heatmap-scroll">{svg_markup}</div>'
        f'<p class="meta heatmap-meta"><span>{summary}</span>{legend()}</p></figure>'
    )


def github_heatmap(data, weeks, in_range):
    days = data["days"]

    def describe(day):
        entry = days.get(day.isoformat(), {"count": 0, "level": 0})
        return entry["level"], [plural(entry["count"], "contribution") if entry["count"] else "No contributions"]

    summary = f"{data['total']:,} contributions in the last year"
    return svg(weeks, describe, "GitHub contributions over the last year"), summary, None


def strava_heatmap(data, weeks, in_range):
    days = data["days"]

    def row(label, km, seconds, run_pace="", climb=0):
        line = f"{label:<6}{km:>5.1f} km  {run_pace:>8}  {duration(seconds):>7}"
        return line + (f"  +{climb} m" if climb >= 50 else "")

    def describe(day):
        entry = days.get(day.isoformat())
        if not entry:
            return 0, ["Rest day"]
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
    summary = f"{plural(runs, 'run')}, {km:,.0f} km, avg {pace(seconds, km)} in the last year"
    return svg(weeks, describe, "Runs over the last year"), summary, "running"


def x_heatmap(data, weeks, in_range):
    days = data["days"]

    def describe(day):
        entry = days.get(day.isoformat(), {"count": 0, "level": 0})
        return entry["level"], [plural(entry["count"], "post") if entry["count"] else "No posts"]

    posts = sum(days[key]["count"] for key in in_range if key in days)
    return svg(weeks, describe, "Posts on X over the last year"), f"{plural(posts, 'post')} in the last year", None


def linkedin_heatmap(data, weeks, in_range):
    days = data["days"]

    def describe(day):
        entry = days.get(day.isoformat())
        if not entry:
            return 0, ["No engagement"]
        parts = [plural(entry[field], noun) for field, noun in
                 (("reactions", "reaction"), ("comments", "comment"), ("reposts", "repost")) if entry[field]]
        return entry["level"], [plural(entry["engagements"], "engagement"), " · ".join(parts)]

    total = sum(days[key]["engagements"] for key in in_range if key in days)
    summary = f"{plural(total, 'engagement')} in the last year"
    return svg(weeks, describe, "LinkedIn engagement over the last year"), summary, "engagement"


HEATMAPS = {"github": github_heatmap, "strava": strava_heatmap, "x": x_heatmap, "linkedin": linkedin_heatmap}


def render(data, profiles):
    """Every profile becomes a logo link, with its heatmap underneath when there is data for it."""
    weeks = calendar_weeks(date.fromisoformat(data["today"]))
    in_range = {day.isoformat() for week in weeks for day in week if day}
    sections = []
    for entry in profiles:
        source = data.get(entry["id"])
        heatmap = HEATMAPS[entry["id"]](source, weeks, in_range) if source else None
        sections.append(profile(entry, heatmap))

    footer = ""
    if HEATMAPS.keys() & data.keys():
        updated = datetime.fromisoformat(data["updated"])
        stamp = f"{updated:%b} {updated.day}, {updated.year} {updated:%H:%M} UTC"
        footer = f'<p class="meta">Heatmaps update automatically. Last refresh: {stamp}.</p>'
    return f'<div class="profiles">{"".join(sections)}</div>{footer}'
