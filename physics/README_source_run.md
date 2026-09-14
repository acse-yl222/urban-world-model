# SCALED 风场（潜空间域分解）→ 温度，core008 全部建筑范围

运行：2026-09-10 22:18 到 2026-09-11 03:12，RTX 5090。脚本 `physics_model/run_core008_scaled_latent.py`，出图
`physics_model/plot_core008_scaled.py --dir physics_model_result/scaled_latent`。设置与权重哈希见 `run_config.json`，日志 `run.log`。

## 模型与方法

- 权重：SCALED-Tutorial 发布的 `weight/inference.pth`（潜空间回归 U-Net，8 入 4 出）和 `weight/compression.pth`（3D VAE，压缩比 4，4 潜通道）。
- 方法：照搬 SCALED-Surrogate-Computational-Physics-Model 的 `inference_inmemory.py` 流程，改为单 GPU：
  1. 几何一次性编码：256 米物理块 + 8 米 halo（边界 replicate），潜空间去 2 格 halo 后拼成整域几何潜场 [1,4,16,704,768]；z=0 层强制固体。
  2. 每步在潜空间推进：256 潜格（1024 米）块 + 4 潜格 halo，共 3×3 = 9 块，输入 4 通道速度潜场 + 4 通道几何潜场，输出下一步速度潜场；状态不回物理空间。
  3. 解码：潜场 reflect 补 4 格 halo，64 潜格块解码为 288 米后裁 256 米核心，共 132 块。
- 网格：1 米体素 `south_kensington_core008_voxel_1m_domain4096`，域 X=[480,3552)、Y=[640,3456)、Z=[0,64) 米，即 [64, 2816, 3072]，覆盖全部建筑（X 625–3474，Y 754–3348）。减 (2116, 2124) 得区域坐标。
- 时间：从静止起步 100 步，每步按教师包解释为 25 秒（50 个 NN4PDEs 步 × 0.5 秒）。

## 风场结果（`wind/`）

| 项目 | 值 |
| --- | --- |
| 几何编码 | 141 秒，一次 |
| 每步 U-Net 推理 | 3.9 秒（9 块） |
| 每步解码 + 粗化 + 存盘 | 约 167 秒（132 块，只为存结果） |
| 峰值显存 | 24.4 GiB（解码块） |
| 均值风速（4 米流体格） | 第 10 步峰值 1.63 → 第 30 步 1.00 → 第 50 步后在 1.10–1.18 间振荡，第 100 步 1.12 m/s |
| 步间 RMS 变化 | 第 50 步后稳定在 0.076–0.084 |
| 后 19 帧的时间标准差（10 米层） | 0.080 m/s |

第 50 步后流场进入统计定常状态：均值不再漂移，步间变化保持恒定，说明模型在给定几何下维持了一个带湍动的准定常流，而不是衰减。来流自西向东（u 均值 +1.11 m/s），建筑背风侧尾流、街道绕流清晰，1024 米潜空间块之间没有可见接缝。

文件：`wind4m_000..100.npy`（4 米粗化，[3,16,704,768]，m/s，+x 东 +y 北，建筑内为 0）、`latent/0001..0100.pt`（每步潜场 float16，可再解码）、`latent_geometry.pt`、`latent_initial.pt`、`velocity_final_1m_raw_czyx_float16.npy`（第 100 步 1 米场 [3,64,2816,3072]，u 为 NN4PDEs 原始约定，取负为东向）、`solid_1m_zyx.npy`、`metrics.json`。

图：`figures/wind_step100.png`（4 米，10/40 米层）、`wind_final_1m_whole.png`、`wind_final_1m_core.png`（008 核心 1 米放大，2/10/30 米层）、`wind_spinup_10m.gif`（100 步演化）、`wind_convergence.png`。

## 温度结果（`temperature/`）

用第 82 到 100 步（0 到 450 秒）的时变风场，教师包未改动的受控热求解器和 15 通道单步温度 U-Net，4 米网格 [16,704,768]，热场景同前（环境 26、地面/屋顶 30 °C）。流体格 MAE（°C）：

| 时刻 | 递归 U-Net | 单步 U-Net | 持续性 |
| --- | --- | --- | --- |
| +90 s | 0.347 | 0.347 | 0.192 |
| +180 s | 0.607 | 0.277 | 0.321 |
| +270 s | 0.908 | 0.270 | 0.407 |
| +360 s | 1.192 | 0.266 | 0.465 |
| +450 s | 1.495 | 0.263 | 0.504 |

