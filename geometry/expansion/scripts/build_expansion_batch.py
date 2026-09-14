"""Assemble one declared expansion batch; preserve earlier artifacts and verify independent import."""
import bpy, json, sys, importlib.util, hashlib, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--batch',required=True)
parser.add_argument('--run',required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
assert '/' not in args.batch and '/' not in args.run
BATCH=ROOT/args.batch
CONFIG=json.loads((BATCH/'manifest.json').read_text())
RUN=ROOT/'output'/args.run
if (RUN/'verification.json').exists() and json.loads((RUN/'verification.json').read_text()).get('delivered'):
    raise RuntimeError('Refusing to overwrite a delivered run; choose a new --run')
RUN.mkdir(parents=True,exist_ok=True)
FEATURES=[json.loads(p.read_text()) for p in sorted((BATCH/'features').glob('*.json'))]
assert FEATURES and {f['id'] for f in FEATURES}=={f['id'] for f in CONFIG['features']}
assert len({f['id'] for f in FEATURES})==len(FEATURES)
IDS={f['id'] for f in FEATURES}
PREVIOUS_IDS={id for e in CONFIG['prior_exports'] for id in e['ids']}
CONTEXT=json.loads((BATCH/'reports/context.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def material(spec):
    m=bpy.data.materials.new(spec['name']);m.use_nodes=True
    color=(*spec['color'],spec.get('opacity',1));m.diffuse_color=color
    bs=m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=color
    bs.inputs['Roughness'].default_value=spec.get('roughness',.8)
    bs.inputs['Metallic'].default_value=spec.get('metalness',0)
    return m

source_mats={name:material(spec) for name,spec in CONTEXT['materials'].items()}
authored=[];results={};input_paths=[BATCH/'reports/context.json',BATCH/'manifest.json',Path(__file__)]
input_paths += [BATCH/path for path in CONFIG.get('interface_evidence_files',[])]
for feature in FEATURES:
    mats={k:source_mats[name] for k,name in feature['material_keys'].items()}
    # Evidence-based palette adjustments retain the surrounding scene's muted values.
    overrides=CONFIG.get('material_overrides',{}).get(feature['slug'],{})
    for key,color in overrides.items():
        old=mats[key];mats[key]=old.copy();mats[key].name=feature['name']+' | '+key
        mats[key].diffuse_color=(*color,1);mats[key].node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1)
    module_path=BATCH/'modules'/(feature['slug']+'.py')
    spec=importlib.util.spec_from_file_location(feature['slug'],module_path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    before=set(bpy.data.objects);results[feature['id']]=module.build(feature,mats)
    created=[o for o in bpy.data.objects if o not in before]
    assert created and all(o.type=='MESH' for o in created)
    assert set(results[feature['id']]['created'])=={o.name for o in created}
    # Explicitly audited source ground for entries lacking a source support mesh.
    ground_z=CONFIG.get('primary_entry_ground_z',{}).get(feature['id'])
    if ground_z is not None:
        assert feature.get('entry') and feature['entry'].get('existing_support_z') is None
        entry=results[feature['id']]['interfaces']['entrance']
        x,y,z=entry['threshold_xyz'];nx,ny,_=entry['outward_normal'];ux,uy=-ny,nx
        half=entry['clear_width_m']/2+.12;top=z-.006
        assert 0 <= top-ground_z < .15, 'Unexpected ground/threshold gap requires interface review'
        inset=min(-.12,(Vector(entry['door_leaf_xyz'])-Vector(entry['threshold_xyz'])).dot(Vector(entry['outward_normal']))-.10)
        profile=CONFIG.get('entry_approach_profiles',{}).get(feature['id'])
        knots=[(inset,top)]+(profile['knots'] if profile else [(.20,top),(.90,ground_z)])
        assert all(knots[i+1][0]>knots[i][0] for i in range(len(knots)-1))
        assert abs(knots[1][1]-top)<1e-6 and knots[1][0]>=.2
        bottom=min(ground_z,*(q[1] for q in knots))-.02
        verts=[(x+ux*s+nx*d,y+uy*s+ny*d,h) for d,h in knots for s in [-half,half]]
        verts += [(x+ux*s+nx*d,y+uy*s+ny*d,bottom) for d,h in knots for s in [-half,half]]
        N=2*len(knots);faces=[(0,N,N+1,1),(N-2,N-1,2*N-1,2*N-2)]
        for i in range(len(knots)-1):
            j=2*i
            faces += [(j,j+1,j+3,j+2),(N+j,N+j+2,N+j+3,N+j+1),(j,j+2,N+j+2,N+j),(j+1,N+j+1,N+j+3,j+3)]
        mesh=bpy.data.meshes.new('finite entry approach from audited ground');mesh.from_pydata(verts,[],[tuple(reversed(face)) for face in faces]);mesh.update()
        ob=bpy.data.objects.new(feature['name']+' | supporting slab and short approach',mesh);bpy.context.collection.objects.link(ob)
        mesh.materials.append(material({'name':feature['name']+' | estimated approach paving','color':[.38,.39,.37]}))
        ob['semantic_type']='entry_support';ob['ground_status']='source ground datum; short approach profile estimated, not surveyed'
        created.append(ob);results[feature['id']].setdefault('coordinator_created',[]).append(ob.name)
    entrance=results[feature['id']].get('interfaces',{}).get('entrance') or {}
    for index,support in enumerate(entrance.get('additional_supports',[])):
        assert ground_z is not None, 'Porch supports require audited ground'
        ring=[tuple(p) for p in support['polygon_xy']];top=support['top_z'];bottom=min(ground_z-.01,top-.02)
        assert len(ring)==4, 'Non-quadrilateral porch requires explicit triangulation'
        if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1]))<0:ring.reverse()
        verts=[(x,y,z) for z in [bottom,top] for x,y in ring]
        faces=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
        mesh=bpy.data.meshes.new('finite porch support');mesh.from_pydata(verts,[],faces);mesh.update()
        ob=bpy.data.objects.new(feature['name']+' | porch supporting slab '+str(index),mesh);bpy.context.collection.objects.link(ob)
        mesh.materials.append(mats['trim']);ob['semantic_type']='entry_support';ob['ground_status']='estimated porch slab connecting retained threshold to audited ground'
        created.append(ob);results[feature['id']].setdefault('coordinator_created',[]).append(ob.name)
    for index,passage in enumerate(results[feature['id']].get('interfaces',{}).get('passages',[])):
        a=Vector(passage['start_xyz']);b=Vector(passage['end_xyz']);n=(b-a).normalized();u=Vector((-n.y,n.x,0));half=passage['clear_width_m']/2
        assert abs(a.z-b.z)<.001, 'Sloping passage requires a separate floor contract'
        corners=[a-n*.15-u*half,a-n*.15+u*half,b+n*.15+u*half,b+n*.15-u*half]
        verts=[tuple(p+Vector((0,0,dz))) for dz in [-.026,-.006] for p in corners]
        faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
        mesh=bpy.data.meshes.new('finite passage supporting slab');mesh.from_pydata(verts,[],faces);mesh.update()
        ob=bpy.data.objects.new(feature['name']+' | passage supporting slab '+str(index),mesh);bpy.context.collection.objects.link(ob)
        mesh.materials.append(material({'name':feature['name']+' | passage paving','color':[.28,.29,.28]}))
        ob['semantic_type']='entry_support';ob['ground_status']='finite floor under audited source road display datum; not surveyed'
        created.append(ob);results[feature['id']].setdefault('coordinator_created',[]).append(ob.name)
    for index,entry in enumerate(results[feature['id']].get('interfaces',{}).get('additional_entrances',[])):
        x,y,z=entry['threshold_xyz'];nx,ny,_=entry['outward_normal'];ux,uy=-ny,nx
        half=entry['clear_width_m']/2+.12
        extra_ground=entry.get('audited_ground_z')
        inset=min(-.12,(Vector(entry['door_leaf_xyz'])-Vector(entry['threshold_xyz'])).dot(Vector(entry['outward_normal']))-.10)
        corners=[(-half,inset),(half,inset),(half,.90),(-half,.90)]
        top=z-.006
        if extra_ground is not None:
            assert 0 <= top-extra_ground < .15
            verts=[(x+ux*s+nx*d,y+uy*s+ny*d,height) for height in (extra_ground-.02,top) for s,d in corners]
            faces=[(0,1,2,3),(7,6,5,4)]+[(i,i+4,(i+1)%4+4,(i+1)%4) for i in range(4)]
        else:
            verts=[(x+ux*s+nx*d,y+uy*s+ny*d,top) for s,d in corners];faces=[(0,3,2,1)]
        mesh=bpy.data.meshes.new('finite additional entry support');mesh.from_pydata(verts,[],faces)
        ob=bpy.data.objects.new(feature['name']+' | additional entry support '+str(index),mesh)
        bpy.context.collection.objects.link(ob);mesh.materials.append(mats['trim'])
        ob['semantic_type']='entry_support';ob['ground_status']='finite estimated surface, not surveyed'
        created.append(ob)
        results[feature['id']].setdefault('coordinator_created',[]).append(ob.name)
    for o in created:
        o['building_id']=feature['id'];o['research_object_id']=feature['id']+'::'+args.batch+'::'+o.name
        o['geometry_fidelity']='Mapped footprint; source-informed architectural features with estimated and artistic details'
        o['expansion_status']='reference-informed exterior refinement; dimensions not surveyed'
        o['source_record']='geometry/expansion/'+args.batch+'/references/'+feature['slug']+'/sources.json'
        assert len(o.data.materials)>0
    authored.extend(created)
    input_paths.extend([module_path,BATCH/'features'/(feature['slug']+'.json')])
    input_paths.extend(p for p in (BATCH/'references'/feature['slug']).rglob('*') if p.is_file())

