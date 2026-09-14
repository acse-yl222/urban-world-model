# Batch14 preflight — read-only local audit

Authoritative frontier currently records **35 completed IDs**. No target is marked delivered or modified by this audit. Source classification uses original extras and mappings, not mesh-count accuracy. Older next_ring_candidates_03 snapshot called14staged; current frontier supersedes that status.

## Targets

### 12 Queen's Gate Place Mews — way-810633524
- Full polygon: 4 outer corners, area 116.591213430m², valid=True, holes=0, fully inside existing AOI. Source building=house, levels=2.
- Index: 1 mapped source node, node/mesh 3361/3361; status procedural facade baseline. Target in completed=False; pending status=pending_evidence.
- Existing candidate audit found parent membership=[], part tag=None, aliases=[], protected positive overlaps=[]. These are local-source checks, not proof of current real-world ownership.
- Independent intersection with available completed feature polygons: positive-area overlaps=[]; contacts=[['way-810633525', 18.264376564865504]].
- Immediate neighbour data from source GIS:
  - way-810633525: distance 0.000000m, shared line 18.264377m, overlap 0.000000m²; house/address tag 14.
  - relation-11163686: distance 0.000000m, shared line 0.000000m, overlap 0.000000m²; house/address tag None.
  - way-810633523: distance 0.000000m, shared line 18.389597m, overlap 0.000000m²; house/address tag 10.
- `batch12/reports/context.json` contains 5 target primitive objects; all immediate neighbour IDs covered=True; missing=[]. Primitive split is not duplicate buildings.
  - ['Detailed | painted entrance']: x[461.633798,461.832659],y[-458.237510,-457.207481],z[-0.000387758,2.300505410]. Original source leaf/roof, not authoring-ready wall-plane threshold.
  - ['Detailed | slate grey roof']: x[460.969341,480.192769],y[-460.892066,-451.610497],z[6.849599535,6.849599535]. Original source leaf/roof, not authoring-ready wall-plane threshold.

### 16 Queen's Gate Place Mews — way-810633526
- Full polygon: 5 outer corners, area 116.440076952m², valid=True, holes=0, fully inside existing AOI. Source building=house, levels=2.
- Index: 1 mapped source node, node/mesh 3363/3363; status procedural facade baseline. Target in completed=False; pending status=pending_evidence.
- Existing candidate audit found parent membership=[], part tag=None, aliases=[], protected positive overlaps=[]. These are local-source checks, not proof of current real-world ownership.
- Independent intersection with available completed feature polygons: positive-area overlaps=[]; contacts=[['way-810633525', 18.269793834051082]].
- Immediate neighbour data from source GIS:
  - way-810633527: distance 0.000000m, shared line 18.478654m, overlap 0.000000m²; house/address tag 18.
  - way-810633525: distance 0.000000m, shared line 18.269794m, overlap 0.000000m²; house/address tag 14.
  - relation-11163686: distance 0.000000m, shared line 2.146053m, overlap 0.000000m²; house/address tag None.
- `batch12/reports/context.json` contains 5 target primitive objects; all immediate neighbour IDs covered=True; missing=[]. Primitive split is not duplicate buildings.
  - ['Detailed | painted entrance']: x[481.559622,481.738044],y[-467.717375,-466.683475],z[-0.000044037,2.299643838]. Original source leaf/roof, not authoring-ready wall-plane threshold.
  - ['Detailed | slate grey roof']: x[463.276144,482.347749],y[-473.466151,-464.042305],z[6.850278612,6.850278612]. Original source leaf/roof, not authoring-ready wall-plane threshold.

### 2 Princes Gate Mews — way-851362836
- Full polygon: 5 outer corners, area 83.239888210m², valid=True, holes=0, fully inside existing AOI. Source building=house, levels=2.
- Index: 1 mapped source node, node/mesh 5259/5259; status procedural facade baseline. Target in completed=False; pending status=pending_evidence.
- Existing candidate audit found parent membership=[], part tag=None, aliases=[], protected positive overlaps=[]. These are local-source checks, not proof of current real-world ownership.
- Independent intersection with available completed feature polygons: positive-area overlaps=[]; contacts=[['way-851362835', 8.168523790839526]].
- Immediate neighbour data from source GIS:
  - way-851362852: distance 0.000000m, shared line 3.584928m, overlap 0.000000m²; house/address tag 85.
  - way-851362835: distance 0.000000m, shared line 8.168524m, overlap 0.000000m²; house/address tag 1.
  - way-851362837: distance 0.000000m, shared line 8.154738m, overlap 0.000000m²; house/address tag 3.
  - way-100955530: distance 1.220706m, shared line 0.000000m, overlap 0.000000m²; house/address tag None.
