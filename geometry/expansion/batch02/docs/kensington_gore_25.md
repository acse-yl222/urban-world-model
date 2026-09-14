# 25 Kensington Gore — batch 02 module

State: **authored; awaiting coordinator assembly and visual QA**.

`modules/kensington_gore_25.py` implements `build(feature, materials)`. Requires CCW ring in the agreed EPSG:32630 local metre frame and coordinator-supplied Blender materials named masonry, trim, glass, door, roof and metal. Use pale stucco for masonry, limestone/stucco for trim and dark metal for sash frames. The module only creates new objects in the active collection, with unique `building_id` / `research_object_id`. It returns created names, parameters, `interfaces.entry`, architectural observations and uncertainty.

## Individual design

Historic England list entry 1275267 identifies three principal storeys, attic, stucco, slate, a canted bay, polygonal corner, first-floor balcony, coupled Ionic porch columns and pedimented dormers. The module follows these building-specific features. It retains all 26 mapped perimeter segments and the approx. 389.977 m² footprint; no convex hull and no adjoining wall deletion. Main wall is the supplied approx. 10.0 m inherited estimate; attic adds 2.3 m. Neither height is a measurement. Eight principal northern window positions are distributed over the mapped bay returns; exact spacing is interpreted.

Wall panels are constructed around real holes with 0.4 m thickness and glazing recessed 0.34 m. Dark sash frames, pale architraves, projecting sills, segmental and triangular window hoods, quoins and brackets are geometry. A continuous mitered cornice uses common offset-loop vertices, avoiding independent box end gaps. Front/corner balconies have rail beams, turned balusters and supporting slabs, rather than unsupported balusters. Two small chimney stacks have estimated positions.

The roof uses the full concave mapped ring and a continuous 0.9 m inset ring for a mansard attic; the top is tessellated over the concave inset. The inset was checked valid and completely contained in the footprint. Dormers have true front apertures, recessed glazing and projecting pedimented roofs. Their rear construction/roof profile remains estimated. No basement void was cut; the source-reported basement is documented but omitted from exterior excavation.

## Entrance interface

Latest coordinator feature supplies the northern edge 5 entrance, centre `[489.53412288116346,109.79207841907818]`, clear width `1.0487051118960364 m`, threshold z `0.05016532631000725 m`, support z `0.044 m`. The opening projects this supplied location onto the same mapped edge; the metadata returns the original centre/threshold. A slight Ionic-inspired paired-column porch projects about 0.85 m, with the column bases seated on a finite slab. The coordinator must inspect the supporting apron and neighbouring paths before final export. Column capitals are simplified estimates, not exact carved Ionic ornament.

## Evidence and uncertainty

Two Mike Peel photographs from 2025-05-07 (CC BY-SA 4.0) were downloaded at original resolution and actually inspected. They show the Queen’s Gate/Napier statue corner ensemble, with pale ornate stucco, black sash frames, cornices, balustrades and upper dormers. They include adjacent properties and statue/vehicle occlusion; precise assignment of every visual detail to this footprint is uncertain. Target-specific type and storey count rely on the Historic England official list entry, not a claimed direct measurement from photos.

Sources/licences/hashes/inspection status: `references/kensington_gore_25/sources.json`. Photos are unmodified references; none is an exported texture. Street-facing proportions, posterior facades, roof angles, ornament, dimensions and chimney placement are artistic/visual estimates explicitly allowed by the user. No Google imagery/tiles were acquired or derived.

## Checks

Python AST valid. Signed footprint area is positive (CCW). Miter inset polygon is valid, area 308.171 m² and covered by the full footprint. No Blender process was run by this agent; numerical mesh tests, entrance/ground continuity, neighbour intersections, roof views, final reimport and front/rear visual checks belong to the coordinator. Authored detail is not a claim of survey accuracy or completed visual verification.

Coordinator review corrections: roof caps accept Blender tessellator integer or Vector returns; all output mesh normals recalculated with bmesh. Continuous ground-level plinth removed to keep the doorway clear. Door has no lower/mid sash rail, centre stile or projecting sill across its threshold; window components retain those details.


Coordinator update 2026-09-13: integrated locally; native reopening, independent GLB import, material/entry/roof checks and current rendered views passed. See STATUS.md for final scope and limitations.
