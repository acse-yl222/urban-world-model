"""Verify roof coverage, entrance interfaces and material round-trip for batch 02."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/'output/batch02_v1';BATCH=ROOT/'batch02'
features=[json.loads(p.read_text()) for p in sorted((BATCH/'features').glob('*.json'))]
ids={f['id'] for f in features}
bpy.ops.wm.open_mainfile(filepath=str(RUN/'master.blend'))
verification=json.loads((RUN/'verification.json').read_text())
dg=bpy.context.evaluated_depsgraph_get();reports=[]

def inside(x,y,ring):
    result=False
    for a,b in zip(ring,ring[1:]+ring[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:result=not result
    return result

def edge_distance(x,y,ring):
    distances=[]
    for a,b in zip(ring,ring[1:]+ring[:1]):
        dx=b[0]-a[0];dy=b[1]-a[1];t=max(0,min(1,((x-a[0])*dx+(y-a[1])*dy)/(dx*dx+dy*dy)))
        distances.append(math.hypot(x-a[0]-t*dx,y-a[1]-t*dy))
    return min(distances)

for f in features:
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('building_id')==f['id'] and not o.get('context_only')]
    trees=[(o,BVHTree.FromObject(o,dg)) for o in objects]
    module=verification['module_results'][f['id']];interfaces=module['interfaces']
    entry=interfaces.get('entrance') or interfaces.get('entry')
    entries=[entry]+interfaces.get('additional_entrances',[])
    clearance=[]
    for entry in entries:
        assert entry is not None,f['id']
        c=Vector(entry['threshold_xyz']);n=Vector(entry.get('outward_normal') or [*entry['outward_normal_xy'],0]).normalized();u=Vector((-n.y,n.x,0))
        leaf=Vector(entry['door_leaf_xyz']);depth=max(.01,-(leaf-c).dot(n)-.055)
        width=min(1.0,entry['clear_width_m']-.06);ray_count=0
        for lateral in [-width/2,-width/4,0,width/4,width/2]:
            for height in [.012,.06,.2,1.,2.]:
                start=c+u*lateral+n*.20+Vector((0,0,height))
                for o,tree in trees:
                    if any(s in o.name.lower() for s in ['door','hardware']):continue
                    hit,_,_,distance=tree.ray_cast(start,-n,.20+depth)
                    assert hit is None,(f['id'],o.name,lateral,height,distance)
                ray_count+=1
        support_trees=[BVHTree.FromObject(o,dg) for o in bpy.context.scene.objects if o.type=='MESH' and o.get('building_id')==f['id'] and (o.get('context_only') or o.get('semantic_type')=='entry_support' or 'porch slab' in o.name)]
        for lateral in [-.42,0,.42]:
            start=c+u*lateral+n*.12+Vector((0,0,1))
            heights=[hit.z for tree in support_trees if (hit:=tree.ray_cast(start,Vector((0,0,-1)),2)[0]) is not None]
            assert heights and -.012<=max(heights)-c.z<=.008,(f['id'],'unsupported entry',lateral,heights)
        clearance.append({'threshold_xyz':list(c),'rays':ray_count,'checked_width_m':width})
    ring=f['ring'];xs=[p[0] for p in ring];ys=[p[1] for p in ring]
    max_z=max(v.co.z for o in objects for v in o.data.vertices)
    eaves=module['parameters'].get('eaves_height_m',module['parameters'].get('main_wall_height_m',f['height_m']))+f['base_z']
    samples=0
    for ix in range(math.ceil((max(xs)-min(xs))/1.25)):
        x=min(xs)+.625+ix*1.25
        for iy in range(math.ceil((max(ys)-min(ys))/1.25)):
            y=min(ys)+.625+iy*1.25
            if not inside(x,y,ring) or edge_distance(x,y,ring)<.45:continue
            start=Vector((x,y,max_z+1));hits=[p.z for o,tree in trees if (p:=tree.ray_cast(start,Vector((0,0,-1)),max_z+2)[0]) is not None]
            assert hits and max(hits)>eaves-.15,(f['id'],'roof hole',x,y,hits)
            samples+=1
    assert samples>20
    reports.append({'building_id':f['id'],'entrances':clearance,'roof_coverage_samples':samples,'footprint_area_m2':f['area_m2']})

def material_signature(objects):
    result={}
    for o in objects:
        if o.type!='MESH':continue
        colors=[]
        for m in o.data.materials:
            bs=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
            colors.append([*bs.inputs['Base Color'].default_value,bs.inputs['Roughness'].default_value,bs.inputs['Metallic'].default_value])
        result[o['research_object_id']]=colors
    return result
expected=material_signature([o for o in bpy.context.scene.objects if o.get('building_id') in ids and not o.get('context_only')])
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(RUN/'replacement.glb'))
actual=material_signature([o for o in bpy.context.scene.objects if o.type=='MESH'])
assert set(actual)==set(expected)
for key in expected:
    assert len(expected[key])==len(actual[key])
    assert max(abs(a-b) for x,y in zip(expected[key],actual[key]) for a,b in zip(x,y))<1e-6,key
result={'passed':True,'buildings':reports,'material_values_roundtrip_passed':True,'master_sha256':hashlib.sha256((RUN/'master.blend').read_bytes()).hexdigest(),'replacement_sha256':hashlib.sha256((RUN/'replacement.glb').read_bytes()).hexdigest(),'scope':'Exterior entry clearance before intentionally closed door assemblies, sampled mapped roof coverage and PBR round-trip. Not a survey or accessibility certification.'}
(RUN/'interface_check.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
