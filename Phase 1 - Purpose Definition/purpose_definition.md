# Phase 1 – Purpose Definition

Status (2026-11-07): purpose, domain, scenarios, personas, CQs and the first ER model agreed. Information gathering and the qualitative evaluation are next.

Files in this folder:
- `purpose_definition.md` – this file (working notes of the phase)
- `PFsheet.xlsx` – Purpose Formalization sheet (entity types, properties, focus, CQs)
- `er_diagram.dot` – source of the ER diagram (Graphviz); regenerate with
  `dot -Tpdf er_diagram.dot -o er_diagram.pdf` and `dot -Tpng -Gdpi=150 er_diagram.dot -o er_diagram.png`
- `er_diagram.pdf`, `er_diagram.png` – rendered ER diagram (the PDF is used in the report)

## Abbreviations and terms
- **KG** – Knowledge Graph
- **CQ** – Competency Question: a question, written the way a real user would ask it, that the finished KG must be able to answer. In the Evaluation phase each CQ is turned into a SPARQL query and run on the KG.
- **SAT** – Società degli Alpinisti Tridentini: the Trentino section of the Italian Alpine Club, responsible for the official hiking trail network in Trentino and for numbering and grading its trails.
- **CAI** – Club Alpino Italiano (Italian Alpine Club): defines the official trail difficulty scale used in Italy (T = tourist, E = hiking, EE = expert hikers, EEA = expert hikers with equipment, i.e. via ferrata).
- **OSM** – OpenStreetMap: the free, community-built map of the world.
- **POI** – Point of Interest: a place a hiker might want to visit or find along the way (mountain hut, restaurant, lake, peak, castle, viewpoint).
- **GTFS** – General Transit Feed Specification: the standard open format for public transport stops, lines and timetables.
- **Ascent / descent** – the total metres a trail climbs / descends (elevation gain / loss).
- **Incline** – how steep a trail is, as a category: gentle, moderate or steep.

## Informal purpose
Help hikers in Trentino – especially inexperienced ones – find trails that suit them and prepare for them. Given a user's experience level, incline preference and means of transport (car or public transport), the KG returns suitable trails with: duration, length, ascent and descent; where the trail starts; parking options or how to get there by public transport; huts or restaurants along the way (or advice to pack lunch); the option to take a cable car or lift up and hike mostly downhill; required equipment and clothing recommendations; and warnings about recent heavy rain or snow. Experienced hikers can use the same KG to find trails at their level and choose the maximum ascent and duration they want.

## Domain of interest
- **Space:** Trentino = the Autonomous Province of Trento (whole province, without South Tyrol). SAT trail network and, around it: trail starting points, car parks, huts and restaurants, other points of interest, lifts, public transport stops and lines, weather and snow measuring stations.
- **Time:** everything relative to a **reference date** ("today"): last 7 days of weather/snow measurements + forecast for the reference date (the build downloads ~30 days). Trails, POIs, lifts and car parks are downloaded from OpenStreetMap once, on a fixed date.
  - **Live mode:** reference date = current date, real Meteotrentino forecast.
  - **Presentation scenario:** reference date in late June 2026 (summer season); historical weather/snow, the timetable valid then; the weather observed on the demo day is used as the forecast (past forecasts are not available). The run is frozen for the report.
- Planned extension: planning for a future date; forecasts store both forecastDate and issueDate.

## Scenarios
| ID | Scenario |
|---|---|
| S1 | Find a suitable trail (experience level, incline preference, duration) |
| S2 | Get to the trail (car → trail start + parking; no car → stop + line) |
| S3 | Plan food (hut/restaurant along the trail, otherwise pack lunch) |
| S4 | Prepare gear and clothing (difficulty → equipment; weather + altitude → clothing) |
| S5 | Check conditions (recent heavy rain or snow near the trail) |
| S6 | Trails near a place (user location or attraction); lift up and hike down |

## Personas
| Persona | Profile | Scenarios |
|---|---|---|
| Sofia, 24 (main) | Erasmus student in Trento, beginner, has a car | S1–S5 |
| Jonas, 26 | Beginner in Trento, no car | S1, S2, S4, S5 |
| Giulia, 38 | Parent of two young children | S1, S2, S3, S6 |
| Marco, 45 | Experienced local hiker | S1, S3, S4, S5 |
| Luca, 31 | Tourist information office | S5, S6 |

