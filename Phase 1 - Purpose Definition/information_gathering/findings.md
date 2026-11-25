# Information gathering – findings (24 Nov 2026)

How the data was examined: each source was opened and queried directly (Overpass queries on OSM,
the catalogue files of the Meteotrentino archive, the snow and forecast services, the Trentino
Trasporti open data page). `download_data.py` downloads everything into `raw/` and
`profile_data.py` writes `profile_report.md` with fill rates; run both to get the frozen copies
used by the KG and the exact figures for the report.

## Sources

| # | Dataset | Source / format | Licence | Etypes |
|---|---|---|---|---|
| 1 | SAT trails | OSM route relations (`route=hiking`, operator SAT), Overpass JSON | ODbL | Trail, Trailhead, DifficultyLevel |
| 2 | POIs, car parks, lifts, municipalities, bus stops | OSM, Overpass JSON | ODbL | PointOfInterest, CarPark, Lift, Municipality |
| 3 | Public transport | Trentino Trasporti GTFS, extra-urban + urban zip (CSV) | CC BY 4.0 | TransportStop, TransitLine |
| 4 | Weather stations + daily observations | archivio.meteotrentino.it (JSON catalogue, Parquet daily series) | CC BY 4.0 | WeatherStation, DailyObservation |
| 5 | Snow fields | Meteotrentino services `listaCampiNeve`, `tuttiUltimiRilieviNeve` (XML) | CC BY 4.0 | WeatherStation (snow), DailyObservation |
| 6 | Forecasts | meteo.report open data (JSON, one file per location) | CC BY 4.0 | WeatherForecast |
| 7 | Equipment / condition rules | compiled by the team (CAI/SAT, mountain rescue guidance) | own | Equipment, HikingCondition, ExperienceLevel, InclineCategory |

## What the data contains

### 1. SAT trails (OSM)
- 1,657 hiking route relations in the province; **1,133 operated by SAT**.
- SAT fill rates: ref 100%, reg_ref 95%, cai_scale 95%, distance 94%, ascent 92%, descent 92%,
  duration:forward 95%, duration:backward 94%, from/to 96%, **name 39%**, ele:from/ele:to 1%,
  roundtrip 2%. Formats are clean (all durations HH:MM, all distances numeric km).
- Difficulty (SAT): E 784, EE 184, **T only 34**, EEA 71 (stored as EEA:F / EEA:PD / EEA:D / EEA:MD
  = via ferrata grade), missing 60.
- Duration: median 2h10, quartiles 1h15–3h30, max ~8h.
- **Trails are network segments, not hikes**: 599 start and 841 end at a junction with another trail
  ("bivio …"); 504 run junction to junction; only 197 have neither end at a junction.
- Start/end coordinates are not tags: they come from the relation geometry (first/last point).
- No altitude in the tags (ele:from/to 1%); maxAltitudeM and trailhead altitude must be computed.

### 2. Other OSM data (counts in the province)
- Alpine huts 235, wilderness huts (bivacchi) 162, restaurants 1,511, cafés/bars 1,336,
  peaks 1,981, viewpoints 939, lakes 254, attractions 298.
- Car parks 10,859 (7,175 not marked private/customers) – many are small or private.
- Lifts: 207 cable cars / gondolas / chair lifts, 489 lift station nodes.
- Bus stop nodes 4,032 (GTFS is the better source for stops).
- Not yet checked (Overpass was overloaded): opening_hours of huts and lifts, ISTAT codes on
  municipalities → see profile_report.md after running the scripts.

### 3. GTFS (Trentino Trasporti)
- Two feeds (extra-urban, urban), CSV in zip, CC BY 4.0.
- **Current feed: calendar 10 Sep 2026 – 25 Jun 2027** (the website says 31 Aug 2026 – 8 Jun 2027; the data
  is what counts). June 2026 is not covered.

### 4. Weather stations and daily observations (archivio.meteotrentino.it, opened Nov 2026)
- 207 stations (117 active, 85–3,093 m, 42 active stations ≥ 1,500 m), GeoJSON with code, name,
  altitude, active flag, series codes.
- Daily files for all stations up to yesterday: 10.75 daily precipitation, 400.75 / 400.76 daily
  min / max temperature – **gap-free** (missing values reconstructed with AI, flagged by
  quality codes). Times in solar time (UTC+1). Covers both the last 7 days and June 2026.
- Snow is not in the archive.
- The old live service (used by project 7) only returns the last ~40 hours, so it is not used.

