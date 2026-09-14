/* Where the big models come from. Locally (and on the workstation) they sit in models/; on the GitHub Pages copy the
   243 MB city model is too large for the repository and is fetched in parts from the companion Pages site
   urban-world-model-models (see model-source.js; release assets lack CORS headers). Everything else the page loads
   (supplement, refined buildings, field frames, replay data) is small enough to live in this repository. */
export const ON_PAGES = /\.github\.io$/.test(location.hostname);
export const RELEASE_BASE = 'https://github.com/acse-yl222/urban-world-model/releases/download/models-v1/';
export const MODEL_BASE = ON_PAGES ? RELEASE_BASE : new URL('../models/', import.meta.url).href;
export const CITY_GLB = MODEL_BASE + 'south_kensington_core008_web.glb';
export const TILE_GLB = MODEL_BASE + 'south_kensington_current.glb';
