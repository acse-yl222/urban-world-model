> Scope update: way-24436429 moved intact to ../deferred/ pending current-site evidence; active scope is two unnamed wings. Three-target preparation below is historical.

# Batch08 bounded preparation

Prepared 2026-09-13. Features and manifest are ready for evidence review, not completed geometry. Source GLB is untouched. No modules, Blender execution or completion-state changes were made.

| ID | Working slug | Full footprint | Original eaves estimate | Entry edge | Shared edges |
|---|---|---:|---:|---:|---|
| way-850528335 | campus_wing_850528335 | 5 vertices, 206.837 m² | 13.150658 m above base | 4 | 0,1 against 24436446; 2,3 against Science Museum |
| way-850528336 | campus_wing_850528336 | 6 vertices, 246.854 m² | 13.149094 m above base | 5 | 0 against 24436446; 3 against Science Museum |
| way-24436429 | temporary_exhibit_24436429 | 4 vertices, 173.651 m² | 13.149915 m above base | 1 | none found |

All three OSM records are building=yes, without roof, layer, height or level tags. Temporary Exhibit is an OSM name with tourism=attraction, not a temporary=yes tag or proof of current use/existence. The two unnamed footprints lie between Science Museum and way-24436446; campus affiliation is not established. No internet claim about their present appearance was made during this local preparation.

All polygons are valid, counterclockwise, without holes; the full mapped perimeter is preserved. No positive-area mapped overlap, parent relation or source-part alias was found. Small nearly collinear segments remain present. Projection is EPSG:32630 minus [695238.304719173,5709236.965026026], Blender east/north/up.

Original leaf and support geometry exists for all three. Wall-plane entry centers are projected to their edges with errors below 4e-14 m; original leaf centers are retained separately with approximately 0.16 m recess. Thresholds sit 5.98–6.81 mm above the existing z=0.044 support. Those are source-model interface measurements, not surveyed entrances. Do not place plinths or window frames across these apertures.

The three nearly identical 13.15 m eaves and four inferred floors reflect the old typology baseline, not three independent observations. Treat height/levels as requiring evidence review before design; in particular do not infer a four-storey exhibit from the name. Shared boundary lengths are 41.289 m and 35.444 m for 335, 7.818 m each for 336. Actual neighbour wall tops remain unknown, so no shared-height interval is fabricated; retain complete opaque shared walls until verified openings or exposed upper wall sections can be established.

## Context provenance

Fresh bounded extraction covers all three targets plus Science Museum way-27765411 and way-24436446: 5 IDs, 40 meshes, no missing required IDs. The broad seed queried all mapped footprints within 35 m, with parent relations assembled, then selected existing source assets. This exactly covers the final required set. batch07 context was not reused.

Original core008 GLB was decoded via local Three/Meshopt using `reports/extract_context.mjs`; scalar PBR only, no texture maps. Delivered batch02–06 replacements were inspected in chronological report order; none contains these five IDs, so these local meshes remain original-source context. Detailed source geometry was not decimated. `preparation_audit.json` records nested upstream extraction provenance; its copied_from=self denotes the freshly decoded context read during feature generation, not reuse from an older batch. The preparation script is `geometry/expansion/scripts/prepare_expansion_batch.py`. Source geometry remains unchanged.

Next: establish each asset's current roof/role and permitted visual references, then author only evidence-supported or clearly labelled artistic details. No item is automatically advanced to completed by preparation.
