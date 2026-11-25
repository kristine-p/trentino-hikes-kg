#!/usr/bin/env python3
"""Profile the raw datasets downloaded by download_data.py.

    python profile_data.py

Writes profile_report.md next to this script: for every dataset, the number
of records, the fields that matter for the CQs and how often they are filled.
Standard library only, except the daily weather files (Parquet), which need
pandas + pyarrow; without them that part is skipped with a note.
"""
import csv
import io
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path

# Windows consoles may not use UTF-8: never crash on a character they cannot show
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
OUT = HERE / "profile_report.md"
lines = []


def out(s=""):
    print(s)
    lines.append(s)


def osm(name):
    p = RAW / name
    return json.loads(p.read_text(encoding="utf-8"))["elements"] if p.exists() else None


def fill(elements, keys):
    n = len(elements) or 1
    return " | ".join(f"{k} {100 * sum(1 for e in elements if e.get('tags', {}).get(k)) / n:.0f}%" for k in keys)


def dist(elements, key, top=12):
    c = Counter(e.get("tags", {}).get(key, "-") for e in elements)
    return ", ".join(f"{k}: {v}" for k, v in c.most_common(top))


def section(title):
    out()
    out(f"## {title}")


# --------------------------------------------------------------------- trails
section("Trails (OSM, SAT route relations)")
T = osm("osm_trails_sat.json")
if T is None:
    out("not downloaded")
else:
    out(f"- trails: {len(T)}")
    out(f"- fill rate: {fill(T, ['ref', 'reg_ref', 'name', 'cai_scale', 'distance', 'ascent', 'descent', 'duration:forward', 'duration:backward', 'from', 'to', 'roundtrip', 'ele:from', 'ele:to'])}")
    out(f"- cai_scale: {dist(T, 'cai_scale')}")
    junction = re.compile(r"bivio|incrocio", re.I)
    ends = Counter()
    for e in T:
        f = bool(junction.search(e["tags"].get("from", "")))
        t = bool(junction.search(e["tags"].get("to", "")))
        ends["both ends at a junction" if f and t else "one end at a junction" if f or t else "no end at a junction"] += 1
    out(f"- endpoints: {dict(ends)}")
    G = osm("osm_trails_sat_geom.json")
    if G is None:
        out("- geometry: not downloaded (osm_trails_sat_geom.json)")
    else:
        with_geom = {e["id"] for e in G if any(m.get("geometry") for m in e.get("members", []))}
        pts = sum(len(m.get("geometry") or []) for e in G for m in e.get("members", []))
        out(f"- with geometry: {len(with_geom)} of {len(T)} trails ({pts:,} points)")
    bad = [e["tags"]["duration:forward"] for e in T if e["tags"].get("duration:forward") and not re.fullmatch(r"\d{1,2}:\d{2}", e["tags"]["duration:forward"])]
    out(f"- durations not in HH:MM: {len(bad)} {bad[:5]}")

# ----------------------------------------------------------------------- POIs
section("Points of interest (OSM)")
P = osm("osm_poi.json")
if P is None:
    out("not downloaded")
else:
    def poi_type(t):
        return t.get("amenity") or t.get("tourism") or ("peak" if t.get("natural") == "peak" else None) or ("lake" if t.get("water") == "lake" else "other")
    groups = {}
    for e in P:
        groups.setdefault(poi_type(e.get("tags", {})), []).append(e)
    for k, g in sorted(groups.items(), key=lambda x: -len(x[1])):
        out(f"- {k}: {len(g)} | {fill(g, ['name', 'ele', 'opening_hours', 'website'])}")

# -------------------------------------------------------------------- parking
section("Car parks (OSM)")
C = osm("osm_parking.json")
if C is None:
    out("not downloaded")
else:
    out(f"- car parks: {len(C)}")
    out(f"- access: {dist(C, 'access')}")
    out(f"- parking type: {dist(C, 'parking')}")
    out(f"- fill rate: {fill(C, ['name', 'fee', 'capacity', 'access'])}")

# ---------------------------------------------------------------------- lifts
section("Lifts (OSM aerialways)")
L = osm("osm_lifts.json")
if L is None:
    out("not downloaded")
else:
    out(f"- lifts: {len(L)} | types: {dist(L, 'aerialway')}")
    out(f"- fill rate: {fill(L, ['name', 'opening_hours', 'aerialway:occupancy', 'aerialway:duration', 'foot', 'operator'])}")
    S = osm("osm_lift_stations.json") or []
    out(f"- lift station nodes: {len(S)} | fill rate: {fill(S, ['name', 'ele'])}")

# ------------------------------------------------------------- municipalities
section("Municipalities (OSM admin_level 8)")
M = osm("osm_municipalities.json")
if M is None:
    out("not downloaded")