单步模式从 +180 秒起优于持续性基线并稳定在 0.26 °C；递归模式误差线性增长到 1.5 °C，与前两轮一致，温度模型的递归迁移仍不可用。
图：`figures/temperature_comparison_10m.png`、`temperature_mae.png`。

## 与物理空间分块版（`../scaled/`）的对比

同一权重、同一几何、重叠区域第 40 步（物理版）对第 100 步（潜空间版）：

| | 物理空间分块 | 潜空间分块 |
| --- | --- | --- |
| 每步耗时 | 457 秒（240 块，各 2 次编码 + 1 次解码） | 3.9 秒推理（+167 秒可选解码） |
| 均值风速走势 | 第 9 步 1.19 后持续衰减到 0.77 m/s | 第 50 步后定常约 1.12 m/s |
| 10 米层均值风速（重叠区） | 0.52 m/s | 0.79 m/s |
| 10 米层速度相关系数 | 0.72 | |
| 分块痕迹 | 早期明显，后期轻微 | 无 |

差异来源：物理版每步都把状态经 VAE 解码再编码，误差累积并逐步耗散动量；潜空间版与训练方式一致（潜场到潜场），不经过这个环节。后续应以潜空间版为准。

## 解释边界

- 无 CFD 或实测参考；SCALED 权重在原 1024 米 South Kensington 算例上训练，本次是新几何迁移。
- 64 米高度截断了 86 米以内的高层部分。
- 25 秒/步的物理时间映射沿用教师包解释；绝对时间尺度未经验证。
- 热场景为实验设定，温度参考是改编的受控求解器。
- 4 米保守粗化会封闭窄街。

## 污染物输运（`pollution/`，2026-09-11 补充）

Yuhang 的 `physical_transport.py`（未改动）在本目录已存的 4 米粗化风场（`wind4m_000..100.npy`，底部 64 米、16 层）上求解，
1 米网格 5.5 亿格超出显存，故未在 1 米上做。设置：每个风场步 25 秒 = 50 个 0.5 秒子步，帧间线性插值，从第 0 步（静止）驱动；
速度换算为格/秒（m/s ÷ 4）；ub 1 m/s、vb 0、源强 0.1、容差 1e-6。源：域坐标 x 520–600 米、y 848–3248 米、z 8–32 米，即城市西侧上游的连续线源。
100 步耗时约 1 分钟。第 100 步域内质量 1781 万（累计排放 1800 万，出流刚开始）；迎风建筑脚下同样出现辐合堆积热点（最大 4.2 万），原因见 `../scaled_latent_1024/README.md`。
文件：`concentration_001..100_float16.npy`（[16,704,768]）、`slices_z12m_tyx_float16.npy`、`mass.json`、`manifest.json`；图在 `pollution/figures/`。

## 2-D 温度标签模型（`temperature2d/`，2026-09-11 补充）

Yi Qi 的 `south_kensington_temperature.py`（未改动）通过共享风场缓存接入本目录的 SCALED 风场：第 41–100 步 12–16 米层的 4 米粗化 u、v，
每帧 25 秒（1 米网格的时间尺度），共 60 帧 = 1500 秒。建筑足迹、屋顶高度、植被和城市地面掩码与 `../scaled_latent_1024/temperature2d/` 同源
（`geometry_model/geometry/south_kensington_core008_landcover_4m/` 裁到本域 [704,768]），场景为模型默认的夏季午后设定。
脚本 `physics_model/run_core008_temperature2d_scaled_1024.py --dir physics_model_result/scaled_latent`，出图 `plot_core008_temperature2d.py --dir ...`。
结果：dt 1.25 秒、每帧 20 子步，7 秒跑完；流体格均温 31.78 → 31.86 °C，范围 30.78–32.15 °C。因为总时长只有 1500 秒（1024 版为 6000 秒），升温幅度更小；
街区内 12–16 米层风速均值 0.85 m/s，高于 1024 版的 0.39 m/s，是 1 米几何下街道通风更强的体现。
文件与图的组织同 1024 版。

---

# 洪水结果（flood/）— 来源 physics_model_result/scaled_latent/flood/README.md

# 降雨内涝（浅水方程）模拟，core008 South Kensington 全域

