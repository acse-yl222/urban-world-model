# Batch 02 — three additional building refinements

Completed locally on 2026-09-13. Three complete mapped footprints (983.35 m² combined) now replace their original coarse exteriors. Alongside the previous 23 Kensington Gore pilot, the local viewer displays four optional refinements. Original source GLB and unrelated scene assets are preserved.

| Building | Modelled features | Evidence boundary |
|---|---|---|
| 25 Kensington Gore — way-117417421 | Pale stucco, recessed dark sashes, bay returns, cornices, coupled porch columns, balustrades and mansard dormers | Historic England description and inspected 2025 open photographs of the corner ensemble; exact decorative assignment, heights and rear details remain interpreted |
| 41–45 Jay Mews — way-117010286 | Two-storey workshop proportions, broad ground-floor windows, narrower upper windows, simple coping and rainwater pipes | Mapped two-storey footprint and inspected street-context photo; exact target facade not confirmed, so its composition is artistic completion |
| 29 Exhibition Road — way-641757059 | Three main storeys, inset small-pane sashes, brick arches, gabled attic, pitched roof ranges and tall chimneys | Historic England listed-pair description and inspected Robin Sones photograph; this mapped asset is only one component of the pair. Heights, rear faces, bay dimensions and roof arrangement remain estimated |

## Files and viewing

- [Editable master with neighbourhood context](../../output/batch02_v1/master.blend), 88.90 MB.
- [Uncompressed replacement GLB](../../output/batch02_v1/replacement.glb), 3.75 MB, three building IDs, 78 meshes and 69,587 triangles. Context, cameras and review ground are excluded.
- Per-building modules are in `../modules/`, frozen inputs in `../features/`, inspected images and source ledgers in `../references/`.
- [25 Kensington Gore render](../../output/batch02_v1/kensington_gore_25_front.png).
- [41–45 Jay Mews render](../../output/batch02_v1/jay_mews_41_45_front.png).
- [29 Exhibition Road render](../../output/batch02_v1/exhibition_road_29_front.png).
- [Source attribution and licences](ATTRIBUTION.md).

Refresh the local viewer and use **Building refinements · 4** to compare all four buildings with their originals. `?expansion=0` starts with the originals. Each batch loads independently; an unavailable or incorrectly aligned batch leaves its source exteriors available. The final batch URL includes a content revision to avoid stale browser cache.

Suggested local close cameras (append to `/viewer/3d/`): `?cam=465,28,-150,491,6,-102&replay=0` for 25 Kensington Gore, `?cam=500,20,-45,550,4,-35&replay=0` for Jay Mews, and `?cam=880,35,35,844,9,-12&replay=0` for 29 Exhibition Road. Some views remain occluded by neighbouring buildings; the isolated renders show detail separately.

## Verification

Native master reopened; replacement GLB independently imported. All semantic mesh identities and triangle counts retained, zero observed bounds discrepancy, no degenerate triangles. Base colour, roughness and metalness values pass independent import comparison. Roof coverage passes 557 sampled interior points across the mapped footprints. Four entrances pass 100 near-threshold and upper opening rays before intentionally closed door assemblies; original aprons are retained and the new south doorway has a finite estimated support surface.

Current front, entrance, roof and rear renders for every building and neighbourhood-context renders were inspected. Additional south-entry and alternate context views were inspected for 29 Exhibition Road. Continuous roof flashing fixes dark overlapping wall-top corners; door bottom rails and a continuous plinth that would obstruct approaches were removed during review. The scene context contains 67 original building IDs plus replacements; original scalar PBR colours are retained, while source texture maps are omitted only in the diagnostic context copy. The flat review ground and lighting are labelled estimates.

Actual source GLB was decoded through Three.js. Both batches pass exterior-ID matching, per-building horizontal bounds checks, triangle-preserving batching, retained original entrance supports and reversible comparison. Local HTTP responses for HTML, the integration module, attribution and final GLB were checked; the served GLB matches its verified SHA-256. No live browser visual test or full-city visual signoff is claimed.

The recorded heights are modelling estimates, not measured geography. No basement excavations or interiors were fabricated. Physics fields remain the original simulations, and no remote workstation deployment was performed. This batch is delivered as reference-informed/artistically completed geometry; it does not certify geographic precision across the whole region.

## Resume

Run `geometry/expansion/scripts/extract_batch02.mjs` through the existing Three.js loader for a fresh diagnostic context only when needed. Assemble/export/render using Blender with `geometry/expansion/scripts/build_batch02.py`, run `check_batch02.py`, and run the Node `verify_batch02.mjs`. `render_batch02_extra.py` supplies alternate 29 Exhibition Road views. Reports bind inputs and outputs by SHA-256. Use a new output version for future changes.

The explicit pending-refinement inventory originally contained 22 IDs, including small outbuildings and roof features. Four have now been refined. The other 18 are recorded in `../../remaining_frontier.json`; that inventory is not a claim of whole-city coverage. Further batches have not yet started.