else:
    out(f"- municipalities: {len(M)} | {fill(M, ['name', 'ref:ISTAT', 'ele', 'population'])}")

# ----------------------------------------------------------------------- GTFS
section("Public transport (Trentino Trasporti GTFS)")
for name in ("gtfs_extraurbano.zip", "gtfs_urbano.zip"):
    p = RAW / name
    if not p.exists():
        out(f"- {name}: not downloaded")
        continue
    with zipfile.ZipFile(p) as z:
        files = z.namelist()

        def rows(f):
            if f not in files:
                return []
            return list(csv.DictReader(io.TextIOWrapper(z.open(f), encoding="utf-8-sig")))
        stops, routes, cal = rows("stops.txt"), rows("routes.txt"), rows("calendar.txt")
        out(f"- {name}: files {files}")
        out(f"  - stops: {len(stops)} | fields: {list(stops[0]) if stops else []}")
        out(f"  - routes: {len(routes)} | route_type: {dict(Counter(r.get('route_type') for r in routes))}")
        if routes:
            out(f"  - route example: { {k: routes[0][k] for k in list(routes[0])[:6]} }")
        if cal:
            out(f"  - calendar: {min(c['start_date'] for c in cal)} - {max(c['end_date'] for c in cal)}")

# ---------------------------------------------------------------------- meteo
section("Weather stations and daily observations (Meteotrentino archive)")
sp = RAW / "meteo_stations.json"
if not sp.exists():
    out("not downloaded")
else:
    st = [f["properties"] | {"lon": f["geometry"]["coordinates"][0], "lat": f["geometry"]["coordinates"][1]}
          for f in json.loads(sp.read_text(encoding="utf-8"))["features"]]
    act = [s for s in st if s["active"]]
    out(f"- stations: {len(st)}, active: {len(act)}, active altitude range: {min(s['alt'] for s in act)}-{max(s['alt'] for s in act)} m")
    out(f"- active with daily rain series: {sum('10.50' in s['codes'] for s in act)}")
    try:
        import pandas as pd
        for code in ("10.75", "400.75", "400.76"):
            p = RAW / f"meteo_daily_{code}.parquet"
            if not p.exists():
                continue
            df = pd.read_parquet(p)
            out(f"- daily {code}: {len(df)} rows, columns {list(df.columns)}")
            tcol = next((c for c in df.columns if "date" in c.lower() or "time" in c.lower()), None)
            if tcol:
                d = pd.to_datetime(df[tcol])
                recent = df[d >= d.max() - pd.Timedelta(days=7)]
                june = df[(d >= "2026-06-15") & (d <= "2026-06-30")]
                out(f"  - from {d.min()} to {d.max()}; last 7 days: {len(recent)} rows; 15-30 June 2026: {len(june)} rows")
            out(f"  - sample: {df.head(3).to_dict('records')}")
    except ImportError:
        out("- daily Parquet files not profiled: install pandas and pyarrow")

section("Snow fields (Meteotrentino)")
for name in ("snow_fields.xml", "snow_last7days.xml"):
    p = RAW / name
    if not p.exists():
        out(f"- {name}: not downloaded")
        continue
    root = ET.parse(p).getroot()
    recs = list(root)
    strip = lambda t: t.split("}")[-1]  # noqa: E731
    out(f"- {name}: {len(recs)} records, fields {[strip(c.tag) for c in recs[0]] if recs else []}")
    if name == "snow_last7days.xml" and recs:
        vals = [{strip(c.tag): (c.text or "").strip() for c in r} for r in recs]
        out(f"  - snow fields reporting: {len({v['codStaz'] for v in vals})}, dates: {sorted({v['dataMis'][:10] for v in vals})}")
    elif recs:
        out(f"  - example: { {strip(c.tag): (c.text or '').strip() for c in recs[0]} }")

# ------------------------------------------------------------------- forecast
section("Forecasts (meteo.report)")
vp = RAW / "forecast" / "venues.json"
if not vp.exists():
    out("not downloaded")
else:
    venues = json.loads(vp.read_text(encoding="utf-8"))
    out(f"- venues: {len(venues)} | by type: {dict(Counter(v['id_venue_type'] for v in venues))}")
    files = sorted((RAW / "forecast").glob("*/*.json"))
    out(f"- forecast files: {len(files)}")
    if files:
        f = json.loads(files[0].read_text(encoding="utf-8"))
        day = next(iter(f["1440"].values()))
        out(f"- window {f['start']} - {f['end']}; daily steps: {len(f['1440'])}; daily variables: {sorted(day)}")

OUT.write_text("# Raw data profile\n\nGenerated by profile_data.py from the files in raw/ "
               "(see raw/download_log.json for sources and download times).\n" + "\n".join(lines) + "\n", encoding="utf-8")
print(f"\nwritten {OUT}")