运行日期 2026-09-12，RTX 5090。论文：Chen, Nadimy, Heaney, Sharifian, Via Estrem, Nicotina, Hilberts, Pain (2025),
*Solving the discretised shallow water equations using neural networks*, Advances in Water Resources（PII S030917082500017X）。
作者代码开源：`github.com/Amin-Nadimy/Shallow_Water_Equations_NN4PDEs`（已克隆到 `~/workspace/Shallow_Water_Equations_NN4PDEs`，
Carlisle 2005 洪水算例，线性/二次单元两版）。

## 方法

论文思路：把浅水方程（SWE）的离散算子写成神经网络卷积层（权重固定、不训练），在 GPU 上以半隐式方式推进自由表面。本目录的求解器
`physics_model/flood_swe.py` 沿用这一框架（全部算子是张量模板运算 + 隐式自由表面 + 隐式曼宁摩擦），但为了城市干湿边界和建筑做了三处改动，
原因和代价都记录如下：

| 项目 | 论文 Carlisle 代码 | 本求解器 | 原因 |
| --- | --- | --- | --- |
| 网格 | 同位网格，3×3 有限元滤波器 | Arakawa C 网格，界面水深取迎风侧、界面底高取两侧较高值 | 建筑作为实体墙、干格不产生虚假流动、静水精确 |
| 自由表面方程 | 2 次 Jacobi 迭代（β=4） | 共轭梯度（Jacobi 预条件）解到相对残差 1e-7 | 质量守恒可控（本次误差 5 m³ / 40 万 m³） |
| 动量对流 | Petrov–Galerkin 稳定化 | 一阶迎风 | 简单稳健；两者都是非守恒速度形式 |

方程：∂η/∂t + ∇·(H **u**) = R − D；∂**u**/∂t + **u**·∇**u** = −g∇η − g n²|**u**|**u**/H^{4/3}。
每步：迎风对流 + 显式旧表面梯度 → 隐式摩擦 → 解 (I − g Δt² ∇·H∇) Δη = −Δt ∇·(H **û**) + Δt S → 速度修正。
时间步按对流 CFL 0.7 自适应（重力波无限制）。

验证（`verification.json`，`physics_model/test_flood_swe.py`，14 秒）：

| 用例 | 结果 |
| --- | --- |
| 粗糙床面 + 建筑的静水湖，200 步 | 速度、水面起伏、体积变化均为 0 |
| 封闭盆地降雨 20 分钟 | 体积相对误差 1.8e-8 |
| 曼宁均匀流（S=0.01，n=0.03，q=0.2 m²/s） | 水深 0.18488 对解析 0.18488，流速 1.0818 对 1.0818 |
| Stoker 湿床坝溃 hr/hl=0.5，t=20 s | 中间水深偏差 0.7 %，波前位置偏差 3.6 % |
| Stoker 坝溃 hr/hl=0.1（仅记录） | 中间水深 0.48 对 0.40，波前 49 对 62 m，加密网格不收敛 |
| 坡地建筑群降雨 + 排水 + 开边界 | 体积误差 0.016 m³ / 6820 m³，建筑内水深 0 |

强激波的偏差来自非守恒速度形式的动量方程（论文形式相同），城市内涝水深厘米到分米级、激波弱，影响可忽略；若要做溃坝类强激波需改为守恒通量形式。

## 地形与输入（`terrain/`，`physics_model/build_core008_flood_terrain.py`）

- 地面高程：环境署 2022 年 LIDAR 复合 DTM，1 米，裸地（建筑、植被已去除），ODN 基准。四块瓦片 TQ27ne/TQ27nw/TQ28se/TQ28sw
  下载到 `geometry_model/geometry/ea_lidar_dtm_1m/`（TQ27ne 原已在 `expansion/references/phase5_lidar/`）。
- 坐标：网格 → 域 → 区域（−(2116, 2124)）→ EPSG:32630 → EPSG:27700（pyproj OSTN15，精度 1 米）→ 双线性采样。域内 DTM −2.0 到 41.6 m AOD，均值 14.0；
  2946 个无数据/低于 −2 m 的格用最近有效值填补。
- 建筑：core008 1 米体素屋顶高度（`south_kensington_core008_voxel_1m_domain4096/height_m.npy`），建筑格底高 = DTM + max(屋顶高, 3 m)，并标记为实体（不过水、不落雨）。
  1 米格中建筑占 19.8 %。
