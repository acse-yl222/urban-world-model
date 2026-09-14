# Batch 03 adjacency and entrance audit

The three feature files preserve original projected footprints, original decoded door leaves and roof-plane heights. No source asset or feature geometry was altered by this report.

**The entry centres are recessed leaf centres, not facade centres.** Their distance to the footprint edge is 0.159842 m (Jamaican High Commission), 0.159492 m (84 Kensington Gore), and 0.160139 m (Jay Mews). All three are inward, consistent with a designed 0.16 m recess in the procedural source. None passes a 0.02 m facade-centre test. The JSON report gives projected facade centres, actual door normal, source support extents and exact z gaps; do not interpret the recess as a global CRS registration failure.

Use a facade aperture aligned tangentially to the original entry, then explicitly place a recessed leaf. Retain the original support patch and check the final threshold contact. The support surface is z≈0.044 m, just below the decoded thresholds ≈0.05 m.

Shared edges: Jamaican High Commission edge 1 adjoins 29 Exhibition Road for 10.014 m; 84 Kensington Gore edge 7 adjoins way-642055723 for 7.712 m and edge 8 adjoins Oriel House for 5.657 m; Jay Mews edge 4 adjoins way-117010293 for 11.567 m, and edge 2 adjoins way-117010290 for 11.519 m. Retain solid common-height wall portions; never delete entire walls merely for XY adjacency. Keep above-neighbour elevations available. Exact shared polylines and potential source vertical intervals are in the feature audits and report JSON. Updated 29 Exhibition Road geometry must be considered separately; source GLB bounds alone do not describe its current roof.

All selected polygons are valid CCW, no positive-area overlap against local way polygons or polygonized relation members, no parent relation membership and no asset-index source_part aliases. These are inventory consistency checks, not survey accuracy.

`reports/context.json` reuses the already-decoded batch02 context. Coverage was verified for every target and every audited adjacent/detailed neighbour within 35 m. Source context hash and per-ID mesh counts are attached as `reuse_basis`. It retains original material parameters and omits textures only in this diagnostic copy. Current batch01/02 overlays still need to be loaded for up-to-date visual checking.
