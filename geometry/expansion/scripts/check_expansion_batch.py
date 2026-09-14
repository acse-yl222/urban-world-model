"""Verify roof coverage, entrance interfaces and material round-trip for batch 03."""
import bpy,json,math,hashlib,sys,argparse
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--batch',required=True);parser.add_argument('--run',required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);RUN=ROOT/'output'/args.run;BATCH=ROOT/args.batch
features=[json.loads(p.read_text()) for p in sorted((BATCH/'features').glob('*.json'))]
ids={f['id'] for f in features}
config=json.loads((BATCH/'manifest.json').read_text())
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
    assert entry is not None or not f.get('entry'),('Known entrance missing from module',f['id'])
    entries=([entry] if entry else [])+interfaces.get('additional_entrances',[])
    clearance=[];porch_support_samples=0
    for entry in entries:
        assert entry is not None,f['id']
        c=Vector(entry['threshold_xyz']);n=Vector(entry.get('outward_normal') or [*entry['outward_normal_xy'],0]).normalized();u=Vector((-n.y,n.x,0))
        leaf=Vector(entry['door_leaf_xyz']);depth=max(.01,-(leaf-c).dot(n)-.055)
        width=min(1.0,entry['clear_width_m']-.06);ray_count=0
        for lateral in [-width/2,-width/4,0,width/4,width/2]:
            for height in [.012,.06,.2,1.,2.]:
                approach=1.8 if f['id']=='way-641603104' else .20
                start=c+u*lateral+n*approach+Vector((0,0,height))
                for o,tree in trees:
                    if any(s in o.name.lower() for s in ['door','hardware']):continue
                    hit,_,_,distance=tree.ray_cast(start,-n,approach+depth)
                    assert hit is None,(f['id'],o.name,lateral,height,distance)
                ray_count+=1
        support_trees=[BVHTree.FromObject(o,dg) for o in bpy.context.scene.objects if o.type=='MESH' and o.get('building_id')==f['id'] and (o.get('context_only') or o.get('semantic_type')=='entry_support' or 'porch slab' in o.name or 'supporting slab' in o.name)]
        for lateral in [-.42,0,.42]:
            start=c+u*lateral+n*.12+Vector((0,0,1))
            heights=[hit.z for tree in support_trees if (hit:=tree.ray_cast(start,Vector((0,0,-1)),2)[0]) is not None]
            assert heights and -.012<=max(heights)-c.z<=.008,(f['id'],'unsupported entry',lateral,heights)
        if f.get('entry',{}).get('existing_support_z') is None:
            for lateral in [-.42,0,.42]:
                start=c+u*lateral+n*(-depth)+Vector((0,0,1))
                heights=[hit.z for tree in support_trees if (hit:=tree.ray_cast(start,Vector((0,0,-1)),2)[0]) is not None]
                assert heights and abs(max(heights)-c.z)<.012,(f['id'],'unsupported recessed threshold',lateral,heights)
        clearance.append({'threshold_xyz':list(c),'rays':ray_count,'checked_width_m':width})
        for support in entry.get('additional_supports',[]):
            ring=support['polygon_xy'];centre=Vector((sum(p[0] for p in ring)/len(ring),sum(p[1] for p in ring)/len(ring),support['top_z']))
            for p in ring:
                start=Vector((*p,support['top_z'])).lerp(centre,.02)+Vector((0,0,.5))
                hits=[q.z for tree in support_trees if (q:=tree.ray_cast(start,Vector((0,0,-1)),1)[0]) is not None]
                assert hits and abs(max(hits)-support['top_z'])<.002,(f['id'],'porch corner unsupported',list(start),hits)
                porch_support_samples+=1
    # Check the real wall mesh across the shared height interval, not just metadata.
    approach_samples=0
    profile=config.get('entry_approach_profiles',{}).get(f['id'])
    if profile:
        e=interfaces['entrance'];c=Vector(e['threshold_xyz']);n=Vector(e['outward_normal']);u=Vector((-n.y,n.x,0))
        support=[tree for ob,tree in trees if ob.get('semantic_type')=='entry_support']
        for a,b in zip(profile['knots'],profile['knots'][1:]):
            for t in [.05,.5,.95]:
                d=a[0]+t*(b[0]-a[0]);z=a[1]+t*(b[1]-a[1])
                for lateral in [-.42,0,.42]:
                    xy=c+n*d+u*lateral
                    hits=[h.z for tree in support if (h:=tree.ray_cast(Vector((xy.x,xy.y,z+1)),Vector((0,0,-1)),2)[0]) is not None]
                    assert hits and abs(max(hits)-z)<.002,(f['id'],'approach profile mismatch',d,lateral,hits,z)
                    approach_samples+=1
    shared_samples=0
    for wall in interfaces.get('shared_walls',[]):
        if not isinstance(wall,dict):continue
        edge=wall['edge'];a=Vector((*f['ring'][edge],0));b=Vector((*f['ring'][(edge+1)%len(f['ring'])],0));u=(b-a).normalized();n=Vector((u.y,-u.x,0))
        if wall.get('polyline'):
            line=wall['polyline'];a=Vector((*line[0][:2],0));b=Vector((*line[-1][:2],0))
        interval=wall.get('height_interval')
        # Unknown neighbour height is tested as an authored opaque target wall, not a measured common interval.
        lo,hi=interval if interval is not None else (f['base_z'],f['base_z']+f['height_m'])
        wall_groups=['pierced','stone walls','full depth wall piers','full thickness masonry piers','wall below apertures','wall below recessed apertures','wall lintels','curved window head masonry','flush attic solid walls']
        walls=[tree for ob,tree in trees if any(group in ob.name.lower() for group in wall_groups)]
        assert walls
        for frac in [.1,.3,.5,.7,.9]:
            for z in [lo+.3,lo+(hi-lo)*.3,lo+(hi-lo)*.6,hi-.3]:
                start=a.lerp(b,frac)+n*.1+Vector((0,0,z))
                assert any(tree.ray_cast(start,-n,.65)[0] is not None for tree in walls),(f['id'],'shared wall hole',edge,frac,z)
                shared_samples+=1
    if f['id']=='way-641603104':
        slabs=[tree for ob,tree in trees if 'supporting slab' in ob.name]
        for lateral in [-.42,0,.42]:
            for d in [.15,.6,1.,1.5]:
                start=c+u*lateral+n*d+Vector((0,0,1))
                # Recompute entrance frame; shared-wall loop has its own u/n.
                en=Vector(entry['outward_normal']);eu=Vector((-en.y,en.x,0));start=c+eu*lateral+en*d+Vector((0,0,1))
                hits=[q.z for tree in slabs if (q:=tree.ray_cast(start,Vector((0,0,-1)),2)[0]) is not None]
                assert hits and abs(max(hits)-c.z)<.008,('portico support gap',d,lateral,hits)
    passage_reports=[]
    for passage in interfaces.get('passages',[]):
        a=Vector(passage['start_xyz']);b=Vector(passage['end_xyz']);n=(b-a).normalized();u=Vector((-n.y,n.x,0));length=(b-a).length
        gates=set(passage.get('gate_object_names',[]));available={o.name for o in objects}
        assert gates<=available,('Missing declared gate geometry',gates-available)
        if passage.get('gate_state')=='closed_reference':assert gates
        half=passage['clear_width_m']/2-.08;spring=passage['spring_height_m'];crown=passage['clear_height_m'];count=0
        probes=[(l,h) for l in [-half,-half/2,0,half/2,half] for h in [.012,.06,.2,1.,spring-.10]]+[(0,spring+.2),(0,crown-.10)]
        for lateral,height in probes:
            start=a-n*.20+u*lateral+Vector((0,0,height))
            for o,tree in trees:
                if o.name in gates:continue
                assert tree.ray_cast(start,n,length+.40)[0] is None,(f['id'],'blocked masonry passage',o.name,lateral,height)
            count+=1
        floors=[tree for o,tree in trees if o.get('semantic_type')=='entry_support']
        floor_count=0
        for t in [.02,.25,.5,.75,.98]:
            for lateral in [-half*.8,0,half*.8]:
                c=a.lerp(b,t)+u*lateral;hits=[q.z for tree in floors if (q:=tree.ray_cast(c+Vector((0,0,1)),Vector((0,0,-1)),2)[0]) is not None]
                assert hits and abs(max(hits)-c.z)<.012,(f['id'],'unsupported passage floor',t,lateral,hits)
                floor_count+=1
        passage_reports.append({'masonry_clearance_rays':count,'floor_samples':floor_count,'intentional_gate_objects':sorted(gates),'gate_state':passage.get('gate_state'),'scope':'Architectural opening through masonry; closed gate is intentional and does not imply public or unobstructed access.'})
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
    assert samples>0
    reports.append({'building_id':f['id'],'entrances':clearance,'entrance_check_status':'checked' if entries else 'not applicable: no known entrance in source contract','porch_support_samples':porch_support_samples,'approach_profile_samples':approach_samples,'passages':passage_reports,'shared_wall_samples':shared_samples,'roof_coverage_samples':samples,'footprint_area_m2':f['area_m2']})

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