- 土地覆盖：`south_kensington_core008_landcover_4m/` 的草地 + 树冠（占 17.7 %），其余为铺装。
- 网格与本目录风场一致：1 米 [2816, 3072]（域 X=[480,3552)、Y=[640,3456)），4 米 [704, 768]；行 0 在南、列 0 在西。`terrain/preview_terrain_4m.png` 为地形预览。

## 场景（`run_config.json`）

参照 2021 年 7 月 12 日伦敦/肯辛顿-切尔西暴雨（约 90 分钟 40–50 mm）：

| 项目 | 取值 |
| --- | --- |
| 降雨 | 15 分钟块 14.8 / 29.6 / 74.0 / 44.4 / 22.2 / 14.8 mm/h，共 50 mm / 90 min，随后 90 分钟退水，总 3 小时 |
| 排水 | 铺装与屋顶 12 mm/h（环境署地表水风险图的城市排水扣除量）；草地/树下 20 mm/h 下渗、无雨水管 |
| 屋顶径流 | 超出 12 mm/h 的部分全部转到最近的地面格（落水管 / 雨水口冒溢） |
| 曼宁 n | 铺装 0.02，绿地 0.05 |
| 边界 | 域最外 2 格每步清空（开边界，记为出流） |
| 初始 | 全干 |

## 结果

两次运行，同一场景、同一地形：

| | `run_4m/` | `run_1m/` |
| --- | --- | --- |
| 网格 | 704×768，Δt 0.5 s，21668 步 | 2816×3072，Δt ≤0.15 s，75053 步 |
| 耗时 | 35 秒（1.6 ms/步） | 17.8 分钟（14 ms/步，CG 平均 14 次迭代） |
| 降雨总量（地面 + 屋顶转移） | 400.5 千 m³ | 401.2 千 m³ |
| 峰值地表蓄水 / 时刻 | 236.6 千 m³ / 75 min | 236.3 千 m³ / 75 min |
| 3 小时末：地表 / 已排走 / 出域 | 198.3 / 172.4 / 29.7 千 m³ | 197.9 / 172.3 / 31.0 千 m³ |
| 质量平衡误差 | −23 m³ | −5.5 m³ |
| 最大水深 >10 cm 的面积 | 74.1 ha | 73.6 ha |
| 最大水深 >30 cm / >50 cm 的面积 | 20.9 / 8.6 ha | 21.0 / 9.5 ha |
| 地面最大水深的 99 分位 | 0.56 m | 0.59 m |
| 最大水深（DTM 深坑内） | 5.9 m | 8.1 m |
| 地面最大流速 99 分位 | — | 1.0 m/s（99.9 分位 1.7 m/s） |

4 米与 1 米的最大水深在地面格上相关系数 0.83，总量几乎相同：4 米已能给出统计结果，1 米才能分辨街道两侧和庭院内的积水形态，以 `run_1m/` 为主结果。

兴趣点 25 米半径内的最大水深（1 米）：South Kensington 站 3.60 m（车站的露天路堑，DTM 低至 −0.1 m AOD）、Imperial 学院 Exhibition Road 入口 1.67 m（入口旁有一处 3.6 m 深的 DTM 下沉区）、
Earl's Court 站 1.01 m、Queen's Gate / Old Brompton Rd 0.48 m、Gloucester Road 站 0.36 m、Kensington High St 0.14 m；Natural History Museum 和 Royal Albert Hall 两点周围 25 米全是建筑。

图（`run_1m/figures/`，`run_4m/figures/` 同名）：`max_depth_whole.png`（全域最大水深，北向上）、`max_depth_core.png`（008 精细核心放大）、
`max_speed_hazard.png`（最大流速与水深×流速危险度）、`time_series.png`（雨强、体积、淹没面积、兴趣点水深）、`depth_evolution.gif`（水深演化）。

空间格局：水沿街道向低处汇集并在路口、庭院和公园低洼处积水；海德公园的九曲湖（Serpentine / Long Water）和肯辛顿花园的圆池在 DTM 里是洼地，模拟中自然蓄满，
说明地形和汇水方向正确；西侧 Earl's Court 至 Gloucester Road 的地铁明挖路堑成为最深的连续水带。地面流速普遍 <1 m/s，危险度 h·v 在街道上多低于 0.5 m²/s。

