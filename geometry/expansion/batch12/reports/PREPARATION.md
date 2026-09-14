# Batch 12 bounded preparation

Prepared only data/interfaces/context for three audited ring02 candidates. No modules, Blender, changes outside batch12, or root progress changes. `prepare_expansion_batch.py` decoded original entry/materials from bounded context and used full local OSM geometry. Source data and original assets were not edited.

| Target | Corners | Source levels | Estimated wall height m | Entry edge | Original base m |
| --- | ---: | ---: | ---: | ---: | ---: |
| 27 Princes Gate | 5 | 5 | 16.301500 | 4 | -0.000697540 |
| 47 Princes Gardens | 4 | 5 | 16.300690 | 0 | -0.000030580 |
| 14 Queens Gate Place Mews | 4 | 2 | 6.849886 | 1 | -0.000481603 |

All three polygons are valid, CCW, hole-free and have no positive mapped overlaps, source parent relations or asset part aliases. All three are outside the exact 74-asset protected set obtained from source-informed/inherited Phase4 statuses. Original source addresses and levels are not independently photo-confirmed. Heights remain original procedural estimates; no image research, facade identity verification or roof inference has occurred in this preparation task.

`normalized_shared_wall_segments` preserves every shared edge segment: 27 Princes Gate has three, 47 Princes Gardens two, 14 Queens Gate Place Mews two. Original neighbour geometry is also retained. Shared heights are baseline estimates. **28 Princes Gate / way-359620473 is mapped but absent from asset_index, original GLB decode, source parent relations and source-part alias records.** Its 32.645 m shared boundary with 27 is retained with null height; no fake surrogate context mesh or guessed height is supplied. Full-target opacity is a conservative pending authoring policy, not an assertion of measured neighbour height. This is the sole explicit context gap.

Context has195 actual meshes for39 present building IDs, with40 IDs tracked including absent way359620473. Source plus all currently delivered batch02–11 overlays were considered; none replaces these bounded nearby asset IDs. The extractor preserves this one verified missing-neighbour exception and still rejects any unexpected missing asset. See `preparation_audit.json` and `normalized_interface_audit.json`. Source statuses and protected neighbour checks are embedded in the features.

Ground audit uses actual transformed triangle barycentric hits, not bounding boxes as supporting surfaces. All three threshold/.5/1m samples hit only Site ground at−.05 m; no original per-building entry support exists. Original door thresholds are about−.0007 to0 m, giving roughly49–50 mm clearance above that ground. Keep these source poses documented; **coordinator must choose finite approach/support and final datum** before modules are frozen. Preparation has not shifted buildings, created support or declared accessible routes.

The manifest is a prepared-feature envelope only; root owns coordination and build registration. Reproducibility: bounded `extract_context.mjs`, source `prepare_expansion_batch.py`, `inspect_source_ground.mjs`, then `normalize_interfaces.py`. If preparation is rerun, normalization must be reapplied; the generic preparer intentionally reports missing way359620473 until its explicit absence is carried forward. No successful delivered state is claimed.
