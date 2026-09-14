# 85 Princes Gate Mews — evidence preparation

Module prepared and frozen against final coordinator contract; assembled numerical/visual acceptance pending. Full six-corner101.4609m²plan and originaledge0 entry remain fixed.

An exact-address historical source conflicts with the source OSM two levels: reproduced High Court judgment [2015]EWHC2458(Admin), §14–15, calls85 an existing three-storey dwelling and distinguishes a proposed new basement that would make four. The reproduction was actually read; direct BAILII/NationalArchives copies did not open. ItsSW9 postcode andRoyalCollegeofArt rear reference differ from local mapped context and remain recorded discrepancies. This is architectural historical evidence only, not current legal or construction advice.

RBKC's indexed PP/14/06202/A/14/2228738 record at exact85 SW72PS describes an enlarged side/rear dormer at second-floor level, appeal dismissed19January2015. It supports a roof-level alteration history, not permission to assert an implemented new dormer. The basement appeal record likewise cannot prove that basement exists. Neighbour3's2003mansard permission is not transferred.

The MrIgnavy2023 CC BY-SA2.0 east-mews photo was actually re-viewed. White-painted brick, sashes and slate upper roofs are visible but85is not identified; roundedcorner/dormer positions are context only. No exact85image geometry or commercial website photograph has been derived.

Final coordinator-authorized interpretation: keep inherited main eaves6.849712875m over two main levels, add an explicitly estimated inset upper/roof tier 2.1m high to reflect historicalthree-storey evidence, without claiming measured roof shape or transplanting neighbouring dormers. SourceOSM2must remain archived, and no basement is excavated. The sourceOSM2 remains archived; the final feature records2main levels plus1roof tier,3visible tiers total. Full provenance at ../references/princes_gate_mews_85/sources.json.

## Module and interfaces

`build(feature, materials)` preserves base0.000338367882m, two-main-floor eaves6.849712875105m and all six footprint vertices. The primary west-facing edge0 doorway remains XY[961.8015700034,−272.3647308471], threshold=base, clear width1.049859465m. Leaf recess0.34m and wall thickness0.40m are authored estimates. No new entrance, bottom door crossbar, ground ramp or external porch is introduced.

The lower facade is individual to this ring: four west upper sash bays with three lower casements around the offset source door; south has two bays; east edge2 only upper windows above the low shared interval. Fourteen main-wall apertures include the source door. All three normalized common-wall intervals remain dynamically consumed: low east neighbour100955530 through3.698276718m; north edges5/4 against1/2. Full walls are retained, with0 conflicting lower-wall apertures.

A complete original-footprint cap at main top+0.008m closes the baseline volume. The six-point upper ring is inset0.65m, contains a distinct roof-tier volume rising2.1m overall, and returns five real recessed upper apertures only on west/south free faces. These are simple inset-tier windows, not copied or claimed implemented side/rear dormers. Nineteen total authored apertures comprise14main plus5upper, separately recorded in parameters and roof_parts. Inset wall tops are embedded30mm into a70mm-thick closed roof slab; its top is8.950051243m absolute. No coplanar roof/wall top is exposed. The full baseline footprint is not replaced by the smaller upper ring.

Three visible tiers are a historical-text interpretation; the roof shape,0.65m setback,2.1m height and all glazing dimensions remain artistic assumptions. The inset third tier does not increase shared-boundary wall-height intervals. No basement, rooftop plant or roof-terrace access is fabricated. Ground−.05m to the original near-zero threshold is coordinator-owned finite support.

All geometry uses injected materials. Returned interfaces have entrance (threshold_xyz/outward_normal/door_leaf_xyz/clear_width_m/clear_height_m/leaf_recess_m), empty additional supports and additional entrances, and all3shared_wall polyline/interval records. Horizontal frames stop at vertical frame inner edges and crossing bars have distinct front-face depths. Mesh emission compacts unused vertices and recalculates normals. Tessellation resolves returned float32Vectors against inputVectors before addressing unchanged double-precision source vertices.

## Checks and freeze

AST and float32 non-Blender stub checks passed finite vertices, valid indices/materials, all vertices referenced,3shared records and0main-aperture conflicts. Shapely surrogate tessellation confirms the upper roof slab is closed with every edge used twice; this is not Blender tessellation, export or actual rendered review. Complete bottom cap uses the whole original polygon. Coordinator numerical/visual integration remains pending.

Module SHA256: `f804ad4d80a79e6077f581282c84beec58d84c80be747e261224f38dfb2ba8f8`.


## First-build roundtrip repair

First full build52173 failed exact triangle-count roundtrip at the front/rear intermediate course. Its selected edges0 and1 are consecutive, but the previous band helper capped both ends of each edge, creating two coincident opposing internal quads at their shared mitre. Export/import removed duplicate internal faces. The helper now caps only exposed ends of each contiguous selected run; external surfaces, original footprint, entry, upper tier and shared-wall intervals are unchanged. No checking tolerance was relaxed.

Coordinator's isolated diagnostic7965 using the absolute Blender executable passed all33object IDs and3596triangles before/after GLB export/import. Evidence is in `../reports/85_module_roundtrip.json` and `../reports/85_roundtrip.log`. This is a module-only numerical result, not complete scene/ground or visual acceptance. Full rebuild24222 is pending at this record; frozen geometry is not altered further.
