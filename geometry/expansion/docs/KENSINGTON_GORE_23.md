# 23 Kensington Gore — authored single-building module

Stage: **module authored; assembly/visual QA owned by coordinator**. Not a claim of survey or photo-matched reconstruction.

`geometry/expansion/modules/kensington_gore_23.py` exports `build(feature, materials)`. `feature` is the coordinator’s projected `feature.json` with exact CCW `ring`, `base_z`, `height_m`, and `entry`. Materials must include Blender material values for `masonry`, `trim`, `glass`, `door`, `roof`, `metal`; use the original masonry 3 and adjoining scene’s material palette. Module creates only new mesh objects in the active collection and returns JSON-serializable `created` names, parameters, openings and interfaces. It does not clear or export a scene, change shared materials, or acquire data.

## Geometry

Complete OSM concave footprint is retained. Four storeys use the inherited 13.15 m estimated wall height, base z=0.05 m supplied by coordinator. Shell walls have 0.38 m thickness and are built around real apertures, not solid walls behind applied windows. Glass sits 0.33 m behind the facade. Each aperture has thick sash frames, mullions, architraves, stepped lintel and projecting sill. The first upper storey has shallow guard rails on selected public elevations. Banding and stepped cornice organize the elevations. The west edge is conservatively blind; adjoining walls need coordinator visual inspection.

The eastern entrance retains feature.entry centre `[519.6182046930795,106.01294227927758]`, uses the edge-normal projection for the leaf/opening, retains 1.05 m clear width, and returns threshold z=0.05 m to meet existing support z=0.044 m. No invented basement stairs, underground lightwell or external ramp is added. Door hardware and a transom provide architectural depth. Coordinator owns the finite support patch and path continuity.

The roof deck is tessellated over the full concave ring using Blender’s polygon tessellator; no convex hull. A low parapet/coping and a small interior hipped roof volume are **artistic completion**. That volume’s rectangle is checked within the source footprint; no observed roof-equipment claim is made.

## What is known and what is imagined

Known from local OSM: complete mapped footprint, address, residential tag and four levels. Retained from prior model: approximate overall height, existing entrance vicinity and finish palette. Everything else—window numbers/proportions, facade composition, side/back elevations, roof structure, cornice and rails—is explicit artistic completion authorized by the user.

Eight bounded search queries found no confirmed photo of this exact building. Two CC BY-SA photographs were downloaded and visually inspected: Richard Croft’s 2011 Kensington Gore view and Oxfordian Kissuth’s November 2009 street view. They show neighbouring red-brick residential architecture, dressed pale surrounds, sash windows, ironwork and grey upper roofs. They are **style context only**. Adjacent 25 Kensington Gore’s Historic England OGL description supports nearby stucco/slate/classical detailing but does not establish the design of number 23. Do not transfer either source’s precise bay counts or scale as observed evidence.

Source URLs, licences, image inspection status and hashes are recorded in `references/kensington_gore_23/sources.json`. No image texture is embedded; there was no Google Maps capture/derivation. References remain openly attributed. Preserving existing masonry 3 may differ from neighbourhood photograph hues, intentionally avoiding a claim of target colour observation.

## Checks and remaining work

Python AST parsed successfully. Projected ring is CCW and the interior roof rectangle is fully contained by the Shapely footprint. A first py_compile invocation could not write the system cache; AST validation avoids bytecode creation. Coordinator must run Blender assembly, check object ownership/materials/bounds and roof triangulated area, inspect front/entry/roof/rear views, independently reimport the export, and verify neighbour/ground clashes before delivery. This module alone does not finish those checks.
