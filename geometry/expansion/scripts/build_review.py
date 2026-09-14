"""Assemble the first expansion building, export and check an independent import."""
import bpy, json, sys, importlib.util, hashlib, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'output'/'kensington_gore_23_v1'
RUN.mkdir(parents=True,exist_ok=True)
FEATURE=json.loads((ROOT/'feature.json').read_text())
CONTEXT=json.loads((ROOT/'reports/context.json').read_text())
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
keys={'masonry':'Detailed | urban masonry 3','trim':'Detailed | limestone trim',
      'glass':'Detailed | recessed blue grey glazing','door':'Detailed | painted entrance',
      'roof':'Detailed | slate grey roof','metal':'Detailed | Stevens black coated window metal'}
mats={k:source_mats[v] for k,v in keys.items()}
module_path=ROOT/'modules/kensington_gore_23.py'
spec=importlib.util.spec_from_file_location('building_module',module_path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
before=set(bpy.data.objects)
result=module.build(FEATURE,mats)
authored=[o for o in bpy.data.objects if o not in before]
assert authored and all(o.type=='MESH' for o in authored)
if 'created' in result:assert set(result['created'])=={o.name for o in authored}
for o in authored:
    o['building_id']=FEATURE['id'];o['research_object_id']=FEATURE['id']+'::expansion::'+o.name
    o['geometry_fidelity']='Mapped footprint; source-reported levels; artistically completed architecture'
    o['expansion_status']='single-building artistic refinement; not surveyed or facade-verified'
    o['source_record']='geometry/expansion/references/kensington_gore_23/sources.json'
    assert len(o.data.materials)>0

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
bpy.ops.object.select_all(action='DESELECT')
for o in authored:o.select_set(True)
bpy.context.view_layer.objects.active=authored[0]
bpy.ops.export_scene.gltf(filepath=str(RUN/'replacement.glb'),export_format='GLB',use_selection=True,export_extras=True,export_yup=True,export_draco_mesh_compression_enable=False)

# Native master also contains existing neighbours for examining the actual seam.
context_objects=[]
for record in CONTEXT['objects']:
    if record['id']==FEATURE['id'] and record['extras'].get('semantic_type')!='entry_support':continue
    mesh=bpy.data.meshes.new('context mesh')
    p=record['positions'];ind=record['indices']
    mesh.from_pydata([p[i:i+3] for i in range(0,len(p),3)],[],[ind[i:i+3] for i in range(0,len(ind),3)])
    for name in record['materials']:mesh.materials.append(source_mats[name])
    for group in record['groups']:
        for pi in range(group['start']//3,min(len(mesh.polygons),(group['start']+group['count'])//3)):
            mesh.polygons[pi].material_index=group['materialIndex']
    obj=bpy.data.objects.new('CONTEXT | '+record['name'],mesh);bpy.context.collection.objects.link(obj)
    obj['context_only']=True;obj['building_id']=record['id'];context_objects.append(obj)

scene=bpy.context.scene
scene['scope']='One replacement building with existing neighbourhood context; only replacement exported'
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
bpy.ops.mesh.primitive_plane_add(size=280,location=(511.65,105.24,.02));ground=bpy.context.object
ground.name='Review support plane | estimated';ground.data.materials.append(groundmat);ground['review_only']=True
camera_data=bpy.data.cameras.new('Review camera');camera=bpy.data.objects.new('Review camera',camera_data)
scene.collection.objects.link(camera);scene.camera=camera;camera_data.type='ORTHO';camera_data.clip_end=2000
camera.location=(560,145,42);target=Vector((511.65,105.24,7));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera_data.ortho_scale=43
bpy.ops.wm.save_as_mainfile(filepath=str(RUN/'master.blend'),compress=False)
record={'building_id':FEATURE['id'],'module_result':result,'expected':expected,'source_hashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [module_path,ROOT/'feature.json',ROOT/'reports/context.json']},'replacement_sha256':hashlib.sha256((RUN/'replacement.glb').read_bytes()).hexdigest(),'visual_reviewed':False,'delivered':False}

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

# Reopen the saved master for all review renders.
bpy.ops.wm.open_mainfile(filepath=str(RUN/'master.blend'))
scene=bpy.context.scene;camera=scene.camera
shots=[('front',(560,145,30),(512,105,7),40,False),('entrance',(534,110,5),(519.6,106,1.5),7,False),('roof',(515,105,85),(511.65,105,7),36,False),('rear',(465,70,30),(511.65,105,7),40,False),('context',(590,170,85),(520,80,9),150,True)]
for name,position,target,scale,show_context in shots:
    for o in scene.objects:
        if o.get('context_only'):o.hide_render=not show_context
    camera.location=position;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=scale
    scene.render.filepath=str(RUN/(name+'.png'));bpy.ops.render.render(write_still=True)
print(json.dumps({k:record[k] for k in ['objects','triangles','roundtrip_bounds_max_error_m','numerical_pass']}))