### 5. Snow fields
- Last 7 days of manual snow surveys; currently 10 snow fields reporting (season just started).
- Fields (AINEVA codes, Italian): dataMis (date), codStaz (e.g. 8PAN), hs = snow depth cm,
  hn = fresh snow cm, ta/tmin/tmax, … ; "//" = missing.
- Snow field codes differ from station codes (8PAN ↔ T0008 via the station notes); the snow field
  list gives coordinates in UTM → convert to lat/lon.
- **No surveys in summer**: in the June presentation scenario there are no snow observations.

### 6. Forecasts (meteo.report, Euregio)
- Locations: municipalities and passes (type 2), hamlets reusing their municipality's
  forecast (type 8), 28 mountain areas (type 5) with forecasts at 1,500 / 2,000 / 2,500 / 3,000 m.
- **6 days ahead**, daily (1440) and 3-hourly (180) steps. Daily variables: temperature_maximum,
  temperature_minimum, rain_fall, rain_probability, fresh_snow, snow_level, freezing_level,
  sky_condition (letter codes), sunshine_duration, wind_speed, wind_gust, wind_direction.
- **No issue date** in the file, only the forecast window; updated twice a day.

## Coverage of the CQs

| CQ | Covered by | Status |
|---|---|---|
| CQ1, CQ2 level / incline | cai_scale, ascent, distance | ok (T rare: beginners get T + E) |
| CQ3 near me / near a place | trail geometry, POIs | ok (computed distance) |
| CQ4 lift up, hike down | lifts geometry + trail ends, ascent/descent | ok, lift seasons to check |
| CQ5 duration, length, ascent, descent | duration, distance, ascent, descent | ok (~92–95%) |
| CQ6 hut / restaurant on the way | POIs + trail geometry | ok (computed) |
| CQ7 car park, back to the car | car parks, trail ends, roundtrip/out-and-back | ok; trail segments are the main issue |
| CQ8 public transport from/to Trento | GTFS stops + lines | ok for live; June 2026 timetable missing |
| CQ9 equipment | cai_scale → team rules | ok |
| CQ10 clothing today | forecast (incl. altitude levels, freezing level) + altitude | altitude to compute |
| CQ11 recent rain / snow | archive daily rain; snow fields; forecast fresh_snow | rain ok; snow winter only |
| CQ12 combined | all | ok once the above are solved |

## Decisions to take (team)
1. **Trail segments.** Options: (a) a "hike" is a SAT trail with at least one end not at a
   junction (~629 trails) and can be walked out-and-back; (b) chain segments into longer hikes
   (much more work). Suggested: (a), chaining as a future improvement.
2. **Trail name.** Only 39% named → display name "SAT 420A: Le Laste – Trincee" built from
   ref, from and to.
3. **Altitude.** Not in the tags. Options: elevation service / digital terrain model on the start,
   end and highest point; or drop maxAltitudeM and use the forecast mountain levels. Needed for
   CQ10 and for picking the nearest station at a similar altitude.
4. **Difficulty levels.** Keep T, E, EE, EEA as DifficultyLevel; store the via ferrata grade
   (F, PD, D, MD) as an attribute of EEA trails.
