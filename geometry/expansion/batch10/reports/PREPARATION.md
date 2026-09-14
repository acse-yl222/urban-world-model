# Batch10 bounded preparation

Frozen preparation only,2026-09-13. Three targets follow next_ring_candidates.json. OSM addresses await exact-building evidence; no module, Blender or global completion operation was performed.

| ID | Slug | Area m² | OSM levels | Model wall height m | Entry edge |
|---|---|---:|---:|---:|---:|
| way-809238783 | queens_gate_3 | 151.603 | 6 | 19.451353 | 2 |
| way-809238780 | queens_gate_mews_24a | 237.266 | 2 | 6.849868 | 0 |
| way-809238784 | queens_gate_4 | 144.947 | 6 | 19.449694 | 2 |

All three full seven-point polygons are valid CCW, hole-free, without positive-area overlap, parent relation membership or source-part aliases. Mapped corners are retained, including concavities. CRS remains EPSG32630 minus [695238.304719173,5709236.965026026], Blender Xeast Ynorth Zup. Height is an old levels-to-metres conversion, not surveyed elevation. The2-storey mews must not inherit the6-storey neighbour typology.

## Entry and actual source surface

Original leaf tangent position, threshold and approximately.16m recess are retained; aperture centre is separately projected to its mapped wall. Entry normals and clear widths are in features. No original per-building entry-support mesh was found. Door bottoms are approximately-.000762m for3QueensGate,-.000341m for24aMews,+.000120m for4QueensGate.

Decoded triangle intersection explicitly examined ground, terrain, road, path, paving, sidewalk, asphalt, traffic and support objects, at threshold and.5/1m outward for each target. All9points hit only `Site_|_ground`, z=-.050000000745m. The result is a flat scene datum, not terrain survey. Thus old door bases stand approximately49–50mm above it. Nearby object bounds do not establish surface coverage. Finite approach/ground treatment belongs to coordinator; no.044/.05 prior-batch support is assumed. Reproducible script:inspect_source_ground.mjs; raw triangles-to-points results:source_ground_audit.json.

## Neighbour interfaces

3QueensGate shares edge0 with staged1–2QueensGate for13.697m, common interval up to16.299444m; edge5 with4QueensGate for14.165m, common interval up to19.449815m. 24aMews shares edge4 with staged1–2QueensGate for5.033m, interval up to6.849527m. 4QueensGate shares edge0 with3QueensGate, edge5 with5QueensGate for14.600m, and edge3 withway809386116 for4.213m (low neighbour top6.850225m). These are model potential common intervals; retain walls and suppress unverified openings within them. Do not delete whole walls solely by adjacency, particularly exposed sections above the low mews.

Current batch09 feature heights are explicitly staged, not delivered geometry. `staged_neighbour_heights.json` distinguishes main walls and maximum roof values. Cheval mainwall is16.30m above base; recessed attic is+2.20m, giving approximately18.50m above base. The attic maximum is not a shared-wall height. Cheval has no exact shared boundary with this batch's target polygons. Relevant1–2QueensGate adjacencies carry staged classification and preserve original height basis separately.

## Context provenance

Fresh bounded decode covers35asset IDs/191meshes from every mapped footprint within35m of these three targets, which includes all required neighbours. Source core008 is preserved and undecimated. Delivered overlays through batch07 were checked in chronological order; none contains relevant35IDs. Batch08 and09 were not included as delivered, and their staged geometry is not silently substituted into context. Features can use an explicitly labelled current staged height while the retained context mesh remains old; coordinator must use intended active geometry for final QA.

`preparation_audit.json` records requiredcoverage and nested extractionprovenance. Its copied_from=self means feature preparation read newly decoded context, not reuse of old context. `extract_context.mjs` reproduces original plus delivered overlay extraction. No textures downloaded; scalar PBR metadata preserved for diagnostic rendering. No item is marked complete by this preparation.
