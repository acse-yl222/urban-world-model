# 47 Princes Gardens / way-640808103 — evidence preparation

Bounded research and single-building module completed for coordinator integration. Ground, manifest, feature and global completion remain unchanged. No Blender run.

## Identity and official facts

[Westminster Planning Applications Sub Committee,23October2018](https://westminster.moderngov.co.uk/documents/s29524/ITEM%2004%20AND%2005%20-%2048%20PRINCES%20GARDENS%20LONDON%20SW7%202PE.pdf), Items4&5, page7§6.1–6.2, identifies **46–48PrincesGardens as three terraced houses with five storeys above basement**, connected to **78–80PrincesGateMews**. It describes15self-contained residential units across the group. The implemented2007approval included replacement windows, rear extensions/terraces, garage alterations and a roof plant area. The report header marks the application building unlisted. These are dated official facts, not a survey of current2026condition or a per-OSM-part allocation. Public factual prose is paraphrased; document photographs/plans are not used for geometry.

Do not confuse this target with47PrincesGate,44–48PrincesGate,8–15PrincesGardens,47PrincesGardens Acton, or Margate. No target-specific HE listing was established by this search; the2018header does not prove unchanged statutory status in2026. A2006official educational-establishment schedule names47PrincesGardens historically, but cannot establish present whole-building use and was not used for morphology.

## Licensed images actually viewed

1. [Grand entrances on Princes Gardens, Geograph7768871](https://commons.wikimedia.org/wiki/File:Grand_entrances_on_Princes_Gardens_-_geograph.org.uk_-_7768871.jpg), **David Martin, CC BY-SA2.0,5May2024**. Close oblique terrace view at metadata51.498585,-.173238. Visible pale channelled stucco, Doric porch columns, triglyph frieze, turned balcony balustrades, upper Corinthian-style capitals, sash windows and basement railing. No readable47numeral and roof mostly outside frame. It is presently **terrace context pending exact assignment**, not a verified47elevation. Coordinate metadata is not a measured camera pose.
2. [Parking in Princes Gardens, Geograph7829218](https://commons.wikimedia.org/wiki/File:Parking_in_Princes_Gardens_-_geograph.org.uk_-_7829218.jpg), **Mr Ignavy, CC BY-SA2.0,13January2024**. Square view through bare trees with classical terraces and modern infill. **Square context only**; no isolated47facade. Do not transfer opposite-side window counts to target.

Both original JPEGs were downloaded unchanged and actually inspected. No image pixels are exported as textures. Attribution and applicable share-alike terms accompany any contextual geometric adaptation. [Ledger](../references/princes_gardens_47/sources.json) holds per-image hashes, sources and observations. A third candidate, Robert Lamb's2013view upPrincesGardens, has metadata only and was not acquired/used; category inventory is discovery, not evidence.

## Next bounded modelling decision

Current feature binds way640808103 to the middle47parcel within46–48, preserving all four corners. Five main storeys have official support; metric main/roof heights do not. Retain coordinate and entry contracts rather than guessing from photographs. Do not assign the whole46–48complex or its three mews wings to this singleOSMway. Roof plant's historical presence does not specify equipment type, position or shape. Rear terraces and roof outline likewise require mapped/photographic corroboration or explicit estimated completion; no speculative equipment, basement excavation or copied stair levels.

Evidence permits contextual classical-stucco detailing if exact targetphoto cannot be resolved, with that limitation retained. Current stage is **module prepared, identity group established, exact image-to-parcel assignment unresolved**; this is not integration or delivery.

## Authored module and interfaces

`modules/princes_gardens_47.py` exports `build(feature,materials)` with masonry/trim/glass/door/roof/metal keys; returns generic entrance/shared-wall contracts,25opening records and full roof parts. Four-point256.798m² polygon remains complete. MainH16.300690m and five floor intervals follow current feature; original base/threshold-0.000030580107m stays dynamic and unchanged. Absolute walltop16.300659443m, roof/parapetmax16.740659443m. Complete flat deck follows source roof: no unverified mansard, plant or garage volumes.

Front edge0 has three estimated bays, with the inherited entrance replacing the relevant ground window. Real.44m wall apertures and.35m inset glass/door; differentiated sash and first-floor casement frames, architraves, simplified Corinthian details, central pediment and turned balustrades. Doric porch is adapted from nearby terrace context. Extra small second-floor balconies and ornament dimensions are artistic completion, not a documented47-specific survey. Rear uses restrained estimated openings; both long side walls are wholly retained and blind.

Normalized shared edges1 and3 retain their exact polylines and common-height intervals against48 and46. Every planned opening is tested against both; no raised side parapet/coping is authored. Continuous mitred stringcourses stay inside footprint. Front/rear low parapets end.25–.28m before corners; front ornamental/balcony endpoints remain inside lateral boundary limits. Roof remains a full cap despite those parapet breaks.

Entry XY[949.760770888,-173.827013320], normal[-.169336588,.985558278,0], clearwidth1.051250633m unchanged. Leaf recession.35m,2.88m clearhead, no raised bottom frame. `entrance.additional_supports` requests a finite2.6×1.24m local rectangle for the porch columns at top=base; coordinator alone supplies slab/approach from auditedground-.05m. Photograph steps and lower-ground excavations are not copied into the fixed scene datum.

Photograph7768871 camera metadata projects to localXY[963.215356,-176.101958], near the east side of this parcel; camera metadata accuracy and missing readable house number prevent exact façade allocation. It supports nearby terrace character, not confirmed47window counts. Material recommendation is pale stucco, as observed in this local context; final injection belongs to coordinator.

Validation: AST passed; mocked API control-flow/material/finite-index/interface check passed with2sharedsegments and25openings, zero shared-wall overlaps. Roof tessellation was intentionally omitted in that mock, so this is not a Blender or topology test. Current module requires actual assembly, roof/entry rays and all-view visual inspection before acceptance. [Check record](../references/princes_gardens_47/control_flow_check.json).
