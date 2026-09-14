# 29 Exhibition Road / way-641757059

Stage: module built, syntax checked; Blender integration and render QA owned by coordinator.

Research used two search queries and one actually inspected street photograph. Wikidata Q26506840 identifies the listed pair; Historic England 1211833 supplies official facts. Robin Sones's 11 February 2020 Geograph 6577545 photograph, viewed at its 640 × 480 original resolution, visibly confirms brickwork, small-pane white sashes, steep gables, high chimney stacks and the corner elevation. No Google imagery was acquired or geometry derived from Google. Source ledger in `../references/exhibition_road_29/sources.json` records rights, attribution and observations.

The module keeps the exact nine-point concave footprint, including rear returns. Three full storeys replace the baseline's speculative four-storey treatment; the original 13.15024 m wall-height estimate is retained as the eaves datum, with attic roofs above it. This is an estimated height allocation, not a measured elevation. Red brick Queen Anne detailing is composed separately from the earlier Kensington Gore model: segmental ground arches, cut-brick cornices, simplified split pediments, small-pane sashes, paired steep roof ranges, gable attic apertures and chimney stacks. Wall and attic openings are real voids with independent inset glass and frames.

The original north entrance remains and is returned as `interfaces.entrance`. A second south entrance appears in `interfaces.additional_entrances`; its placement is approximate and its surface support is coordinator-owned. No terrain cut or basement was fabricated. All concave walls remain regardless of neighbours.

Suggested material palette: masonry linear RGB (0.30, 0.105, 0.060), roof (0.24, 0.072, 0.04), trim (0.76, 0.73, 0.65); roughness 0.72–0.9. These muted tones represent red brick and tiled roofs. Export textures are procedural, with no photograph embedded.

Unknown: exact total/eaves height, rear fenestration, roof intersections and dormer layout, brick sculpture, actual entry doorstep levels. Ornament and dimensions are interpreted, not survey measurements. The source describes the full listed pair, while the mapped polygon may cover only one component. The model intentionally stays within the supplied asset's footprint.

Attribution: Historic England, List Entry 1211833, Open Government Licence v3.0. Jamaican High Commission, Exhibition Road by Robin Sones, CC BY-SA 2.0 (https://creativecommons.org/licenses/by-sa/2.0/). Photo-informed geometry is an interpreted adaptation with considerable simplification; those contributions are provided CC BY-SA 2.0. OSM plan attribution remains © OpenStreetMap contributors, ODbL, under the coordinator's existing source ledger.

Coordinator entry clearance review applied: doors omit bottom sash rails, door leaves start at threshold, and threshold slab top equals baseline base level. Module frozen for assembly after Python syntax validation.


Coordinator update 2026-09-13: integrated locally; native reopening, independent GLB import, material/entry/roof checks and current rendered views passed. See STATUS.md for final scope and limitations.
