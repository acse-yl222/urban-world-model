# Batch 04 status — 2026-09-13

Local geometry integration and numerical checks passed for **3 new buildings**:

- Jay Mews — `way-117010293`
- Princes Gate Court — `way-27917475`
- Albert Close context — `way-642055723`

The cumulative Three.js replacement check reports **10 distinct building IDs**, with original baseline meshes hidden before replacement and entry-support meshes retained. This count includes the earlier batches; it is not 10 new buildings in batch 04.

The current replacement contains 69 objects / 113,673 triangles. Independent reimport reports zero maximum bounds error. The interface check passes 1,004 roof samples, 120 shared-wall samples and 75 entrance rays, with scalar material values matching after export/reimport. These are modelling checks, not evidence of geographic accuracy.

The coordinator reports visually inspecting 15 individual-building images plus the overview. Following the final door-component naming correction, roof construction was also reviewed in code. Final delivery/progress flags remain coordinator-owned: this document records local integration success without modifying `verification.json`, progress or remaining-frontier files. At this documentation snapshot, the verification file still has its pre-signoff visual/delivery flags.

Artifacts:

- [Editable master Blender file](../../output/batch04_v1/master.blend)
- [Replacement GLB](../../output/batch04_v1/replacement.glb)
- [Numerical verification](../../output/batch04_v1/verification.json)
- [Interface and material checks](../../output/batch04_v1/interface_check.json)
- [Local Three.js loader/batching check](../reports/viewer_check.json)
- [Source attribution](ATTRIBUTION.md)
- [Uncertainty and limits](UNCERTAINTY.md)

Snapshot hashes:

- Master: `ffa18b351bc19e0656ef4e55625c56c56fff41cb3ab6910d6fec5295ebe4616f`
- Replacement: `e03387bf2a98b5c7280bb8f1dcc74abd94879adec439bcb64d44f3727202d40d`

No live-browser visual review or full-city accuracy/completeness claim applies. Two anonymous/contextual features retain substantial artistic completion; Princes Gate Court is photo-informed rather than surveyed.
