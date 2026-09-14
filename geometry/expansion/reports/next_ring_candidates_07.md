# 下一圈07候选（只读审计）

刷新当前53已交付、3个batch20暂存锚点、58个curated排除项和74保护资产。18个接触baseline中16个具有正共边。以下6栋保留完整OSM轮廓，未裁切或扩大AOI；关系成员、building:part、source_part_ids别名及任何mapped建筑正面积重叠均排除。六栋都直接核对主GLB node/mesh存在，无需补充GLB才能替换。

|候选|锚点|锚点状态|共边m|角点数|
|---|---|---|---:|---:|
|way-640097057 22 Princes Gate|way-392603602|delivered|31.506|4|
|way-809238789 9 Queen's Gate|way-809238788|delivered|23.101|6|
|way-640457473 2 Montrose Court|way-640457472|delivered|10.650|4|
|way-809386115 22 Queen's Gate Mews|way-809386116|staged_batch20_not_delivered|11.474|7|
|way-810633520 4 Queen's Gate Place Mews|way-810633521|staged_batch20_not_delivered|14.917|10|
|way-851362840 5 Princes Gate Mews|way-851362839|staged_batch20_not_delivered|8.055|4|

22 Queen’s Gate Mews现因staged23才有真正共边，不能仍以4Queen’s Gate角点作合格锚点。其他未选正共边候选包括24Queen’sGateMews，仅是后续候选，不提前入队。18/20Queen’sGateMews仍仅点接触，排除。

- 22 Princes Gate: 22 Princes Gate: official14–25 group is a research lead; five source levels. Do not borrow school23 sign/current-use or exact openings without identification.
- 9 Queen's Gate: 9 Queens Gate: six source levels may need reconciliation with listed-group floor semantics; do not lower height without coordinated evidence.
- 2 Montrose Court: 2 Montrose Court: separate two-level small polygon; not deferred large Montrose Court asset.
- 22 Queen's Gate Mews: 22 Queens Gate Mews: now positive common edge with staged23, formerly corner-only to4 Queens Gate. Exact-address joint planning is not asbuilt proof.
- 4 Queen's Gate Place Mews: 4 Queens Gate Place Mews: ten-corner complete footprint, two levels; distinct from4 Queens Gate Mews and staged6, preserve all returns.
- 5 Princes Gate Mews: 5 Princes Gate Mews: separate four-point two-level house, staged4a is only anchor; nearby loft permissions cannot be transferred.

完整WGS84及投影polygon、共边线、GLB真实nodes/meshes/extras/materialaccessors、alias与正面积审计存JSON。平顶及窗片结构只是baseline辅助证据，不是面数质量判定。共边edge编号是原OSM顺序，authoring前需CCW重算。

此轮未联网/下载/Blender/图片实看；未改queue/frontier/任何batch输入。暂存锚点不算交付，所有候选都需后续独立证据、原入口、地面和共享高度审查。