def signatures(objects):
    report={}
    for o in objects:
        if o.type!='MESH':continue
        o.data.calc_loop_triangles()
        points=[o.matrix_world@v.co for v in o.data.vertices]
        assert points and all(math.isfinite(v) for p in points for v in p)
        bounds=[min(p[a] for p in points) for a in range(3)]+[max(p[a] for p in points) for a in range(3)]
        degenerate=sum(1 for t in o.data.loop_triangles if ((points[t.vertices[1]]-points[t.vertices[0]]).cross(points[t.vertices[2]]-points[t.vertices[0]])).length<1e-9)
        assert degenerate==0,(o.name,degenerate)
        report[o['research_object_id']]={'bounds':bounds,'triangles':len(o.data.loop_triangles),'materials':sorted(m.name for m in o.data.materials if m)}
    return report

bpy.context.view_layer.update()
expected=signatures(authored)
frozen_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in input_paths}
bpy.ops.object.select_all(action='DESELECT')
for o in authored:o.select_set(True)
bpy.context.view_layer.objects.active=authored[0]
bpy.ops.export_scene.gltf(filepath=str(RUN/'replacement.glb'),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_draco_mesh_compression_enable=False)

# Native master also contains existing neighbours for examining the actual seam.
context_objects=[]
for record in CONTEXT['objects']:
    if record['id'] in IDS|PREVIOUS_IDS and record['extras'].get('semantic_type')!='entry_support':continue
    mesh=bpy.data.meshes.new('context mesh')
    p=record['positions'];ind=record['indices']
    mesh.from_pydata([p[i:i+3] for i in range(0,len(p),3)],[],[ind[i:i+3] for i in range(0,len(ind),3)])
    for name in record['materials']:mesh.materials.append(source_mats[name])
    for group in record['groups']:
        for pi in range(group['start']//3,min(len(mesh.polygons),(group['start']+group['count'])//3)):
            mesh.polygons[pi].material_index=group['materialIndex']
    obj=bpy.data.objects.new('CONTEXT | '+record['name'],mesh);bpy.context.collection.objects.link(obj)
    obj['context_only']=True;obj['building_id']=record['id'];context_objects.append(obj)

for prior in CONFIG['prior_exports']:
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/prior['path']))
    for o in set(bpy.data.objects)-before:
        if o.get('building_id') in IDS:bpy.data.objects.remove(o,do_unlink=True)
        else:o['context_only']=True
    input_paths.append(ROOT/prior['path'])

