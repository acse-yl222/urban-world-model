# Imperial outward geometry expansion — initial audit (2026-09-12)

Status: **pending_evidence**. This bounded audit selected one building; no Blender process, geometry creation, scene mutation or network acquisition was performed.

## Actual quality frontier

The main `south_kensington_core008_web.glb` metadata identifies 74 distinct building IDs with either inherited Phase4 geometry or a source-informed landmark module. Their aggregate GLB X/Z envelope is `[482.609, -156.380, 909.284, 436.579]` metres. This is an envelope of attributed detailed modules, **not** a continuous accurate region or an independently verified accuracy boundary. The exact ID inventory is in `candidate.json`. There are 22 explicitly labelled procedural-baseline nodes within or along this region. A building-by-building quality frontier with internal gaps is therefore the appropriate expansion model.

The scene extras expressly say photo-informed reconstruction, not surveyed accuracy; some elevations and dimensions remain estimated. `all_buildings_at_RSM_standard` is false. Materials named `Detailed | urban masonry`, limestone trim and glazing also occur on explicit procedural baseline geometry. Neither material names nor polygon counts establish accuracy. The viewer campus camera rectangle is not a quality boundary.

The current coordinate contract is EPSG:32630 minus `[695238.304719173,5709236.965026026]`. Blender is east/north/up; exported GLB is east/up/south. Use this final frame, not stale scene-level campus-local descriptions. Existing registration diagnostics show consistency against mapped controls, not survey validation.

## First building

**23 Kensington Gore — `way-117417431`** is a small, bounded northwestern gap suitable for the first individual refinement. Its complete mapped footprint covers 319.122 m². WGS84 centroid is longitude -0.179579399, latitude 51.501268241; bounding box `[west,south,east,north]` is `[-0.1797289,51.5011639,-0.1794317,51.5013662]`.

The footprint is approximately 0.983 m from the source-informed Stevens Building (`way-205276847`) and 3.668 m from Darwin Building (`way-438951124`), satisfying a 150 m first-ring search limit. These are distances between mapped polygons, not measured physical clearance. It is also 25.527 m from 197 Queen’s Gate (`way-117417430`). Prioritising this gap extends the detailed frontier without jumping across an unrelated district.

Its existing node is `23 Kensington Gore | way-117417431 exterior`; extras explicitly state `OSM footprint; procedural facade baseline` and `mapped procedural baseline; individual refinement pending`. The nominal height is based on four OSM levels × 3.15 m + 0.55 m, and 39 windows are labelled estimated. It uses generic masonry/limestone/glazing/door/slate materials. Preserve and reconcile the separate `Entry approaches | entry-support::way-117417431::41::0` node during any later replacement.

## Available evidence and missing source

Usable local mapped evidence: `geometry/completion/sources/osm_buildings.json`, with source/ODbL ledger in `geometry/completion/sources/sources.json`. This supplies the complete plan footprint and four-level tag, not facade proportions or roof form. Existing GLB geometry supplies identity and interfaces but is not independent reconstruction evidence. No candidate-specific elevation/roof image has been inspected in this audit.

Search was limited to this project’s relevant geometry scripts/manifests, `/Users/yl222/Desktop/3D-Code_Agent/urban Geometry`, a shallow directory inventory of `/Users/yl222/Desktop/3D-Code_Agent`, and filename searches to six directory levels under `/Users/yl222/Desktop/3D-Code_Agent/litereality-Agent`, excluding dependencies and unrelated scan/asset directories. No original Imperial detailed authoring project, candidate module or candidate image evidence ledger was found in those searched locations. This is not a claim that none exists elsewhere on the machine.

`urban Geometry` contains old `city_sk.glb`, `city_sk2.glb` and scene/compare PNGs. The existing building-completion status notes the compare image depicts a different earlier model and lacks a licence/date ledger. It is not a basis for candidate geometry derivation. The current GLB contains references such as `docs/building_audits/sherfield_building.md` and `detailed_phase2_build.json`, but matching source files were not located. Original source module path is therefore null in the candidate record.

Existing local baseline workflow scripts are `geometry/completion/scripts/audit.py`, `candidates.py`, `prepare.py`, `build.py` and `render_review.py`. They perform footprint coverage and procedural supplementation, not evidence-backed individual facade refinement. The applicable authoring skill is `/Users/yl222/.codex/skills/region-to-geometry/SKILL.md`.

## Executable next unit

Locate the original detailed project/evidence ledger or acquire and inspect permitted photos and roof evidence for 23 Kensington Gore. Then create only `geometry/expansion/modules/kensington_gore_23.py` under a complete-footprint and shared-boundary contract, with observed/estimated dimensions recorded separately. Author real openings, recesses, frames, entry and evidenced roof structure. Keep the original baseline until an isolated replacement has passed numerical, independent GLB reimport and front/entrance/roof/rear visual checks. Do not count this audit as a built or integrated module, and do not advance the ring until the building passes review.
