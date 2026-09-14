import bpy,json,math,hashlib
from pathlib import Path
ROOT=Path('/Users/yl222/Desktop/UrbanWorldModelVisualizer/geometry_expansion')
RUN=ROOT/'output/batch06_v1'
bpy.ops.wm.open_mainfile(filepath=str(RUN/'master.blend'))
def dist(p,a,b):
 d=(b[0]-a[0],b[1]-a[1]);t=max(0,min(1,((p[0]-a[0])*d[0]+(p[1]-a[1])*d[1])/(d[0]*d[0]+d[1]*d[1])))
 return math.hypot(p[0]-a[0]-t*d[0],p[1]-a[1]-t*d[1])
def inside(p,ring):
 hit=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:hit=not hit
 return hit
rows=[]
for slug in ['mews_outbuilding_1154608372','service_building_788306098']:
 f=json.loads((ROOT/'batch06/features'/f'{slug}.json').read_text());ring=f['ring'];maximum=0;count=0
 for obj in bpy.data.objects:
  if obj.type!='MESH' or obj.get('context_only') or obj.get('building_id')!=f['id']:continue
  for v in obj.data.vertices:
   p=obj.matrix_world@v.co;count+=1
   if not inside(p,ring):maximum=max(maximum,min(dist(p,a,b) for a,b in zip(ring,ring[1:]+ring[:1])))
 assert count and maximum<.002,(slug,maximum)
 rows.append({'id':f['id'],'vertices_checked':count,'maximum_outside_mapped_ring_m':maximum})
report={'passed':True,'replacement_sha256':hashlib.sha256((RUN/'replacement.glb').read_bytes()).hexdigest(),'buildings':rows,'interpretation':'No authored ancillary vertex extends more than 2 mm beyond its inherited footprint. Existing 0.05571 m2 Huxley footprint sliver is retained. This bounds new outward projection, not a claim of zero mesh intersections or surveyed contact.'}
(ROOT/'batch06/reports/ancillary_footprint_check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
