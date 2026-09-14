# 下一圈06候选审计（只读规划）

基于47个已交付ID和batch18的3个临时锚点。现有AOI未扩大；6栋完整轮廓均在范围内且未裁切。74保护资产、done/staged/deferred、parent/part别名及任意mapped建筑正面积重叠均排除。16个接触基线中14个有正长度共边，选取以下6栋；仅点接触不合格。

|候选ID/源名|锚点|状态|距离m|共边m|
|---|---|---|---:|---:|
|way-392603602 St. Nicholas Preparatory School|way-640097056|delivered|0.000|31.480|
|way-809238788 8 Queen's Gate|way-809238787|delivered|0.000|14.416|
|way-640457472 1 Montrose Court|way-640097054|delivered|0.000|7.273|
|way-809386116 23 Queen's Gate Mews|way-809238784|delivered|0.000|4.213|
|way-810633521 6 Queen's Gate Place Mews|way-810633522|staged_batch18_not_delivered|0.000|14.917|
|way-851362839 4a Princes Gate Mews|way-851362838|staged_batch18_not_delivered|0.000|8.088|

完整源WGS84/投影多边形、共边折线、GLBextras/屋顶accessor/窗片统计、alias排除结果存JSON。源metadata明确baseline，平顶/四点窗片结构仅为补充证据，不据面数声称质量。共边edge编号为源顺序，未来CCWfeature需重新计算。

- St. Nicholas Preparatory School：Source name St.Nicholas Preparatory School is historical/unverified current identity. Appears next address after24PrincesGate; no postal23 assignment without evidence. Nearby Jordiferrer23–25 photo is only a lead. Source5levels; institution/currentuse/facade exact binding requires research.
- 8 Queen's Gate：8QueensGate is in the same street sequence as7. Source6levels may conflict with historical listed terrace five includingattic; audit independently, retaining original source height until coordination.
- 1 Montrose Court：1MontroseCourt is a small separate2level mapped house, NOT road-conflict deferred MontroseCourt way111491435. Preserve exactID; no name-based merge or apartment-block identity transfer. Shares longer wall with26 and shorter with27.
- 23 Queen's Gate Mews：23QueensGateMews is distinct from23PrincesGateMews and23QueensGatePlaceMews. It has a positive common edge with4QueensGate; unlike20/22QueensGateMews which only touch anchor corners. Roof/entry unreviewed.
- 6 Queen's Gate Place Mews：6QueensGatePlaceMews has source asset and direct edge with staged8. Source sparse3windows is not ancillary/outbuilding evidence. Do not transfer street-frontdoor if original entry is rear.
- 4a Princes Gate Mews：Source addr4aPrincesGateMews is distinct from4. Exact4loft permission and3mansard history cannot be transferred. Source2levels roof shape unconfirmed; staged4upperroof is inset and not boundarywallheight.

南向缺口已独立确认：22Queen’sGatePlaceMews way810633529在主GLB和306补充GLB均无资产，不可直接替换；24同街way810633530确有补充GLB资产，但距当前staged20约6.690m，中间隔着缺失22，未满足直接正共边。当前可沿8向6继续。20/22Queen’sGateMews（不同街）只有角点接触，排除；选中的23Queen’sGateMews有4.213m共边。

本次没有联网、下载或新实看照片，也未运行Blender。仅生成本JSON/Markdown，不改queue、frontier、scene或任何构建输入。候选均待独立证据、地面/入口、共享高度和roof审查，不是交付清单。