- `batch11/reports/context.json` contains 5 target primitive objects; all immediate neighbour IDs covered=True; missing=[]. Primitive split is not duplicate buildings.
  - ['Detailed | painted entrance']: x[968.198562,969.234265],y[-254.807376,-254.636047],z[0.000117231,2.300080289]. Original source leaf/roof, not authoring-ready wall-plane threshold.
  - ['Detailed | slate grey roof']: x[963.714670,975.170950],y[-263.453391,-253.742709],z[6.849801137,6.849801137]. Original source leaf/roof, not authoring-ready wall-plane threshold.

## Context preparation requirements

- Use `batch12/reports/context.json` for the two southern targets and `batch11/reports/context.json` for2PrincesGateMews, with explicit source provenance. These bounded sets cover the immediate neighbours listed above. Union by source/object identity, not just building ID (each asset has multiple material primitives); deduplicate shared objects. Do not claim a fresh35m neighbourhood until recomputed for all3fullpolygons.
- The local context copies include old baselines for now-delivered anchors. Replace entire matching anchor object sets using current delivered GLBs, never stack a duplicate replacement on old geometry. For12/16 use **batch12_v1/replacement.glb** for14way810633525; for2use **batch11_v1/replacement.glb** for1way851362835,69–70and71–72if present. Filter overlays by included IDs and preserve unrelated protected assets.
- Source footprint data and exact adjacency geometry exist in `reports/next_ring_candidates_03.json` and the underlying GIS named there. Rebuild CCW feature rings while preserving every corner; compute normalized shared segments (especially16 short2.146mcontact withrelation11163686). Point contact of12with that relation is not a shared wall. Recheck relation/member aliases and all positive-area overlaps for the final selected scope.
- Decode each original door leaf into centre, width, tangent and threshold, then project only normal offset onto its wall edge; retain original_leaf separately. Source meshes exist, and coordinator subsequently prepared the three batch14features/entry contracts; inspect their current ground audit before freezing.
- Independently sample actual original ground/road/path/paving/traffic triangles at each entry and outward0.5/1m, using source-ground inspection scripts. Do not inherit-.05or+.068solely from a neighbouring batch. Context excludes a guarantee of ground coverage. Coordinate axes already east/north/up with fixedEPSG32630origin; do not reproject decoded vertices.
- Derive common wall intervals from **latest delivered module wall tops**, not roof/parapet/chimney maxima.14and1roof articulation changed after initial baseline. Other listed neighbours remain source estimates. Source levels2do not establish current attic or roof shape.

## Evidence gaps and bounded next action

- No new internet or image inspection was performed in this preflight. Candidate diagnostics are planning-only; exact12/16/2facade, roof and use remain pending evidence. Reuse existing14/1reference ledgers only as leads/context until each target is actually identified. A neighbouring mews photograph does not prove identical garage doors or window counts.
-12/16multipleUPRNs are address references, not mapped building-part aliases; do not split or merge volume merely from a semicolon list. Avoid confusing Queen’sGatePlaceMews with Queen’sGateMews/Gardens.2PrincesGateMews is not PrincesGate house2.
- Prepare batch14features/manifest/context with current35completed provenance, then delegate single-building evidence/modules. Preserve the three original baseline assets until validated replacement; no automatic completion or root-state mutation. Revision27is now delivered (35count unchanged), coordinator-owned and unrelated to these immediate contacts.

## Inputs checked

- `geometry/expansion/remaining_frontier.json` SHA256 `0b1acded7e4102ce0bce583074c779c6aee049478a46ea4cf69af28df3783706`
- `geometry/expansion/asset_index.json` SHA256 `6761b9d09550ff951ce0e243669c1511fe0104f17d4678ea975583aa0944a636`
- `geometry/expansion/reports/next_ring_candidates_03.json` SHA256 `c0b6e2a380909f266272858e9f6f0a7ed8ddb8023a0c1eb80f6fe9ea0c9b3ae4`
- `geometry/expansion/batch11/reports/context.json` SHA256 `4adab3a7fd359c59f0495e430832c44592bf3b01542d599354c7c963e7f46d0a`
- `geometry/expansion/batch12/reports/context.json` SHA256 `e4677e15e7a8a26a33c8b6f2c377cc926d72a200ae75ee48780cfda06f812ee3`

## Coordinator preparation update

After this independent source audit, root unioned11+12seed and preparedbatch14features/manifest. Fresh context extractor41724and groundaudit55160 were running at notification. The three prepared features retain4/5/5corners, twolevels and approximately6.85m estimated mainheight. Root reports and inputs were not modified by this review. Final context/ground results supersede preflight requirements when complete.
