"""Check actual roof triangles and entry clearance in the saved master."""
import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/'output/kensington_gore_23_v1'
bpy.ops.wm.open_mainfile(filepath=str(RUN/'master.blend'))
f=json.loads((ROOT/'feature.json').read_text());r=f['ring']
area=abs(sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(r,r[1:]+r[:1])))/2
roof=next(o for o in bpy.context.scene.objects if o.name=='23 Kensington Gore | mapped roof deck')
roof.data.calc_loop_triangles()
roof_area=sum(abs((roof.data.vertices[t.vertices[1]].co-roof.data.vertices[t.vertices[0]].co).cross(roof.data.vertices[t.vertices[2]].co-roof.data.vertices[t.vertices[0]].co).z)/2 for t in roof.data.loop_triangles)
assert abs(roof_area-area)<.01,(roof_area,area)
entry=f['entry'];c=Vector((*entry['center_xy'],entry['threshold_z']))
normal=Vector((*entry['outward_normal_xy'],0)).normalized();u=Vector((-normal.y,normal.x,0))
dg=bpy.context.evaluated_depsgraph_get()
excluded=['recessed doors','door central stile','door fanlight transom','door hardware']
obstacles=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('building_id')==f['id'] and not o.get('context_only') and not any(o.name.endswith(v) for v in excluded)]
trees=[(o,BVHTree.FromObject(o,dg)) for o in obstacles]
casts=0
for lateral in [-.50,-.25,0,.25,.50]:
    for height in [.012,.05,.20,1.,2.]:
        start=c+u*lateral+normal*.20+Vector((0,0,height))
        for obj,tree in trees:
            loc,norm,idx,dist=tree.ray_cast(start,-normal,.485)
            assert loc is None,(obj.name,lateral,height,dist)
        casts+=1
support=next(o for o in bpy.context.scene.objects if o.get('context_only') and o.get('building_id')==f['id'])
tree=BVHTree.FromObject(support,dg)
for lateral in [-.45,0,.45]:
    start=c+u*lateral+normal*.1+Vector((0,0,1))
    loc,_,_,_=tree.ray_cast(start,Vector((0,0,-1)),2)
    assert loc is not None and abs(loc.z-.044)<.002,(lateral,loc)
report={'passed':True,'mapped_roof_area_m2':area,'triangle_roof_area_m2':roof_area,'entry_clearance_rays':casts,'checked_clear_width_m':1.0,'nominal_leaf_width_m':1.05,'jamb_clear_width_m':1.02,'threshold_to_existing_support_step_m':.006,'door_assembly_excluded_from_clearance':excluded,'master_sha256':hashlib.sha256((RUN/'master.blend').read_bytes()).hexdigest(),'scope':'Exterior opening before intentionally closed door leaf, including near-threshold samples. Not accessibility compliance or survey accuracy.'}
(RUN/'interface_check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
