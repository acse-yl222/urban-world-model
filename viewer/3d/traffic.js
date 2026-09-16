/* SUMO traffic replay for scenes without the South Kensington demo package (scene.json `traffic`): cars from a one-hour
   SUMO run on the OSM road network and the recorded signal states, both already in the model frame
   (scenes/<id>/traffic/, built by scenes/white_city/tools/run_sumo.py + build_traffic.py). Reuses demo_rev02's instanced
   car layer, signal poles / heads and lane ribbons. Synthetic demand and synthetic signal timings, not observed traffic. */
import * as THREE from 'three';
import { createActorLayer, carColorForId } from '../../agents/demo_rev02/actors/actor-layer.js';
import { createSignalLayerV2 } from '../../agents/demo_rev02/signals-v2.js';
import { addRoadSurfaces } from '../../agents/demo_rev02/stations.js';

const DEMO = new URL('../../agents/demo_rev02/', import.meta.url).href;
async function readJSON(url) { const r = await fetch(url); if (!r.ok) throw new Error(`${url}: ${r.status}`); return r.json(); }

export async function createTraffic({ scene, base, onProgress = () => {} }) {
  onProgress('Traffic replay (SUMO)…');
  const manifest = await readJSON(base + 'replay.json');
  const group = new THREE.Group(); group.name = 'SUMO traffic'; scene.add(group);
  const [roads, layer, frames, buffer, tlsText] = await Promise.all([readJSON(base + 'roads.json'), readJSON(base + 'signal_layer.json'), readJSON(base + 'replay/frames_index.json'),
    fetch(base + 'replay/traffic_flow.f32').then(r => { if (!r.ok) throw new Error('traffic_flow.f32 ' + r.status); return r.arrayBuffer(); }), fetch(base + 'replay/tls_frames.jsonl').then(r => r.text())]);
  const roadMesh = addRoadSurfaces(group, roads);
  const ROAD_COLOR = roadMesh.material.color.clone();
  const signals = createSignalLayerV2(group, layer, tlsText.trim().split('\n').filter(Boolean).map(l => JSON.parse(l)));
  signals.setPathsVisible(false);
  const binary = new Float32Array(buffer);
  const peak = Math.max(1, ...frames.map(f => f.count));
  const actors = await createActorLayer({ scene: group, carURL: DEMO + 'actors/sedan_4p5m.glb', uavURL: DEMO + 'assets/hexacopter_cargo.glb', carCapacity: Math.min(4000, peak + 50), uavCapacity: 1 });
  actors.uavs.group.visible = false;
  const duration = manifest.seconds;

  const frameMap = fr => { const m = new Map(); if (!fr) return m; const o = fr.offset_bytes / 4; for (let i = 0; i < fr.count; i++) { const k = o + i * 5; m.set(binary[k], binary.subarray(k + 1, k + 5)); } return m; };
  let cur = new Map(), curIdx = -1;
  function carsAt(t) {
    const idx = Math.floor(t), a = frames[idx], b = frames[idx + 1], f = t - idx;
    if (!a) return [];
    if (curIdx !== idx) { cur = frameMap(a); curIdx = idx; }
    const nxt = f > 0 ? frameMap(b) : new Map(), out = [];
    for (const [id, v] of cur) {
      const w = nxt.get(id); let x = v[0], z = v[1], yaw = v[2], sp = v[3];
      if (w) { x += (w[0] - x) * f; z += (w[1] - z) * f; let d = w[2] - yaw; d = Math.atan2(Math.sin(d), Math.cos(d)); yaw += d * f; sp += (w[3] - sp) * f; }
      out.push({ nativeId: id, x, y: 0.275, z, headingRadians: yaw, speed: sp, color: carColorForId(id) });
    }
    out.sort((p, q) => p.nativeId - q.nativeId); out.forEach((r, i) => r.idIndex = i); return out;
  }
  const T = {
    group, manifest, roadMesh, signals, actors, duration, t: 0, playing: true, speed: 1, count: 0, moving: 0,
    update(t) { const cars = carsAt(t); actors.updateCars(cars); signals.update(t); T.count = cars.length; T.moving = cars.filter(c => c.speed > 0.1).length; },
    tick(now, dt) { if (T.playing) { T.t += dt * T.speed; if (T.t >= duration - 1) T.t = 0; } T.update(T.t); },
    setVisible(v) { group.visible = v; },
    applyLayers({ cars = true, signals: sig = true, roads: rd = true, paths = false } = {}) { actors.cars.group.visible = cars; signals.setVisible(sig); roadMesh.visible = rd; signals.setPathsVisible(paths); },
    highlightRoads(on) { roadMesh.material.color.copy(on ? new THREE.Color('#3d8be6') : ROAD_COLOR); roadMesh.material.emissive.set(on ? '#123a6e' : '#000000'); roadMesh.material.needsUpdate = true; },
    get stats() { return `SUMO replay · ${T.count} cars (${T.moving} moving) · ${layer.counts.tls} signalled junctions, ${layer.counts.heads} heads · ${roads.counts.lanes} lanes · peak ${manifest.vehicles_peak} vehicles`; },
    get info() { return manifest.claim; },
  };
  T.update(0);
  return T;
}
export const timeString = s => { const t = Math.max(0, Math.floor(s)); return `${String(Math.floor(t / 60)).padStart(2, '0')}:${String(t % 60).padStart(2, '0')}`; };
