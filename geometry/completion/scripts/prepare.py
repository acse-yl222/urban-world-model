import sys,json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.deps'))
from shapely.geometry import shape,LineString,mapping
from shapely.strtree import STRtree
from shapely.ops import unary_union
import mapbox_earcut as earcut
import numpy as np
D=json.load(open(R/'reports/candidates.json'));lanes=json.load(open(R.parent/'agents/demo_rev02/data/roads.json'))['lanes'];roads=[LineString([(p[0],-p[2]) for p in l['world_xyz']]).buffer(l['width_m']/2) for l in lanes if len(l['world_xyz'])>1];tree=STRtree(roads)
chosen=[];deferred=[];polys=[]
for c in sorted(D['candidates'],key=lambda c:-c['area_m2']):
 p=shape(c['geometry']);road_overlap=unary_union([roads[i] for i in tree.query(p)]).intersection(p).area
 if road_overlap>0.5 or any(p.intersection(q).area>0.5 for q in polys):
  c['defer_reason']='road or candidate overlap';c['road_overlap_m2']=road_overlap;deferred.append(c);continue
 t=c['tags'];levels=float(t.get('building:levels','2' if t.get('building') in ['garage','garages','shed'] else '4').split(';')[0]);height=max(3.0,levels*3.15+0.55)
 c.update(height_m=height,height_basis='OSM levels × 3.15m + 0.55m (estimated floor pitch)' if 'building:levels' in t else 'typology estimate',road_overlap_m2=road_overlap,parts=[])
 for poly in ([p] if p.geom_type=='Polygon' else p.geoms):
  rings=[list(poly.exterior.coords)[:-1]]+[list(r.coords)[:-1] for r in poly.interiors];v=np.array([xy for r in rings for xy in r],dtype=np.float64);ends=np.cumsum([len(r) for r in rings],dtype=np.uint32);tri=earcut.triangulate_float64(v,ends).reshape(-1,3)
  aa=sum(abs(np.cross(v[b]-v[a],v[d]-v[a]))/2 for a,b,d in tri)
  assert abs(aa-poly.area)<1e-5
  c['parts'].append({'rings':rings,'vertices':v.tolist(),'triangles':tri.tolist()})
 chosen.append(c);polys.append(p)
json.dump({'buildings':chosen,'deferred':deferred,'attribution':'© OpenStreetMap contributors, ODbL 1.0; https://www.openstreetmap.org/copyright','coordinate_frame':'EPSG:32630 minus [695238.304719173,5709236.965026026]; Blender X east Y north Z up','limitations':'OSM mapped footprints; estimated heights and procedural facades; not a satellite-complete reconstruction. Existing physical fields not recomputed.'},open(R/'geometry.json','w'),indent=2)
print('selected',len(chosen),'deferred',len(deferred),'area',sum(c['area_m2'] for c in chosen))
