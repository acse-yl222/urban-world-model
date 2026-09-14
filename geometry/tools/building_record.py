#!/usr/bin/env python3
"""Write geometry/building_record.json and .md: which buildings of the city model are authored detail, procedural baseline,
OSM supplement or refined (and in which batch). Read from assets/index.json (built by assets/tools/build_asset_library.mjs)
and the refinement manifests; nothing is shown in the viewer, this file is the record.

    python3 geometry/tools/building_record.py
"""
import glob, json, os, datetime
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
idx = json.load(open(os.path.join(ROOT, 'assets', 'index.json')))
manifests = {}
for m in glob.glob(os.path.join(ROOT, 'geometry', 'expansion', '*', 'manifest.json')):
    for f in json.load(open(m))['features']:
        manifests.setdefault(f['id'], []).append({'batch': os.path.basename(os.path.dirname(m)), 'name': f['name'], 'levels': f.get('levels'), 'height_m': f.get('height_m'), 'height_basis': f.get('height_basis')})
pilot = os.path.join(ROOT, 'geometry', 'expansion', 'feature.json')
if os.path.exists(pilot):
    f = json.load(open(pilot)); manifests.setdefault(f['id'], []).append({'batch': 'pilot', 'name': f['name'], 'levels': f.get('levels'), 'height_m': f.get('height_m'), 'height_basis': f.get('height_basis')})
rows = []
for bid, b in idx['buildings'].items():
    r = {'id': bid, 'names': b['names'], 'detail_class': b['detail_class'], 'has': b['has'], 'bbox': b['bbox']}
    if 'refined' in b['has']:
        r['refined'] = manifests.get(bid, [])
    rows.append(r)
rows.sort(key=lambda r: ({'authored_detail': 0, 'procedural_baseline': 2, 'supplement_estimated': 3}.get(r['detail_class'], 1), r['id']))
out = {'generated': datetime.datetime.now().isoformat(timespec='minutes'), 'source': 'assets/index.json + geometry/expansion/*/manifest.json',
       'counts': {'authored_detail': sum(r['detail_class'] == 'authored_detail' for r in rows), 'procedural_baseline': sum(r['detail_class'] == 'procedural_baseline' for r in rows),
                  'supplement_estimated': sum(r['detail_class'] == 'supplement_estimated' for r in rows), 'refined': sum('refined' in r['has'] for r in rows)}, 'buildings': rows}
json.dump(out, open(os.path.join(ROOT, 'geometry', 'building_record.json'), 'w'), indent=1)
c = out['counts']
md = [f"# Building record\n\nGenerated {out['generated']} from `assets/index.json` and the refinement manifests. Classes: **authored_detail** = detailed in the original core008 model (campus and landmark modules); **procedural_baseline** = OSM footprint with a procedural facade; **supplement_estimated** = the 306 footprints added by `geometry/completion`; **refined** = replaced by the `geometry/expansion` task (batch given). A building keeps its original file next to the refined one.\n",
      f"| class | count |\n|---|---:|\n| authored_detail | {c['authored_detail']} |\n| procedural_baseline | {c['procedural_baseline']} |\n| supplement_estimated | {c['supplement_estimated']} |\n| refined (any class) | {c['refined']} |\n",
      "## Refined buildings\n\n| id | name | batch | levels | height m | height basis |\n|---|---|---|---:|---:|---|"]
for r in rows:
    if 'refined' in r['has']:
        for m in (r.get('refined') or [{'batch': '?', 'name': r['names'][0], 'levels': '', 'height_m': '', 'height_basis': ''}]):
            h = m['height_m']; h = f'{h:.1f}' if isinstance(h, (int, float)) else (h or '')
            md.append(f"| `{r['id']}` | {m['name']} | {m['batch']} | {m['levels'] or ''} | {h} | {(m['height_basis'] or '')[:70]} |")
md.append("\n## Authored detail (original model)\n\n| id | name |\n|---|---|")
for r in rows:
    if r['detail_class'] == 'authored_detail': md.append(f"| `{r['id']}` | {', '.join(r['names'][:2])} |")
md.append(f"\nThe {c['procedural_baseline']} procedural and {c['supplement_estimated']} supplement buildings are listed only in the JSON (and in `assets/buildings/<id>/meta.json`).\n")
open(os.path.join(ROOT, 'geometry', 'building_record.md'), 'w').write('\n'.join(md))
print('record:', c)