scene=bpy.context.scene
scene['scope']=CONFIG['scope']
scene['uncertainty']='Footprint and levels mapped; facade, roof and unseen details artistically completed; not measured reconstruction'
scene['context_render_limit']='Existing neighbour scalar PBR colours retained; texture maps omitted in diagnostic context only'
scene.render.engine='CYCLES';scene.cycles.samples=24
scene.cycles.use_denoising=True
scene.render.resolution_x=1200;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
scene.world.color=(.5,.5,.5)
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.65,.72,.8,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value=.7
sun_data=bpy.data.lights.new('Review daylight','SUN');sun_data.energy=2;sun_data.angle=.15
sun=bpy.data.objects.new('Review daylight',sun_data);scene.collection.objects.link(sun);sun.rotation_euler=(.5,-.6,-.5)
groundmat=material({'name':'Review ground | estimated flat support','color':[.38,.39,.37]})
bpy.ops.mesh.primitive_plane_add(size=CONFIG.get('review_ground_size',700),location=(*CONFIG.get('review_ground_center_xy',[670,60]),CONFIG.get('review_ground_z',.02)));ground=bpy.context.object
ground.name='Review support plane | estimated';ground.data.materials.append(groundmat);ground['review_only']=True
camera_data=bpy.data.cameras.new('Review camera');camera=bpy.data.objects.new('Review camera',camera_data)
scene.collection.objects.link(camera);scene.camera=camera;camera_data.type='ORTHO';camera_data.clip_end=2000
camera.location=(560,145,42);target=Vector((511.65,105.24,7));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.ortho_scale=43
bpy.ops.wm.save_as_mainfile(filepath=str(RUN/'master.blend'),compress=False)
record={'building_ids':sorted(IDS),'module_results':results,'expected':expected,'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in input_paths},'replacement_sha256':hashlib.sha256((RUN/'replacement.glb').read_bytes()).hexdigest(),'visual_reviewed':False,'delivered':False}

# Independent import after deleting the current scene's geometry.
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(RUN/'replacement.glb'))
actual=signatures([o for o in bpy.context.scene.objects if o.type=='MESH'])
assert set(actual)==set(expected),(len(actual),len(expected))
max_error=0
for key,value in expected.items():
    other=actual[key];assert other['triangles']==value['triangles'],key
    assert len(other['materials'])==len(value['materials']),key
    max_error=max(max_error,max(abs(a-b) for a,b in zip(value['bounds'],other['bounds'])))
