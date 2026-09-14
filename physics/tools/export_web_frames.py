#!/usr/bin/env python3
"""Pre-render the field frames the viewer plays into small PNGs (physics/web/), so that remote viewers stream ~100 KB per
frame instead of 1-9 MB of raw float16. The viewer (viewer/frames.js) uses these when physics/web/index.json exists and
falls back to the raw .npy Range reads otherwise; the raw arrays stay the source of truth.

    uv run --with numpy,pillow python3 physics/tools/export_web_frames.py [--only wind,temp,...]

Encoding: 8-bit grey PNG per frame, value = lo + png/255 * (hi - lo) over a fixed range recorded in index.json (so the readout
is quantised to 1/255 of the range); wind is an RGB PNG with u, v, w each quantised over +-WIND_MAX; the 1 m shadow mask is a
1-bit PNG. Row 0 = south (same orientation as the arrays); nothing is flipped.
"""
import json
import os
import sys
import time

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PHYS = os.path.join(ROOT, 'physics')
OUT = os.path.join(PHYS, 'web')
only = None
for a in sys.argv[1:]:
    if a.startswith('--only'): only = set(a.split('=', 1)[1].split(','))
WIND_MAX = 2.5   # m/s, +- range for u, v, w (99.9th percentile of |u| in the run is ~2.2)

LAYERS = {
    # key: (array, kind, range, note) — kind 'gray' | 'rgb3' | 'bit'
    'wind':    ('wind/uvw_z8-12m_tcyx.npy', 'rgb3', [-WIND_MAX, WIND_MAX], 'u, v, w at 8-12 m'),
    'temp':    ('temperature2d/temperature_tyx.npy', 'gray', [30.0, 33.0], '2-D temperature 12-16 m, C'),
    'poll':    ('pollution/concentration_z12-16m_tyx.npy', 'gray', None, 'log10 concentration, range [-1, 4] (0.1 .. 1e4); stored log10(max(c, 0.1))'),
    'flood':   ('flood/depth_4m_tyx.npy', 'gray', [0.0, 2.0], 'water depth m (values above 2 m saturate)'),
    'floodMax': ('flood/max_depth_4m_yx.npy', 'gray', [0.0, 2.0], 'maximum depth m'),
    'solar_20260621': ('solar/ghi_4m_20260621_tyx.npy', 'gray', [0.0, 1000.0], 'GHI W/m2'),
    'solar_20261221': ('solar/ghi_4m_20261221_tyx.npy', 'gray', [0.0, 1000.0], 'GHI W/m2'),
    'shadow_20260621': ('solar/shadow_1m_20260621_tyx.npy', 'bit', None, '1 m shadow mask, 1 = shaded'),
    'shadow_20261221': ('solar/shadow_1m_20261221_tyx.npy', 'bit', None, '1 m shadow mask, 1 = shaded'),
    'diurnal_ground': ('temperature3d_solar/diurnal_20260621_ground_surface_c_tyx.npy', 'gray', [5.0, 45.0], 'ground surface C'),
    'diurnal_air0':   ('temperature3d_solar/diurnal_20260621_air_0_4m_c_tyx.npy', 'gray', [5.0, 45.0], 'air 0-4 m C'),
    'diurnal_air12':  ('temperature3d_solar/diurnal_20260621_air_12_16m_c_tyx.npy', 'gray', [5.0, 45.0], 'air 12-16 m C'),
}
index = {'generated': time.strftime('%Y-%m-%dT%H:%M'), 'encoding': 'png; value = lo + v/255*(hi-lo); rgb3 = (u,v,w); bit = mask', 'layers': {}}
if os.path.exists(os.path.join(OUT, 'index.json')):
    index['layers'] = json.load(open(os.path.join(OUT, 'index.json')))['layers']
os.makedirs(OUT, exist_ok=True)


def q(a, lo, hi):
    return np.clip(np.round((a.astype(np.float32) - lo) / (hi - lo) * 255), 0, 255).astype(np.uint8)


for key, (rel, kind, rng, note) in LAYERS.items():
    if only and key not in only: continue
    src = os.path.join(PHYS, rel)
    if not os.path.exists(src): print('missing', rel); continue
    arr = np.load(src, mmap_mode='r')
    frames = arr.shape[0] if arr.ndim >= 3 and key != 'floodMax' else 1
    d = os.path.join(OUT, key); os.makedirs(d, exist_ok=True)
    t0 = time.time(); total = 0
    for k in range(frames):
        fr = arr[k] if frames > 1 else arr
        p = os.path.join(d, f'{k:03d}.png')
        if kind == 'gray':
            if key == 'poll':
                img = q(np.log10(np.maximum(fr.astype(np.float32), 0.1)), -1.0, 4.0); rng_used = [-1.0, 4.0]
            else:
                img = q(fr, rng[0], rng[1]); rng_used = rng
            Image.fromarray(img, 'L').save(p, optimize=True)
        elif kind == 'rgb3':
            rgb = np.stack([q(fr[c], rng[0], rng[1]) for c in range(3)], axis=-1); rng_used = rng
            Image.fromarray(rgb, 'RGB').save(p, optimize=True)
        else:
            Image.fromarray((fr > 0).astype(np.uint8) * 255, 'L').convert('1').save(p, optimize=True); rng_used = [0, 1]
        total += os.path.getsize(p)
    meta = {'source': rel, 'kind': kind, 'range': rng_used, 'frames': frames, 'shape_yx': list(arr.shape[-2:]), 'note': note, 'bytes': total, 'avg_kb': round(total / frames / 1024, 1)}
    index['layers'][key] = meta
    print(f'{key:16s} {frames:4d} frames  {total/1e6:6.1f} MB  {meta["avg_kb"]:6.1f} KB/frame  {time.time()-t0:5.1f} s')
json.dump(index, open(os.path.join(OUT, 'index.json'), 'w'), indent=1)
print('wrote', os.path.join(OUT, 'index.json'))
