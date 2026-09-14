> Scope update, 2026-09-13: active batch07 now contains only two ordinary wings. Roof way-850407202 is preserved under `../deferred/` and remains pending evidence. The three-target preparation below is historical. See `roof_evidence_investigation.md`.

# Batch 07 preparation

Three labels are working identifiers, not verified names or postal addresses. Full footprints and existing source assets preserved. No completion state advanced.

## Rear features

`way-703836510`: four-point 149.288 m² footprint, original estimated eaves 13.150821 m, south-facing entry edge 1 projected onto the wall plane. `way-1133279024`: nine-point 194.279 m² footprint, estimated eaves 13.150522 m, entry edge 4. Both have four levels inferred from the old procedural height, not from observed elevations or OSM level tags. Original leaf points and 0.16 m recess are separately retained.

## Roof-only feature: do not turn into a building

`way-850407202` is explicitly `building=roof`, `layer=1`; no height, min_height, levels or entrance are provided. The complete five-point mapped footprint is 208.120 m². Feature fields levels/base_z/height_m/platform_elevation_m/roof_surface_z_m are **null** because actual support/platform elevation is unresolved. Source estimates are stored separately.

The old GLB has nine masonry triangles spanning z=0.050619..3.749381 m and three flat roof triangles at 3.749381 m. It is an old generic extrusion containing vertical masonry, not verified evidence for a real open canopy or enclosed building. Layer 1 is relative ordering, not a one-storey or 1 m instruction. No door or support assembly exists in the source feature.

The roof footprint has no positive-area overlap, parent relation membership or part alias. It touches Chemistry RCS1 on edge 0 for 32.127 m, Dyson on edge 2 for 32.049 m and Science Museum on edge 1 for 6.490 m. A connecting roof over the narrow gap is a plausible interpretation; actual support, underside clearance and platform datum remain unknown. See `roof_semantic_audit.json`.

Neighbour decoded full-geometry z ranges: Chemistry RCS1 [-0.055,20.888], Dyson [-0.309,18.989], Science Museum [0.047,37.057]. These include roofs/details; **they are not eaves or support heights**. Wall-top values remain null where no semantically identified roof plane is available. Do not insert a high canopy at those maxima or blind an entire facade based on them.

## Context and checks

All target polygons valid CCW, no holes or positive-area local way/relation overlap, no parent/part alias. Exact target/35 m neighbour coverage was decoded after initial source-only preparation identified missing neighbours. Final context contains 14 buildings and 296 meshes, including complete original Dyson detail, about 573 MB JSON. The Node extractor now streams per-object JSON to avoid the V8 single-string limit; no geometry decimation or source modification.

Latest-delivered batch02/03/04 replacement files were checked as context inputs, but none has a building in this particular required neighbourhood. Batch05/06 are staged and excluded. Thus original geometry is the latest available geometry for these 14 IDs, not an assumption that all later batches are complete.

Next authoring must resolve the roof semantic/interface contract separately; a roof-only mesh with explicitly estimated clearance can be considered under the user’s artistic-completion authority, but preparation has neither designed nor validated it.
