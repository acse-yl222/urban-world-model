# Roof evidence investigation and deferral

Date: 2026-09-13. Target: way-850407202. Decision: pending evidence; excluded from active batch07 validation. No replacement module was authored and no source asset was changed.

The complete original prepared feature is preserved byte-for-byte at ../deferred/campus_roof_850407202.json. Context intentionally retains the original asset. The initial geometric audit remains roof_semantic_audit.json. Its suggested future roof-specific authoring is superseded by this deferral until support and clearance evidence is available.

## What is established

OSM maps building=roof, layer=1 on a five-point, approximately 32 by 6.5 metre strip (208.120 square metres). Layer is relative ordering, not a metre height or a storey count. The footprint touches RCS1 along 32.127 m, Science Museum along 6.490 m and Dyson along 32.049 m. No positive-area mapped parent overlap or parent/part alias was found in the bounded audit.

Original geometry is a generic masonry extrusion capped at z=3.749381 m, explicitly labelled typology estimate. Its 3.698762 m extrusion does not establish a real canopy or support height. Neighbour geometry maxima include roofs and other features and cannot supply the target elevation.

## Evidence and limits

The [Imperial August 2023 article](https://www.imperial.ac.uk/news/247075/peter-cheungs-reflective-journey-stepping-down/amp/) confirms a completed sheltered link between Dyson and RCS1. The [July 2024 article](https://www.imperial.ac.uk/news/254703/summer-holidays-what-they/) announced replacement of RCS1 mezzanine roof/skylights. These may describe different structures; neither identifies the complete OSM strip or establishes metric support height. Only factual text was used, with no copyrighted imagery acquired or derived.

AccessAble search-index text describes access from Dyson level 2 to RCS1 level 1 via lift/stairs; its direct page returned 403. The RCS1 evacuation PDF also returned 403 and remains an indexed lead, not an inspected plan. Named floors are not calibrated elevations.

One image was downloaded and actually inspected: Shadowssettle, RCS 1 Chemistry Building, 23 November 2019, [Commons source](https://commons.wikimedia.org/wiki/File:RCS_1_Chemistry_Building,_Imperial_College_Road.jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). It shows the ornate street facade and entrance, not this narrow roof or its supports. It is context only, not an exported texture or target reconstruction reference. Attribution, file hash, access status and limitations are recorded in ../references/campus_roof_850407202/evidence.json. Five search queries and one inspected photo were sufficient to reach this bounded conclusion.

Roof form, structural support type, roof elevation and clearance range remain unknown. No numerical support range is asserted. A directly identified licensed oblique/aerial image or sectional/elevation evidence is needed before geometry refinement. Original source asset remains in place; this roof is not completed.

## Two-wing independent scope

Active manifest contains only way-703836510 and way-1133279024. Their modules each implement a complete footprint, roof and entrance contract, and have no dependency on the deferred roof ID. Both parse successfully with Python AST. They can proceed independently to the coordinator's Blender assembly, interface and visual validation. This scope review does not claim validation or delivery.

The ordinary wing names are working labels; retained baseline heights and four-storey assignments are estimates. Campus rear retains opaque shared edges against ACEX/Sherfield because precise shared-wall top heights are unresolved. Queens Gate rear has no exact shared boundary in the audited footprint set. Licensed contextual photos do not establish exact facade layouts for either target.
