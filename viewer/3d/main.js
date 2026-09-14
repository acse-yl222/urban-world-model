import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { LineSegments2 } from 'three/addons/lines/LineSegments2.js';
import { LineSegmentsGeometry } from 'three/addons/lines/LineSegmentsGeometry.js';
import { LineMaterial } from 'three/addons/lines/LineMaterial.js';
import { getFrame, f16, loadMask, npy, DATA } from '../npy.js';
import { initFrames, hasLayer, getFrameF32, framesInfo } from '../frames.js';
import { CITY_GLB } from '../config.js';
import { CITY_FROM_PARTS, fetchCityModel } from '../model-source.js';
import { buildProxyCity } from './proxy.js';
// Lite mode: phones, tablets and low-memory machines get a proxy city extruded from the 4 m voxel masks instead of the
// 254 MB model (which needs ~1.6 GB of browser memory). ?lite=1 forces it, ?lite=0 forces the full model.
const qs0 = new URLSearchParams(location.search);
const LITE = qs0.get('lite') === '1' || (qs0.get('lite') !== '0' && (/iPhone|iPad|Android|Mobile/i.test(navigator.userAgent)
  || (navigator.maxTouchPoints > 1 && /Mac/.test(navigator.platform)) || (navigator.deviceMemory !== undefined && navigator.deviceMemory <= 4)));
import { batchStaticCity } from '../../agents/demo_rev02/static-batches.js';
import { createReplay, applyCityFilter, SHOT_ORDER, timeString } from './replay.js';
import { TILE, placeTile, tileClipPlanes, setClipping, tileBuildingCentre, tileBuildingIds, hideReplaced, materialsOf } from './tile.js';
import { EXPANSION_BATCHES, installExpansion } from './expansion.js';

// ------------------------------------------------------------------ grid <-> model alignment
// Field arrays: 4 m cells, 768 cols (west->east) x 704 rows (south->north), domain origin (480, 640) m.
// Model (glTF, Y up): X = domain_x - 2116, Z = -(domain_y - 2124). Verified: the model's building
// extent [-1491,1358] x north [-1370,1224] equals the README's building extent in domain coords.
const W = 768, H = 704, CELL = 4;
const X0 = 480 - 2116;          // west edge of column 0            -> -1636
const ZS = -(640 - 2124);       // Z of the south edge of row 0     ->  1484
const CX = X0 + W * CELL / 2;   // plane centre X                    ->  -100
const CZ = ZS - H * CELL / 2;   // plane centre Z                    ->    76
const CAMPUS = { min: [514, -9], max: [897, 324] };  // Imperial College buildings (X, Z)
const GLB = CITY_GLB;   // viewer/config.js: models/ locally, a GitHub Release on the Pages copy
const SUPPLEMENT_GLB = '../../models/buildings_supplement.glb';
let supplementBatches = null;
const expansions = [];
const TREE_NODE = /simplified canopy|simplified trunk|inherited tre|\btrees?\b|canopy|crown|hedge|planting|planter/i;
const TREE_MAT = /broadleaf|crown|tree bark|hedge|foliage|grass/i;
const FILES = {
  wind: 'wind/uvw_z8-12m_tcyx.npy',
  poll: 'pollution/concentration_z12-16m_tyx.npy',
  temp: 'temperature2d/temperature_tyx.npy',
  flood: 'flood/depth_4m_tyx.npy',          // 19 frames, every 10 min of a 3 h cloudburst (1 m shallow-water run, 4 m block means)
  floodMax: 'flood/max_depth_4m_yx.npy',    // static: maximum depth over the event (shown in overlay mode)
  // Sunlight (physics/solar): clear-sky global horizontal irradiance every 10 min (4 m block means of the 1 m model) and the
  // 1 m direct-beam shadow mask on the hour, for the summer and winter solstice. Both days have their own frame count (manifest).
  solar: { '20260621': 'solar/ghi_4m_20260621_tyx.npy', '20261221': 'solar/ghi_4m_20261221_tyx.npy' },
  shadow: { '20260621': 'solar/shadow_1m_20260621_tyx.npy', '20261221': 'solar/shadow_1m_20261221_tyx.npy' },
  // Day cycle (physics/temperature3d_solar): Yi Qi's 3-D temperature model driven by the solar model, 21 June, hourly 05:00-24:00
  diurnal: { ground: 'temperature3d_solar/diurnal_20260621_ground_surface_c_tyx.npy', air0: 'temperature3d_solar/diurnal_20260621_air_0_4m_c_tyx.npy', air12: 'temperature3d_solar/diurnal_20260621_air_12_16m_c_tyx.npy' },
};
const W1 = 3072, H1 = 2816;   // the 1 m shadow grid (same origin / orientation as the 4 m grid)
const LAYER_Y = { wind: 10, temp: 0.6, iso: 12, poll: 14, particles: 11, flood: 0.8, solar: 0.7, shadow: 0.75, diurnal: 0.6 };
const DIURNAL_RANGE = { ground: [8, 38], groundRel: [-12, 12], air0: [12, 30], air0Rel: [-3, 3], air12: [12, 30] };   // °C per display mode; *Rel = minus the hour's ambient air temperature (series.json: ground 12-35, air 14-28)
const ISO_LEVELS = Array.from({ length: 11 }, (_, i) => +(31.0 + 0.1 * i).toFixed(1));
const ISO_COLORS = ['#ffffb2', '#fed976', '#feb24c', '#fd8d3c', '#f03b20', '#bd0026'];
const TEMP_RANGE = [31.2, 32.2];
const WIND_RANGE = [0, 1.6];
const FLOOD_RANGE = [0.02, 0.6];   // m of water; below 0.02 m counts as dry (manifest hint); 0.6 m ≈ the 99th percentile of ground cells, deeper cells saturate

// ------------------------------------------------------------------ DOM
const $ = id => document.getElementById(id);
const ui = {
  stage: $('stage'), loading: $('loading'), bar: $('bar'), pct: $('pct'), readout: $('readout'),
  lWind: $('l-wind'), lTemp: $('l-temp'), lPoll: $('l-poll'), lFlood: $('l-flood'), oFlood: $('o-flood'), lModel: $('l-model'), lGround: $('l-ground'), lTrees: $('l-trees'), lPart: $('l-part'),
  tempMode: $('temp-mode'), mode: $('mode'),
  lSolar: $('l-solar'), oSolar: $('o-solar'), solarDate: $('solar-date'), solarMode: $('solar-mode'), solarOpen: $('solar-open'),
  lDiurnal: $('l-diurnal'), oDiurnal: $('o-diurnal'), diurnalMode: $('diurnal-mode'), diurnalLo: $('diurnal-lo'), diurnalHi: $('diurnal-hi'), diurnalUnit: $('diurnal-unit'),
  oWind: $('o-wind'), oTemp: $('o-temp'), oPoll: $('o-poll'), nPart: $('n-part'),
  play: $('play'), step: $('step'), timeLabel: $('time-label'), rate: $('rate'), replay: $('replay'),
  info: $('info'), stats: $('stats'), auto: $('auto'),
  lCars: $('l-cars'), lUavs: $('l-uavs'), lSignals: $('l-signals'), lStations: $('l-stations'), lRoads: $('l-roads'), lMap: $('l-map'),
  lTile: $('l-tile'), lBirds: $('l-birds'),
};
const shotButtons = [...document.querySelectorAll('.shot[data-shot]')];
const fieldButtons = [...document.querySelectorAll('.field[data-field]')];
let section = 'campus';   // 'campus' (traffic / UAV tour) | 'fields' (overhead physics fields) | 'free'
let replayLayer = null;   // created after the city loads

// ------------------------------------------------------------------ colour maps
function hex(h) { return [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)]; }
function lut(stops) {
  const st = stops.map(hex), out = new Uint8Array(256 * 3);
  for (let i = 0; i < 256; i++) {
    const x = i / 255 * (st.length - 1), j = Math.min(st.length - 2, Math.floor(x)), f = x - j;
    for (let k = 0; k < 3; k++) out[i * 3 + k] = Math.round(st[j][k] * (1 - f) + st[j + 1][k] * f);
  }
  return out;
}
const TEMP_LUT = lut(['#ffffb2', '#fed976', '#feb24c', '#fd8d3c', '#f03b20', '#bd0026']);
const REDS = lut(['#fff5f0', '#fee0d2', '#fcbba1', '#fc9272', '#fb6a4a', '#ef3b2c', '#cb181d', '#a50f15', '#67000d']);
const BLUES = lut(['#f7fbff', '#deebf7', '#c6dbef', '#9ecae1', '#6baed6', '#4292c6', '#2171b5', '#08519c', '#08306b']);
const FLOOD_LUT = lut(['#9fd8f2', '#4fb3e6', '#1e88d0', '#0d5fb0', '#083b85', '#041f52']);
const DIURNAL_LUT = lut(['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']);
const PURPLES = lut(['#efedf5', '#dadaeb', '#bcbddc', '#9e9ac8', '#807dba', '#6a51a3', '#54278f', '#3f007d', '#2c0060']);

// ------------------------------------------------------------------ renderer / scene
const renderer = new THREE.WebGLRenderer({ canvas: $('gl'), antialias: true, powerPreference: 'high-performance', logarithmicDepthBuffer: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.localClippingEnabled = true;   // the detail tile cuts a hole into the main model
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a2029);
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 5, 30000);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true; controls.dampingFactor = 0.08;
controls.maxPolarAngle = Math.PI / 2 - 0.02;
controls.enabled = false;

scene.add(new THREE.HemisphereLight(0xdfe8f5, 0x3b3f46, 1.1));
const sun = new THREE.DirectionalLight(0xfff2e0, 2.2);
sun.position.set(-1200, 2200, 1500);
scene.add(sun);
scene.add(new THREE.AmbientLight(0xffffff, 0.25));

