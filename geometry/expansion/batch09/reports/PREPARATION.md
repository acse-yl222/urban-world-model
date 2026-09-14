# Batch09 preparation and interface audit

Prepared 2026-09-13. Scope follows the first three candidates in `geometry/expansion/reports/next_ring_candidates.json`. Addresses and Cheval name are OSM source labels pending independent current identification. This is preparation, not geometry completion.

| ID | Slug | Vertices | Area m² | Original eaves estimate m | Levels | Entry edge |
|---|---|---:|---:|---:|---:|---:|
| way-809238778 | hyde_park_gate_1 | 6 | 364.946 | 16.300285 | 5 | 4 |
| way-809238777 | cheval_hyde_park_gate | 9 | 795.111 | 13.149826 | 4 | 7 |
| way-809238779 | queens_gate_1_2 | 18 | 427.527 | 16.299450 | 5 | 0 |

All full polygons are valid, counterclockwise and hole-free, including the 18-vertex Queen's Gate indentation. No positive-area mapped overlap, parent relation membership or source-part alias was found. CRS remains EPSG:32630 minus [695238.304719173,5709236.965026026]; Blender east/north/up. No convex-hull substitution or protected core replacement occurs.

Five levels are explicitly tagged on 778 and 779, but their approximately 16.30 m heights are converted model estimates, not survey. Cheval has no level tag; its four floors and approximately 13.15 m height are inherited typology estimates. Existing detailed trim should be preserved or improved, not discarded solely because source glazing uses flat quads.

## Entrances and ground

All three original door leaves were decoded. Thresholds are near z=0 (-0.000026, +0.001123 and -0.000005 m), unlike the earlier frontier assets near z=.05. No per-building entry-support asset was found. Do not reuse prior batches' z=.044 paving automatically. Inspect source ground at the projected wall-plane threshold before authoring any approach.

Entry wall-plane centers are projected from original leaves; their original centers and approximately .16 m recess remain separately recorded. Tangent position, normal, clear width and leaf base are preserved. Numerical projection checks are in preparation_audit.json and are below the .02 m tolerance. These interfaces reproduce the old scene, not surveyed doorway positions.

## Shared walls

778 edge0 and Cheval edge6 share 30.645 m. Their original-model common height spans approximately z=.001123 to 13.150948 m. Cheval edge0 shares 13.255 m with 776 (model top13.150031); edge2 shares8.440m with761 (top9.999535). Queen's Gate edge15 shares13.697m with783 (common model top16.299444), and edge3 shares5.033m with780 (top6.849527). These are estimated potential intervals, not proven fire walls or measured facade heights. Retain complete walls; unverified openings on common intervals stay opaque. After neighbouring module heights change, the coordinator must refresh the relevant shared interval. Above-neighbour walls must not be automatically deleted.

25 Kensington Gore is 31.065 m from778, with no shared boundary. Its delivered replacement geometry and current height are used in context. More distant nearby protected/detailed buildings are retained as context only.

## Context provenance and scope

Fresh bounded source decoding selected all existing building assets whose assembled mapped footprints are within35m of any target:31IDs,200meshes. This broader seed includes every target and every required interface neighbour; preparation_audit.json reports no missing IDs. Existing batch08 context was not reused.

Original core008 source was decoded with local Three/Meshopt (`reports/extract_context.mjs`). Delivered02–07 overlays were checked in chronological report order. Batch02 replaces25KensingtonGore way117417421; no other relevant IDs occur in those overlays. Its old source exterior was removed from context and original entry support retained. No source file was modified; no mesh decimation or texture acquisition occurred. Scalar PBR metadata only is included.

The audit's copied_from=self records reading the fresh context during feature preparation; nested upstream_context_provenance records actual extraction and overlays. Context is reusable for this batch's bounded checks, not proof of all-city or visual coverage.

No modules were written, Blender was not run and no completed/global state was changed. Evidence review and source-scene ground inspection are the next gates.

## Source ground follow-up

`source_ground_audit.json` now records direct decoded vertical triangle hits at each of the3 entrances and at .5/1m outward: all9 samples hit only `Site_|_ground` at z=-.050000000745m. The original leaf near0 therefore stands approximately5cm above the baseline surface. This ground is a constant plane over the large original AOI, not terrain survey. Nearby broad bounding boxes of central kerb, stone, entry-support-union skirts and ground001 do not yield hits at these points and must not be treated as support. The coordinator may provide a separately reviewed finite approach; no automatic .044m paving assumption was introduced. `inspect_source_ground.mjs` reproduces the scoped decoded surface inspection.