## 文件

- `terrain/`：`dtm_1m_yx.npy`、`bed_block_1m_yx.npy`、`footprint_1m_yx.npy`、`grass/vegetation_1m_yx.npy` 及 4 米版本、`building_fraction_4m_yx.npy`、`metadata.json`、`preview_terrain_4m.png`。
- `run_*/`：`max_depth_m.npy`、`max_speed_m_s.npy`、`max_hazard_hv_m2_s.npy`、`arrival_time_gt10cm_s.npy`（首次超过 10 cm 的时刻，NaN 为未淹）、`final_depth_m.npy`、
  `frames/depth_NNN_float16.npy`（4 米每 5 分钟含 `speed_`，1 米每 10 分钟仅水深）、`frames/manifest.json`、`series.json`（每分钟统计）、`poi_depth_series.json`、
  `summary.json`、`run_config.json`、`run.log`。
- `verification.json`：求解器验证结果。

重跑：`physics_model/run_core008_flood_swe.py --cell 1 --frame_seconds 600 --save_speed 0`（或 `--cell 4`），参数 `--rain_scale`、`--sewer_mm_h`、`--infiltration_mm_h`、`--hours`、`--n_paved`、`--n_green`、
`--roof_to_ground 0`；出图 `physics_model/plot_core008_flood.py --run physics_model_result/scaled_latent/flood/run_1m`。

## 解释边界

- 无该区域实测淹没或 2021 年事件的观测对照；雨型、排水 12 mm/h、下渗、曼宁系数都是设定值。排水按均匀速率扣除，没有管网模型，退水阶段地表水消退速度完全由这一速率决定。
- DTM 中的真实深坑（地铁明挖路堑、施工基坑、采光井）会集中大量水：4 米运行中 >0.5 m 积水体积的约 40 % 位于比周围低 1.5 m 以上的坑内；最大水深、最大流速（15.9 m/s，出现在 18 米高的路堑壁上、水膜 0.15 mm）都由这些陡坎产生，
  解读应看 99 分位和面积指标。
- 建筑用 core008 体素而非 DTM 上的建筑（DTM 为裸地），二者边界可能相差 1–2 米；建筑内部（含下沉庭院、地下车库入口）不参与计算。
- 屋顶径流转移到最近地面格是简化；域外来水（北侧 Notting Hill 高地）只有域内 DTM 覆盖的部分，边界 2 格吸收水量。
- 非守恒动量形式对强激波（溃坝类）不准，见验证表。

---

# 光照结果（solar/）— 来源 physics_model_result/scaled_latent/solar/README.md

# 光照（太阳直射阴影、天空可见度、清空辐照度），core008 South Kensington 全域 1 米

运行日期 2026-09-12，RTX 5090，PyTorch。模块 `physics_model/solar_np.py`，运行 `physics_model/run_core008_solar.py`，
出图 `physics_model/plot_core008_solar.py`，验证 `physics_model/test_solar_np.py` → `verification.json`。

## 方法：NN4PDEs 式的可见度传输

与风场（SCALED/NN4PDEs）和洪水（浅水方程卷积求解）同一思路：所有算子是权重由几何决定、不训练的张量层。

- **直射阴影（ShadowNet）**。高度场 H = DTM + core008 建筑（`flood/terrain/bed_block_1m_yx.npy`）。太阳方位 d、高度角 a 时，格点 x 被遮挡当且仅当
  max_s [H(x + s d) − s·tan a] > H(x)。令倾斜场 G = H − tan a·(x·d)，条件变成沿射线的**滑动最大值** max_{0<s≤S} G(x + s d) > G(x)，即射线方向上的一维传输/可见度扫描。
  滑动最大值用倍增递归实现：M₁ = T_d G，M_{2k} = max(M_k, T_{k d} M_k)，T 为平移层、max 为形态学激活，S 米射线只需 log₂S 层。
  射线方向用模长 16–32 格的整数向量逼近（角度误差 < 0.05°），平移全部是精确整数位移、无插值；第 0 层沿该向量逐格取最近邻样本覆盖前 |p| 格。
- **地平线角与天空可见度（HorizonNet）**。每个方位（16 个）在 18 个高度角（2°–87°）上调用 ShadowNet，取最低可见高度角为地平线角 β_k，
  各向同性天空的 SVF = mean_k cos²β_k。
