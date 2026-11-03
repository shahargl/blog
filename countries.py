"""Offline coordinate to country lookup against data/borders.json.

The borders are Natural Earth's 1:50m admin-0 countries (public domain), outer
rings only, rounded to 0.01 degrees.
"""

import json
import os
from functools import cache
from pathlib import Path

BORDERS = Path(__file__).resolve().parent / "data" / "borders.json"
# Coastlines at this scale cut off beaches and harbours, so nearby points are tried too.
# Optional "AA=BB,CC=DD" mapping, kept in the environment rather than the public repo.
RELABEL = dict(pair.split("=") for pair in os.environ.get("COUNTRY_RELABEL", "").split(",") if "=" in pair)
NEARBY = [(dy, dx) for step in (0.02, 0.05, 0.1, 0.2) for dy in (-step, 0, step) for dx in (-step, 0, step) if dy or dx]


@cache
def polygons():
    result = []
    for code, country in json.loads(BORDERS.read_text()).items():
        for ring in country["polygons"]:
            xs, ys = [x for x, _ in ring], [y for _, y in ring]
            area = (max(xs) - min(xs)) * (max(ys) - min(ys))
            result.append((area, (min(xs), min(ys), max(xs), max(ys)), ring, code))
    # Smallest first, so enclaves win over the country around them.
    result.sort(key=lambda item: item[0])
    return result


@cache
def names():
    return {code: country["name"] for code, country in json.loads(BORDERS.read_text()).items()}


def inside(ring, x, y):
    hit = False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            hit = not hit
    return hit


def exact(lat, lng):
    for _, (min_x, min_y, max_x, max_y), ring, code in polygons():
        if min_x <= lng <= max_x and min_y <= lat <= max_y and inside(ring, lng, lat):
            return code
    return None


@cache
def country(lat, lng):
    """ISO 3166 alpha-2 code for a coordinate, or None in open water."""
    lat, lng = round(lat, 2), round(lng, 2)
    code = exact(lat, lng)
    for dy, dx in NEARBY:
        if code:
            break
        code = exact(lat + dy, lng + dx)
    return RELABEL.get(code, code)


def name(code):
    return names().get(code, code)
