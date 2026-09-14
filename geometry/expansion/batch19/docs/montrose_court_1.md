# 1 Montrose Court — evidence and proposed interpretation

Target `way-640457472` is the northernmost small two-storey house east of the Montrose Court service road, as distinguished in paragraph 2 of the Montrose Court Holdings v Shamash judgment. It is not the eight-storey block or the deferred road-conflict asset `way-111491435`.

The exact-address Westminster committee minutes of 16 December 2014, item 9, record conditional approval for replacement two-storey side extension, relocation of entrance and two basement levels. Permission is not proof of construction. The existing mapped footprint and source entrance remain authoritative for this scene; no basement is excavated and no historical relocated entry is invented.

An architect's 2015 Montrose Court project describes a house in the estate's 1950s terrace with clean white render. It does not name the house number: its refurbishment, porch and photographs cannot be attributed to number 1. Copyright photographs were not derived. The licensed Lewis Clarke street photo was actually viewed: it shows the classical Princes Gate frontage, not an identified view of this rear house. Its ornament is not transferred.

Proposed model: retain source two levels and estimated main height, full five-corner footprint, source east entry and all three normalized shared wall segments. A plain complete flat roof, contained low edging, simple deeply recessed rectangular casements and an understated entry are explicitly artistic completion. No evidence establishes an attic, mansard, chimney, garage or roof terrace here. Exact window positions and roof material remain unknown.

Sources and individual rights are in `../references/montrose_court_1/sources.json`. No photographic texture is exported. This document currently records research, not a validated or delivered model. The coordinator owns ground support and assembly.

## Frozen module contract

`build(feature, materials)` consumes current dynamic base/height, original entry and every normalized shared segment. It returns created objects, parameters, real aperture intervals, roof parts, source IDs, observations/uncertainties and generic `interfaces.entrance` / `shared_walls`. Parent owns all approach/support geometry.

Retained full five-corner footprint; two main levels at source H6.849992113m. Twelve real apertures including the retained east door; shared edges1/3/4 have no overlapping holes. Free edges0/2 carry the estimated low rim, maximum absolute z7.139982374m. The complete deck is H+.008 above the wall/eaves top, while rim bottoms embed to H-.025; no elevated third tier. Main entry is not moved or supplemented with an unverified second entrance.

Window/door framework joins are segmented; modern casement bars do not cross rail overlays. Bands cap only true free-run ends, meshes compact unused vertices, tessellation maps float32 Vector results back to original double coordinates. Static AST and mocked API contract checks passed, with three shared segments and zero aperture/shared conflicts. These are not Blender/export/render checks; coordinator verification remains pending.

Module SHA-256 `91ac291b7e20c411c789590aeca7f876a3035646ae4fc563163cc4724e770a31`. Input is frozen for coordinator assembly; not a delivery claim.
