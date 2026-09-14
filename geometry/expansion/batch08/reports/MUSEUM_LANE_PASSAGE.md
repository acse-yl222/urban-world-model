# Museum Lane passage interface, way-850528336

The current bounded OSM map query identifies **way-699773494**, named Museum Lane, `highway=service`, `tunnel=building_passage`, `access=private`, with5mph maximum speed. It joins western way4907924 and eastern way699773493. This is a direct mapped passage, not an inferred axis through a rectangle centroid.

West threshold is `[873.3066294457531,-348.2019856693223]` on target **edge4**. East threshold is `[881.086946954485,-347.0218340763822]` on **edge1**. Both have zero mapped-boundary distance. The axis center is `[877.196788200119,-347.61190987285227]`; west-to-east direction `[.9886907285879792,.14996880743731614]`; length through footprint7.869313713m. Coordinate frame is the established EPSG32630 local Blender east/north/up frame. Preserve complete footprint and create passage through its full depth. The old generated door lies elsewhere on edge5 and is not the evidence for this passage.

No width, height or elevation tag was returned. The module author's proposed4m clear width is a labelled visual/artistic estimate, not an OSM or surveyed dimension. The auditor actually inspected the exact-building licensed `museum_lane.jpg` already acquired by the building agent: central round arch, iron gate and narrow flanking pavement are visible. The photo supports an arch/gated passage; it does not calibrate metric dimensions or prove current public access. See that agent's `references/campus_wing_850528336/sources.json` for Jpbowen2012 photo rights and RBKC section4.15 identification. No remote-west335 imagery was used.

The local `agents/demo_rev02/data/roads.json` has no passenger lane within25m of this footprint. That filtered traffic display cannot substitute for the service-passage map, and its default3.2m lane parameter is not a passage width. Its display elevation is likewise not surveyed ground.

Source: one small bounded OpenStreetMap API map request, retrieved2026-09-13, saved `museum_lane_osm.xml`; © OpenStreetMap contributors, ODbL, https://www.openstreetmap.org/copyright. Full relevant path coordinates and tags are in `museum_lane_paths.json`; exact interface/provenance in `museum_lane_passage_interface.json`. No features, modules, global state or original assets were modified by this audit.

## Original surface profile

The five-point source GLB inspection covers west-.9m, west wall, passage center, east wall and east+.9m. Each point hits original ground at-.05, road-network at0, extension ground001 at.0143625438 and extension road-network001 at.0287593144m. The original traffic road MuseumLane segments4907924/699773494/699773493 cover all five points at **z=.25m**. These are display/model planes, not surveyed grade.

If original traffic-road geometry is visible, its .25m plane is the uppermost road surface and the passage floor should coordinate with that active layer. If viewer filtering hides original traffic geometry and the replacement passenger-lane layer omits the private passage, .0287593144m is the surviving source road plane. The coordinator must choose the active rendering state explicitly before fitting the floor; no .044 or .05 support assumption is justified. Raw per-object triangle hits are in passage_ground_audit.json and reproduce via inspect_passage_ground.mjs. No source terrain or module was changed.
