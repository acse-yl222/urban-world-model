"""Assemble the third expansion batch, export and check an independent import."""
import bpy, json, sys, importlib.util, hashlib, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/'batch03'
RUN=ROOT/'output'/'batch03_v1'
RUN.mkdir(parents=True,exist_ok=True)
FEATURES=[json.loads(p.read_text()) for p in sorted((BATCH/'features').glob('*.json'))]
IDS={f['id'] for f in FEATURES}
PREVIOUS_IDS={'way-117417431','way-117417421','way-117010286','way-641757059'}
CONTEXT=json.loads((BATCH/'reports/context.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

# Preserve the two unchanged batch02 assets in a separate GLB; 29 is revised in this batch.
bpy.ops.import_scene.gltf(filepath=str(ROOT/'output/batch02_v1/replacement.glb'))
bpy.ops.object.select_all(action='DESELECT')
legacy=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('building_id') in {'way-117010286','way-117417421'}]
for o in legacy:o.select_set(True)
bpy.context.view_layer.objects.active=legacy[0]
bpy.ops.export_scene.gltf(filepath=str(RUN/'retained_batch02.glb'),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_draco_mesh_compression_enable=False)
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
for feature in FEATURES:
    mats={k:source_mats[name] for k,name in feature['material_keys'].items()}
    # Evidence-based palette adjustments retain the surrounding scene's muted values.
    overrides={'kensington_gore_84':{'masonry':(.46,.24,.16),'trim':(.85,.81,.69),'roof':(.30,.12,.08)},
               'jay_mews_117010283':{'masonry':(.61,.58,.50),'trim':(.81,.79,.72)},
               'exhibition_road_29':{'masonry':(.40,.19,.12),'trim':(.76,.73,.65),'roof':(.30,.12,.08)},
               'jamaican_high_commission':{'masonry':(.40,.19,.12),'trim':(.76,.73,.65),'roof':(.30,.12,.08)}}.get(feature['slug'],{})
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
    for index,entry in enumerate(results[feature['id']].get('interfaces',{}).get('additional_entrances',[])):
        x,y,z=entry['threshold_xyz'];nx,ny,_=entry['outward_normal'];ux,uy=-ny,nx
        half=entry['clear_width_m']/2+.12
        verts=[(x+ux*s+nx*d,y+uy*s+ny*d,z-.006) for s,d in [(-half,-.12),(half,-.12),(half,.90),(-half,.90)]]
        mesh=bpy.data.meshes.new('finite additional entry support');mesh.from_pydata(verts,[],[(0,3,2,1)])
        ob=bpy.data.objects.new(feature['name']+' | additional entry support '+str(index),mesh)
        bpy.context.collection.objects.link(ob);mesh.materials.append(source_mats['Detailed | Extension entrance paving union'])
        ob['semantic_type']='entry_support';ob['ground_status']='finite estimated surface, not surveyed'
        created.append(ob)
        results[feature['id']].setdefault('coordinator_created',[]).append(ob.name)
    for o in created:
        o['building_id']=feature['id'];o['research_object_id']=feature['id']+'::batch03::'+o.name
        o['geometry_fidelity']='Mapped footprint; source-informed architectural features with estimated and artistic details'
        o['expansion_status']='reference-informed exterior refinement; dimensions not surveyed'
        o['source_record']='geometry/expansion/batch03/references/'+feature['slug']+'/sources.json'
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

for prior in ['kensington_gore_23_v1','batch02_v1']:
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'output'/prior/'replacement.glb'))
    for o in set(bpy.data.objects)-before:
        if o.get('building_id') in IDS:bpy.data.objects.remove(o,do_unlink=True)
        else:o['context_only']=True
    input_paths.append(ROOT/'output'/prior/'replacement.glb')

scene=bpy.context.scene
scene['scope']='Three additions and corrected 29 Exhibition Road; earlier deliveries shown in neighbourhood context'
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
bpy.ops.mesh.primitive_plane_add(size=700,location=(670,60,.02));ground=bpy.context.object
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
    cx,cy=f['center_xy'];h=f['height_m'];entry=f['entry'];nx,ny=entry['outward_normal_xy'];ux,uy=-ny,nx
    span=max(max(p[a] for p in f['ring'])-min(p[a] for p in f['ring']) for a in range(2))
    scale=max(28,span*1.5)
    front=(cx+nx*45+ux*22,cy+ny*45+uy*22,h+14)
    rear=(cx-nx*45-ux*22,cy-ny*45-uy*22,h+14)
    ex,ey=entry['center_xy'];ep=(ex+nx*12,ey+ny*12,4.5)
    for name,pos,target,sc in [('front',front,(cx,cy,h*.45),scale),('entrance',ep,(ex,ey,1.5),7),('roof',(cx,cy,85),(cx,cy,0),scale),('rear',rear,(cx,cy,h*.45),scale)]:
        shots.append((f['slug']+'_'+name,pos,target,sc,f['id'],False))
    shots.append((f['slug']+'_context',(cx+nx*80+ux*45,cy+ny*80+uy*45,85),(cx,cy,h*.5),130,None,True))
shots.append(('overview',(680,370,400),(670,60,5),520,None,True))
for name,position,target,scale,only_id,show_context in shots:
    for o in scene.objects:
        if o.get('context_only'):o.hide_render=not show_context
        elif o.type=='MESH' and o.get('building_id') in IDS:o.hide_render=only_id is not None and o['building_id']!=only_id
    camera.location=position;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
    scene.render.filepath=str(RUN/(name+'.png'));bpy.ops.render.render(write_still=True)
for rel,digest in record['source_hashes'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==digest,('Input changed during render',rel)
print(json.dumps({k:record[k] for k in ['objects','triangles','roundtrip_bounds_max_error_m','numerical_pass']}))
