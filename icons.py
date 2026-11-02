"""Inline SVG icons from assets/icons (Bootstrap Icons, MIT licensed)."""

import re
from functools import cache
from pathlib import Path

ICONS = Path(__file__).resolve().parent / "assets" / "icons"


@cache
def icon(name, css_class="icon"):
    markup = (ICONS / f"{name}.svg").read_text().strip()
    markup = re.sub(r'\s(width|height|class)="[^"]*"', "", markup)
    return markup.replace("<svg", f'<svg class="{css_class}" aria-hidden="true" focusable="false"', 1)
