# Batch03 — delivered locally

2026-09-13. Three new assets: Jamaican High Commission (way-641603104), 84 Kensington Gore (way-492431542), and Jay Mews (way-117010283). Revised 29 Exhibition Road (way-641757059) is the adjoining northern wing; its speculative shared-face south entrance and duplicate double-gabled roof were removed. Earlier files are preserved.

The current viewer loads seven distinct refined IDs across the pilot, retained batch02 and batch03. All seven source exteriors are reversible using Building refinements; the original entry supports remain. The two unchanged batch02 assets are exported separately as retained_batch02.glb, so the revised29 overlay does not overlap its old overlay.

## Artifacts

- [Editable Blender master](../../output/batch03_v1/master.blend), with diagnostic existing-neighborhood context and earlier refinements.
- [Uncompressed new/revised GLB](../../output/batch03_v1/replacement.glb): 105 mesh objects, 56849 triangles, 4 IDs. This is3 new buildings+1 revision, not4 newly completed.
- [Current neighborhood view](../../output/batch03_v1/kensington_gore_84_context.png), plus21 current review PNGs.
- [Numerical/export record](../../output/batch03_v1/verification.json), [interface checks](../../output/batch03_v1/interface_check.json), [viewer checks](../reports/viewer_check.json).
- [Sources and attribution](ATTRIBUTION.md), individual feature/module/reference files, [continuation instructions](CONTINUE.md).

## Verification and limits

Native master reopened; independent GLB reimport retained IDs, object triangle counts, PBR values and bounds (maximum difference0m at exported float precision). Four entrance interfaces pass100 lateral/height rays including threshold-level checks; Jamaican portico checked from1.8m outside and support sampled along its slab.467 interior roof samples and120 shared-wall mesh samples pass. Full source GLB decode with Three.js passes alignment, batching, triangle preservation, original-support retention and on/off comparison for seven IDs. Local HTTP returns200 and serves the verified GLB bytes.

All21 final views actually reviewed. Portico spandrel black gaps, open dormer backs and linking-roof underside gap corrected. No live-browser or full-city visual review, remote deployment or physics recalibration is claimed. Diagnostic context omits neighboring texture maps but keeps scalar PBR; the viewer still loads the unchanged original textured city. Heights, bay dimensions and hidden details remain estimated or artistic, especially Jay Mews/84 and29's northern wing. The Jamaican entrance omits the historic raised terrace to preserve the current scene ground connection.

Coverage:7 of22 explicitly queued source-refinement IDs are now authored;15 candidates remain, including ancillary/roof features requiring scope review. This is not whole-city coverage. Progress and nearest-frontier ordering are saved; no unattended background service is installed.

Final replacement SHA256: `4498dbd5a5d58a7769455c0bcd2fafff67545fb164675510aa0a9f93d13d4e45`.
