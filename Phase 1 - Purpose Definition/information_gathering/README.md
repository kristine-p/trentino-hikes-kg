# Information gathering

- `findings.md` – what each data source contains, coverage of the CQs, open decisions
- `download_data.py` – downloads all raw datasets into `raw/` (Python standard library only)
- `profile_data.py` – writes `profile_report.md` with record counts and fill rates
  (needs pandas and pyarrow from the root `requirements.txt` for the Parquet weather files)

## Run
First set up and activate the project environment (root README, "Setup"). Then, from the
repository root:
```
python "Phase 1 - Purpose Definition/information_gathering/download_data.py"          # all: osm gtfs meteo forecast (~10-20 min)
python "Phase 1 - Purpose Definition/information_gathering/download_data.py" meteo    # one group only
python "Phase 1 - Purpose Definition/information_gathering/profile_data.py"
```

OpenStreetMap is queried through public Overpass servers, which are often busy (`HTTP Error 502`,
`Query timed out`). The script then tries the next server, and after a full round waits and tries
again. OSM files that are already in `raw/` are skipped, so if it stops, just run the `osm` group
again; add `--force` to download them all again.

Trail geometry is too heavy for one query, so it is downloaded separately: `osm_trails_sat.json`
holds the trails' tags, and `osm_trails_sat_geom.json` their geometry, fetched by relation id in
batches of 100 (parts are kept in `raw/osm_trails_sat_geom_parts/` until all batches are in, so an
interrupted run continues where it stopped). Join the two files on the relation `id`.

| Script | Input | Output |
|---|---|---|
| `download_data.py` | the online sources listed in the script | `raw/*` (incl. `osm_trails_sat.json` + `osm_trails_sat_geom.json`) and `raw/download_log.json` |
| `profile_data.py` | `raw/*` | `profile_report.md` |

## Reproducibility
`raw/` is not committed (see `.gitignore`); only `raw/download_log.json` is, as the record of the
URL, query, server and time of every file of the snapshot this project uses. `profile_report.md`
(also committed) gives its record counts and fill rates.

The sources change over time, so a new download gives slightly different data. To work on the
project's snapshot, use the cleaned data in the repository; re-run the download only to rebuild it
from scratch or to update it (and then commit the new log and profile report together with it).
Re-running a group overwrites its files; OSM files already in `raw/` are skipped unless `--force`.