// dark base plate under the model so the field planes have a ground even outside the site mesh
const base = new THREE.Mesh(new THREE.PlaneGeometry(W * CELL + 400, H * CELL + 400), new THREE.MeshStandardMaterial({ color: 0x2b2f35, roughness: 1 }));
base.rotation.x = -Math.PI / 2; base.position.set(CX, -0.5, CZ);
scene.add(base);

const model = new THREE.Group();
scene.add(model);

// ------------------------------------------------------------------ field planes (textures)
function makePlane(y, opacity, renderOrder) {
  const data = new Uint8Array(W * H * 4);
  const tex = new THREE.DataTexture(data, W, H, THREE.RGBAFormat);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.minFilter = THREE.LinearFilter; tex.magFilter = THREE.LinearFilter; tex.generateMipmaps = false;
  const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, opacity, depthWrite: false, side: THREE.DoubleSide });
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(W * CELL, H * CELL), mat);
  mesh.rotation.x = -Math.PI / 2; mesh.position.set(CX, y, CZ); mesh.renderOrder = renderOrder;
  mesh.visible = false;
  scene.add(mesh);
  return { mesh, tex, data, mat, fade: 0 };
}
const tempPlane = makePlane(LAYER_Y.temp, +ui.oTemp.value, 1);
const windPlane = makePlane(LAYER_Y.wind, +ui.oWind.value, 2);
const pollPlane = makePlane(LAYER_Y.poll, +ui.oPoll.value, 3);
const floodPlane = makePlane(LAYER_Y.flood, +ui.oFlood.value, 1);
const solarPlane = makePlane(LAYER_Y.solar, +ui.oSolar.value, 1);
const diurnalPlane = makePlane(LAYER_Y.diurnal, +ui.oDiurnal.value, 1);
// 1 m shadow mask: the uint8 frame (1 = shaded) is expanded into an RGBA texture of the full 1 m grid (34.6 MB): a dark veil where
// shaded, a faint warm tint where sunlit, so the model's own streets show through. (A single-channel R8 texture sampled from a
// ShaderMaterial rendered nothing under the logarithmic depth buffer, so the plain textured plane is used, as for the 4 m layers.)
function makeShadowPlane() {
  const data = new Uint8Array(W1 * H1 * 4);
  const tex = new THREE.DataTexture(data, W1, H1, THREE.RGBAFormat);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.minFilter = THREE.LinearFilter; tex.magFilter = THREE.NearestFilter; tex.generateMipmaps = false;
  const mat = new THREE.MeshBasicMaterial({ map: tex, transparent: true, opacity: +ui.oSolar.value, depthWrite: false, side: THREE.DoubleSide });
  const mesh = new THREE.Mesh(new THREE.PlaneGeometry(W * CELL, H * CELL), mat);
  mesh.rotation.x = -Math.PI / 2; mesh.position.set(CX, LAYER_Y.shadow, CZ); mesh.renderOrder = 1; mesh.visible = false;
  scene.add(mesh);
  return { mesh, tex, data, mat, fade: 0 };
}
const shadowPlane = makeShadowPlane();
function uploadShadow(u8) {
  const d = shadowPlane.data, n = W1 * H1;
  for (let i = 0, o = 0; i < n; i++, o += 4) {
    if (u8[i]) { d[o] = 18; d[o + 1] = 28; d[o + 2] = 96; d[o + 3] = 158; } else { d[o] = 255; d[o + 1] = 234; d[o + 2] = 150; d[o + 3] = 80; }   // shade: blue-violet veil; sun: warm wash
  }
  shadowPlane.tex.needsUpdate = true;
}

let footprint = null, solidWind = null, studyArea = null;
function paintWind(uv) {
  const d = windPlane.data, n = W * H, inv = 255 / (WIND_RANGE[1] - WIND_RANGE[0]);
  for (let i = 0; i < n; i++) {
    const o = i * 4;
    if (solidWind && solidWind[i]) { d[o + 3] = 0; continue; }
    const u = uv[i], v = uv[n + i], w = uv[2 * n + i];
    let k = (Math.sqrt(u * u + v * v + w * w) - WIND_RANGE[0]) * inv; k = k < 0 ? 0 : k > 255 ? 255 : k | 0;
    d[o] = BLUES[k * 3]; d[o + 1] = BLUES[k * 3 + 1]; d[o + 2] = BLUES[k * 3 + 2]; d[o + 3] = 235;
  }
  windPlane.tex.needsUpdate = true;
}
// ------------------------------------------------------------------ isotherms (marching squares on a 2x-averaged grid)
const ISO_STRIDE = 2, NX = W / ISO_STRIDE, NY = H / ISO_STRIDE;
const isoGrid = new Float32Array(NX * NY);
const ISO_MAX_SEG = 600000;
const iso = { pos: new Float32Array(ISO_MAX_SEG * 6), col: new Float32Array(ISO_MAX_SEG * 6), geom: null, lines: null, count: 0 };
iso.material = new LineMaterial({ vertexColors: true, linewidth: 2, transparent: true, opacity: +ui.oTemp.value, depthWrite: false, worldUnits: false });
iso.material.resolution.set(window.innerWidth, window.innerHeight);
const ISO_LUT = lut(ISO_COLORS);
const ISO_RGB = ISO_LEVELS.map((_, L) => { const k = Math.round(L / (ISO_LEVELS.length - 1) * 255); return [ISO_LUT[k * 3] / 255, ISO_LUT[k * 3 + 1] / 255, ISO_LUT[k * 3 + 2] / 255]; });
function uploadIsotherms(n) {
  if (iso.lines) { scene.remove(iso.lines); iso.geom.dispose(); iso.lines = null; }
  if (!n) return;
  iso.geom = new LineSegmentsGeometry();
  iso.geom.setPositions(iso.pos.subarray(0, n * 6));
  iso.geom.setColors(iso.col.subarray(0, n * 6));
  iso.lines = new LineSegments2(iso.geom, iso.material);
  iso.lines.renderOrder = 3; iso.lines.frustumCulled = false;
  iso.lines.visible = tempPlane.fade > 0 && ui.tempMode.value === 'iso';
  scene.add(iso.lines);
}
function paintIsotherms(vals) {
  // average 2x2 blocks; blocks touching a building become NaN so contours stop at walls
  for (let j = 0; j < NY; j++) for (let i = 0; i < NX; i++) {
    const r0 = j * ISO_STRIDE, c0 = i * ISO_STRIDE;
    const a = r0 * W + c0, b = a + 1, c = a + W, d = c + 1;
    const blocked = (footprint && (footprint[a] || footprint[b] || footprint[c] || footprint[d])) || (studyArea && !(studyArea[a] && studyArea[b] && studyArea[c] && studyArea[d]));
    isoGrid[j * NX + i] = blocked ? NaN : (vals[a] + vals[b] + vals[c] + vals[d]) * 0.25;
  }
  const pos = iso.pos, col = iso.col;
  const y = LAYER_Y.iso, sx = ISO_STRIDE * CELL;
  let n = 0;
  const px = (i, j) => [X0 + (i * ISO_STRIDE + ISO_STRIDE / 2) * CELL, ZS - (j * ISO_STRIDE + ISO_STRIDE / 2) * CELL];
  const put = (x1, z1, x2, z2, rgb) => {
    if (n >= ISO_MAX_SEG) return;
    const o = n * 6;
    pos[o] = x1; pos[o + 1] = y; pos[o + 2] = z1; pos[o + 3] = x2; pos[o + 4] = y; pos[o + 5] = z2;
    col[o] = rgb[0]; col[o + 1] = rgb[1]; col[o + 2] = rgb[2]; col[o + 3] = rgb[0]; col[o + 4] = rgb[1]; col[o + 5] = rgb[2];
    n++;
  };
  for (let j = 0; j < NY - 1; j++) for (let i = 0; i < NX - 1; i++) {
    const v0 = isoGrid[j * NX + i], v1 = isoGrid[j * NX + i + 1], v2 = isoGrid[(j + 1) * NX + i + 1], v3 = isoGrid[(j + 1) * NX + i];
    if (v0 !== v0 || v1 !== v1 || v2 !== v2 || v3 !== v3) continue;
    const lo = Math.min(v0, v1, v2, v3), hi = Math.max(v0, v1, v2, v3);
    const [x0, z0] = px(i, j);
    for (let L = 0; L < ISO_LEVELS.length; L++) {
      const lv = ISO_LEVELS[L];
      if (lv < lo || lv >= hi) continue;
      const idx = (v0 >= lv ? 1 : 0) | (v1 >= lv ? 2 : 0) | (v2 >= lv ? 4 : 0) | (v3 >= lv ? 8 : 0);
      if (idx === 0 || idx === 15) continue;
      // edge points: e0 top (v0-v1, +x), e1 right (v1-v2, -z), e2 bottom (v3-v2), e3 left (v0-v3)
      const t01 = (lv - v0) / (v1 - v0), t12 = (lv - v1) / (v2 - v1), t32 = (lv - v3) / (v2 - v3), t03 = (lv - v0) / (v3 - v0);
      const e0 = [x0 + t01 * sx, z0], e1 = [x0 + sx, z0 - t12 * sx], e2 = [x0 + t32 * sx, z0 - sx], e3 = [x0, z0 - t03 * sx];
      const rgb = ISO_RGB[L];
      switch (idx) {
        case 1: case 14: put(e3[0], e3[1], e0[0], e0[1], rgb); break;
        case 2: case 13: put(e0[0], e0[1], e1[0], e1[1], rgb); break;
        case 3: case 12: put(e3[0], e3[1], e1[0], e1[1], rgb); break;
        case 4: case 11: put(e1[0], e1[1], e2[0], e2[1], rgb); break;
        case 5: case 10: put(e3[0], e3[1], e0[0], e0[1], rgb); put(e1[0], e1[1], e2[0], e2[1], rgb); break;
        case 6: case 9: put(e0[0], e0[1], e2[0], e2[1], rgb); break;
        case 7: case 8: put(e3[0], e3[1], e2[0], e2[1], rgb); break;
      }
    }
  }
  iso.count = n;
  uploadIsotherms(n);
}
function paintTemperature(vals) {
  const d = tempPlane.data, inv = 255 / (TEMP_RANGE[1] - TEMP_RANGE[0]);
  for (let i = 0; i < W * H; i++) {
    const o = i * 4;
    if ((footprint && footprint[i]) || (studyArea && !studyArea[i])) { d[o + 3] = 0; continue; }
    let k = (vals[i] - TEMP_RANGE[0]) * inv; k = k < 0 ? 0 : k > 255 ? 255 : k | 0;
    d[o] = TEMP_LUT[k * 3]; d[o + 1] = TEMP_LUT[k * 3 + 1]; d[o + 2] = TEMP_LUT[k * 3 + 2]; d[o + 3] = 235;
  }
  tempPlane.tex.needsUpdate = true;
}
function paintFlood(vals) {
  const d = floodPlane.data, inv = 255 / (FLOOD_RANGE[1] - FLOOD_RANGE[0]);
  for (let i = 0; i < W * H; i++) {
    const o = i * 4, h = vals[i];
    if (!(h > FLOOD_RANGE[0]) || (footprint && footprint[i])) { d[o + 3] = 0; continue; }
    let k = (h - FLOOD_RANGE[0]) * inv; k = k > 255 ? 255 : k | 0;
    d[o] = FLOOD_LUT[k * 3]; d[o + 1] = FLOOD_LUT[k * 3 + 1]; d[o + 2] = FLOOD_LUT[k * 3 + 2]; d[o + 3] = (150 + k * 0.4) | 0;
  }
  floodPlane.tex.needsUpdate = true;
}
// Sunlight: a lighting overlay rather than a heat map. Shade = 1 - GHI / open-sky GHI of the frame (99th percentile, roofs see the
// open sky) is painted as a dark veil, sunlit cells get a faint warm tint, so the model's own streets show through the shadows.
let solarOpen = 0;
function paintSolar(vals) {
  const d = solarPlane.data, n = W * H;
  const sorted = Float32Array.from(vals).sort(); solarOpen = sorted[Math.floor(n * 0.99)];
  const dusk = solarOpen < 15, inv = dusk ? 0 : 1 / solarOpen;
  for (let i = 0; i < n; i++) {
    const o = i * 4;
    let sh = dusk ? 1 : 1 - vals[i] * inv; sh = sh < 0 ? 0 : sh > 1 ? 1 : sh;
    // same look as the 1 m shadow layer: warm wash where the cell sees the full sky, blue-violet veil scaled by the shade fraction
    if (sh > 0.08) { const t = Math.pow(sh, 0.8); d[o] = 18; d[o + 1] = 28; d[o + 2] = 96; d[o + 3] = (158 * t) | 0; }
    else { d[o] = 255; d[o + 1] = 234; d[o + 2] = 150; d[o + 3] = 80; }
  }
  ui.solarOpen.textContent = dusk ? 'dusk' : `${solarOpen.toFixed(0)} open sky`;
  solarPlane.tex.needsUpdate = true;
}
const diurnalArray = () => FILES.diurnal[ui.diurnalMode.value.replace('Rel', '')];
const diurnalAmbient = k => manifest?.temperature3d_solar?.diurnal?.['diurnal_2026-06-21']?.ambient_c?.[k];
function paintDiurnal(vals) {
  const mode = ui.diurnalMode.value, rel = /Rel$/.test(mode), d = diurnalPlane.data, [lo, hi] = DIURNAL_RANGE[mode], inv = 255 / (hi - lo), air = !/^ground/.test(mode);
  const ref = rel ? (diurnalAmbient(frameIndex(state.step).diurnal) ?? 0) : 0;
  for (let i = 0; i < W * H; i++) {
    const o = i * 4;
    if (footprint && footprint[i] && !air) { d[o + 3] = 0; continue; }   // the surface map has no value inside buildings; the air layers do
    let k = (vals[i] - ref - lo) * inv; k = k < 0 ? 0 : k > 255 ? 255 : k | 0;
    d[o] = DIURNAL_LUT[k * 3]; d[o + 1] = DIURNAL_LUT[k * 3 + 1]; d[o + 2] = DIURNAL_LUT[k * 3 + 2]; d[o + 3] = 235;
  }
  ui.diurnalLo.textContent = (rel && lo > 0 ? '+' : '') + lo; ui.diurnalHi.textContent = (rel ? '+' : '') + hi; ui.diurnalUnit.textContent = rel ? 'Δ°C vs ambient air' : '°C';
  diurnalPlane.tex.needsUpdate = true;
}
function paintPollution(vals) {
  const d = pollPlane.data;
  for (let i = 0; i < W * H; i++) {
    const o = i * 4, c = vals[i];
    if (!(c > 0.1)) { d[o + 3] = 0; continue; }
    let f = (Math.log10(c) + 1) / 4; f = f > 1 ? 1 : f;   // 0.1 -> 0, 1000 -> 1
    const k = (f * 255) | 0;
    d[o] = PURPLES[k * 3]; d[o + 1] = PURPLES[k * 3 + 1]; d[o + 2] = PURPLES[k * 3 + 2];
    d[o + 3] = Math.min(255, 40 + f * 260) | 0;
  }
  pollPlane.tex.needsUpdate = true;
}

