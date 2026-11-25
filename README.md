# Trentino Hikes KG

Knowledge Graph project for the *Knowledge Graphs* course (UniTn, 2026), project proposal no. 12:
**Trentino Hikes, extended with weather information**.

The KG models the hiking trails of Trentino together with nearby points of interest and weather
observations, so that it can answer competency questions such as:

- Where are the main trails around me?
- Which trails are closest to popular tourist destinations?
- Which trail can be done in under N hours?
- What is the elevation of this trail?
- Which trail passes close to a restaurant?
- Which trail had no rain in the last three days? Which trail is covered in snow?

The project follows the **iTelos** methodology. This repository is based on the official
[KG-2026 project template](https://github.com/mayukh-bagchi-research/KG-2026-UniTn-ProjectGitRepoTemplate).

## Repository structure

| Folder | iTelos phase | Contents |
|---|---|---|
| `Phase 1 - Purpose Definition/` | Purpose definition | Scenarios, personas, competency questions, ER model, informal etype/property labels |
| `Phase 2 - Language Definition/` | Language definition | Fixed language terms, alignment to the Language Teleontology (LTLO / UKC), cleaned datasets |
| `Phase 3 - Knowledge Definition/` | Knowledge definition | Teleology (TLO/ETG) built from reference fragments, alignment to the Knowledge Teleontology (KTLO), dataset-to-schema alignment |
| `Phase 4 - Entity Definition/` | Entity definition | Entity identification, data mappings, the final KG (EG) |
| `Evaluation/` | Evaluation | KG statistics, knowledge/data layer metrics, SPARQL queries for the CQs and their results |
| `Metadata/` | Metadata | Metadata for the language, knowledge, data and KG resources |
| `Documentation/` | Report and slides | `report/` = LaTeX project report (also synced to Overleaf), final presentation |

## Data sources

| Data | Source | Licence |
|---|---|---|
| SAT hiking trails | [OpenStreetMap](https://wiki.openstreetmap.org/wiki/Trentino/Sentieri) (Overpass API) | ODbL |
| Points of interest, car parks, lifts, municipalities | OpenStreetMap (Overpass API) | ODbL |
| Public transport stops and lines | [Trentino Trasporti GTFS](https://www.trentinotrasporti.it/it/opendata-it) | CC BY 4.0 |
| Weather stations, daily rain and temperature | [Meteotrentino archive](https://archivio.meteotrentino.it) | CC BY 4.0 |
| Snow fields | [Meteotrentino open data](https://dati.trentino.it/dataset/dati-recenti-dei-campi-neve) | CC BY 4.0 |
| Weather forecasts | [meteo.report open data](https://meteo.report/open_data/forecasts/trentino.json) | CC BY 4.0 |

Details, coverage of the competency questions and open decisions:
`Phase 1 - Purpose Definition/information_gathering/findings.md`.

### Raw data, reproducibility and credits
- The raw downloads are **not in the repository** (`raw/` is in `.gitignore`). Re-create them with
  `download_data.py` (see the README in `Phase 1 - Purpose Definition/information_gathering/`).
- The sources change over time (OpenStreetMap is edited daily, forecasts and snow surveys only cover
  a few days, the GTFS feed is replaced), so a new download gives slightly different data.
  `raw/download_log.json` (committed) records the URL, query and time of every file of the snapshot
  this project uses, and `profile_report.md` its record counts and fill rates. The cleaned data and
  the KG built from that snapshot are the frozen basis of the report.
- Credits, required by the licences for everything published here that is derived from the data:
  - Map data © OpenStreetMap contributors, available under the Open Database License (ODbL);
    published data derived from it must also be under the ODbL.
  - Weather, snow and station data: Provincia Autonoma di Trento – Meteotrentino, CC BY 4.0.
  - Forecasts: meteo.report open data (Euregio weather services), CC BY 4.0.
  - Public transport: Trentino Trasporti S.p.A., CC BY 4.0.

## Setup

The scripts need **Python 3.9 or newer** (check with `python --version` on Windows,
`python3 --version` on macOS). All Python packages are installed in **one virtual environment at
the repository root**. Each person creates their own; `.venv/` is not committed.

**Windows** (PowerShell or Command Prompt, in the repository folder):
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
If PowerShell refuses to run `activate`, run once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

**macOS** (Terminal, in the repository folder):
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Each new session, activate the environment again (second line above); the prompt then starts
with `(.venv)` and the command is `python` on both systems.

### Conventions
- Run scripts from the **repository root**, e.g.
  `python "Phase 1 - Purpose Definition/information_gathering/download_data.py"`.
  Scripts find their own files relative to their own folder, so this works from anywhere.
- A new package goes into `requirements.txt` (with a minimum version) in the same commit as the
  script that uses it; the others then run `pip install -r requirements.txt` again.
- Text files are read and written as **UTF-8** (`encoding="utf-8"`), so the scripts give the same
  result on Windows and macOS.
- Every script that downloads or transforms data is documented in the README of its folder:
  input files, output files and how to run it.

## Building the report

The report in `Documentation/report/` must be compiled with **XeLaTeX** (the `latexmkrc` file sets this).
On Overleaf: Menu → Compiler → XeLaTeX.

## Team

- Team Member 1
- Team Member 2
