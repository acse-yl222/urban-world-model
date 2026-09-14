# 下一圈候选审计04（仅规划）

基于现有6181资产、35个已交付ID与当前batch14的3个临时锚点。既定AOI不扩大；74个保护资产、已交付/当前/待处理、父体或part别名及正面积轮廓重叠均排除。17个直接接触基线中选取以下6个，每栋都有正长度共边，不是仅点接触。

|候选|区域|锚点（状态）|共边长度m|目标边|到已交付最近距离m|
|---|---|---|---:|---|---:|
|way-640097055 25 Princes Gate|north|way-640097054 (delivered)|40.308|[4, 5, 6]|0.000|
|way-640808105 48 Princes Gardens|east|way-640808103 (delivered)|30.671|[4]|0.000|
|way-809238786 6 Queen's Gate|west|way-809238785 (delivered)|14.401|[6]|0.000|
|way-810633523 10 Queen's Gate Place Mews|south|way-810633524 (staged_batch14_not_delivered)|18.390|[1]|6.331|
|way-810633527 18 Queen's Gate Place Mews|south|way-810633526 (staged_batch14_not_delivered)|18.479|[4]|6.292|
|way-851362837 3 Princes Gate Mews|east|way-851362836 (staged_batch14_not_delivered)|8.155|[4]|10.086|

每个候选的原GLB extras明确记为程序化基线，且其屋顶position accessor竖轴恒定、窗体顶点/三角组织对应四点双三角窗片。结论结合来源语义与几何特征，不以mesh数量判定质量。完整mapped footprint、精确共边折线、原节点metadata、材质与primitive统计均存JSON。所有选中轮廓完整处于现有AOI内，未裁切。

- 25 Princes Gate：Existing licensed Jordiferrer23–25 image is a promising target-specific lead from prior research, not newly inspected here.25 is outside HE1227201 group26–31; do not transplant revised four-main-plus-attic semantics.
- 48 Princes Gardens：Adjacent47 delivered; no exact48 photo inspected here. Review terrace use/storeys and east neighbour158555530 before interpreting exposed walls.
- 6 Queen's Gate：Adjacent5 and HE1226082 terrace text already researched; group five-storey vs OSM6 discrepancy must be reviewed for6 rather than copying predecessor.
- 10 Queen's Gate Place Mews：Adjacent12 staged,14 delivered showroom nearby.2010 image is street context only; no10 exact facade/use proof, do not infer motor showroom.
- 18 Queen's Gate Place Mews：Adjacent16 staged. Source18 has only one nominal window; sparse baseline is not evidence of ancillary use. It also shares4.53m with terrace relation11163686; coordinate parent-independent party-wall ownership.
- 3 Princes Gate Mews：Adjacent2 currently staged; exact3 evidence not inspected. Small mews footprint also shares rear edge with100955530; verify neighbour roof/height.

这次只做本地源资产/轮廓审计，没有下载新批量数据，也没有实看候选的最新实景照片。已有照片路径只是下一步证据线索，不能据此宣布立面匹配。所有候选仍须单栋身份、地面入口、共墙高度和许可照片审查；不是可直接替换授权或已完成清单。未修改frontier、queue、manifest、viewer或任何模型。