- **辐照度（逐点层）**。ASHRAE 清空模型：DNI = A·exp(−B/sin a)，DHI = C·DNI，A、B、C 按月取值。地面 GHI = 直射(未遮挡)·sin a·树冠透过率 + DHI·SVF + 反照率·开阔天空 GHI·(1 − SVF)。
  屋顶不含地面反射项。树冠格（core008.glb 材质，4 米掩码，占 0.3%）透过率 0.3，只衰减自身不投影。
- 太阳位置：NOAA 算法（含大气折射），取域中心 51.49985 N、−0.18848 E；本地时间夏令时 UTC+1、冬季 UTC。

验证（`verification.json`，1 秒）：

| 用例 | 结果 |
| --- | --- |
| 太阳位置 6 月 21 日 / 12 月 21 日 12:00 UTC | 高度角 61.94° / 15.12°，方位 178.8° / 180.3°（与 NOAA 计算器一致） |
| 随机建筑群阴影 vs 沿精确方位逐格行进的暴力法 | 4 个太阳位置格子不一致率 0–1.2%（差异全在长阴影边缘） |
| 20 米高 4×4 米柱在 10°/30°/60° 的影长 | 113 / 34 / 11 m，解析 113.4 / 34.6 / 11.5 m |
| 宽 20 米、高 20 米无限长街谷底部中心 SVF | 0.451，解析积分 0.447（Oke 1981 公式同为 0.447） |

## 结果

两天（2026 年夏至、冬至），每 10 分钟一帧，全域 1 米 [2816, 3072]。SVF 一次 0.8 秒，两天共 146 帧 1.7 秒（每帧约 12 毫秒）。

| | 6 月 21 日 | 12 月 21 日 |
| --- | --- | --- |
| 日出–日落（本地） | 04:50–21:10，16.5 h | 08:10–15:50，7.8 h |
| 太阳最大高度角 | 61.9° | 15.1° |
| 地面平均直射时数 / 10–90 分位 | 12.7 h / 6.0–16.2 h | 4.4 h / 0–7.3 h |
| 直射不足 1 小时的地面比例 | 0.9 % | 23.7 % |
| 清空日累计辐射：开阔天空 / 地面均值 / 屋顶均值 | 8.21 / 7.38 / 7.78 kWh/m² | 0.99 / 0.72 / 0.81 kWh/m² |
| 地面 SVF 均值（10–90 分位） | 0.837（0.49–0.99） | 同 |

冬至太阳最高 15°，20–30 米的建筑北侧拖出 75–110 米长的阴影，街道南北向的才能在正午见到太阳；夏至几乎全部街道每天都有数小时直射。

图（`figures/`）：`svf.png`、`<date>_shadows_core.png`（08:00–18:00 每两小时的核心区阴影）、`<date>_sunlit_hours_irradiation_core.png`、
`<date>_sunlit_hours_whole.png`、`<date>_time_series.png`、`<date>_ghi_day.gif`。

## 文件

- `svf/`：`svf_1m_yx.npy`、`svf_4m_yx.npy`、`horizon_deg_4m_kyx.npy`（16 方位地平线角，k=0 为北、顺时针 22.5°）、`summary.json`。
- `<date>/`：`shadow_1m_packed/shadow_NNN.npy`（`np.packbits(axis=1)` 压缩的 1 米阴影，`np.unpackbits(..., axis=1)[:, :3072]` 解开）、
  `ghi_4m_tyx_float16.npy` [T, 704, 768] W/m²、`ghi_1m_hourly/ghi_HH00_float16.npy`、`sunlit_hours_1m_yx.npy`、`daily_irradiation_kwh_m2_1m_yx.npy`、
  `daily_direct_kwh_m2_1m_yx.npy`、`frames.json`（每帧本地时间、太阳位置、DNI/DHI、地面遮挡比例、均值 GHI）、`summary.json`。
- `run_config.json`、`run.log`、`verification.json`。

网格与本目录其它结果一致（行 0 在南、列 0 在西，域 X=[480,3552)、Y=[640,3456)）。其它日期：`run_core008_solar.py --dates 2026-03-21 --minutes 5`。

## 解释边界

