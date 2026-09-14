# Batch 05 — bounded preparation

Three selected full footprints only. All original source assets and batch04 build inputs unchanged. Batch04 is not delivered or counted complete by this preparation.

## Albert Close (OSM way-642055722)

`way-642055722`: 5 vertices, area 91.674 m², original estimated eaves 13.149974 m, levels 4 (inherited four-floor procedural estimate, not OSM observation).

Entry edge 3 uses wall-plane centre; original leaf point/recess retained separately. Threshold z 0.050287 m.

- Shared edges [1] with `way-81742939`: 10.010 m. Existing basis wall interval [0.05028659858567419, 13.200260443548753]; keep complete shared walls.

## Albert Close (OSM way-642055721)

`way-642055721`: 4 vertices, area 84.600 m², original estimated eaves 13.150506 m, levels 4 (inherited four-floor procedural estimate, not OSM observation).

Entry edge 2 uses wall-plane centre; original leaf point/recess retained separately. Threshold z 0.049627 m.

- Shared edges [0] with `way-81742939`: 10.508 m. Existing basis wall interval [0.04962729290093648, 13.20013286893731]; keep complete shared walls.

## Mews outbuilding (OSM way-1154608369)

`way-1154608369`: 4 vertices, area 52.870 m², original estimated eaves 3.700263 m, levels 1 (OSM levels).

Original asset has only masonry and roof, zero estimated windows, and no door/support mesh. `entry=null`, `small_solid_outbuilding=true`. OSM explicitly records one level. Do not turn this into a speculative multi-storey building or invent a mapped entrance. Any later added door must be separately labelled artistic and receive a real ground-interface contract.


## Validation and context

All three polygons are valid CCW. No positive-area way/relation overlaps, parent memberships or asset part aliases. A bounded source decode was required because batch04 context did not include the targets. New context contains 42 buildings / 585 meshes and every exact audited target/35 m neighbour ID. Actual per-object source provenance is retained. Only previously delivered batch02/03 replacement geometry is incorporated. The current staged batch04 modules are represented only as explicit height hints in features, not as completed geometry.

Reusable `prepare_expansion_batch.py` now handles existing assets without a door: null entrance, preserved one-level tags and source roof height. It never fabricates a default entrance to make preparation pass. It only writes selected batch files. No Blender or automatic completion transition was performed.
