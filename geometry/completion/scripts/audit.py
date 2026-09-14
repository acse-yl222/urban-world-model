"""Audit OSM buildings against the preserved web GLB; never edits the baseline."""
import sys,json,struct,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps'))
import numpy as np
from pyproj import Transformer
from shapely.geometry import Polygon,box
with open(ROOT.parent/'south_kensington_core008_web.glb','rb') as f:
 f.read(12);length,_=struct.unpack('<II',f.read(8));D=json.loads(f.read(length))
S=json.load(open(ROOT/'sources/osm_buildings.json'))
features={e['type']+'-'+str(e['id']):e for e in S['elements']}
def bounds(n):
 if 'mesh' not in n:return None
 pts=[]
 for p in D['meshes'][n['mesh']]['primitives']:
  a=D['accessors'][p['attributes']['POSITION']]
  if 'min' not in a:continue
  norm={5120:127,5121:255,5122:32767,5123:65535}.get(a['componentType'],1) if a.get('normalized') else 1
  for v in itertools.product(*zip(a['min'],a['max'])):
   v=np.array(v)/norm
   if 'matrix' in n:v=(np.array(n['matrix']).reshape(4,4).T@np.r_[v,1])[:3]
   else:
    v=v*np.array(n.get('scale',[1,1,1]))
    if 'rotation' in n:
     x,y,z,w=n['rotation'];q=np.array([x,y,z]);v=v+2*np.cross(q,np.cross(q,v)+w*v)
    v+=n.get('translation',[0,0,0])
   pts.append(v)
 if not pts:return None
 return [np.min(pts,axis=0).tolist(),np.max(pts,axis=0).tolist()]
records=[];known=set();pairs=[]
tf=Transformer.from_crs(4326,32630,always_xy=True)
for n in D['nodes']:
 e=n.get('extras',{});ids=set(filter(None,[e.get('osm_id'),e.get('building_id')]+e.get('source_part_ids',[])));ids={('way-'+str(x)) if isinstance(x,int) else x for x in ids};known|=ids
 b=bounds(n)
 if not b:continue
 records.append({'name':n.get('name',''),'ids':sorted(ids),'bounds':b})
 key=e.get('osm_id');f=features.get(key,{})
 if 'exterior' in n.get('name','') and f.get('geometry') and len(ids)==1:
  p=np.array([tf.transform(v['lon'],v['lat']) for v in f['geometry']]);center=(p.min(axis=0)+p.max(axis=0))/2
  target=[(b[0][0]+b[1][0])/2,-(b[0][2]+b[1][2])/2];pairs.append([*center,*target])
a=np.array(pairs);origin=a[:,:2].mean(axis=0);X=np.c_[a[:,:2]-origin,np.ones(len(a))];Y=a[:,2:]
mask=np.ones(len(a),dtype=bool)
for _ in range(5):
 A=np.linalg.lstsq(X[mask],Y[mask],rcond=None)[0];err=np.linalg.norm(np.einsum('ij,jk->ik',X,A)-Y,axis=1);mask=err<1
report={'control_buildings':len(a),'inliers':int(mask.sum()),'median_error_m':float(np.median(err[mask])),'max_inlier_error_m':float(err[mask].max()),'crs':'EPSG:32630','projected_origin':origin.tolist(),'projected_to_model_east_north_affine':A.tolist(),'known_id_count':len(known)}
json.dump({'registration':report,'nodes':records,'known_ids':sorted(known)},open(ROOT/'reports/model_inventory.json','w'),indent=2)
print(json.dumps(report,indent=2))
