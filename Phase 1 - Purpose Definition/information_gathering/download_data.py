#!/usr/bin/env python3
"""Download the raw datasets of the Trentino Hikes KG (information gathering).

Run from anywhere:
    python download_data.py            # everything
    python download_data.py osm meteo  # only some groups

Only the Python standard library is needed. Files are written to ./raw/ next
to this script, together with raw/download_log.json (source URL, time, size)
so that the report can state exactly what was downloaded and when.

Groups
  osm     OpenStreetMap via Overpass (several public servers, files already
          downloaded are skipped unless --force): SAT trails (with geometry), points of
          interest, car parks, lifts, municipalities, bus stops
  gtfs    Trentino Trasporti GTFS feeds (extra-urban and urban)
  meteo   Meteotrentino: station catalogue, daily rain / min / max temperature
          (archivio.meteotrentino.it), snow fields (list + last 7 days)
  forecast  meteo.report local forecasts (list of venues + one file per venue)

All sources are CC BY 4.0 (Meteotrentino, Trentino Trasporti) or ODbL (OSM).
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# Windows consoles may not use UTF-8: never crash on a character they cannot show
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(errors="replace")

RAW = Path(__file__).resolve().parent / "raw"
LOG = RAW / "download_log.json"
UA = {"User-Agent": "trentino-hikes-kg (university project, UniTn KG course)"}

# Public Overpass servers, tried in this order; the next one is used when one
# is overloaded (HTTP 429/502/504) or times out. Same OSM data on all of them.
OVERPASS_SERVERS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
AREA = 'area["ISO3166-2"="IT-TN"]->.a;'  # Autonomous Province of Trento

OSM_QUERIES = {
    # SAT trails: tags only (light). Their geometry (needed for start/end points
    # and the "passes near" computations) is too heavy for one query on the
    # public servers, so get_trail_geometry() fetches it in batches by id.
    "osm_trails_sat.json":
        'relation["route"="hiking"]["operator"~"Alpinisti Tridentini"](area.a);'
        "out tags;",
    "osm_poi.json":
        "("
        'nwr["tourism"~"^(alpine_hut|wilderness_hut|viewpoint|attraction)$"](area.a);'
        'nwr["amenity"~"^(restaurant|cafe|bar)$"](area.a);'
        'node["natural"="peak"](area.a);'
        'nwr["water"="lake"](area.a);'
        ");out tags center;",
    "osm_parking.json":
        'nwr["amenity"="parking"](area.a);out tags center;',
    "osm_lifts.json":
        'way["aerialway"~"^(cable_car|gondola|chair_lift|mixed_lift)$"](area.a);'
        "out geom;",
    "osm_lift_stations.json":
        'node["aerialway"="station"](area.a);out tags;',
    "osm_municipalities.json":
        'relation["boundary"="administrative"]["admin_level"="8"](area.a);'
        "out tags center;",
    "osm_bus_stops.json":
        'node["highway"="bus_stop"](area.a);out tags;',
}

GTFS = {
    "gtfs_extraurbano.zip": "https://www.trentinotrasporti.it/opendata/google_transit_extraurbano_tte.zip",
    "gtfs_urbano.zip": "https://www.trentinotrasporti.it/opendata/google_transit_urbano_tte.zip",
}

ARCHIVE = "https://archivio.meteotrentino.it/share/"
# daily series, AI-reconstructed (gap-free) versions of the "Annali" values
DAILY_CODES = {
    "10.75": "daily precipitation mm (09-09)",
    "400.75": "daily minimum temperature C",
    "400.76": "daily maximum temperature C",
}
SNOW = {
    "snow_fields.xml": "https://dati.meteotrentino.it/service.asmx/listaCampiNeve",
    "snow_last7days.xml": "https://dati.meteotrentino.it/service.asmx/tuttiUltimiRilieviNeve",
}
FORECAST_INDEX = "https://meteo.report/open_data/forecasts/trentino.json"


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_log():
    return json.loads(LOG.read_text(encoding="utf-8")) if LOG.exists() else {}


def save_log(log):
    LOG.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")


def fetch(url, data=None, timeout=300, tries=4):
    """GET (or POST when data is given) with simple retries."""
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001 - report and retry
            wait = 20 * (i + 1)
            print(f"   ! {e} - retry in {wait}s" if i < tries - 1 else f"   ! {e}")
            if i == tries - 1:
                raise
            time.sleep(wait)


def save(name, content, url, log, note=""):
    path = RAW / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    log[name] = {"url": url, "downloaded_at": now(), "bytes": len(content), "note": note}
    save_log(log)
    print(f"   saved {name} ({len(content) / 1e6:.1f} MB)")


def overpass(q, rounds=5):
    """Run an Overpass query, trying each server in turn, `rounds` times."""
    data = urllib.parse.urlencode({"data": q}).encode()
    last = None
    for r in range(rounds):
        for server in OVERPASS_SERVERS:
            host = server.split("/")[2]
            try:
                req = urllib.request.Request(server, data=data, headers=UA)
                with urllib.request.urlopen(req, timeout=240) as resp:
                    content = resp.read()
                # an overloaded server may answer 200 with an error remark and partial data
                js = json.loads(content)
                remark = js.get("remark", "")
                if "error" in remark.lower():
                    raise RuntimeError(f"Overpass error: {remark[:200]}")
                # every query of this project has results; an empty answer means the
                # server could not run it (e.g. a mirror without the area index)
                if not js.get("elements"):
                    raise RuntimeError("empty result")
                return content, server
            except Exception as e:  # noqa: BLE001 - report and try the next server
                last = e
                print(f"   ! {host}: {e}")
        if r < rounds - 1:
            wait = min(60 * (r + 1), 180)
            print(f"   all servers failed, new round in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"all Overpass servers failed: {last}")


def get_osm(log, force=False):
    for name, body in OSM_QUERIES.items():
        if (RAW / name).exists() and not force:
            print(f"-> OSM {name}: already downloaded, skipped (use --force to download again)")
            continue
        q = f"[out:json][timeout:180];{AREA}{body}"
        print(f"-> OSM {name}")
        content, server = overpass(q)
        save(name, content, server, log, note=q)
        time.sleep(10)  # be polite to the public Overpass servers
    get_trail_geometry(log, force=force)


GEOM_BATCH = 100  # trails per geometry query


def get_trail_geometry(log, force=False):
    """Geometry of the SAT trails, fetched by relation id in batches.

    Each batch is saved in raw/osm_trails_sat_geom_parts/ as soon as it
    arrives, so an interrupted run continues where it stopped. At the end the
    batches are merged into raw/osm_trails_sat_geom.json and the parts deleted.
    """
    name = "osm_trails_sat_geom.json"
    if (RAW / name).exists() and not force:
        print(f"-> OSM {name}: already downloaded, skipped (use --force to download again)")
        return
    tags = json.loads((RAW / "osm_trails_sat.json").read_text(encoding="utf-8"))["elements"]
    ids = sorted(e["id"] for e in tags)
    parts = RAW / "osm_trails_sat_geom_parts"
    parts.mkdir(exist_ok=True)
    batches = [ids[i:i + GEOM_BATCH] for i in range(0, len(ids), GEOM_BATCH)]
    template = "[out:json][timeout:180];relation(id:<ids>);out skel geom;"
    print(f"-> OSM {name}: {len(ids)} trails in {len(batches)} batches")
    servers = set()
    for i, batch in enumerate(batches, 1):
        part = parts / f"batch_{i:02d}.json"
        if part.exists() and not force:
            continue
        q = template.replace("<ids>", ",".join(map(str, batch)))
        content, server = overpass(q)
        part.write_bytes(content)
        servers.add(server)
        print(f"   batch {i}/{len(batches)} ({len(content) / 1e6:.1f} MB)")
        time.sleep(5)
    elements = []
    for part in sorted(parts.glob("batch_*.json")):
        elements += json.loads(part.read_text(encoding="utf-8"))["elements"]
    missing = set(ids) - {e["id"] for e in elements}
    if missing:
        print(f"   ! {len(missing)} trails without geometry, e.g. {sorted(missing)[:5]}")
    content = json.dumps({"elements": elements}).encode("utf-8")
    save(name, content, ", ".join(sorted(servers)) or "earlier run", log,
         note=f"{template} in batches of {GEOM_BATCH} ids from osm_trails_sat.json")
    for part in parts.glob("batch_*.json"):
        part.unlink()
    parts.rmdir()


def get_gtfs(log):
    for name, url in GTFS.items():
        print(f"-> GTFS {name}")
        save(name, fetch(url), url, log)


def get_meteo(log):
    for cat in ("stations", "variables", "summary", "quality_codes"):
        url = f"{ARCHIVE}catalog/{cat}.json"
        print(f"-> archive {cat}")
        save(f"meteo_{cat}.json", fetch(url), url, log)
    summary = json.loads((RAW / "meteo_summary.json").read_text(encoding="utf-8"))
    files = {a["code"]: a["daily"] for a in summary["aggregates"]}
    for code, desc in DAILY_CODES.items():
        url = ARCHIVE + files[code]
        print(f"-> archive daily {code} ({desc})")
        save(f"meteo_daily_{code}.parquet", fetch(url), url, log, note=desc)
    for name, url in SNOW.items():
        print(f"-> snow {name}")
        save(name, fetch(url), url, log)


def get_forecast(log):
    print("-> forecast venues")
    index = fetch(FORECAST_INDEX)
    save("forecast/venues.json", index, FORECAST_INDEX, log)
    venues = json.loads(index)
    # venue type 8 (hamlets) reuses the file of its municipality: skip duplicates
    urls = sorted({v["url"] for v in venues if v.get("url")})
    print(f"   {len(venues)} venues, {len(urls)} distinct forecast files")
    for i, url in enumerate(urls, 1):
        save(f"forecast/{url.rsplit('/', 2)[-2]}/{url.rsplit('/', 1)[-1]}", fetch(url), url, log)
        if i % 50 == 0:
            print(f"   {i}/{len(urls)}")
        time.sleep(0.2)


GROUPS = {"osm": get_osm, "gtfs": get_gtfs, "meteo": get_meteo, "forecast": get_forecast}

if __name__ == "__main__":
    args = sys.argv[1:]
    force = "--force" in args
    wanted = [a for a in args if a != "--force"] or list(GROUPS)
    unknown = [g for g in wanted if g not in GROUPS]
    if unknown:
        sys.exit(f"unknown group(s) {unknown}; choose from {list(GROUPS)} (and --force)")
    RAW.mkdir(parents=True, exist_ok=True)
    log = load_log()
    for g in wanted:
        if g == "osm":
            get_osm(log, force=force)
        else:
            GROUPS[g](log)
    print(f"done - see {LOG}")
