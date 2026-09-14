# 3 Princes Gate Mews — evidence preparation

Module prepared and frozen against the coordinator contract; assembly and rendered validation pending. Full five-point plan and original edge4 entry are retained.

RBKC official indexed planning search identifies PP/03/02019 at exact3PrincesGateMews: mansard roof addition and elevation alterations granted17December2003; companion CC/03/02020 covers substantial demolition. Direct page open failed, so this is explicitly indexed factual text, not a reviewed drawing. Grant does not establish implementation or2026 appearance. The source2levels/H6.849876m remains an estimate, and a flat roof must not be described as verified existing form.

Mr Ignavy's30September2023 geograph7709856 photo was actually re-viewed, CC BY-SA2.0. It shows white painted brick, divided sashes, slate dormers and a rounded corner. Exact3 is not legibly identified; image is streetscape context only, and its curved corner/dormer layout is not transferable as factual3 geometry. No licensed exact facade or roof has been established. Commercial search snippets interleave recommendation cards with other properties; no dimensions or photographs derived.

Sources and rights remain in ../references/princes_gate_mews_3/sources.json. Proposed model should distinguish retained main-envelope assumptions from possible historical mansard. Original entry must not be replaced by a pictured neighbouring door; previous frame repairs (butt joints and separated crossing faces) apply to all generated frames.

## Editable construction and uncertainty

Retained base0.0000666793 m, main H6.8498760469 m and two floors. The northern facade has three upper divided sash openings, two wider lower casements and the original central entry. Rear edge1 has two windows per floor; the short rear edge2 has only an upper opening above its low neighbour's common-wall interval. Total11 real wall apertures include one door. Exact bays, materials and dimensions remain artistic completion, not photographed no.3 facts.

All three normalized shared segments become independent aperture exclusions. Edges0/3 remain blank over their common heights; edge2 preserves its complete low common wall against way100955530 through z3.698276718. Above that only the prescribed upper window is present. No neighbouring wall is deleted. Original entry threshold, XY and width remain; leaf recess0.34 m and wall thickness0.40 m are authored geometry parameters. No bottom frame or plinth crosses the entry.

The roof is explicitly a **historically motivated artistic hypothesis**: PP/03/02019 approval does not prove its implementation. The complete five-point lower cap at main top+0.008 m, continuous sloped perimeter and upper cap inset0.75 m close one volume. Roof maximum is7.999942726 m (H+1.15 m). No dormer, terrace door, skylight or habitable third level is asserted. Top inset and rise are estimates authorized by the coordinator. Roof base includes every original corner and shared-edge boundary; no convex hull substitutes the source plan.

Roof caps and sides share actual mesh indices. Final meshes compact unreferenced vertices before creation and recalculate normals. Door/window horizontal frames terminate inside vertical frame edges; central bars/transoms have separate face depths to avoid coplanar intersection marks. Mitred eaves top H−0.015 is below the roof base H+0.008. No raised party-wall coping is added.

`build(feature, materials)` uses injected masonry/trim/glass/door/roof/metal and returns created, parameters, openings, roof_parts, observations/uncertainty, and generic interfaces. Entrance includes threshold_xyz, outward_normal, door_leaf_xyz, clear_width_m, clear_height_m and leaf_recess_m; additional_supports/stair_treads/additional_entrances are empty. Shared records include edge/polyline/s_interval/height_interval and openings. Ground−.05 m and its finite threshold support remain coordinator-owned.

## Checks and freeze

AST and a non-Blender mock passed finite vertices, index/material interfaces, all vertices referenced,3 shared intervals and0 aperture conflicts. A separate Shapely triangulation surrogate checks that every roof edge belongs to exactly2 faces after bottom/top caps, without treating this as Blender tessellation or rendering validation. The complete roof has shared indices rather than coincident disconnected caps. Current Blender export, source integration and images must still be checked by the coordinator.

Module SHA256: `5a63d3da79f9dee8e571d5286ec4c87fbb7ddc81b6766dfbdebbfca11226902e`.

Build99890 revealed float32 Vector versus original double tuple mismatch in roof cap lookup. The repaired module resolves tessellator Vector results against its actual Vector inputs (or consumes returned integer indices), then addresses the unchanged original double-precision roof vertex array. No rounding or tolerance change is used. A float32-input/vector-result mock with independent triangle tuples passed, including closed roof edge incidence2,11 apertures and3 shared intervals with0 conflicts. Historical reference check remains the pre-repair artifact; current repaired check was temporary. Blender rerun and rendered review remain pending.