- 仅清空模型，没有云；ASHRAE 系数为月度经验值，实际日累计辐射会明显低于此（伦敦年均约为清空值的 45–55%）。
- 2.5D 柱体建筑：悬挑、拱廊被填实；没有立面辐照（需要 3-D 体素版本）。
- 树木不在高度场里，不投影，只在树冠格衰减直射。
- 只算一次地面反射（反照率 0.2 × 开阔天空 GHI × (1 − SVF)），没有多次反射和立面反射。
- 阴影按"每格一个平顶柱"的离散约定计算，和精确几何相比边缘差 ≤ 1 格。

---

# 光照-温度耦合（temperature3d_solar/）— 来源 physics_model_result/scaled_latent/temperature3d_solar/README.md

# 光照 → 温度耦合：NN4PDEs 太阳模型驱动 Yi Qi 3-D 温度物理模型，core008 全域 4 米

运行日期 2026-09-12。脚本 `physics_model/run_core008_temperature3d_solar.py`（单时刻对比）、`run_core008_temperature3d_diurnal.py`（夏至整日链式），
出图 `plot_core008_temperature3d_solar.py`、`plot_core008_temperature3d_diurnal.py`。Yi Qi 的 `south_kensington_temperature_3d.py` 文件未改动，
只在运行时替换两个函数。

## 耦合方式（单向：太阳 → 温度）

Yi Qi 3-D 模型的地表能量平衡把吸收短波写成 (1 − 反照率) × GHI × (1 − shade)，GHI 是全域单一数值，shade 来自它自带的逐建筑投影循环；
长波下行辐射也是全域单值。本目录把这两处换成太阳模型的空间场：

| 项 | 原模型 | 耦合后 |
| --- | --- | --- |
| `compute_building_shadow_field` | 逐建筑投影，0/1，平滑两遍 | 1 − GHI_cell / GHI_open：ShadowNet 1 米阴影聚合到 4 米的受光比例 × 直射 × 树冠透过率 + 散射 × SVF + 反照率 × GHI × (1 − SVF) |
| 直射/散射拆分 | 无 | 直射 = (1 − 云量) × ASHRAE 清空 DNI × sin(高度角)，上限为模型 GHI；散射 = 模型 GHI − 直射 |
| `solve_surface_temperature_excess_c` 的长波下行 | L_sky（Brutsaert 全域单值） | L_sky × SVF + σ·T_air⁴ × (1 − SVF)（墙面按气温辐射） |

其余（潜热、蓄热比例、人为热、对流系数、平流扩散求解器、边界条件）完全是模型原来的。风场：SCALED `scaled_latent` 4 米 81–100 步（统计定常），
16 层 × 4 米，v 取负、行翻转到模型的图像坐标（行 0 在北），每帧 90 秒。建筑足迹取体素第 1 层（4–8 米），因为 4 米高度场在非建筑格也是 4 米（z=0 层强制固体的约定）。
速度缓存 `velocity_cache/` 由 `save_shared_full_velocity_cache` 写出，可被模型的 `load_cached_full_velocity_fields` 直接读取。

两个小坑：模型 import 了速度模块里没有的 `rotate_2d_field`（只在被绕开的几何提取里用到），运行时补一个 `np.rot90` 实现；trellis2 环境没有 matplotlib，
模型自带的图和动画关闭，用 PIL 出图。

## 单时刻对比（`native/`、`solar_coupled/`、`compare/`）

模型默认场景 2025-07-25 13:00 UTC（气温 24.2 °C、云量 0.47、太阳高度角 56.7°、模型 GHI 806 W/m² → 直射 375 + 散射 431），30 分钟（20 帧 × 90 秒），
两次各 12 秒，学习区（建筑范围）内统计：

| | 原模型 | 耦合 | 差（耦合 − 原） |
| --- | --- | --- | --- |
| 地面遮挡 / 辐射亏缺均值 | 0.036 | 0.086 | 阴影 + 街谷散射损失 |
| 地表温度均值 | 28.97 °C | 28.76 °C | −0.21 °C（5–95 分位 −1.50 到 +0.46，极值 −6.4 / +5.4） |
| 0–4 米气温均值（30 分钟末） | 26.57 °C | 26.22 °C | −0.34 °C（5–95 分位 −0.90 到 0.00），相关系数 0.993 |

