/* City model source. Locally the packed .glb sits in models/ and is loaded straight by GLTFLoader. On the GitHub Pages copy
   the 254 MB file lives in the companion repository acse-yl222/urban-world-model-models, split into parts under GitHub's
   100 MB limit and served by that repository's Pages site (which sends Access-Control-Allow-Origin: *; release assets do not,
   which is why the model is not fetched from a release). The parts are fetched in parallel and concatenated here. */
import { ON_PAGES, MODEL_BASE } from './config.js';

export const MODELS_PAGES = 'https://acse-yl222.github.io/urban-world-model-models/';
export const CITY_MANIFEST = MODELS_PAGES + 'core008/manifest.json';
export const CITY_LOCAL = MODEL_BASE + 'south_kensington_core008_web.glb';

/** Fetch the city model as one ArrayBuffer (Pages: from the parts), reporting {loaded, total} like GLTFLoader's progress. */
export async function fetchCityModel(onProgress = () => {}) {
  const man = await (await fetch(CITY_MANIFEST, { cache: 'force-cache' })).json();
  const parts = man.parts, total = man.total_bytes, got = parts.map(() => 0);
  const report = () => onProgress({ loaded: got.reduce((a, b) => a + b, 0), total });
  const buffers = await Promise.all(parts.map(async (p, i) => {
    const r = await fetch(MODELS_PAGES + 'core008/' + p.file); if (!r.ok) throw new Error(`model part ${p.file}: HTTP ${r.status}`);
    const reader = r.body.getReader(), chunks = [];
    for (;;) { const { done, value } = await reader.read(); if (done) break; chunks.push(value); got[i] += value.byteLength; report(); }
    const out = new Uint8Array(p.bytes); let o = 0; for (const c of chunks) { out.set(c, o); o += c.byteLength; }
    if (o !== p.bytes) throw new Error(`model part ${p.file}: got ${o} of ${p.bytes} bytes`);
    return out;
  }));
  const all = new Uint8Array(total); let o = 0; for (const b of buffers) { all.set(b, o); o += b.byteLength; }
  return all.buffer;
}
export const CITY_FROM_PARTS = ON_PAGES;
