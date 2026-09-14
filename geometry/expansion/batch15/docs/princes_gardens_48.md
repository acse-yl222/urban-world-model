# 48 Princes Gardens — evidence preparation

Module prepared and frozen against the coordinator's current contract. Blender assembly and rendered review remain pending.

The [Westminster planning report dated 23 October 2018](https://westminster.moderngov.co.uk/documents/s29524/ITEM%2004%20AND%2005%20-%2048%20PRINCES%20GARDENS%20LONDON%20SW7%202PE.pdf), §6.1–6.2, identifies 46–48 as three houses with five storeys above basement, linked to 78–80 Princes Gate Mews. It records implemented 2007 windows/rear extensions/terraces/plant works. Only public factual prose is used; no broad reuse license for document photographs or plans is claimed. The report is historical, not a 2026 as-built survey.

The David Martin 2024 CC BY-SA 2.0 Grand entrances image was actually re-viewed. It supports the group's pale stucco/classical vocabulary, but no 48 number or exact parcel assignment is established. Doric porticos and balustrades must not be moved to the source rear entrance. The supplied entry edge 3 points south and remains fixed; exact modern rear details are unknown.

A new Christine Matthews 2008 CC BY-SA 2.0 image (geograph 1128862) was downloaded and actually viewed. Despite its Commons caption calling the dominant building 48, camera metadata locates it on the north side of the square beside Ethos, while the supplied target is south. The visible sports-centre adjacency is consistent with that conflicting northern view. This is retained as a rejected exact-identity lead; it cannot substantiate target 48's bays, porch or roof. No reliance on the caption alone.

Planned model retains the full five-point footprint, five source levels and estimated 16.299748 m main height, with true recessed windows and complete roof. Source rear entry is preserved; hidden roof and rear window detail remain explicitly estimated. Ground and normalized adjacency remain owned by the coordinator; the module consumes the frozen contract. Full provenance/hashes are in ../references/princes_gardens_48/sources.json.

## Construction and interfaces

The complete five-point 219.964202 m² polygon remains unchanged. Main H=16.299748255 m, dynamic base=0.000240307 m, five floors use proportional intervals [0,.225,.455,.655,.835,1]. Three narrow north-front bays provide tall first-floor casements, upper sash windows and restrained group-context stucco dressings. The south rear uses two bays where the original offset door permits; there are25 actual apertures including the source door. The short western return stays solid. Precise bay placement, balustrades, mouldings and rear layout are artistic completion. No front entrance or Doric porch is inferred; the source rear door remains at edge3, XY[951.318065754,-204.691238039], clear width1.049627404 m and original threshold. Leaf recess is0.35 m within a0.44 m wall.

Both normalized shared segments are preserved independently. East edge4 against delivered47 uses the feature interval. West edge1 against way158555530 has no scene asset or known height: source_neighbour_height_interval remains null, while the operational height_interval is explicitly a full-target aperture exclusion. This does not assign a height to the missing neighbour. No shared walls are deleted and neither segment contains an aperture.

The complete footprint roof deck is at absolute z16.307988562 (H+.008); estimated front/rear parapets on edges0/3 reach16.739988562. Shared side edges have no raised parapets. Continuous mitred stringcourses remain contained; their last top and the front cornice top end at H-.015, separated from the cap. Geometry is grouped by semantic component/material, with normals recalculated and unreferenced vertices compacted before mesh creation.

`build(feature, materials)` returns created, parameters, openings, roof_parts, observations, uncertainty and interfaces. Generic entrance includes threshold_xyz/outward_normal/door_leaf_xyz/clear_width_m/clear_height_m/leaf_recess_m and no authored additional supports, stairs or ramp. shared_walls returns2 polyline/edge/s_interval/height_interval records with explicit source-height semantics.

The original ground is-.05 m through.9 m outward, then the original road is0 m at1 m. The coordinator's finite approach profile handles this transition; this module supplies no ground and makes no accessibility claim. Existing source entry and footprint are not shifted.

## Validation and freeze

AST parse and mocked Blender control-flow/material/index/interface checks passed. All emitted vertices are finite and referenced; face indices are valid;25 openings have0 conflicts with the2 shared exclusion intervals. Mock roof tessellation is deliberately omitted, so this is not Blender, roof-topology or rendered validation. No global inputs or neighbour assets were modified.

Module SHA256: `6d38636f9c5d7c03b6e7c11a92b474b981b683d1bdc28e97fc18effed43bfe1a`.

Entrance/frame joint repair after first build86045: vertical stone surrounds now end at the stone head underside; sash/entrance top rails and sash horizontal rails terminate inside the side-frame edges. First-floor central mullions stop inside upper/lower rails and their face is10mm forward of meeting rails. Window architrave uprights also end below the head and above the sill, removing analogous coplanar corners. Original aperture bounds, door pose, full footprint, roof and shared interfaces remain unchanged. AST/mock checks still show25 apertures and0 shared conflicts. Current rebuilt images must verify the repair; no tolerance changes or Blender run by author.