// ------------------------------------------------------------------ wind particles (comet tails)
const TAIL = 7;
const wind = { uv: null, n: 0, x: null, y: null, age: null, hist: null, geom: null, lines: null, fade: 0 };
function buildParticles(n) {
  if (wind.lines) { scene.remove(wind.lines); wind.geom.dispose(); }
  wind.n = n; wind.x = new Float32Array(n); wind.y = new Float32Array(n); wind.age = new Uint16Array(n);
  wind.hist = new Float32Array(n * TAIL * 2);
  const segs = n * (TAIL - 1);
  wind.geom = new THREE.BufferGeometry();
  wind.geom.setAttribute('position', new THREE.BufferAttribute(new Float32Array(segs * 2 * 3), 3));
  wind.geom.setAttribute('color', new THREE.BufferAttribute(new Float32Array(segs * 2 * 3), 3));
  const mat = new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.9, blending: THREE.AdditiveBlending, depthWrite: false });
  wind.lines = new THREE.LineSegments(wind.geom, mat);
  wind.lines.renderOrder = 4; wind.lines.visible = false; wind.lines.frustumCulled = false;
  scene.add(wind.lines);
  for (let i = 0; i < n; i++) respawn(i, true);
}
function respawn(i, randomAge) {
  const x = Math.random() * W, y = Math.random() * H;
  wind.x[i] = x; wind.y[i] = y; wind.age[i] = randomAge ? (Math.random() * 100) | 0 : 0;
  for (let k = 0; k < TAIL; k++) { wind.hist[(i * TAIL + k) * 2] = x; wind.hist[(i * TAIL + k) * 2 + 1] = y; }
}
function stepParticles(dtSec) {
  if (!wind.uv) return;
  const n = W * H, uv = wind.uv, pos = wind.geom.attributes.position.array, col = wind.geom.attributes.color.array;
  const vis = dtSec * 60;             // visual seconds of physical time per real second, in cells: (m/s) * s / 4 m
  const invR = 1 / (WIND_RANGE[1] - WIND_RANGE[0]);
  for (let i = 0; i < wind.n; i++) {
    let x = wind.x[i], y = wind.y[i];
    const c = x | 0, r = y | 0, idx = r * W + c;
    const u = uv[idx], v = uv[n + idx], sp = Math.hypot(u, v);
    wind.age[i]++;
    if (sp < 0.03 || wind.age[i] > 160) { respawn(i, false); continue; }
    x += u * vis / CELL; y += v * vis / CELL;
    if (x < 0 || x >= W || y < 0 || y >= H) { respawn(i, false); continue; }
    // shift history
    const h = i * TAIL * 2;
    for (let k = TAIL - 1; k > 0; k--) { wind.hist[h + k * 2] = wind.hist[h + (k - 1) * 2]; wind.hist[h + k * 2 + 1] = wind.hist[h + (k - 1) * 2 + 1]; }
    wind.hist[h] = x; wind.hist[h + 1] = y; wind.x[i] = x; wind.y[i] = y;
    const t = Math.min(1, (sp - WIND_RANGE[0]) * invR);
    const R = 0.45 + 0.55 * t, G = 0.65 + 0.35 * t, B = 1.0;
    for (let k = 0; k < TAIL - 1; k++) {
      const s = (i * (TAIL - 1) + k) * 6;
      const ax = wind.hist[h + k * 2], ay = wind.hist[h + k * 2 + 1], bx = wind.hist[h + (k + 1) * 2], by = wind.hist[h + (k + 1) * 2 + 1];
      pos[s] = X0 + ax * CELL; pos[s + 1] = LAYER_Y.particles; pos[s + 2] = ZS - ay * CELL;
      pos[s + 3] = X0 + bx * CELL; pos[s + 4] = LAYER_Y.particles; pos[s + 5] = ZS - by * CELL;
      const fa = 1 - k / (TAIL - 1), fb = 1 - (k + 1) / (TAIL - 1);
      col[s] = R * fa; col[s + 1] = G * fa; col[s + 2] = B * fa;
      col[s + 3] = R * fb; col[s + 4] = G * fb; col[s + 5] = B * fb;
    }
  }
  wind.geom.attributes.position.needsUpdate = true;
  wind.geom.attributes.color.needsUpdate = true;
}

