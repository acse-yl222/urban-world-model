# Building completion — 2026-09-12

306 OSM building footprints integrated into the local web viewer as a separate 3.6 MB GLB, with estimated heights and procedural facade/window baselines. Original core008 GLB is unchanged. This is a partial OSM coverage repair, not a completed satellite reconstruction.

The audit considered 6,631 mapped building features intersecting the ground bounds. It found 309 conservative candidates wholly within the ground rectangle, with less than 2% overlap against represented OSM polygons / building bounds. 306 passed candidate/traffic-lane overlap checks (maximum tolerated road overlap 0.5 m²). Others, including crossing-boundary buildings, small structures, and ambiguous overlaps, remain in reports/candidates.json. No completeness claim applies to this conservative selection.

Registration: EPSG:32630 minus [695238.304719173,5709236.965026026], Blender X east/Y north/Z up; GLB X east/Y up/Z south. Checked against 5,838 source/model controls, median fitted residual 0.023 m; this is registration consistency, not survey accuracy. Existing scene's campus-local metadata does not describe the final outer-building frame correctly.

Verification: polygon roof triangulated areas checked, holes preserved, candidate and road overlaps checked, supplement independently reimported in Blender with all 306 IDs and zero observed bounds discrepancy. Three.js loader and batching retained all 62,512 triangles in four batches. Saved .blend reopened for front/roof/rear renders. Browser visual QA unavailable (CUA has no browser; native Chrome call timed out). No full-city visual signoff claimed.

Web control: Added buildings · 306. The existing station detail tile clips the supplement exactly as it clips the original model, preventing duplicate display inside the active tile. This means not all 306 additions are visible when the detail tile is on. Turning Buildings off also hides the supplement.

Sources: OpenStreetMap, © OpenStreetMap contributors, ODbL; https://www.openstreetmap.org/copyright. Raw extract and derived geometry are included. No satellite pixels are exported or traced.

Imagery: an existing local city_sk2_satellite_compare.png was inspected for discovery, but depicts a different earlier model and has no available licence/date ledger; not used to derive geometry. The public Environment Agency catalogue returned 2008 RGB / 2012 nighttime coverage. No usable current authorised imagery was acquired; independent satellite-only omissions remain unverified.

Deferred conflicts: Montrose Court way-111491435 (12.58 m² road overlap), Baden-Powell House way-392722404 (12.92 m²), way-851973718 (18.19 m²). Montrose is independently confirmed absent from all model-node bounds, but was not added because of the road conflict.

Height, roof shape, window layout, materials and floor pitch are estimates, not photogrammetric recovery. Facades are procedural baselines. Existing physical fields and solid masks were not recomputed after these additions; they remain results for the original geometry. Local viewer code is updated; remote workstation deployment was not performed.

Reproduction: install dependencies listed in scripts, run audit.py, candidates.py, prepare.py, then Blender build.py and render_review.py. Node viewer loader/batching check: node --experimental-loader ./geometry/completion/scripts/three-loader.mjs geometry/completion/scripts/verify-viewer.mjs.
