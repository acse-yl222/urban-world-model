# 71–72 Princes Gate / way-851362855

Module prepared for coordinator integration, not delivered. `build(feature,materials)` uses masonry/trim/glass/door/roof/metal and returns created names, parameters, generic entrance/shared-wall contracts, opening records, roof parts and evidence IDs. No Blender was run by the author.

## Observed and source-reported

The actually viewed [Elekes Andor 2010 photograph](https://commons.wikimedia.org/wiki/File:71-72_Princes_Gate,_Kensington,_September_2010.jpg) is **CC BY-SA3.0**. Visible72 and distant69–70 column lettering establish this entrance group. It shows white channelled stucco, a deep Doric porch, square column feet, triglyphs, sash windows, a wooden panelled door/transom and lantern pair. Editable simplified geometry adapts those features; no pixels are used as textures. Detailed ornament and measured placement are not established. Its steps and basement railings are visible but not calibrated to this scene.

[Historic England1266085](https://historicengland.org.uk/listing/the-list/list-entry/1266085) supplies the late1860s classical group, five main storeys plus basement, three windows per historic house, columned/balustraded first floor, second-floor balcony/pediment details and bracketed cornice. Official text is OGLv3; HE photos/maps excluded. [RBKC appraisal§3.32](https://www.rbkc.gov.uk/sites/default/files/media/documents/Queens%20Gate%20Conservation%20Area%20Appraisal_0.pdf) adds later mansard roofs and first-floor French casements. Only factual prose is used, not unlicensed PDF photographs. See [source ledger](../references/princes_gate_71_72/sources.json).

## Geometry and uncertainty

All14 mapped corners and416.897m² are retained. Main wall uses the current feature's16.301177789m above base; five levels use fractions[0,.225,.455,.655,.835,1]. This remains a source formula estimate, not surveyed height. Six frontage bays represent two historic three-bay houses; exact spacing and original inter-house division are estimates. Ground windows are omitted where the preserved single entry requires clearance; no second guessed door is added.

Walls have actual .44m-deep openings and .35m recessed glazing/leaf. Upper and ground details differ, with Corinthian-inspired first-floor shafts/capitals, French casement bars, selected central pediments, turned balustrades, cornice hoods, modillions and channel strips segmented around apertures. Complex leaf carving is simplified. Rear additions/return windows are estimated; narrow notch cheeks remain opaque.

The complete concave roof is capped at base+H. An additional **1.8m estimated mansard**, consistent with official roof-form prose, follows the same concave outline at lower inset.30m and upper inset1.20m. Both offset rings passed independent GIS validity/containment (outside area0); upper/lower areas301.924/387.117m². Absolute roof maximum18.175177793m. No rooftop plant, chimneys, dormers or terrace railings are invented without roof evidence. Roof metric form is not visible in the acquired close photo.

## Interfaces

Current coordinator base/threshold **.074000003695m** is6mm above decoded visible paving **.068000003695m**, replacing the original buried pose archived in the feature. Original tangent XY[928.063380846,-286.714291760], edge0 outward[-.984781590,-.173796490,0], clear width1.051148037m retained. No raised door-bottom frame, guessed stairs or basement excavation. Door leaf is recessed .35m with2.88m head. `entrance.additional_supports` requests a finite2.6×1.24m rectangle for twoDoric column feet, top=base; only coordinator authors ground support.

**All four normalized shared segments** are consumed directly: edges9 and13 against69–70, and edges2 and6 againstV&A relation29795. Contract includes each exact polyline, along-edge interval, clipped common-height interval and empty opening list. Every planned window is tested against every segment, so disjoint MultiLineString pieces are not lost. Main shared walls remain complete. 69–70 author supplied mainwalltop16.30043975 and estimatedroofmax18.10043975; The approximately.07474m difference between the two authored main wall tops comes from the coordinator baseline correction, not a measured street slope. No raised shared-edge parapet/coping is authored. Continuous mitred bands stay within footprint; projecting cornice/balcony is restricted to free frontage with trimmed ends.

## Validation boundary

AST parsed. A **mocked API control-flow check**, explicitly omitting roof tessellation, executed all authoring branches: finite vertex/index/material checks,4 shared contracts,64 openings and zero overlapping shared-wall openings. This is not a Blender test, mesh closure certification or visual review. Evidence is in [control-flow record](../references/princes_gate_71_72/control_flow_check.json). Coordinator must build, test roof/entry interfaces, inspect all current views and decide integration/delivery. Material injection should use observed pale stucco, without changing protected neighbouring assets.