// ------------------------------------------------------------------ time / frames / sequencing
// Timeline = wind step 1..100 (25 s each). Pollution shares it; the 2-D temperature run starts at step 41
// (its frame k = step - 40). In "seq" mode the three fields play one after another, each alone.
// The flood run has its own clock (19 frames, every 10 min of a 3 h cloudburst), so its phase uses steps 1..19 at 2 steps/s
// and, in overlay mode, the static maximum-depth map is shown instead.
const PHASES = { wind: { start: 1, end: 100, label: 'Wind speed · 8–12 m' }, temp: { start: 41, end: 100, label: 'Temperature · 2-D model (12–16 m)' }, poll: { start: 1, end: 100, label: 'Pollutant concentration · 12–16 m' },
  flood: { start: 1, end: 19, rate: 2, label: 'Flooding · surface water depth (3 h cloudburst, 1 m shallow-water model)' },
  // Sunlight and the day cycle have their own clocks: 10-min GHI frames (99 on 21 June, 47 on 21 December) or hourly 1 m shadows
  // (17 / 7 frames); the coupled temperature run is hourly 05:00-24:00 (20 frames). `end` of the solar phase follows the day / mode.
  solar: { start: 1, end: 99, rate: 12, label: 'Sunlight · clear-sky irradiance (1 m shadow model, 4 m block means)' },
  diurnal: { start: 1, end: 20, rate: 2, label: 'Day cycle · solar-coupled 3-D temperature model, 21 June' } };
const PHASE_ORDER = ['wind', 'temp', 'solar', 'diurnal', 'poll', 'flood'];
const OVERLAY_LABEL = 'Overlay · wind speed / temperature / sunlight / day cycle / pollution / flooding';
const state = { step: 1, playing: false, timer: null, token: 0, loading: false, fields: { wind: null, temp: null, poll: null, flood: null, solar: null, shadow: null, diurnal: null }, introDone: false, phase: 'wind' };
let floodMeta = null, manifest = null;   // manifest entry of flood/depth_4m_tyx.npy (time_s, rain_mm_h); the whole manifest (solar / diurnal frame times)
fetch(DATA + 'manifest.json').then(r => r.json()).then(m => { manifest = m; floodMeta = m.arrays?.[FILES.flood] ?? null; solarPhaseSetup(); }).catch(() => {});
const solarFile = () => (ui.solarMode.value === 'shadow' ? FILES.shadow : FILES.solar)[ui.solarDate.value];
const solarKey = () => (ui.solarMode.value === 'shadow' ? 'shadow_' : 'solar_') + ui.solarDate.value;
// Decoded frame of a layer: the pre-rendered PNG (physics/web/, ~100 KB) when present, else the raw .npy Range read.
// Both give the same array layout (wind: [u..., v..., w...]; shadow: Uint8Array 0/1).
function frame(key, file, k, raw = false) {
  if (hasLayer(key)) return getFrameF32(key, k);
  return getFrame(file, k).then(a => raw ? a : f16(a));
}
function prefetch(key, file, k) { if (hasLayer(key)) getFrameF32(key, k); else getFrame(file, k); }
const solarMeta = () => manifest?.arrays?.[solarFile()];
function solarPhaseSetup() {   // frame count and rate of the solar phase follow the chosen day and display mode
  const meta = solarMeta(), shadow = ui.solarMode.value === 'shadow';
  PHASES.solar.end = meta?.shape?.[0] ?? (shadow ? (ui.solarDate.value === '20260621' ? 17 : 7) : (ui.solarDate.value === '20260621' ? 99 : 47));
  PHASES.solar.rate = shadow ? 2 : 12;
  PHASES.solar.label = `Sunlight · ${ui.solarDate.value === '20260621' ? '21 June' : '21 December'} · ${shadow ? '1 m shadows on the hour' : 'clear-sky irradiance every 10 min'}`;
}
// the scene's sun follows the real sun position of the solar frame (azimuth 0 = north, clockwise; model north = -Z)
const SUN_DEFAULT = { pos: sun.position.clone(), intensity: sun.intensity };
function placeSun(altDeg, azDeg) {
  if (altDeg === undefined) { sun.position.copy(SUN_DEFAULT.pos); sun.intensity = SUN_DEFAULT.intensity; return; }
  const alt = THREE.MathUtils.degToRad(Math.max(altDeg, 2)), az = THREE.MathUtils.degToRad(azDeg), r = 3000;
  sun.position.set(r * Math.cos(alt) * Math.sin(az), r * Math.sin(alt), -r * Math.cos(alt) * Math.cos(az));
  sun.intensity = SUN_DEFAULT.intensity * (0.35 + 0.65 * Math.min(1, Math.max(0, altDeg) / 40));
}
function floodFrame(step) { return seqMode() && state.phase === 'flood' ? Math.max(0, Math.min(PHASES.flood.end - 1, step - 1)) : null; }   // null = static max depth
function frameIndex(step) {
  const own = ph => seqMode() && state.phase === ph;
  return { wind: step - 1, poll: step - 1, temp: Math.max(0, Math.min(60, step - 40)), flood: floodFrame(step),
    solar: Math.min(PHASES.solar.end - 1, step - 1),                                   // overlay: the 100 wind steps run through the day
    diurnal: own('diurnal') ? Math.min(19, step - 1) : Math.min(19, Math.floor((step - 1) / 5)) };
}
function seqMode() { return ui.mode.value === 'seq'; }
function activeLayers() {
  if (seqMode()) return { wind: state.phase === 'wind', temp: state.phase === 'temp', poll: state.phase === 'poll', flood: state.phase === 'flood', solar: state.phase === 'solar', diurnal: state.phase === 'diurnal' };
  return { wind: ui.lWind.checked, temp: ui.lTemp.checked, poll: ui.lPoll.checked, flood: ui.lFlood.checked, solar: ui.lSolar.checked, diurnal: ui.lDiurnal.checked };
}
function repaint() {
  const f = state.fields, act = activeLayers();
  if (!f.wind) return;
  if (act.wind || windPlane.fade > 0) paintWind(f.wind);
  if (act.poll || pollPlane.fade > 0) paintPollution(f.poll);
  if ((act.flood || floodPlane.fade > 0) && f.flood) paintFlood(f.flood);
  if ((act.solar || solarPlane.fade > 0) && f.solar && ui.solarMode.value !== 'shadow') paintSolar(f.solar);
  if ((act.diurnal || diurnalPlane.fade > 0) && f.diurnal) paintDiurnal(f.diurnal);
  if (act.temp || tempPlane.fade > 0) {
    if (ui.tempMode.value === 'iso') { paintIsotherms(f.temp); } else { paintTemperature(f.temp); }
  }
}
async function loadStep(step) {
  try { return await loadStepInner(step); } catch (e) { state.loading = false; console.error('frame load failed', e); }
}
async function loadStepInner(step) {
  const token = ++state.token, fi = frameIndex(step);
  const act = activeLayers(), wantFlood = act.flood || floodPlane.fade > 0, wantSolar = act.solar || solarPlane.fade > 0, wantDiurnal = act.diurnal || diurnalPlane.fade > 0;
  const shadowMode = ui.solarMode.value === 'shadow';
  // fetch only what is shown or fading (plus a first frame of each field for the readout); every other layer keeps its last frame
  const wantWind = act.wind || windPlane.fade > 0 || !state.fields.wind, wantPoll = act.poll || pollPlane.fade > 0 || !state.fields.poll, wantTemp = act.temp || tempPlane.fade > 0 || !state.fields.temp;
  state.loading = true;
  const dKey = 'diurnal_' + ui.diurnalMode.value.replace('Rel', '');
  const [wr, pr, tr, fr, sr, dr] = await Promise.all([wantWind ? frame('wind', FILES.wind, fi.wind) : null, wantPoll ? frame('poll', FILES.poll, fi.poll) : null, wantTemp ? frame('temp', FILES.temp, fi.temp) : null,
    wantFlood ? (fi.flood === null ? (hasLayer('floodMax') ? getFrameF32('floodMax', 0) : npy(FILES.floodMax).readAll().then(f16)) : frame('flood', FILES.flood, fi.flood)) : null,
    wantSolar ? frame(solarKey(), solarFile(), fi.solar, shadowMode) : null,
    wantDiurnal ? frame(dKey, diurnalArray(), fi.diurnal) : null]);
  if (token === state.token) state.loading = false;
  if (token !== state.token) return;
  if (sr) { if (shadowMode) { state.fields.shadow = sr; state.fields.solar = null; uploadShadow(sr); } else { state.fields.solar = sr; state.fields.shadow = null; } }
  if (dr) state.fields.diurnal = dr;
  // decode only what is shown (the raw frames stay cached for the readout)
  if (wr) state.fields.wind = wr;
  if (pr) state.fields.poll = pr;
  if (tr) state.fields.temp = tr;
  if (fr) state.fields.flood = fr;
  wind.uv = state.fields.wind;
  repaint();
  const ph = PHASES[state.phase];
  const sm = wantSolar ? solarMeta() : null, sAlt = sm?.altitude_deg?.[fi.solar], sAz = sm?.azimuth_deg?.[fi.solar];
  placeSun(seqMode() && state.phase === 'solar' && sAlt !== undefined ? sAlt : undefined, sAz);
  if (seqMode() && state.phase === 'flood') {
    const k = fi.flood, ts = floodMeta?.time_s?.[k], rain = floodMeta?.rain_mm_h?.[k];
    ui.timeLabel.textContent = `Flooding · frame ${k + 1} / ${ph.end} · t = ${ts !== undefined ? Math.round(ts / 60) : k * 10} min` + (rain !== undefined ? ` · rain ${rain.toFixed(1)} mm/h` : '');
  } else if (seqMode() && state.phase === 'solar') {
    const k = fi.solar, tl = sm?.time_local?.[k];
    ui.timeLabel.textContent = `${ui.solarDate.value === '20260621' ? '21 June' : '21 December'} · ${tl ?? `frame ${k + 1}`} local · sun altitude ${sAlt !== undefined ? sAlt.toFixed(0) + '°' : '–'} · ${k + 1} / ${ph.end}`;
  } else if (seqMode() && state.phase === 'diurnal') {
    const k = fi.diurnal, dm = manifest?.temperature3d_solar?.diurnal?.['diurnal_2026-06-21'], hr = dm?.hours_local?.[k], amb = dm?.ambient_c?.[k];
    ui.timeLabel.textContent = `21 June · ${hr !== undefined ? String(hr).padStart(2, '0') + ':00' : `hour ${k + 1}`} local · ambient ${amb !== undefined ? amb.toFixed(1) + ' °C' : '–'} · ${k + 1} / ${ph.end}`;
  } else ui.timeLabel.textContent = seqMode()
    ? `${ph.label} · frame ${step - ph.start + 1} / ${ph.end - ph.start + 1} · t = ${step * 25} s`
    : `Step ${step} · t = ${step * 25} s` + (step < 41 ? ' · temperature run not started' : '') + (act.flood ? ' · flood layer = maximum depth of the 3 h event' : '');
  for (let k = 1; k <= 4; k++) { const n = step + k; if (n <= ph.end) { const f = frameIndex(n); if (act.wind) prefetch('wind', FILES.wind, f.wind); if (act.poll) prefetch('poll', FILES.poll, f.poll); if (act.temp) prefetch('temp', FILES.temp, f.temp); if (act.flood && f.flood !== null) prefetch('flood', FILES.flood, f.flood); if (act.solar) prefetch(solarKey(), solarFile(), f.solar); if (act.diurnal) prefetch(dKey, diurnalArray(), f.diurnal); } }
}
function setStep(s) {
  const lo = seqMode() ? PHASES[state.phase].start : 1, hi = seqMode() ? PHASES[state.phase].end : 100;
  state.step = Math.max(lo, Math.min(hi, s)); ui.step.min = lo; ui.step.max = hi; ui.step.value = state.step;
  loadStep(state.step);
}
function setPhase(phase) {
  state.phase = phase;
  ui.stage.textContent = seqMode() ? `Sequence · ${PHASES[phase].label}` : OVERLAY_LABEL;
  if (section === 'fields' && state.introDone && seqMode()) ui.lGround.checked = ui.lTrees.checked = phase === 'flood' || phase === 'solar';   // flood and sunlight read better with the streets and green areas under them; the other fields hide them
  applyLayers();
  setStep(PHASES[phase].start);
  if (state.playing) setPlaying(true);   // phases can have their own rate (flood plays at 2 frames/s)
  setSectionUI();
}
function tick() {
  if (state.loading) return;   // previous frame still loading: wait for it rather than cancelling it (that starved the painter)
  if (state.step < (seqMode() ? PHASES[state.phase].end : 100)) { setStep(state.step + 1); return; }
  if (seqMode()) {
    const i = PHASE_ORDER.indexOf(state.phase);
    if (i === PHASE_ORDER.length - 1 && ui.auto.checked && section === 'fields') { runCampus(); return; }
    setPhase(PHASE_ORDER[(i + 1) % PHASE_ORDER.length]);
  } else setStep(1);
}
function setPlaying(p) {
  state.playing = p; if (section !== 'campus') ui.play.textContent = p ? '❚❚' : '▶';
  clearInterval(state.timer); state.timer = null;
  const rate = section === 'campus' ? 12 : (seqMode() && PHASES[state.phase].rate) || +ui.rate.value;
  if (p) state.timer = setInterval(tick, 1000 / rate);
}
const RATES = { replay: [[0.5, '0.5×'], [1, '1×'], [2, '2×'], [4, '4×'], [10, '10×']], fields: [[2, '2 steps/s'], [4, '4 steps/s'], [8, '8 steps/s'], [12, '12 steps/s'], [20, '20 steps/s']] };
function setRateOptions(kind, value) {
  ui.rate.replaceChildren(...RATES[kind].map(([v, l]) => { const o = document.createElement('option'); o.value = v; o.textContent = l; return o; }));
  ui.rate.value = String(value);
}
ui.play.addEventListener('click', () => {
  if (section === 'campus' && replayLayer) { replayLayer.playing = !replayLayer.playing; ui.play.textContent = replayLayer.playing ? '❚❚' : '▶'; }
  else setPlaying(!state.playing);
});
ui.rate.addEventListener('change', () => { if (section === 'campus' && replayLayer) replayLayer.speed = +ui.rate.value; else if (state.playing) setPlaying(true); });
ui.step.addEventListener('input', () => { if (section === 'campus' && replayLayer) { replayLayer.t = +ui.step.value; replayLayer.update(replayLayer.t); } else setStep(+ui.step.value); });
ui.mode.addEventListener('change', () => { if (seqMode()) setPhase(state.phase); else { ui.stage.textContent = OVERLAY_LABEL; applyLayers(); setStep(state.step); } });
document.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
  if (e.key === ' ') { e.preventDefault(); setPlaying(!state.playing); }
  else if (e.key === 'ArrowLeft') setStep(state.step - 1);
  else if (e.key === 'ArrowRight') setStep(state.step + 1);
});

