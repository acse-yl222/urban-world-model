# Jamaican High Commission / way-641603104

Stage: authored module, Python syntax checked, frozen for coordinator assembly. No Blender process launched by building agent.

The newly prepared footprint places this building south of 29 Exhibition Road, sharing a 10.014 m north wall. This resolves an earlier ambiguity: the well-photographed double-gabled Prince Consort Road facade belongs to this southern asset. The northern 29 asset should not duplicate its portico. The new batch includes a separately corrected copy of 29.

Actually inspected source: Robin Sones, *Facade, Jamaican High Commission, Prince Consort Road*, 11 February 2020, Geograph 6577546, original 640 × 480 JPEG, CC BY-SA 2.0. Historic England 1211833 text was reviewed under OGL v3.0. The photograph shows twin major gables, central small dormers, tall chimneys, a balustraded central double-arch portico, red brick and white small-pane sash windows. Sources/attribution/hash are recorded in `../references/jamaican_high_commission/sources.json`.

Authored interpretation: three main storeys use the inherited 13.14977 m eaves height without reducing the original wall envelope. The south frontage has six sash axes, real recessed window openings, segmental heads, cut-brick details and a true open double-arch portico. Twin gabled roof ranges contain pierced attic windows, central small dormers and high chimneys. Roof floor covers the complete concave polygon. Decorative dimensions, roof intersections and unseen elevations remain artistic estimates.

Entrance contract: preserve original south doorway lateral position and project threshold onto its mapped wall; recess the independent door leaf. No door bottom rail, no lifted leaf, threshold slab top equals base. The central portico pier is shifted away from the inherited door axis so it cannot block the opening. Photographed historic terrace elevation is deliberately simplified at the existing scene threshold; no basement or stairs/ground cuts are invented.

Shared interface: entire north edge 1 is a retained blind wall with no new speculative apertures; its geometry is not deleted. All other concave returns remain. Coordinator owns support geometry, merged shared-wall checks and final QA.

Suggested material colors: muted brick masonry (0.30, 0.105, 0.060), roof (0.24, 0.072, 0.04), trim (0.76, 0.73, 0.65), all procedural. Geometry informed by Robin Sones's CC BY-SA 2.0 photo is an adaptation provided CC BY-SA 2.0 with attribution; no photograph is embedded as a texture. OSM plan retains © OpenStreetMap contributors attribution under coordinator ledger.

Entry support addition: a finite 1.55 m deep portico slab covers all three piers, top at inherited z0 and bottom z0−0.006 m; it does not form an elevated threshold. This authored slab is owned by the module.

## First export visual review — batch03_v1

Actually viewed front, entrance, roof, rear and context renders and compared to inspected Geograph 6577546. The twin gables, two central roof windows, chimney positions, sash subdivision and double-arch entrance communicate the photographed architectural vocabulary. Exact sculpted brick relief, facade bay projections, roof slopes and raised entrance terrace are simplified; the result remains a photo-informed interpretation, not a surveyed reproduction.

Entrance render exposed triangular dark slits between rectangular spandrel strips and elliptical voussoirs. Fixed the module to make each continuous spandrel prism share the exact arch's 24 sampled outer-arc endpoint coordinates, from depth 0.12 to 1.4 m, and meet the balcony underside. Syntax checked; new render validation pending coordinator rebuild.

Roof render shows both gabled ranges inside the stepped footprint. Independent 101 × 101 point grids per range returned zero outside samples (20,402 total); no roof-range correction required. Roof cap covers all concave returns and shared north face is blind. Rear review also identifies simplified open-backed central dormer boxes and an elevated linking roof plate with a shallow visible undercut; these are not evidence of observed historic detail. Reported to coordinator for optional closure refinement. No unrelated module changes made in this visual iteration.

Final visual-defect correction before next rebuild: central roof plate is now a solid linking roof volume extending from E−0.06 (exact deck level) to the unchanged top E+0.43, eliminating its suspended underside gap. Both central dormers have rear masonry panels at facade depth −1.52 m, behind the front glazing at −0.87 m; front apertures remain clear. All three modified XY rectangles passed independent 41 × 41 footprint sample checks with zero outside samples. Python syntax passed. Inputs frozen for coordinator rebuild; no Blender run by agent.