## Competency questions
| ID | CQ | Scenario | Personas |
|---|---|---|---|
| CQ1 | I'm an inexperienced hiker and don't like steep climbs – which trails suit me? | S1 | Sofia, Jonas, Giulia |
| CQ2 | I'm an experienced hiker – which trails match my level, and how do they compare in ascent and duration? | S1 | Marco |
| CQ3 | Which suitable trails start near me, or near a place I want to visit? | S6 | all, Luca |
| CQ4 | Can I take a cable car or lift up and then hike mostly downhill? | S6 | Sofia, Giulia |
| CQ5 | How long does this trail take, how long is it, and what are its ascent and descent? | S1 | all |
| CQ6 | Is there a hut or restaurant on the way, or should I pack lunch? | S3 | Sofia, Giulia, Marco |
| CQ7 | I have a car – where does the trail start and where can I park? | S2 | Sofia, Giulia, Marco |
| CQ8 | I don't have a car – how do I get to the trail by public transport (which stop, which line)? | S2 | Jonas |
| CQ9 | What equipment do I need for this trail? | S4 | all |
| CQ10 | How should I dress for this trail today, given the forecast and the altitude? | S4 | all |
| CQ11 | Has there been heavy rain or snow near this trail recently – should I be careful? | S5 | all, Luca |
| CQ12 | I'm inexperienced, have a car and don't like steep trails – what are my options today, how long do they take, where do I park, do I need lunch, and what should I wear and bring? | S1–S5 | Sofia |

## Concepts (16 etypes)
- **Core:** Trail, Trailhead, DifficultyLevel, ExperienceLevel, InclineCategory, Equipment
- **Common:** Municipality, CarPark, TransportStop, TransitLine, PointOfInterest, Lift
- **Contextual:** WeatherStation (stationType = weather | snow), DailyObservation, WeatherForecast, HikingCondition

Attributes and relationships: see `er_diagram.png` and Section 3 of the report.

## Decisions (2026-11-07)
- Keep all 16 etypes (each is required by at least one CQ).
- Weather stations and snow measuring sites = one etype with `stationType`.
- Huts, restaurants and attractions = one etype `PointOfInterest` with `poiType`.
- Proximity relationships are computed from coordinates. **Draft distances, to be reviewed after information gathering:** POI along a trail 200 m; car park and public transport stop from a trailhead 500 m; lift top station from a trailhead 300 m.
- User language is modelled as knowledge: ExperienceLevel → suitable DifficultyLevels (beginner → T, E; experienced → EE, EEA); InclineCategory thresholds on ascent per km; HikingCondition rules (variable, operator, threshold, windowDays) → recommended Equipment. Thresholds come from hiking guidelines (CAI, SAT, alpine clubs, mountain rescue) and are documented.

## Planned datasets
1. Trails – SAT trail register / OpenStreetMap hiking routes
2. Points of interest, car parks, lifts – OpenStreetMap
3. Public transport – Trentino Trasporti GTFS (extra-urban; archived versions for the demo date)
4. Weather – Meteotrentino open data (stations, daily measurements, municipality forecasts, CC-BY 4.0)
5. Snow – Meteotrentino snow measuring sites, daily snow depth
6. Equipment & clothing rules – compiled by the team

## Known limitations
- Snow/rain on a trail is estimated from the nearest station, not observed on the trail.
- Public transport access depends on stop–trailhead distance matching.
- Lift opening seasons are poorly recorded in OpenStreetMap.
- Presentation scenario uses the observed weather as the forecast.

## Teacher's answers (meeting, 16 Nov 2026)
The teacher liked the project; general advice: look at the data first, then decide.
1. Scope (12 CQs / 16 etypes / 17 relationships): look at the data before keeping or cutting.
2. Demo mode (June 2026 presentation scenario): allowed. Synthetic data may be generated if needed (label it as synthetic).
3. Reference date: "system variable" (more robust) vs "user-queried date" (simpler). System variable = one stored reference date in the KG that all queries read; user-queried = the date is a parameter written into each query. Leaning towards the system variable (fits live mode + demo mode).
4. How the forecast is stored is really important: decide after seeing Meteotrentino's forecast format (own entity vs attributes; keep old forecasts or only latest; same structure as observations?).
5. Subclasses vs type field for huts/restaurants/attractions: subclasses are more well-behaved, a type field more flexible; see the data and fix the CQs first.
6. Tools: Protégé, GraphDB and similar are preferred.
Not answered / to check: title with "weather"; computed "near" relationships from coordinates.