// ------------------------------------------------------------------ layer controls (with per-layer fades)
const groundMeshes = [];   // flat, wide meshes of the model (site ground, roads, paving)
const treeMeshes = [];     // canopies, trunks, hedges, planters
// South Kensington detail tile (tile.js): the main model is clipped inside the tile's plate, the tile outside it
let mainScene = null, mainBatches = null, tileGroup = null, tileBatches = null, tileIds = new Set();
const tileHidden = new Set();          // main / supplementary meshes the tile replaces (hidden while the tile is on)
const holeMaterials = new Set();       // materials of the main model's ground / road layers: clipped inside the tile
const tileHole = tileClipPlanes(false), tileKeep = tileClipPlanes(true);
function applyTile() {
  if (!tileGroup) return;
  const on = ui.lTile.checked;
  tileGroup.visible = on; tileBatches.visible = on;
  for (const o of tileHidden) o.visible = !on;
  setClipping(holeMaterials, on ? tileHole : null, true);
  applyLayers();   // ground / tree toggles respect the hidden set
}
const replaced = m => tileGroup && ui.lTile.checked && tileHidden.has(m);
ui.lTile.addEventListener('input', applyTile);
$('l-supplement').addEventListener('input', applyLayers);
$('l-expansion').checked = new URLSearchParams(location.search).get('expansion') !== '0';
$('l-expansion').addEventListener('input', applyLayers);
const FADE_SEC = 0.6;
function applyLayers() {
  const on = state.introDone, act = activeLayers();
  windPlane.target = on && act.wind ? 1 : 0;
  tempPlane.target = on && act.temp ? 1 : 0;
  pollPlane.target = on && act.poll ? 1 : 0;
  floodPlane.target = on && act.flood ? 1 : 0;
  solarPlane.target = on && act.solar && ui.solarMode.value !== 'shadow' ? 1 : 0;
  shadowPlane.target = on && act.solar && ui.solarMode.value === 'shadow' ? 1 : 0;
  diurnalPlane.target = on && act.diurnal ? 1 : 0;
  model.visible = ui.lModel.checked;
  if (supplementBatches) supplementBatches.visible = $('l-supplement').checked;
  for (const expansion of expansions) expansion.setEnabled($('l-expansion').checked);
  base.visible = ui.lGround.checked;
  for (const m of groundMeshes) m.visible = ui.lGround.checked && !replaced(m);
  for (const m of treeMeshes) m.visible = ui.lTrees.checked && !replaced(m);
  updateFades(0);
}
function updateFades(dt) {
  let changed = false;
  for (const L of [windPlane, tempPlane, pollPlane, floodPlane, solarPlane, shadowPlane, diurnalPlane]) {
    const t = L.target ?? 0;
    if (L.fade !== t) { L.fade = dt > 0 ? (L.fade < t ? Math.min(t, L.fade + dt / FADE_SEC) : Math.max(t, L.fade - dt / FADE_SEC)) : L.fade; changed = true; }
  }
  const isoMode = ui.tempMode.value === 'iso';
  windPlane.mesh.visible = windPlane.fade > 0;
  windPlane.mat.opacity = +ui.oWind.value * windPlane.fade;
  wind.lines.visible = windPlane.fade > 0 && ui.lPart.checked;
  wind.lines.material.opacity = 0.9 * windPlane.fade;
  tempPlane.mesh.visible = tempPlane.fade > 0 && !isoMode;
  tempPlane.mat.opacity = +ui.oTemp.value * tempPlane.fade;
  if (iso.lines) iso.lines.visible = tempPlane.fade > 0 && isoMode;
  iso.material.opacity = +ui.oTemp.value * tempPlane.fade;
  pollPlane.mesh.visible = pollPlane.fade > 0;
  pollPlane.mat.opacity = +ui.oPoll.value * pollPlane.fade;
  floodPlane.mesh.visible = floodPlane.fade > 0 && !!state.fields.flood;
  floodPlane.mat.opacity = +ui.oFlood.value * floodPlane.fade;
  solarPlane.mesh.visible = solarPlane.fade > 0 && !!state.fields.solar;
  solarPlane.mat.opacity = +ui.oSolar.value * solarPlane.fade;
  shadowPlane.mesh.visible = shadowPlane.fade > 0 && !!state.fields.shadow;
  shadowPlane.mat.opacity = +ui.oSolar.value * shadowPlane.fade;
  diurnalPlane.mesh.visible = diurnalPlane.fade > 0 && !!state.fields.diurnal;
  diurnalPlane.mat.opacity = +ui.oDiurnal.value * diurnalPlane.fade;
  return changed;
}
for (const el of [ui.lWind, ui.lTemp, ui.lPoll, ui.lFlood, ui.lSolar, ui.lDiurnal]) el.addEventListener('input', () => {
  if (seqMode()) { ui.mode.value = 'overlay'; ui.stage.textContent = OVERLAY_LABEL; }
  applyLayers(); repaint(); setStep(state.step);
});
for (const el of [ui.lModel, ui.lGround, ui.lTrees, ui.lPart, ui.oWind, ui.oTemp, ui.oPoll, ui.oFlood, ui.oSolar, ui.oDiurnal]) el.addEventListener('input', applyLayers);
for (const el of [ui.solarDate, ui.solarMode]) el.addEventListener('change', () => {   // new day / display: the phase gets its frame count and rate, then restarts
  solarPhaseSetup(); state.fields.solar = state.fields.shadow = null; applyLayers();
  if (seqMode() && state.phase === 'solar') { ui.stage.textContent = `Sequence · ${PHASES.solar.label}`; setStep(PHASES.solar.start); if (state.playing) setPlaying(true); } else setStep(state.step);
});
ui.diurnalMode.addEventListener('change', () => { state.fields.diurnal = null; setStep(state.step); });
ui.tempMode.addEventListener('input', () => { applyLayers(); repaint(); });
function applyReplayLayers() { replayLayer?.applyLayers({ cars: ui.lCars.checked, uavs: ui.lUavs.checked, signals: ui.lSignals.checked, stations: ui.lStations.checked, roads: ui.lRoads.checked, trafficMap: ui.lMap.checked, birds: ui.lBirds.checked }); }
for (const el of [ui.lCars, ui.lUavs, ui.lSignals, ui.lStations, ui.lRoads, ui.lMap, ui.lBirds]) el.addEventListener('input', applyReplayLayers);
// ---- bird tracker module (panel): follow the flock centroid or a single bird; holds the "Birds" view until another tab is chosen
const birdUI = { box: $('bird-tracker'), target: $('bird-target'), mode: $('bird-mode'), readout: $('bird-readout') };
function setupBirdTracker() {
  if (!replayLayer?.birds) return;
  for (let i = 0; i < replayLayer.birds.stats.birds; i++) { const o = document.createElement('option'); o.value = i; o.textContent = `Bird ${String(i + 1).padStart(3, '0')}`; birdUI.target.append(o); }
  birdUI.box.style.display = '';
}
function applyBirdTracking() {
  if (!replayLayer?.birds) return;
  const v = birdUI.target.value;
  if (v === '') { replayLayer.trackBirds(null); if (replayLayer.shot === 'birds') replayLayer.shotUntil = performance.now(); return; }
  if (section !== 'campus') runCampus();
  replayLayer.stopShots(); flight = null; controls.enabled = true;
  replayLayer.shot = 'birds'; replayLayer.shotUntil = Infinity; replayLayer.label = SHOTS_BIRDS_LABEL; setSectionUI();
  replayLayer.trackBirds(v === 'flock' ? 'flock' : +v, birdUI.mode.value);
}
const SHOTS_BIRDS_LABEL = 'Birds · tracking (hold; pick another view to resume the tour)';
birdUI.target.addEventListener('change', applyBirdTracking);
birdUI.mode.addEventListener('change', applyBirdTracking);
ui.nPart.addEventListener('change', () => { buildParticles(+ui.nPart.value); applyLayers(); });

