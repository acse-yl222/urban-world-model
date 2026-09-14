# Batch 09 uncertainty and interface boundaries

Preparation record only. Numerical integration, roof closure, entry support and final visual acceptance belong to the coordinator. This document does not declare delivery. The 778 roof module is undergoing its author's slope-gap correction; claims about its final mesh must follow the ensuing build and review, not this source summary.

## Building identity and form

| Asset | Supported evidence | Estimated or unresolved |
|---|---|---|
| 809238778, 1 Hyde Park Gate | Full six-point mapped footprint; source five levels; licensed 2022 north-corner photograph shows local tower and rounded-dormer mansard | Historical 1a Queen's Gate tower assigned to eastern return by spatial inference, not cadastral proof. Tower base 6×6m at edge4 s≈7m and inward≈3.4m is an estimated contained placement, not independently mapped. Rear faces, precise ornament and dormer placement remain estimates |
| 809238777, Cheval 2–4 Hyde Park Gate | Official property identity; HE five-storey terrace description; same licensed north-group photo establishes continuous mansard/dormer character | Exact division of photo bays across parcel boundaries remains uncertain. Seven authored north bays/dormers, rear openings, attic extent and detail dimensions are artistic interpretation. No tower is assigned to Cheval |
| 809238779, 1–2 Queen's Gate | Complete 18-point footprint and five source levels; two licensed entrance photographs identify number 2 and show columns, doorway and balustrade | Separate southern block, not the north-group tower. Entrance photos do not show roof. Main H≈16.29945m retains source level-derived estimate; flat roof/parapet, hidden facades and most spacing are artistic completion. Delicate ornament is simplified |

RBKC §3.24 describes a thirty-metre tower without an explicit ground datum, top endpoint or survey precision. A rough same-face photographic ratio suggested a broad main-cornice range about 20–23m. The coordinator selected **21.5m main height above each base** jointly for 778 and Cheval, with **2.5m attic rise**; these are visual estimates. Their local tower target is **base+30m**, a rounded interpretation of the prose. Perspective, depth and uncertain grade prevent treating this as calibrated photogrammetry. Old level-conversion heights remain baseline provenance; neither their replacement nor extra detail proves metric accuracy. All five storeys regenerate from the new main height rather than stretching one top storey.

## Ground and entrances

[Source-ground audit](../reports/source_ground_audit.json) decodes original `south_kensington_core008_web.glb` triangles and tests each entry plus 0.5m and 1m outward points. The nine sampled positions hit `Site | ground` at **z=-0.050000000745m**. This is a source-scene baseline plane, not surveyed street topography; road/path/paving/traffic checks do not justify substituting a surface from another batch. No per-building original entrance support was found.

Preserved thresholds are approximately -0.00002597m (778), +0.00112269m (Cheval), and -0.00000515m (1–2 Queen's Gate). Door centres are projected onto mapped wall planes while retaining original leaf centres separately; the old roughly 16cm leaf recess must not be interpreted as a footprint error or moved doorway. Coordinator-authored finite supports connect the sampled source ground to these near-zero thresholds. Cheval and 1–2 supply additional support polygons for portico columns. Module requests do not establish that a support slab already exists or has passed inspection.

Entrance photos show steps at number 2, but uncalibrated imagery cannot determine their absolute levels against this scene. No guessed staircase, excavated basement or basement window pit is introduced. Listing-reported basements are architectural facts, not permission to invent terrain interfaces.

## Shared walls and roof boundaries

778 edge0 and Cheval edge6 retain full-main-height opaque party walls after the coordinated 21.5m correction. Remaining adjacency constraints use feature intervals; neighbouring source-model heights are estimates, and whole walls are retained. Cheval's existing attic XY stays contained with minimum inset about 1.489m; its 2.5m roof and dormers create no new shared-boundary contact. Existing cornice projection up to 0.42m and front porch/balcony extents still require seam review. The estimated local 778 tower is inside its footprint and away from the Cheval shared edge; containment is not proof of real tower dimensions.

1–2 Queen's Gate edge15 is blind against 3 Queen's Gate. Its edge3 is blind below the inherited 24a Mews wall interval around 6.8495m, with upper wall openings subject to coordinator collision review. The batch10 24a module subsequently removes raised parapet/coping on attached edge4, retaining a complete deck and only a modest eaves top about H+0.02m there; this is a staged adjacent design, not an independently validated existing condition.

Full concave source footprints remain the basis of the roof decks. Dormer cuts, roof joins, finials, columns and shared seams need actual mesh checks and multiple views after assembly. Python syntax or GIS containment alone does not validate those features. No live-browser, full-city, survey-accuracy or completed-delivery claim is made here.
