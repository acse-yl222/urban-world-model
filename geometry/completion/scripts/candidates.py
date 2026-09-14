import sys,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'.deps'))
from shapely.geometry import Polygon,LineString,box,mapping
from shapely.ops import polygonize,unary_union
from shapely.strtree import STRtree
from shapely import make_valid
from pyproj import Transformer
I=json.load(open(R/'reports/model_inventory.json'));S=json.load(open(R/'sources/osm_buildings.json'));known=set(I['known_ids']);tf=Transformer.from_crs(4326,32630,always_xy=True)
origin=[695238.304719173,5709236.965026026]
def ring(g):
 return [(a-origin[0],b-origin[1]) for a,b in [tf.transform(v['lon'],v['lat']) for v in g]]
def geom(e):
 if e.get('geometry'):
  g=e['geometry']
  if len(g)<4 or g[0]!=g[-1]:return None
  return Polygon(ring(g))
 if e['type']=='relation':
  ou=[];inn=[]
  for m in e.get('members',[]):
   if m.get('geometry') and len(m['geometry'])>1:(inn if m.get('role')=='inner' else ou).append(LineString(ring(m['geometry'])))
  if not ou:return None
  return unary_union([make_valid(p) for p in polygonize(ou)]).difference(unary_union([make_valid(p) for p in polygonize(inn)]))
area=box(-1293.6877,-1215.3131,1294.2519,1215.6142);allp=[];represented=[];memberids=set()
for e in S['elements']:
 if e['type']=='relation' and e.get('tags',{}).get('building'):
  memberids|={'way-'+str(m['ref']) for m in e.get('members',[]) if m.get('type')=='way' and m.get('role') in ('outer','inner','')}
for e in S['elements']:
 p=geom(e)
 if p is None or p.is_empty or not p.is_valid:continue
 key=e['type']+'-'+str(e['id'])
 if key in known:represented.append(p)
 if e.get('tags',{}).get('building') and p.intersects(area):allp.append((key,e,p))
# Existing authored campus meshes may carry their original numeric IDs only.
for n in I['nodes']:
 if n['ids']:
  lo,hi=n['bounds']
  if hi[1]-lo[1]>2:represented.append(box(lo[0],-hi[2],hi[0],-lo[2]))
tree=STRtree(represented);c=[];rejected=[]
for key,e,p in allp:
 if key in known or key in memberids:continue
 overlap=unary_union([represented[i] for i in tree.query(p)]).intersection(p).area/p.area
 record={'id':key,'tags':e['tags'],'area_m2':p.area,'existing_overlap_ratio':overlap,'boundary_crossing':not area.covers(p),'geometry':mapping(p)}
 if p.area>=10 and overlap<0.02 and area.covers(p) and e['tags'].get('building') not in ['roof','construction','ruins']:c.append(record)
 else:rejected.append(record)
json.dump({'candidates':c,'deferred':rejected,'scope_model_east_north':list(area.bounds)},open(R/'reports/candidates.json','w'),indent=2)
print('within scope',len(allp),'nonoverlapping candidates',len(c),'deferred',len(rejected))
print([(v['id'],round(v['area_m2']),v['tags'].get('name')) for v in sorted(c,key=lambda v:-v['area_m2'])[:30]])
import os;os.environ['MPLCONFIGDIR']=str(R/'reports/.mpl')
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(14,14))
for p in represented:
 if not p.intersects(area):continue
 for pp in ([p] if p.geom_type=='Polygon' else getattr(p,'geoms',[])):
  if pp.geom_type=='Polygon':ax.fill(*pp.exterior.xy,color='#bbbbbb',linewidth=0)
for j,v in enumerate(c):
 from shapely.geometry import shape
 p=shape(v['geometry'])
 for pp in ([p] if p.geom_type=='Polygon' else p.geoms):ax.fill(*pp.exterior.xy,color='#ec542d',linewidth=0)
 ax.text(p.centroid.x,p.centroid.y,str(j),fontsize=6)
ax.set(xlim=(-1294,1295),ylim=(-1216,1216),aspect='equal',title=f'OSM/model audit: {len(c)} candidate omissions (orange); existing coverage (grey)');fig.savefig(R/'reports/candidates.png',dpi=150)