// ------------------------------------------------------------------ camera choreography
const ease = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const campusCentre = new THREE.Vector3((CAMPUS.min[0] + CAMPUS.max[0]) / 2, 15, (CAMPUS.min[1] + CAMPUS.max[1]) / 2);
const domainCentre = new THREE.Vector3(CX, 0, CZ);
function fitDistance() {
  const vFov = THREE.MathUtils.degToRad(camera.fov), hFov = 2 * Math.atan(Math.tan(vFov / 2) * camera.aspect);
  return 1.08 * Math.max((H * CELL / 2) / Math.tan(vFov / 2), (W * CELL / 2) / Math.tan(hFov / 2));
}
function campusPose(azimuth) {
  const dist = 480, elev = THREE.MathUtils.degToRad(32);
  const pos = new THREE.Vector3(
    campusCentre.x + dist * Math.cos(elev) * Math.sin(azimuth),
    campusCentre.y + dist * Math.sin(elev),
    campusCentre.z + dist * Math.cos(elev) * Math.cos(azimuth));
  return { pos, target: campusCentre.clone() };
}
function overheadPose() {
  // near-overhead (5 deg tilt towards the south keeps the orbit controls well-defined)
  const tilt = THREE.MathUtils.degToRad(5), d = fitDistance();
  const target = new THREE.Vector3(domainCentre.x, LAYER_Y.wind, domainCentre.z);
  return { pos: new THREE.Vector3(target.x, target.y + d * Math.cos(tilt), target.z + d * Math.sin(tilt)), target };
}
let flight = null;   // { from, to, t0, dur, onDone }
function flyTo(pose, dur, onDone) {
  flight = { from: { pos: camera.position.clone(), target: controls.target.clone() }, to: pose, t0: performance.now(), dur, onDone };
  controls.enabled = false;
}
function updateFlight(now) {
  if (!flight) return;
  const k = Math.min(1, (now - flight.t0) / flight.dur), e = ease(k);
  camera.position.lerpVectors(flight.from.pos, flight.to.pos, e);
  controls.target.lerpVectors(flight.from.target, flight.to.target, e);
  camera.lookAt(controls.target);
  if (k >= 1) { const f = flight; flight = null; controls.enabled = true; controls.update(); if (f.onDone) f.onDone(); }
}
function campusPoseDeg(azDeg) { return campusPose(THREE.MathUtils.degToRad(azDeg)); }
function setSectionUI() {
  shotButtons.forEach(b => b.classList.toggle('active', section === 'campus' && replayLayer?.shot === b.dataset.shot));
  fieldButtons.forEach(b => b.classList.toggle('active', section === 'fields' && (seqMode() ? state.phase === b.dataset.field : true)));
}
/** Campus section: ground, trees and the traffic / UAV replay visible; the physics fields hidden; the shot tour runs. */
function runCampus() {
  section = 'campus'; placeSun();
  setPlaying(false); state.introDone = false; applyLayers();            // fields fade out
  ui.lGround.checked = true; ui.lTrees.checked = true; applyLayers();
  if (replayLayer) { replayLayer.setVisible(true); replayLayer.playing = true; }
  setRateOptions('replay', replayLayer?.speed ?? 1); ui.play.textContent = '❚❚';
  if (replayLayer) { ui.step.min = replayLayer.traffic?.firstTime ?? 0; ui.step.max = replayLayer.duration || 3600; ui.step.step = 0.1; }
  replayLayer?.startShot('overview');
  setSectionUI();
}
/** Fields section: climb to the overhead view, hide ground / trees / replay, play the three fields in sequence. */
function runFields(phase = 'wind') {
  if (section === 'fields' && state.introDone) { ui.mode.value = 'seq'; setPhase(phase); setPlaying(true); return; }   // already overhead: jump to that field
  section = 'fields';
  replayLayer?.stopShots(); if (replayLayer) replayLayer.playing = false;
  ui.stage.textContent = 'Climbing to the overhead view · aligned with the 4 m simulation grid (3072 × 2816 m)'; ui.info.textContent = '';
  setSectionUI();
  flyTo(overheadPose(), 3800, () => {
    state.introDone = true;
    ui.lGround.checked = false; ui.lTrees.checked = false;
    replayLayer?.setVisible(false);
    setRateOptions('fields', 12); ui.step.step = 1;
    setPhase(seqMode() ? phase : state.phase); setPlaying(true);
  });
}
function playIntro() {
  state.introDone = false; windPlane.fade = tempPlane.fade = pollPlane.fade = floodPlane.fade = solarPlane.fade = shadowPlane.fade = diurnalPlane.fade = 0; placeSun();
  const a0 = campusPoseDeg(-150);
  camera.position.copy(a0.pos); controls.target.copy(a0.target); camera.lookAt(a0.target);
  runCampus();
}
shotButtons.forEach(b => b.addEventListener('click', () => {
  if (!replayLayer) return;
  if (section !== 'campus') { runCampus(); }
  replayLayer.startShot(b.dataset.shot); setSectionUI();
}));
fieldButtons.forEach(b => b.addEventListener('click', () => runFields(b.dataset.field)));
ui.replay.addEventListener('click', playIntro);

