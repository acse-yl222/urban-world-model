# 2 Princes Gate Mews — way-851362836

Module prepared and frozen for coordinator integration; no Blender or rendered validation performed here.

Identity and shape use the supplied OSM feature: five-point footprint83.239888m², two tagged storeys, source estimated main height6.849683905m. The source base/entry threshold0.000117231m remains dynamic. The north-facing edge4 original projected entrance is retained; source leaf depth is archival evidence rather than a measured door survey. Modeled leaf is recessed0.34m into a0.40m real wall opening.

## Evidence and attribution

[OpenStreetMap way851362836](https://www.openstreetmap.org/way/851362836), ©OpenStreetMap contributors, ODbL1.0, supplies local-snapshot footprint/address/levels. This is not a claim to current field measurement.

[Princes Gate Mews, geograph7709889](https://commons.wikimedia.org/wiki/File:Princes_Gate_Mews_-_geograph.org.uk_-_7709889.jpg), Mr Ignavy,30September2023, [CC BY-SA2.0](https://creativecommons.org/licenses/by-sa/2.0/), was actually viewed during this task. Local photo is unmodified. Brick walls, pale divided sash windows, simple eaves and dark carriage doors are visible. Target2 cannot be bound to a readable number, so this is explicitly **context only**. No exact window count, garage, upper extension or roof is copied as a factual2 feature. Source ledger and photo hash: `references/princes_gate_mews_2/sources.json`.

Bounded official address searches did not yield a usable exact2 form description. RBKC records for1,14,22,34,68 and85 were not transferred to2. A tour's stop#2 is an ordinal, not an address. No commercial unlicensed photograph or Google tiles were used for geometry.

## Editable construction

Four upper front sash openings and two broader ground casement openings flank the original central entry; the rear exposed edge2 has two windows per floor. Total11 true wall apertures including one door, with full wall-depth piers, lintels, recessed glazing, sash frames and simple brick headers. The pattern, dimensions, pipe and trim are artistic completion, not surveyed details. There is no invented garage opening, front portico, basement, extra storey or roof plant.

All three `audit.normalized_shared_wall_segments` are independently projected to local edge intervals. Edges0/3/1 against1/3/85 retain complete walls and have no conflicting windows. Main walltop6.849801137; roof cap6.857801137; estimated maximum coping7.149801137. The cap tessellates the complete original polygon, including its fifth corner. Raised parapet/coping occur only at free edges2 and4 and stay within the mapped plan. Shared edges have no raised parapet. Roof cap is8mm above walltop and last eaves-band top is15mm below walltop to avoid coplanar black lines. Parapet bottoms penetrate the cap; tops are distinct planes.

`build(feature, materials)` consumes only injected masonry/trim/glass/door/roof/metal. Returns created names, parameters, openings, roof_parts, observations, uncertainty and generic interfaces. `interfaces.entrance` includes threshold_xyz, outward_normal, door_leaf_xyz, clear_width_m, clear_height_m and leaf_recess_m; no additional supports/ramp are authored. `shared_walls` includes all three polyline/s_interval/height_interval/openings records.

Original ground samples are-.050000001m. Ground-to-threshold support belongs to the coordinator. This module does not inherit1's virtual ramp or change the source entrance. Adjacent source wall heights and detailed neighbour context are estimates; no original assets are removed here.

## Checks and freeze

AST parse and mocked Blender control-flow/material/index/interface checks passed: finite vertices, valid face indices,11 openings,3 shared records and0 aperture/shared-height conflicts. Mock tessellation is intentionally omitted, so these are not roof topology or Blender rendering tests. `references/princes_gate_mews_2/control_flow_check.json` records this limitation. Coordinator must inspect current assembled views and ground interfaces before delivery.

Module SHA256: `5aa20327ed290156fd79c52a68f1552ec62e1298d32e3e6adfd7ab17c91fafb1`.

Roundtrip repair: partial-edge bands allocated four unused vertices each in three meshes. Mesh output now compacts referenced vertices and remaps face indices without moving any face. Mock checks additionally require every emitted vertex to be referenced. Blender/GLB roundtrip revalidation remains with the coordinator; tolerances were not changed.
