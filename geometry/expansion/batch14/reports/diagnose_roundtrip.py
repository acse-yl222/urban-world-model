import bpy,json
from pathlib import Path
R=Path('geometry/expansion/output/batch14_v1').resolve()
def sig():
 out={}
 for o in bpy.data.objects:
  if o.type!='MESH' or o.get('context_only') or o.get('building_id') not in {'way-810633524','way-810633526','way-851362836'}:continue
  pts=[o.matrix_world@v.co for v in o.data.vertices];used={i for p in o.data.polygons for i in p.vertices}
  out[o['research_object_id']]={'bounds':[min(v[i] for v in pts) for i in range(3)]+[max(v[i] for v in pts) for i in range(3)],'unused':len(pts)-len(used)}
 return out
bpy.ops.wm.open_mainfile(filepath=str(R/'master.blend'));a=sig()
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(R/'replacement.glb'));b=sig()
for k in a:
 error=max(abs(x-y) for x,y in zip(a[k]['bounds'],b[k]['bounds']))
 if error>.001:print('MISMATCH',k,error,a[k],b[k])
