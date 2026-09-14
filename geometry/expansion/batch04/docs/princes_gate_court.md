# Princes Gate Court — way-27917475

Stage: module authored, syntax checked, awaiting coordinator Blender integration and numerical/visual QA. No Blender process run by building agent.

The 22-point OSM outline is the large six-storey U-shaped mansion block north of 29 Exhibition Road, not a nearby small historic house or the separate 1–11 Prince's Gate redevelopment. Its 1,454.86 m² full footprint, recessed east-facing courtyard, west returns and original 19.44712 m eaves height remain preserved.

Two search queries located the actual courtyard photograph: Philip Halling, Geograph 396643, 9 April 2007, CC BY-SA 2.0. The original linked JPEG was downloaded and actually viewed. It shows red brick, small-pane white sash windows, pale stone base, two upper horizontal stone bands, stone vertical corner bays and white roof dormers. Westminster's 2017 planning committee indexed excerpt independently describes the recessed frontage, two projecting wings, pitched roof slope and dormers. The PDF itself returned HTTP403; this is recorded as text-only indexed evidence, not a full-document review. No Google imagery was acquired.

The module models six rows of genuine pierced openings around the full concave perimeter, recessed glazing and independent sash joinery. It adds a stone base, upper string courses, two interpreted dressed-stone courtyard return bays and a dressed-stone entrance. The inherited north entrance is retained with wall-projected threshold, recessed door leaf, no bottom rail and no raised doorstep.

Source reconciliation: OSM says flat roof plus one roof level, while the courtyard photograph shows dormered sloping edges. A complete concave flat deck is retained, with individually inset sloping perimeter ranges and closed white dormers only where the range passes an interior footprint check. Exact segments and dormer positions are artistic estimates, not proof of current roof alterations. No invented roof equipment is added.

Common wall: edge 12 contacts 29 Exhibition Road over z=0.05183…13.19978 m. Apertures overlapping that common interval are suppressed while full wall geometry remains; upper openings above the neighbouring eaves may remain. Coordinator must inspect the merged actual roofs rather than equating chimney height with shared-wall height.

Recommended muted red brick palette: masonry (0.30, 0.09, 0.05), trim (0.76, 0.73, 0.66), roof (0.115, 0.125, 0.14), roughness 0.75–0.9. Materials are procedural, with no photo pixels embedded. Photo-informed adaptation contributions are provided CC BY-SA 2.0 with Philip Halling attribution; OSM attribution © OpenStreetMap contributors, ODbL.

Unknowns: rear-window layout, precise pane counts per bay, current dormer alterations, roof drainage/services, measured heights and historic entrance location. The 2007 photo supports architectural vocabulary and massing character, not a complete current survey.

Visual/code review of first batch04 front and rear renders: the dormer cap strips seen above the far sloping-range rear closures are not open-backed or floating. Each dormer already has a rear closure at depth −1.70, extending from H−0.06 to H+2.40; the cap underside is H+2.38, so the rear/side walls overlap it by 0.02 m and reach the main deck. The inward tall dark faces belong to the estimated sloping roof ranges (back closure at depth −2.30, H−0.06…H+2.35); these can occlude dormer walls from the rear, leaving only caps visible above them. Front glazing remains clear and visible. No roof closure change required from the inspected views. The flat central-deck/perimeter-attic roof arrangement remains an artistic approximation, not observed roof-plan evidence.

The entrance central stile was renamed `door central stile` for explicit door-assembly classification. It remains an intentional part of the closed door rather than a passage obstruction. Module re-frozen after syntax validation.