// ------------------------------------------------------------------ hover readout
const ray = new THREE.Raycaster(), ndc = new THREE.Vector2(), groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0), hit = new THREE.Vector3();
renderer.domElement.addEventListener('pointermove', e => {
  if (!state.introDone) return;
  ndc.set((e.clientX / window.innerWidth) * 2 - 1, -(e.clientY / window.innerHeight) * 2 + 1);
  ray.setFromCamera(ndc, camera);
  if (!ray.ray.intersectPlane(groundPlane, hit)) { ui.readout.hidden = true; return; }
  const c = Math.floor((hit.x - X0) / CELL), r = Math.floor((ZS - hit.z) / CELL);
  if (c < 0 || c >= W || r < 0 || r >= H || !state.fields.wind) { ui.readout.hidden = true; return; }
  const i = r * W + c, n = W * H, f = state.fields;
  const u = f.wind ? f.wind[i] : NaN, v = f.wind ? f.wind[n + i] : NaN, w = f.wind ? f.wind[2 * n + i] : NaN;
  const dom = `Domain x ${480 + c * CELL} m, y ${640 + r * CELL} m · cell (${c}, ${r})`;
  const lines = [dom,
    `Wind |V| ${Math.hypot(u, v, w).toFixed(2)} m/s  (u ${u.toFixed(2)}, v ${v.toFixed(2)}, w ${w.toFixed(2)})`,
    ...(f.temp ? [`Temperature ${f.temp[i].toFixed(2)} °C` + (footprint && footprint[i] ? ' (building cell)' : '')] : []),
    ...(f.poll ? [`Concentration ${f.poll[i] < 10 ? f.poll[i].toFixed(2) : f.poll[i].toFixed(0)}`] : [])];
  if (f.flood) lines.push(`Flood depth ${f.flood[i] > 0.02 ? f.flood[i].toFixed(2) + ' m' : 'dry'}` + (seqMode() && state.phase === 'flood' ? '' : ' (maximum of the event)'));
  if (f.solar) lines.push(`Sunlight GHI ${f.solar[i].toFixed(0)} W/m²` + (solarOpen >= 15 ? ` (${(100 * f.solar[i] / solarOpen).toFixed(0)} % of open sky)` : ''));
  if (f.shadow) { const c1 = Math.floor(hit.x - X0), r1 = Math.floor(ZS - hit.z); if (c1 >= 0 && c1 < W1 && r1 >= 0 && r1 < H1) lines.push(`Sunlight · 1 m cell ${f.shadow[r1 * W1 + c1] ? 'in shadow' : 'sunlit'}`); }
  if (f.diurnal) { const amb = diurnalAmbient(frameIndex(state.step).diurnal); lines.push(`Day cycle ${({ ground: 'ground surface', air0: 'air 0–4 m', air12: 'air 12–16 m' })[ui.diurnalMode.value.replace('Rel', '')]} ${f.diurnal[i].toFixed(1)} °C` + (amb !== undefined ? ` (${(f.diurnal[i] - amb >= 0 ? '+' : '')}${(f.diurnal[i] - amb).toFixed(1)} vs ambient ${amb.toFixed(1)})` : '')); }
  ui.readout.textContent = lines.join('\n'); ui.readout.hidden = false;
});
renderer.domElement.addEventListener('pointerleave', () => { ui.readout.hidden = true; });

// ------------------------------------------------------------------ render loop
let last = performance.now();
function animate(now) {
  requestAnimationFrame(animate);
  const dt = Math.min(0.05, (now - last) / 1000); last = now;
  if (replayLayer && section === 'campus') {
    const boundary = replayLayer.tick(now, dt);
    ui.stage.textContent = replayLayer.label; ui.info.textContent = replayLayer.info; ui.stats.textContent = replayLayer.stats;
    birdUI.readout.textContent = replayLayer.birdInfo || '';
    if (replayLayer.shot === 'birds' && replayLayer.shotUntil !== Infinity && replayLayer.birdTarget === 'flock' && birdUI.target.value !== 'flock') { birdUI.target.value = 'flock'; }   // the tour's own flock shot
    else if (replayLayer.shot !== 'birds' && birdUI.target.value !== '') birdUI.target.value = '';
    ui.timeLabel.textContent = `Replay ${timeString(replayLayer.t)} · ${replayLayer.speed}×`; ui.step.value = replayLayer.t;
    if (ui.rate.value !== String(replayLayer.speed)) ui.rate.value = String(replayLayer.speed);
    if (boundary) { setSectionUI(); if (replayLayer.cycleDone) { if (ui.auto.checked) runFields(); else replayLayer.startShot('overview'); } }
  }
  updateFlight(now);
  if (controls.enabled) controls.update();
  updateFades(dt);
  if (state.introDone && wind.lines.visible) stepParticles(dt);
  renderer.render(scene, camera);
}
renderer.domElement.addEventListener('pointerdown', () => { if (section === 'campus') { if (flight) { flight = null; controls.enabled = true; } replayLayer?.cancelCamera(); } });
window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
  iso.material.resolution.set(window.innerWidth, window.innerHeight);
});

// ------------------------------------------------------------------ memory: drop the source geometry of batched meshes
// batchStaticCity merges the visible city meshes into a few float32 batches and hides the sources. The hidden sources kept
// their (quantised) attribute arrays: ~1.5 GB of JS heap for the 36k geometries, which pushed the tab into constant garbage
// collection and made the field playback stall. The sources that can be shown again (the originals behind "Building
// refinements", the meshes the station tile replaces, ground / trees) keep their geometry; everything else hidden gets an
// empty one.
const EMPTY_GEOMETRY = new THREE.BufferGeometry();
function releaseBatchedGeometry() {
  const keep = new Set([...groundMeshes, ...treeMeshes, ...tileHidden]);
  for (const e of expansions) for (const o of e.originals) keep.add(o);
  if (tileGroup) tileGroup.traverse(o => keep.add(o));
  let n = 0, bytes = 0;
  model.traverse(o => {
    if (!o.isMesh || o.visible || keep.has(o) || o.geometry === EMPTY_GEOMETRY) return;
    for (const a of Object.values(o.geometry.attributes)) bytes += a.array.byteLength; if (o.geometry.index) bytes += o.geometry.index.array.byteLength;
    o.geometry.dispose(); o.geometry = EMPTY_GEOMETRY; n++;
  });
  console.log(`released ${n} batched source geometries, ${(bytes / 1048576).toFixed(0)} MB`);
}

