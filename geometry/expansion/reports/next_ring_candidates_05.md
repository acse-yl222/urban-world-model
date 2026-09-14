# 下一圈候选审计05（仅规划）

快照：41个已完成ID、batch16的3个临时锚点、74个保护资产。未扩大既定AOI；6栋均完整包含在AOI内，未裁切。18个直接接触的程序化基线中选取以下6个地址明确的候选。当前batch16不计为完成。

|候选|锚点及状态|边界距离m|共边m|距真正已完成最近m|
|---|---|---:|---:|---:|
|way-640097056 24 Princes Gate|way-640097055 / delivered|0.000|31.541|0.000|
|way-809238787 7 Queen's Gate|way-809238786 / delivered|0.000|14.559|0.000|
|way-851362852 85 Princes Gate Mews|way-851362835 / delivered|0.000|4.642|0.000|
|way-810633522 8 Queen's Gate Place Mews|way-810633523 / staged_batch16_not_delivered|0.000|18.266|7.078|
|way-810633528 20 Queen's Gate Place Mews|way-810633527 / staged_batch16_not_delivered|0.000|18.271|5.927|
|way-851362838 4 Princes Gate Mews|way-851362837 / staged_batch16_not_delivered|0.000|8.110|10.411|

完整轮廓（源WGS84及投影XY）、源节点extras/材质/accessor统计、共边折线与邻接均在JSON。所有6栋都有正长度共边，不是仅点接触。原GLB与索引均标程序化基线；平顶accessor及四顶点窗片组织是补充证据，不依mesh数量判定准确性。

逐项排除：已完成、batch16三栋、两项deferred、74保护ID、父relation成员、building:part及source_part_ids别名；对所有其他有效mapped建筑检查正面积重叠，超过1e-5m²即排除，6栋均无。基线原资产保留。JSON中的共边edge编号来自原OSM顺序，未来feature重排CCW时需重新映射。

- 24 Princes Gate：24 is in HE1265482 group14–25; existing Jordiferrer23–25 photo is a promising identity lead only, not newly inspected or automatically assigned to24.
- 7 Queen's Gate：SourceOSM6levels versus HE1226082five including attic must be audited for7. Adjacent6 now has five authored tiers in retained estimated envelope; do not assume seventh/floor count from shared height.
- 85 Princes Gate Mews：85 is a distinct mews house behind1/2; source2levels and mapped6corners do not prove current roof. Prior official search leads mention85 alterations/dormer applications; require direct exact-address review, not another house image.
- 8 Queen's Gate Place Mews：8 is distinct from8QueensGateMews and8QueensGatePlace.2010street reference is context only. Adjacent10 is staged; do not inherit its hip roof as observed.
- 20 Queen's Gate Place Mews：20 is distinct from20QueensGateMews. No exact20image reviewed; neighbour18 is staged and flat roof assumption does not establish20roof.
- 4 Princes Gate Mews：4 is next to staged3. The2003mansard permission is specifically3 and must not be transferred; rear low neighbour100955530 requires height and aperture audit.

V&A大relation、教堂、大型terrace relation与匿名后翼等保留为专项调查候选，不套普通住宅细化。Falmouth/Keogh仍可随后独立审查。

本次没有新联网调查或实看这6栋当前照片；本地照片/官方记录仅是后续线索。尤其24、7、85的身份/层数/屋顶和8、20、4的原入口/共享墙仍须逐栋审查。不是可直接替换或已交付声明。仅生成本JSON和Markdown；queue、frontier、scene、manifest、模块均未修改。