assert max_error<.002,max_error
record.update(numerical_pass=True,roundtrip_bounds_max_error_m=max_error,objects=len(expected),triangles=sum(v['triangles'] for v in expected.values()))
(RUN/'verification.json').write_text(json.dumps(record,indent=2))

for rel,digest in frozen_hashes.items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,('Input changed during build',rel)
# Reopen the saved master for all review renders.
bpy.ops.wm.open_mainfile(filepath=str(RUN/'master.blend'))
scene=bpy.context.scene;camera=scene.camera
shots=[]
for f in FEATURES:
    cx,cy=f['center_xy'];h=f['height_m'];entry=f.get('entry')
    if not entry:
        ring=f['ring'];a,b=max(zip(ring,ring[1:]+ring[:1]),key=lambda ab:math.dist(*ab));length=math.dist(a,b)
        entry={'center_xy':[(a[0]+b[0])/2,(a[1]+b[1])/2],'outward_normal_xy':[(b[1]-a[1])/length,-(b[0]-a[0])/length]}
    nx,ny=entry['outward_normal_xy'];ux,uy=-ny,nx
    span=max(max(p[a] for p in f['ring'])-min(p[a] for p in f['ring']) for a in range(2))
    scale=max(28,span*1.5)
    front=(cx+nx*45+ux*22,cy+ny*45+uy*22,h+14)
    rear=(cx-nx*45-ux*22,cy-ny*45-uy*22,h+14)
    ex,ey=entry['center_xy'];ep=(ex+nx*12,ey+ny*12,4.5)
    for name,pos,target,sc in [('front',front,(cx,cy,h*.45),scale),('entrance',ep,(ex,ey,1.5),7),('roof',(cx,cy,85),(cx,cy,0),scale),('rear',rear,(cx,cy,h*.45),scale)]:
        if name=='entrance' and not f.get('entry'):continue
        shots.append((f['slug']+'_'+name,pos,target,sc,f['id'],False))
    context_camera=CONFIG.get('context_cameras',{}).get(f['slug'],{})
    shots.append((f['slug']+'_context',context_camera.get('position',(cx+nx*80+ux*45,cy+ny*80+uy*45,85)),context_camera.get('target',(cx,cy,h*.5)),context_camera.get('scale',130),None,True))
    for index,additional in enumerate(results[f['id']].get('interfaces',{}).get('additional_entrances',[])):
        p=Vector(additional['threshold_xyz']);normal=Vector(additional['outward_normal'])
        shots.append((f['slug']+'_additional_entrance_'+str(index),p+normal*12+Vector((0,0,4.5)),p+Vector((0,0,1.5)),7,f['id'],False))
    for index,passage in enumerate(results[f['id']].get('interfaces',{}).get('passages',[])):
        a=Vector(passage['start_xyz']);b=Vector(passage['end_xyz']);n=(b-a).normalized();height=passage['clear_height_m'];lift=Vector((0,0,height*.5))
        for side,p,normal in [('west',a,-n),('east',b,n)]:
            shots.append((f['slug']+'_passage_'+str(index)+'_'+side,p+normal*14+lift,p+lift,max(9,height*1.5),f['id'],False))
overview=CONFIG.get('overview',{'position':[680,370,400],'target':[670,60,5],'scale':520})
shots.append(('overview',overview['position'],overview['target'],overview['scale'],None,True))
for name,position,target,scale,only_id,show_context in shots:
    for o in scene.objects:
        if o.get('context_only'):o.hide_render=not show_context
        elif o.type=='MESH' and o.get('building_id') in IDS:o.hide_render=only_id is not None and o['building_id']!=only_id
    camera.location=position;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
    scene.render.filepath=str(RUN/(name+'.png'));bpy.ops.render.render(write_still=True)
for rel,digest in record['source_hashes'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,('Input changed during render',rel)
print(json.dumps({k:record[k] for k in ['objects','triangles','roundtrip_bounds_max_error_m','numerical_pass']}))