5. **Forecast storage** (teacher's question 4): keep only the latest forecast per location and day;
   issueDate = download time (the source has none). The forecast refers to a forecast location
   (municipality, pass or mountain area + altitude level), not always a municipality → either a
   ForecastLocation etype or link only municipality forecasts and use mountain areas for altitude.
6. **Observations.** One DailyObservation per station per day from the archive (rain, min, max
   temperature); snow surveys as DailyObservation of snow fields (snow depth, fresh snow).
   Use the gap-free series and keep the quality code.
7. **Snow in June.** No snow observations in summer → CQ11 in the demo answers on rain, and on the
   forecast fresh_snow / snow_level for high trails.
8. **GTFS for June 2026.** Use the current feed for stops and lines (only the existence of a line is
   used) and state it, or look for an archived summer 2026 feed.
9. **Car parks.** Keep only public car parks (access not private/customers) within the trailhead
   distance.
10. **Model size.** All 16 etypes have data (or are team-defined); no etype has to be cut.

## Additional source checked: visittrentino.info (24 Nov 2026)
- 1,574 curated hikes ("tours") with filters on difficulty, duration, distance, ascent and features.
  Each tour: status open/closed, difficulty (e.g. T1 Easy) and overall difficulty, distance, duration,
  ascent, descent, highest and lowest point, properties (round trip, family-friendly,
  public-transport-friendly, refreshment stops, scenic, …), author's equipment advice, directions,
  start-point weather, GPX/KML export. Tours are **whole hikes** (loops or A→B), not SAT segments.
- Source: Outdooractive project `api-trentino`, content © Trentino Marketing / local tourist boards.
  No open licence found; the data is served with the site's own API key → **not reusable as a dataset
  without permission**.
- Possible uses:
  1. Language: their terms (round trip, family-friendly, public-transport-friendly, refreshment stops,
     T1–T6 difficulty, schema.org `SportsActivityLocation`) as alignment candidates in Phase 2.
  2. Knowledge: safety guidance for the Equipment / HikingCondition rules (layering, check the forecast
     48 h before, match the hike to the least experienced member), cited as a source.
  3. Validation: compare durations / difficulty of a few well-known hikes with our KG.
  4. Data: only with permission (ask the teacher / Trentino Marketing for Outdooractive API access).
- Avalanche bulletin: linked from visittrentino to the Euregio service (avalanche.report), daily
  bulletins as CAAMLv6 JSON; winter only, so outside the summer scope → future improvement for
  live mode in winter (licence to confirm).

## Profile results (download of 25 Nov 2026, `profile_report.md`)
Exact figures of the frozen snapshot in `raw/` (sources and times in `raw/download_log.json`).

| Dataset | Records | Notes |
|---|---|---|
| SAT trails | 1,128 (1,127 with geometry, 456,079 points) | cai_scale/distance 95%, ascent/descent 93%, duration 94–95%, name 39%; endpoints: 507 junction–junction, 434 one end at a junction, 187 none |
| POIs | peaks 1,975; restaurants 1,379 (+ ~90 inside hotels etc.); viewpoints 939; bars 712; cafés 613; attractions 298; lakes 251; alpine huts 235; bivouacs 162 | huts: ele 74%, opening_hours 17% |
| Car parks | 10,859 | access: none 4,169, yes 2,768, private 1,927, customers 1,757, other 238; name 4%, fee 40%, capacity 16% |
| Lifts | 207 (136 chair lifts, 56 gondolas, 15 cable cars); 489 station nodes | opening_hours 3%, foot 0%; stations: ele 17% |
| Municipalities | 166 | ISTAT code and population 100% (complete) |
| GTFS extra-urban | 2,857 stops, 121 routes (120 bus, 1 rail) | calendar 10 Sep 2026 – 25 Jun 2027 |
| GTFS urban | 1,116 stops, 44 routes (43 bus, 1 cable car Trento–Sardagna) | calendar 10 Sep 2026 – 8 Jun 2027 |
| Weather stations | 207 (117 active, 85–3,093 m), 108 active with daily rain | |
| Daily rain / tmin / tmax | 2.95 M / 2.13 M / 2.13 M rows (1920 → 24 Nov 2026) | last 7 days ≈ 120 stations; 15–30 Jun 2026 ≈ 106 stations; value columns min/mean/max/sum + quality code |
| Snow fields | 55 fields; 38 surveys from 12 fields in the last 7 days | coordinates UTM, **utmlat/utmlon labels swapped** |
| Forecasts | 320 locations (184 municipalities/passes, 28 mountain areas, 108 hamlets), 212 files | 6 days, 12 daily variables |

### Cleaning notes for Phase 2
- Durations `05.00`, `08.00` → `05:00`, `08:00`.
- POI type: classify by `amenity` (restaurant, bar, cafe) before `tourism`, so restaurants inside hotels are not lost; map odd values (`yes`, `Apres_Ski,_Caffe`).
- Snow fields: `utmlat` holds the easting and `utmlon` the northing; convert UTM → lat/lon.
- Car parks: drop access private/customers/no/permit/residents; generate display names.
- Trail without geometry: relation 2168823 – check (probably a route made of other routes).
- Daily rain value = column `sum`; temperatures = `min`/`max` of their series; keep `quality`.

### New consequences for the model
- CQ4: lift opening times (3%), foot passengers (0%) and station altitude (17%) are rarely mapped →
  assume gondolas/cable cars carry hikers in summer; chair lifts flagged "check locally".
- `osm_bus_stops.json` is not needed: GTFS has 3,973 stops linked to lines.
- **Demo date:** the GTFS feed starts on 10 Sep 2026 → option to move the presentation scenario
  from late June to mid-September 2026 (still hiking season; GTFS, weather history and forecast
  format available) instead of looking for an archived summer feed.
