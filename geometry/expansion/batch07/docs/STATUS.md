# Batch 07 — two wings delivered locally

Two new assets: Queens Gate rear `way-703836510` and campus rear `way-1133279024`. Cumulative count: 18 refined assets, 4 pending in the initial 22-feature frontier. One pending roof is explicitly deferred for missing shape/support evidence.

[Editable master](../../output/batch07_v1/master.blend), [uncompressed GLB](../../output/batch07_v1/replacement.glb), [overview](../../output/batch07_v1/overview.png). 39 meshes, 11,421 triangles. Native reopening, independent GLB reimport, IDs/materials/bounds passed; 50 entrance rays, 100 conservative opaque-wall samples and 189 roof samples passed. All 11 current renders actually inspected. Actual Three.js loading, reversible comparison and local HTTP checks passed for 18 unique replacement assets.

The four-storey heights and exact facades are estimates. No exact target photograph was confirmed. Shared-wall apertures are conservatively excluded where neighbour heights are unknown; this is not measured shared-wall geometry. Hidden interfaces rely on separate sampled checks. See [attribution](ATTRIBUTION.md), [uncertainty](UNCERTAINTY.md), and [deferred roof evidence](../reports/roof_evidence_investigation.md).

No live-browser/full-city visual certification, survey accuracy certification, physics recomputation or remote deployment. Continue from [project status](../../docs/STATUS.md).