Next step: information gathering (look at each dataset's fields and completeness against the CQs), then finalize the Phase 1 draft with these answers + the Lecture 15 changes.

## Update of 16 Nov 2026 (after Lecture 15 and the teacher's answers)
- Report sections 1-3 written in the template structure: 1 Introduction, 2 Project Design (2.1 Domain of Interest with geographical, temporal and domain boundaries; 2.2 Informal Purpose), 3 Purpose Definition (3.1 Purpose Formalization: scenarios, personas, CQs, concepts identification, ER model; 3.2 Information Gathering and 3.3 Qualitative Evaluation still to complete).
- Lecture 15 formats applied: one-sentence informal purpose, domain boundaries, first-person scenarios, personas with differentiator / technological resources / needs / purposes / personal information, CQ table with common/core/contextual etype columns, identifying vs descriptive attributes, PFsheet.xlsx.
- Weather window changed: 7 days of past observations (not 30) + forecast for the hike day, aiming at up to 7 days ahead; how far the official forecast goes must be checked in information gathering.
- Teacher: title without "weather" is fine; computed "near" links: try it and see what the data allows.
- Future improvements (opening hours, paying for parking, public transport tickets, getting back) are listed under the domain boundaries in Section 2.
- Persona details added for the L15 format (sex, occupation, education, home town) are placeholders the team can change.

## Review notes and decisions (17–18 Nov 2026)
Coursemate's review of sections 1–3:
1. Difficulty scale: the text sounded as if T/E/EE/EEA "don't help". Clarified: the scale is the basis of the recommendations (difficulty → equipment); the KG shows each level with a plain-language explanation. Introduction already changed in Overleaf (scale "tells an experienced hiker at a glance what a trail demands … but the letters mean little to a beginner"; third paragraph: "the KG uses the difficulty scale as the basis of its recommendations … and explains each level in plain language"). Still to align: 2.2 Informal Purpose, scenario S1, 3.1.4 Concepts, design choices, 3.3.
2. "Let people choose their own starting point": two readings – (a) where the user travels from (already CQ3 "near me"; wording to clarify) or (b) where on the trail they start (SAT trails are segments: either direction, intermediate access points, loops). Ask the coursemate which one; (b) to be decided after seeing how OSM splits SAT trails.

Getting back (decided 18 Nov 2026) – the trail must also allow the user to return:
- By car, the trail end must offer one of: (a) loop, ends at the start; (b) end near the same car park; (c) lift from the end back down towards the car park; (d) bus stop with a line that also stops near the car park; (e) out and back – walk back the same way, duration doubled (simplest, always possible).
- By public transport: Trento is the only origin/destination for now (limitation). Start near a stop on a line from Trento; end near a stop on a line back to Trento.
- Timetables / last connection back stay a future improvement; for now only the existence of a line counts.
- Lines are assumed to run in both directions; check against the GTFS data.
Model changes needed: Trail + isLoop and out-and-back duration (derived); Lift + bottom station location and bottomStationNear → CarPark; TransportStop + locatedIn → Municipality. CQ7 → "where do I park, and how do I get back to my car at the end?"; CQ8 → "how do I get there from Trento, and back?". Update scenario S2, Sofia, Jonas, entity/relationship tables, ER diagram, PFsheet, and move "getting back" (without timetables) from future improvements into scope.
Applied on 18 Nov 2026 to S2.tex, S3.tex, er_diagram (now 19 relationships) and PFsheet.xlsx, together with the difficulty-scale wording in 2.2, S1 scenario, 3.1.4, design choices and 3.3.

## Purpose evolution (for the qualitative evaluation)
- Scenarios: 5 → 6 (car/public transport, gear and clothing, lifts added)
- Personas: 4 → 5 (Jonas, no car, added; Sofia is the main persona)
- CQs: 15 technical CQs → 12 user-phrased CQs; translation from user language moved into the KG
- Time scope: presentation scenario in the summer season added
