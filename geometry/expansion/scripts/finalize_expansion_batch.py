#!/usr/bin/env python3
"""Publish a verified local checkpoint only with an explicit, current visual review record."""
import argparse,hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--batch',required=True);parser.add_argument('--run',required=True);parser.add_argument('--review',required=True)
a=parser.parse_args();b=ROOT/a.batch;r=ROOT/'output'/a.run
v=json.loads((r/'verification.json').read_text());ic=json.loads((r/'interface_check.json').read_text());vc=json.loads((b/'reports/viewer_check.json').read_text());review=json.loads(Path(a.review).read_text())
assert v['numerical_pass'] and ic['passed'] and vc['passed']
h=sha(r/'replacement.glb');assert h==v['replacement_sha256']==ic['replacement_sha256']==review['replacement_sha256']
assert sha(r/'master.blend')==ic['master_sha256']
assert review['passed'] and review['actually_inspected'] and review['reviewer']
for name,digest in v['source_hashes'].items():assert sha(ROOT/name)==digest,('Source changed',name)
images={p.name:sha(p) for p in r.glob('*.png')}
assert images and images==review['render_sha256'], 'Incomplete or stale visual coverage'
ids=set(v['building_ids']);assert any(set(q['ids'])==ids and q['sha256']==h for q in vc['batches'])
http=[]
for rel in ['viewer/3d/','viewer/3d/expansion.js','geometry/expansion/output/'+a.run+'/replacement.glb']:
    response=urllib.request.urlopen('http://localhost:8787/'+rel,timeout=20);data=response.read();assert response.status==200
    q={'path':rel,'status':response.status,'bytes':len(data)}
    if rel.endswith('.glb'):assert hashlib.sha256(data).hexdigest()==h;q['sha256']=h
    http.append(q)
(b/'reports/http_check.json').write_text(json.dumps(http,indent=2))
# Archive the exact builder snapshot so future shared-runner revisions stay traceable.
snap=r/'source_snapshots';snap.mkdir(exist_ok=True)
for rel,digest in v['source_hashes'].items():
    if rel.endswith('.py'):
        target=snap/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/rel).read_bytes())
v.update(visual_reviewed=True,delivered=True,master_sha256=ic['master_sha256'],render_sha256=images,visual_review=review,live_browser_visual_reviewed=False,full_city_visual_reviewed=False,delivery_scope='Local reference-informed/artistic exterior or ancillary-shell batch; not geographically certified',builder_snapshots='source_snapshots')
(r/'verification.json').write_text(json.dumps(v,indent=2))
fpath=ROOT/'remaining_frontier.json';front=json.loads(fpath.read_text());old=set(front['completed_ids']);new=ids-old
front['completed_ids']=sorted(old|ids);front['pending']=[q for q in front['pending'] if q['id'] not in ids];front['pending_count']=len(front['pending']);fpath.write_text(json.dumps(front,indent=2))
state={'batch':a.batch,'ids':sorted(ids),'new_ids':sorted(new),'revised_ids':sorted(ids&old),'inventoried':True,'evidence_reviewed':True,'module_built':True,'integrated_local':True,'numerical_checks_passed':True,'render_visual_checks_passed':True,'live_browser_visual_checks_passed':False,'delivered_geometry_batch':True,'geographic_accuracy_certified':False,'replacement_sha256':h,'master':'output/'+a.run+'/master.blend','render_count':len(images)}
(b/'progress.json').write_text(json.dumps(state,indent=2))
p=ROOT/'progress.json';allp=json.loads(p.read_text());allp[a.batch]=state;allp.update(completed_refinement_count=len(front['completed_ids']),explicit_frontier_ids_pending=front['pending_count'],remaining_inventory='remaining_frontier.json',continuation_queue='continuation_queue.json')
if 'initial_frontier_ids' in front:
    allp['initial_frontier_ids_pending']=len(set(front['initial_frontier_ids'])-set(front['completed_ids']))
allp['curated_inventory_count']=len(front['completed_ids'])+front['pending_count']
p.write_text(json.dumps(allp,indent=2))
print(json.dumps({'batch':a.batch,'new':len(new),'completed':len(front['completed_ids']),'pending':front['pending_count'],'sha256':h}))