差异集中在 SVF 低的街谷、庭院和建筑北侧阴影：那里散射与长波收入都少，地表低 1–1.5 °C，局部到 −6 °C（原模型平滑阴影把边缘"涂开"的地方则相反，+5 °C）。
开阔地和公园几乎不变。图 `figures/native_vs_solar_core.png`（阴影/辐射亏缺、地表温度、气温三行对比）、`surface_difference_whole.png`、`air_mean_time_series.png`。

## 夏至整日（`diurnal_2026-06-21/`）

按小时推进：每小时算一次太阳位置 → ShadowNet 受光比例 + SVF → 模型地表能量平衡 → 求解器推进 60 分钟（40 帧 × 90 秒，风场循环），气温场跨小时传递
（求解器是模型 `solve_temperature_fields_3d_torch` 的逐行复制，只加了初始场参数）。设定：晴空（云量 0）、相对湿度 55%、环境气温余弦日变化 15 °C（05:00）到 26 °C（15:00），
04:00 到 24:00 本地时间共 20 小时，395 秒跑完。

| 本地时间 | 太阳高度角 | GHI W/m² | 环境气温 | 地表：城市 / 植被 | 0–4 米气温（相对环境） |
| --- | --- | --- | --- | --- | --- |
| 05:00 | −5.5° | 0 | 15.0 | 12.8 / 11.5 | 14.1（−0.9） |
| 08:00 | 17.8° | 278 | 17.3 | 16.6 / 12.1 | 17.1（−0.2） |
| 11:00 | 45.4° | 719 | 22.2 | 27.1 / 14.6 | 23.6（+1.4） |
| 14:00 | 61.9° | 906 | 25.7 | 34.7 / 17.1 | 27.7（+2.0） |
| 15:00 | 59.8° | 886 | 26.0 | 35.2 / 17.8 | 27.9（+1.9） |
| 18:00 | 37.0° | 599 | 24.8 | 30.5 / 19.2 | 25.8（+1.0） |
| 21:00 | 9.7° | 131 | 21.7 | 22.2 / 19.2 | 21.4（−0.4） |
| 24:00 | −10.4° | 0 | 18.1 | 17.2 / 15.9 | 17.3（−0.8） |

城市地表白天比气温高约 9 °C、夜间低 1–2.5 °C（长波冷却），近地面气温超额在 13–14 点达 +2.0 °C、夜间转为 −0.8 °C；植被地表始终低于气温（模型的潜热项很强），
夜间热岛（城市与植被上空气温差）保持在 0.5 °C 左右。图 `figures/diurnal_time_series.png`、`diurnal_maps_core.png`（06/09/12/15/18/21 点的地表和气温）、`diurnal_air_0_4m.gif`。

## 文件

- `velocity_cache/`：模型格式的 3-D 速度缓存（u/v/w/speed [20,16,704,768]，掩码、高度场、solid/roof 3-D）。
- `native/`、`solar_coupled/`：模型原生输出（模型坐标，行 0 在北）：`temperature_fields_3d_c.npy` [21,16,704,768]、地表温度、shade、`temperature_3d_run_summary.json`。
- `compare/`：域坐标（行 0 在南）的地表温度、0–4 米与 12–16 米气温、阴影场、逐帧 0–4 米气温、`comparison.json`；`solar_coupled_inputs_*.npy` 为耦合输入。
- `diurnal_2026-06-21/`：`hourly_ground_surface_c_tyx.npy`、`hourly_air_0_4m_c_tyx.npy`、`hourly_air_12_16m_c_tyx.npy`（[20,704,768] float16，索引 k = 05:00 + k 小时末）、
  `final_air_3d_c_zyx.npy`、`series.json`（逐小时统计）、`run_config.json`、`run.log`。
- `run_summary.json`、`figures/`。

## 解释边界

- 无观测对照；温度模型的场景参数（潜热、蓄热、人为热、对流系数）沿用模型默认值，它们决定了绝对温度，耦合只改变短波和长波的空间分布。
- 地表能量平衡是瞬时平衡，没有地面热惯性，地表温度对辐射的响应没有滞后；日变化里的夜间冷却因此偏快。
- 云量处理是简化：直射按 (1 − 云量) 折减，其余算散射。
- 阴影来自 1 米高度场（含 DTM 起伏），温度网格 4 米，用受光比例连接；建筑立面没有辐射项。
- 风场是 SCALED 的定常风循环使用，没有热力驱动的环流反馈；耦合是单向的。
