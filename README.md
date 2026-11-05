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

- Trails: [OpenStreetMap – Trentino/Sentieri](https://wiki.openstreetmap.org/wiki/Trentino/Sentieri)
- Trails: [Waymarked Trails – Hiking](https://hiking.waymarkedtrails.org/)
- Weather: Open Data Trentino (environment group) and the resources of project no. 7
- Points of interest / territory: Open Data Trentino, KGE catalog resources

## Building the report

The report in `Documentation/report/` must be compiled with **XeLaTeX** (the `latexmkrc` file sets this).
On Overleaf: Menu → Compiler → XeLaTeX.

## Team

- Team Member 1
- Team Member 2
