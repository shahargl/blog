#!/usr/bin/env python3
"""Imports a LinkedIn post analytics export into data/linkedin.json.

    python linkedin_import.py [export.xlsx]

Export from linkedin.com/analytics/creator/content (past 365 days, Export).
Without a path, the newest AggregateAnalytics_*.xlsx in ~/Downloads is used.
Days from the new export replace overlapping days, older ones are kept.
"""

import json
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path

DATA = Path(__file__).resolve().parent / "data" / "linkedin.json"
KEEP_DAYS = 400
SHEET = "ENGAGEMENT"
MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def read_sheet(path, name):
    with zipfile.ZipFile(path) as workbook:
        shared = []
        if "xl/sharedStrings.xml" in workbook.namelist():
            root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
            shared = ["".join(text.text or "" for text in item.iter(MAIN + "t")) for item in root]
        rels = ET.fromstring(workbook.read("xl/_rels/workbook.xml.rels"))
        targets = {rel.get("Id"): rel.get("Target").lstrip("/").removeprefix("xl/") for rel in rels}
        sheets = ET.fromstring(workbook.read("xl/workbook.xml")).find(MAIN + "sheets")
        sheet = next((sheet for sheet in sheets if sheet.get("name") == name), None)
        if sheet is None:
            sys.exit(f"{path} has no {name} sheet, is it a LinkedIn post analytics export?")
        rows = ET.fromstring(workbook.read("xl/" + targets[sheet.get(REL)])).find(MAIN + "sheetData")
        result = []
        for row in rows:
            values = []
            for cell in row:
                value = cell.find(MAIN + "v")
                text = value.text if value is not None else "".join(t.text or "" for t in cell.iter(MAIN + "t"))
                values.append(shared[int(text)] if cell.get("t") == "s" else text)
            result.append(values)
        return result


def export_path():
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).expanduser()
    exports = sorted(Path.home().glob("Downloads/AggregateAnalytics_*.xlsx"), key=lambda path: path.stat().st_mtime)
    if not exports:
        sys.exit("no export found in ~/Downloads, pass the path to the .xlsx")
    return exports[-1]


def main():
    path = export_path()
    rows = read_sheet(path, SHEET)
    if rows[0][:3] != ["Date", "Impressions", "Engagements"]:
        sys.exit(f"unexpected {SHEET} columns: {rows[0]}")

    imported = {}
    for row in rows[1:]:
        if len(row) < 3 or not row[0]:
            continue
        day = datetime.strptime(row[0], "%m/%d/%Y").date().isoformat()
        imported[day] = {"engagements": int(row[2] or 0), "impressions": int(row[1] or 0)}

    stored = json.loads(DATA.read_text()) if DATA.exists() else {"days": {}}
    days = stored["days"] | imported
    cutoff = (date.today() - timedelta(days=KEEP_DAYS)).isoformat()
    days = {day: entry for day, entry in sorted(days.items()) if day >= cutoff and (entry["engagements"] or entry["impressions"])}

    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps({"updated": max(imported), "days": days}, indent=1) + "\n")
    total = sum(entry["engagements"] for entry in days.values())
    print(f"LinkedIn: {total:,} engagements across {len(days)} days, through {max(imported)} ({path.name})")


if __name__ == "__main__":
    main()
