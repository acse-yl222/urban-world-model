# Batch11 preparation only

Prepared three complete mapped polygons from local OSM, original6181-asset index and decoded core008 GLB. No images researched, modules written, Blender run, global queue changed or completion added. Authoritative delivered snapshot remains20 through batch08. Batch09/10 are staging only and were not used as delivered geometry. Context extraction considered delivered02–08 overlays; none intersected the26 bounded source asset IDs, so context geometry remains original GLB.

| Target | Vertices | Source levels | Estimated wall height | Entry edge |
| --- | ---: | ---: | ---: | ---: |
| 69–70 Princes Gate,851362854 | 8 | 5 | 16.301509m | 6 |
| 71–72 Princes Gate,851362855 | 14 | 5 | 16.301178m | 0 |
| 1 Princes Gate Mews,851362835 | 5 | 2 | 6.850189m | 4 |

All targets explicitly retain procedural-baseline semantics, no protected74 identity, no source parent or part aliases, no positive mapped overlap, no holes and no simplified/cropped vertices. Source addresses and level tags are not independently photographed identity/height verification.

Shared geometry includes disconnected segments.69–70 meets71–72 on edges1/5 and the church on7.71–72 meets69–70 on9/13 and V&A relation29795 on2/6. These are represented as exact `normalized_shared_wall_segments` as well as original MultiLineString geometry. A kernel accepting only LineString would silently miss required opaque walls.1Mews shares edges1/2 with85Mews/2Mews. Original neighbouring eaves are estimates, not surveys. Church and V&A are indexed baselines; the proximity to a named museum does not make their13m baseline accurate. Science Museum and Dyson Design are protected neighbours within35m but not directly shared; their common-wall height is null, and roof maxima must not replace it.

## Ground audit requires different treatment per door

`source_ground_audit.json` tests actual transformed mesh triangles, using barycentric vertical hits at each wall threshold and0.5/1m outward. Candidate names/semantics include all ground, terrain, pavement, sidewalk, entry-support, road, path, paving and asphalt meshes, including Traffic_road. Bounds only cull triangles or describe nearby no-hit objects; a large bounding box is not treated as supporting surface.

69–70 thresholdz=-0.001069m has ground-0.05m at the wall; roadz0 appears at0.5/1m.71–72 thresholdz=-0.000595m lies approximately6.86cm below existing East_road_correction pavingz0.068 at all three samples.1Mews thresholdz=-0.000039m has roadz0 at the wall/0.5m, but a Traffic_road surfacez0.25 also appears at1m. All three lack original per-building support. These source display heights are not surveys. Do not translate buildings or blindly add identical-.05 approaches. The coordinator must choose finite transitions or local surface handling while retaining documented original interfaces.

The report and each feature contain all hits and highest source surfaces. All raw source assets remain unchanged; only batch11 features, manifest, scripts and preparation reports were written. Context has182 meshes for26 bounded building IDs and includes nearby bridge851362857 for later clearance investigation; no bridge semantics were converted to ordinary walls.