// ------------------------------------------------------------------ boot
async function boot() {
  buildParticles(+ui.nPart.value);
  const a0 = campusPose(THREE.MathUtils.degToRad(-150));
  camera.position.copy(a0.pos); controls.target.copy(a0.target); camera.lookAt(a0.target);
  requestAnimationFrame(animate);

  // data first (small), then the model
  const dataReady = (async () => {
    await initFrames(); console.log('field frames:', framesInfo());
    footprint = await loadMask('masks/building_footprint_yx.npy');
    solidWind = await npy('masks/solid_4m_zyx.npy').read(2);   // 8-12 m layer
    studyArea = await loadMask('temperature2d/study_area_mask_yx.npy');
    await loadStep(60);
  })().catch(e => { ui.stage.textContent = 'Data error: ' + e.message; console.error(e); });

  const loader = new GLTFLoader();
  loader.setMeshoptDecoder(MeshoptDecoder);
  // the detail tile downloads alongside the main model and is placed once the main model is batched
  // The station detail tile is off by default (its colours stand out against the main model); ?tile=1 loads it.
  let tileMB = '';
  const tileLoad = new URLSearchParams(location.search).get('tile') !== '1' ? Promise.resolve(null)
    : new Promise((resolve, reject) => loader.load(TILE.url, resolve, ev => { tileMB = ` · tile ${(ev.loaded / 1048576).toFixed(0)} / ${(TILE.bytes / 1048576).toFixed(0)} MB`; }, reject))
      .catch(e => { console.error('detail tile failed to load', e); return null; });
  const onCity = (gltf, resolve) => {
      gltf.scene.updateMatrixWorld(true);
      const box = new THREE.Box3(), size = new THREE.Vector3();
      gltf.scene.traverse(o => {
        if (!o.isMesh) return;
        if (!o.geometry.boundingBox) o.geometry.computeBoundingBox();
        box.copy(o.geometry.boundingBox).applyMatrix4(o.matrixWorld); box.getSize(size);
        // ground-like: thinner than 3 m and wider than 30 m (site ground, roads, paths, paving, kerbs)
        if (size.y < 3 && Math.max(size.x, size.z) > 30) groundMeshes.push(o);
        // trees / vegetation: by node (or ancestor) name, or by material name
        let names = '';
        for (let a = o; a && a !== gltf.scene; a = a.parent) names += (a.name || '') + ' | ';
        const matName = Array.isArray(o.material) ? o.material.map(m => m.name).join(' | ') : (o.material && o.material.name) || '';
        if (TREE_NODE.test(names) || (TREE_MAT.test(matName) && !/tree wells/i.test(matName))) treeMeshes.push(o);
      });
      model.add(gltf.scene);
      resolve(gltf);
  };
  const onCityProgress = ev => {
    const total = ev.total || 254723368, pct = Math.min(100, ev.loaded / total * 100);
    ui.bar.style.width = pct.toFixed(1) + '%';
    ui.pct.textContent = `${(ev.loaded / 1048576).toFixed(0)} / ${(total / 1048576).toFixed(0)} MB · ${pct.toFixed(0)} %${tileMB}`;
  };
  if (LITE) {
    // proxy city from the masks (already needed for the fields), then the replay layers
    ui.pct.textContent = 'Lite mode · building the voxel city…';
    await dataReady;
    const roof = await loadMask('masks/roof_height_m_yx.npy');
    const proxy = buildProxyCity({ footprint, roof, W, H, CELL, X0, ZS });
    model.add(proxy.mesh);
    base.material.color.set(0x8f938c);   // the proxy city has no ground layer: a lighter plate stands in for it
    console.log('lite city:', proxy.boxes, 'columns,', proxy.triangles, 'triangles');
    $('lite-hint').style.display = ''; $('l-supplement').closest('label').style.display = 'none';
    ui.pct.textContent = 'Traffic and UAV replay…';
    replayLayer = await createReplay({ scene, camera, controls, campusCentre, campusPose: campusPoseDeg, flyTo, onProgress: t => { ui.pct.textContent = t; } })
      .catch(e => { console.error('replay unavailable', e); return null; });
    applyReplayLayers(); setupBirdTracker();
  } else {
  await new Promise((resolve, reject) => {
    if (CITY_FROM_PARTS) fetchCityModel(onCityProgress).then(buf => loader.parse(buf, '', gltf => onCity(gltf, resolve), reject)).catch(reject);   // GitHub Pages: parts from the models repository
    else loader.load(GLB, gltf => onCity(gltf, resolve), onCityProgress, err => reject(err));
  }).then(async gltf => {
    // demo_rev02's display filter (hide the GLB's own animated traffic / birds; parked-car filter), then merge the
    // static buildings into a few draw calls. Ground and trees stay separate meshes so their toggles keep working.
    ui.pct.textContent = 'Merging static buildings…';
    await applyCityFilter(gltf.scene);
    for (const batch of EXPANSION_BATCHES) {
      try {
        const refined = await loader.loadAsync(batch.url);
        const expansion = await installExpansion(gltf.scene, refined.scene, batch.ids, batch.projectionM);
        expansions.push(expansion); model.add(expansion.object);
        $('expansion-ctl').style.display = '';
        $('expansion-label').textContent = `Building refinements · ${expansions.reduce((n, e) => n + e.originals.length, 0)}`;
      } catch (error) { console.warn('Building refinement unavailable; original retained', error); }
    }
    const tile = await tileLoad;   // its building ids decide which main-model meshes stay out of the batches
    if (tile) {
      tileIds = tileBuildingIds(tile.scene);
      for (const o of hideReplaced(gltf.scene, tileIds)) tileHidden.add(o);
      // hole materials: the ground layers (site ground, paving, grass, water, road network) and the traffic roads. Materials
      // that any non-flat mesh also uses (roof slates, trims: thin wide building parts land in groundMeshes) are left out so
      // that the main-model buildings kept inside the rectangle are not sliced.
      const flat = new Set(groundMeshes), usedElsewhere = new Set();
      gltf.scene.traverse(o => { if (o.isMesh && o.visible && !flat.has(o) && !/^Traffic_road/.test(o.name)) materialsOf([o], usedElsewhere); });
      for (const m of materialsOf(groundMeshes)) if (!usedElsewhere.has(m)) holeMaterials.add(m);
      holeMaterials.add(base.material);   // the dark base plate would otherwise cut through the tile's railway cutting
      gltf.scene.traverse(o => { if (o.isMesh && o.visible && /^Traffic_road/.test(o.name)) materialsOf([o], holeMaterials); });
      console.log('tile: hole clipping on', holeMaterials.size, 'ground materials:', [...holeMaterials].map(m => m.name).join('; '));
    }
    for (const m of [...groundMeshes, ...treeMeshes]) m.visible = false;
    const batches = await batchStaticCity(gltf.scene); model.add(batches.object);
    for (const m of [...groundMeshes, ...treeMeshes]) if (!tileHidden.has(m)) m.visible = true;
    mainScene = gltf.scene; mainBatches = batches.object;
    if (tile) ui.pct.textContent = 'South Kensington detail tile…';
    $('tile-ctl').style.display = tile ? 'contents' : 'none';
    if (tile) {
      const tGround = [], tTrees = [];
      tileGroup = placeTile(tile, { ground: tGround, trees: tTrees }); model.add(tileGroup);
      // the tile's own ground colour is not wanted: its paving (plate top, footways) takes the main model's ground material
      let paving = null; mainScene.traverse(o => { if (!paving && o.isMesh && /^Site_\|_ground$/.test(o.name)) paving = o.material; });
      if (paving) { const g = paving.clone(); g.clippingPlanes = null; tile.scene.traverse(o => { if (o.isMesh && o.material?.name === 'Warm stone paving') o.material = g; }); }
      else console.warn('tile: main ground material not found, tile paving keeps its own colour');
      for (const m of [...tGround, ...tTrees]) m.visible = false;
      tileBatches = (await batchStaticCity(tile.scene)).object; model.add(tileBatches);   // batches are in world space
      for (const m of [...tGround, ...tTrees]) m.visible = true;
      groundMeshes.push(...tGround); treeMeshes.push(...tTrees);
      setClipping(tileGroup, tileKeep, false); setClipping(tileBatches, tileKeep, false);
      applyTile();
      // alignment check: the same OSM building in both files should land on the same spot
      let ref = null; mainScene.traverse(o => { if (!ref && /way-107039270_exterior/.test(o.name)) ref = o; });
      const c = tileBuildingCentre(tile.scene, '107039270');
      if (ref && c) console.log('tile alignment (19 Exhibition Road) tile centre', c.toArray().map(v => v.toFixed(1)).join(', '), '| main centre', new THREE.Box3().setFromObject(ref).getCenter(new THREE.Vector3()).toArray().map(v => v.toFixed(1)).join(', '));
    }
    ui.pct.textContent = 'Supplementary buildings…';
    const supplement = await loader.loadAsync(SUPPLEMENT_GLB);
    supplement.scene.updateMatrixWorld(true);
    if (tileGroup) for (const o of hideReplaced(supplement.scene, tileIds, { buildingsByCentre: true })) tileHidden.add(o);   // the tile models its own area
    const supplementMerged = (await batchStaticCity(supplement.scene)).object;
    supplementBatches = new THREE.Group();
    supplementBatches.add(supplement.scene, supplementMerged);
    supplementBatches.name = 'OSM missing buildings · estimated heights';
    model.add(supplementBatches);
    applyTile(); applyLayers();
    ui.pct.textContent = 'Traffic and UAV replay…';
    replayLayer = await createReplay({ scene, camera, controls, campusCentre, campusPose: campusPoseDeg, flyTo, onProgress: t => { ui.pct.textContent = t; } });
    applyReplayLayers(); setupBirdTracker();
  }).catch(e => { ui.pct.textContent = 'Loading failed: ' + (e.message || e); console.error(e); throw e; });
  releaseBatchedGeometry();
  }
  await dataReady;
  ui.loading.classList.add('hide');
  // ?pose=campus|overhead jumps straight to that view (no intro); ?step=N picks the time step
  const qs = new URLSearchParams(location.search), pose = qs.get('pose');
  if (qs.has('cam')) {   // ?cam=px,py,pz,tx,ty,tz : fixed free camera over the campus scene (debug / screenshots)
    const v = qs.get('cam').split(',').map(Number);
    ui.auto.checked = false; runCampus(); replayLayer?.stopShots(); flight = null; if (replayLayer) replayLayer.playing = false;
    ui.stage.textContent = 'Free camera';
    if (qs.get('replay') === '0') replayLayer?.setVisible(false);
    if (qs.has('t') && replayLayer) { replayLayer.t = +qs.get('t'); replayLayer.update(replayLayer.t); }
    camera.position.set(v[0], v[1], v[2]); controls.target.set(v[3], v[4], v[5]); camera.lookAt(controls.target);
    controls.enabled = true; section = 'free'; setSectionUI(); return;
  }
  if (pose === 'campus' && qs.get('fields') !== '1') {
    const p = campusPoseDeg(-135); camera.position.copy(p.pos); controls.target.copy(p.target); camera.lookAt(p.target);
    runCampus(); if (qs.has('t') && replayLayer) { replayLayer.t = +qs.get('t'); replayLayer.update(replayLayer.t); }
    if (qs.has('shot')) replayLayer?.startShot(qs.get('shot'));
    if (qs.get('hold') === '1' && replayLayer) replayLayer.shotUntil = Infinity;
    if (qs.get('play') === '0' && replayLayer) replayLayer.playing = false;
    setSectionUI(); return;
  }
  if (pose === 'overhead' || pose === 'campus') {
    section = 'fields'; replayLayer?.setVisible(false); setRateOptions('fields', 12); ui.step.step = 1;
    const p = pose === 'overhead' ? overheadPose() : campusPose(THREE.MathUtils.degToRad(-135));
    camera.position.copy(p.pos); controls.target.copy(p.target); camera.lookAt(p.target); controls.enabled = true;
    state.introDone = pose === 'overhead' || qs.get('fields') === '1';
    if (state.introDone) { ui.lGround.checked = false; ui.lTrees.checked = false; }
    if (qs.has('mode')) ui.mode.value = qs.get('mode');
    if (qs.has('phase')) state.phase = qs.get('phase');
    if (qs.has('solar')) ui.solarMode.value = qs.get('solar');       // ?solar=shadow|ghi
    if (qs.has('day')) ui.solarDate.value = qs.get('day');           // ?day=20260621|20261221
    if (qs.has('diurnal')) ui.diurnalMode.value = qs.get('diurnal'); // ?diurnal=ground|air0|air12
    solarPhaseSetup();
    if (state.introDone && seqMode() && (state.phase === 'flood' || state.phase === 'solar')) ui.lGround.checked = ui.lTrees.checked = true;
    applyLayers(); for (const L of [windPlane, tempPlane, pollPlane, floodPlane, solarPlane, shadowPlane, diurnalPlane]) L.fade = L.target; updateFades(0);
    if (qs.has('step')) setStep(+qs.get('step')); else setStep(state.step);
    ui.stage.textContent = pose === 'overhead' ? 'Overhead view · wind / temperature / sunlight / day cycle / pollution / flooding' : 'Imperial College London, South Kensington campus';
    return;
  }
  setTimeout(playIntro, 400);
}
boot();
window.viewer = { THREE, scene, camera, controls, model, state, renderer, planes: { windPlane, tempPlane, pollPlane, solarPlane, shadowPlane, diurnalPlane, floodPlane }, get replay() { return replayLayer; }, get tile() { return tileGroup; }, get tileBatches() { return tileBatches; } };   // console / debugging access
