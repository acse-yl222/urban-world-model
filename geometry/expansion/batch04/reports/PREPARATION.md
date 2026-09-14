# Batch 04 preparation and current-context audit

Three complete original footprints retained; no source assets, viewer or modules modified.

Entrances are now wall-plane threshold/aperture centres. Their original recessed leaf centres and ~0.16 m recess are separately recorded. Original threshold z and clear width remain unchanged.

## Jay Mews (OSM way-117010293)

ID `way-117010293`; 5 vertices; 129.299 m²; estimated eaves 13.150506 m above base 0.049627 m. Entry edge 3. Valid CCW polygon, zero holes.

No positive-area overlap against locally reconstructed ways/relations; no parent relation membership or asset source-part alias.

- Edges [0] share 11.567 m with `way-117010283` (Jay Mews); potential common wall z interval [0.04962729290093648, 13.200132868937311]. Height source: geometry/expansion/output/batch03_v1/verification.json.
- Edges [1] share 10.578 m with `way-117010289` (The Gore Hotel); potential common wall z interval [0.04962729290093648, 13.200132868937311]. Height source: original decoded GLB; estimates.

## Princes Gate Court

ID `way-27917475`; 22 vertices; 1454.861 m²; estimated eaves 19.447124 m above base 0.051834 m. Entry edge 1. Valid CCW polygon, zero holes.

No positive-area overlap against locally reconstructed ways/relations; no parent relation membership or asset source-part alias.

- Edges [12] share 8.756 m with `way-641757059` (29 Exhibition Road); potential common wall z interval [0.0518339630754685, 13.199784380310632]. Height source: geometry/expansion/output/batch03_v1/verification.json.

## Albert Close (OSM way-642055723)

ID `way-642055723`; 8 vertices; 165.644 m²; estimated eaves 13.149753 m above base 0.049725 m. Entry edge 6. Valid CCW polygon, zero holes.

No positive-area overlap against locally reconstructed ways/relations; no parent relation membership or asset source-part alias.

- Edges [1] share 11.857 m with `way-492431541` (Oriel House); potential common wall z interval [0.04999995231628418, 8.15020884990794]. Height source: original decoded GLB; estimates.
- Edges [2] share 7.712 m with `way-492431542` (84 Kensington Gore); potential common wall z interval [0.05043443817969662, 6.8992867624260885]. Height source: geometry/expansion/output/batch03_v1/verification.json.
- Edges [0] share 4.515 m with `way-81742939` (Albert Hall Mansions (49-86)); potential common wall z interval [0.04972490941426422, 13.19947814014421]. Height source: original decoded GLB; estimates.

## Context coverage

An initial audit rejected blind reuse of batch03 context because Albert Court `relation-5547141` was missing. A bounded Node identity decoder rebuilt the required context from original core008 plus delivered batch02 and batch03 replacement GLBs. All 27 required buildings are now present (358 meshes). Original entry-support surfaces were preserved while superseded building meshes were replaced. Thus context reflects current delivered overlays, not only stale source geometry. Scalar PBR parameters are retained; texture maps omitted only in this diagnostic context.

Latest delivered verification reports supply neighbour main-wall/eaves heights; full geometry z bounds are recorded separately. A tall chimney/roof maximum never automatically extends a blind shared-wall interval. Existing unrebuilt neighbours retain explicit original-source estimates.

Keep all shared walls, default opaque only over justified common-height intervals; above-neighbour portions may remain exterior. Actual openings and irregular roof intersections still require coordinator visual/interface checks.

Reusable scripts: `geometry/expansion/scripts/prepare_expansion_batch.py` (local GIS and feature/audit preparation) followed by `geometry/expansion/scripts/extract_prepared_context.mjs 04` through the existing Three loader (bounded current geometry extraction). The first script refuses to certify missing context IDs; the second resolves them from authoritative source assets. Neither marks a building complete.
