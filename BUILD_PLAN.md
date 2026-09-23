# AGNIMARG — Mid-Semester Review Build Plan (Software-Only Prototype)

**Status: built and working tonight.** This file records what exists, why it was scoped this way, and what's explicitly left for later — so the review reads as an intentional scope decision, not an unfinished project.

## Source documents (read in full before any code was written)

- `agnimarg-architecture-audit-space.html` — original 4-part architecture, team split, 15-point security audit
- `comparativeStudy.html` — global vs. India gap analysis; names EXODUS (dynamic evacuation routing) as the differentiator
- `agnimarg_master_blueprint.html` — full production blueprint: 14 phases, PostGIS, Celery, CesiumJS, XGBoost, YOLO. A multi-week/6-month build, not a one-night one — used here as the terminology/module reference (SENTINEL, EXODUS), not as tonight's task list.
- `Agnimarg_Complete_Software_Tech_Stack_India.pdf` — research-grade exact data-source stack (MOSDAC, Bhoonidhi, INSAT-3DS, etc.), mostly requiring institutional registration. Reference only.
- `AGNIMARG_Prototype_Plan.docx` — **the actionable document.** A ₹0, free-tier, 5-week roadmap for a 4-person team, with an explicit "what to mock/skip for prototype" list. Tonight's build compresses this further (5 weeks → 1 night, solo) but keeps its stack choices and its mocking philosophy.
- `AGNIMARG_Literature_Review.docx` — academic prior-art survey; used for the "novelty" framing in the review, not for implementation.

## Scope decision

Hardware/sensor track: dropped (budget, per your instruction). Full XGBoost/ConvLSTM/PostGIS/CesiumJS production stack: **not built tonight** — that's weeks of work per the project's own blueprint and explicitly flagged there as such. What's built is the software-only slice the Prototype Plan doc itself calls the "₹0 architecture," compressed to what one person can build and verify working in one night.

| Part | Tonight's build | Explicitly deferred (roadmap only) |
|---|---|---|
| INTAKE | Real OSM road network (Overpass API) + real place/hospital data for Nainital, Uttarakhand. Live Open-Meteo weather (no API key). Seeded historical-style fire event (Pangot/Kilbary forest belt) — clearly labeled as seeded, not a live FIRMS feed. | Live NASA FIRMS feed (needs a free personal MAP_KEY you create — swap-in ready), PostGIS, Airflow/Celery ingestion, multi-source corroboration |
| SENTINEL | FWI-style heuristic risk score (temp + humidity + wind — real live/scenario weather in, real number out) driving a real downwind threat-cone geometry (1h/3h/6h rings). HMAC-SHA256 signs every payload. | XGBoost ignition model, CNN-BiLSTM/ConvLSTM spread, MLflow versioning |
| EXODUS | Real NetworkX Dijkstra routing over the real OSM graph. Verifies the HMAC signature before acting — rejects tampered payloads live (demoed, not just claimed). Dynamically re-costs/blocks edges inside the threat cone and reroutes. | OSRM/GraphHopper, multi-modal transit, OR-based vehicle pre-positioning |
| INTERFACE | Single-page Leaflet dashboard: live map, cones, before/after routes, role selector (citizen/authority), human-approval dispatch gate, live audit log. | Real OAuth2/OIDC, real SMS (MSG91), Supabase/Postgres persistence — audit log is in-memory tonight |

## Why the specific security controls built tonight

Per the original audit doc's Tier-1 findings — HMAC signing (finding #1) and the human-approval gate (finding #2) are the two cheapest-to-build, highest-impact controls, so they're real and demoable, not just described. RBAC is a simple role flag (matches the Prototype Plan's own "RBAC: mock" guidance) rather than a full permissions system.

## Repo layout (built)

```
/backend
  main.py         FastAPI app: /api/state, /api/weather, /api/simulate, /api/tamper-demo,
                   /api/dispatch/approve, /api/audit-log — also serves /frontend as static files
  graph_data.py    Loads the OSM graph + seeded event data
  weather.py       Live Open-Meteo fetch (fails soft to a labeled fallback if offline)
  sentinel.py      Risk score + threat-cone geometry + HMAC sign/verify
  exodus.py        Point-in-polygon re-costing, Dijkstra routing, signature verification
  audit.py         In-memory audit log
  data/            road_graph.json, places.json, hotspots.json — generated, committed for offline demo reliability
/frontend
  index.html, style.css, app.js   Leaflet dashboard, no build step
/scripts
  fetch_data.py     Regenerates road_graph.json/places.json from live Overpass API
  seed_hotspots.py  Regenerates hotspots.json (seeded fire event + fire-season scenario weather)
```

## Run it

```
pip install fastapi uvicorn networkx requests
uvicorn backend.main:app --reload
```
Open `http://127.0.0.1:8000/`. Click **"Run simulation (fire-season scenario)"** — this is the reliable demo path (works with or without internet, since only the road/place data was pulled live and is now cached in `backend/data/`). **"Run with live weather instead"** hits Open-Meteo live and shows real current conditions for the region, at the cost of being weaker for a demo when the actual weather is calm (that's *why* the scenario mode exists — see `weather.py`/`seed_hotspots.py` docstrings for the honest reasoning).

## Demo script for the review

1. Show the map: real village (Pangot), real shelter (Sitapur Hospital, Nainital), seeded fire markers — point out the on-screen banner that honestly labels this as seeded, not live.
2. Click "Run simulation" — cones appear (live-computed geometry, not a static image), risk score and HMAC signature shown.
3. Point out the green safe route bending around the red/orange cone vs. the gray baseline route that ignores it — this is the EXODUS differentiator the comparative-study doc calls out.
4. Click "Tamper the signed payload & replay" — show EXODUS reject it. This directly answers Tier-1 audit finding #1 live, not on a slide.
5. Switch role to Citizen, try "Approve dispatch" — denied. Switch to Authority, approve — succeeds, logged. Answers Tier-1 finding #2.
6. Show the audit log — answers Tier-1 finding #4.
7. State plainly what's roadmap vs. built (the table above) — the Complete Software Tech Stack PDF and master blueprint are the "where this goes next" story, not tonight's claim.

## Honest limitations (say these out loud in the review, don't let them be found)

- Fire hotspots are seeded, not a live FIRMS feed (needs a free MAP_KEY you'd create yourself — architecture supports swapping it in without a rewrite).
- Risk score is an explicit FWI-style heuristic, not a trained ML model — same simplification the Prototype Plan doc itself recommends for the prototype stage.
- Audit log is in-memory (resets on server restart) — fine for a live demo, not for production.
- Routing graph covers one bounded region (Nainital) — proof of concept, not national coverage.
