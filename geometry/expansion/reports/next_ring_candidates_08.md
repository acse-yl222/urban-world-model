# 下一圈08候选（只读审计）

当前59已交付、3个batch22暂存锚点、64个curated排除项与74保护资产均已刷新。17个接触baseline中16个具有正长度共边；6栋全部整环在原AOI内，未裁切。排除parentrelation/building:part/sourcepart别名及任意mapped建筑正面积重叠。每栋直接核验主GLBnode/mesh存在，不依赖补充GLB。

|候选|锚点|状态|共边m|完整角点数|
|---|---|---|---:|---:|
|way-640097058 21 Princes Gate|way-640097057|delivered|31.427|4|
|way-640457474 3 Montrose Court|way-640457473|delivered|10.712|4|
|way-809386111 18 Queen's Gate Mews|way-809238789|delivered|3.249|6|
|way-809386114 21 Queen's Gate Mews|way-809386115|staged_batch22_not_delivered|8.629|4|
|way-810633519 2 Queen's Gate Place Mews|way-810633520|staged_batch22_not_delivered|7.818|6|
|way-851362841 6 Princes Gate Mews|way-851362840|staged_batch22_not_delivered|8.033|4|

18Queen’sGateMews新增合格锚点为已交付9Queen’sGate，与8的旧角点接触不算。20Queen’sGateMews仍无正长度共边，排除。三个依赖batch22的锚点暂存不算已交付。

- 21 Princes Gate: 21 Princes Gate continues east from delivered22; five source levels, group identity/reference details need exact-number review.
- 3 Montrose Court: 3 Montrose Court continues separate small-house row from2; not deferred apartment block, two source levels.
- 18 Queen's Gate Mews: 18 Queens Gate Mews now has positive shared edge with delivered9 Queens Gate; prior corner-only relation to8 is not the qualifying anchor.
- 21 Queen's Gate Mews: 21 Queens Gate Mews shares with staged22; source2levels, cannot transfer22 brochure3floor/garage facts.
- 2 Queen's Gate Place Mews: 2 Queens Gate Place Mews continues from staged4; six-point complete outline, distinct from same-number Queens Gate Mews.
- 6 Princes Gate Mews: 6 Princes Gate Mews continues from staged5; source2levels, no direct transfer of prior5loft/refurbishment evidence.

完整OSM WGS84及投影多边形、共边线、原始GLBnode/mesh/extras/materialaccessors和排除审计在JSON。几何primitive统计仅辅助baseline来源核验，不按面数断言质量。edge编号为原source顺序，未来CCWfeature重算。

本次不联网/下载/Blender/照片检查，不改queue/frontier/任何构建输入。候选待新证据、入口地面、共享高度和屋顶合同审查。
