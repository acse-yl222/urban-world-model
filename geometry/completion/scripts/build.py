import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];D=json.load(open(R/'geometry.json'));bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.78;return m
walls=[mat('Supplement | estimated pale stone',(.59,.54,.46)),mat('Supplement | estimated brick',(.40,.24,.17))];roof=mat('Supplement | estimated slate roof',(.18,.21,.23));glass=mat('Supplement | estimated glazing',(.16,.24,.29))
def building(c):
 verts=[];faces=[];mats=[]
 def face(v,mi):
  i=len(verts);verts.extend(v);faces.append(tuple(range(i,i+len(v))));mats.append(mi)
 h=c['height_m'];base=.10
 for p in c['parts']:
  vs=p['vertices']
  for a,b,d in p['triangles']:
   xy=[vs[i] for i in (a,b,d)]
   cross=(xy[1][0]-xy[0][0])*(xy[2][1]-xy[0][1])-(xy[1][1]-xy[0][1])*(xy[2][0]-xy[0][0])
   if cross<0:xy.reverse()
   face([(x,y,h+base) for x,y in xy],1);face([(x,y,base) for x,y in reversed(xy)],0)
  for ri,r in enumerate(p['rings']):
   for a,b in zip(r,r[1:]+r[:1]):
    face([(a[0],a[1],base),(b[0],b[1],base),(b[0],b[1],h+base),(a[0],a[1],h+base)],0)
    # Procedural, explicitly estimated glazing; stays inside mapped footprint.
    dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
    if length<3:continue
    ux,uy=dx/length,dy/length
    count=int(length/3.2)
    for k in range(count):
     mid=(k+.5)*length/count;ww=min(1.3,length/count*.5)
     for floor in range(max(1,round((h-.55)/3.15))):
      z=base+floor*3.15+1.05
      if z+1.5>h:continue
      x=a[0]+ux*mid;y=a[1]+uy*mid
      # Two faces offset either side ensure correct visibility regardless of OSM winding.
      for sign in [-1,1]:
       ox=-uy*.012*sign;oy=ux*.012*sign
       face([(x-ux*ww/2+ox,y-uy*ww/2+oy,z),(x+ux*ww/2+ox,y+uy*ww/2+oy,z),(x+ux*ww/2+ox,y+uy*ww/2+oy,z+1.4),(x-ux*ww/2+ox,y-uy*ww/2+oy,z+1.4)],2)
 me=bpy.data.meshes.new(c['id']);me.from_pydata(verts,[],faces);me.materials.append(walls[0 if c['tags'].get('building') in ['apartments','terrace','house','residential'] else 1]);me.materials.append(roof);me.materials.append(glass)
 for f,mi in zip(me.polygons,mats):f.material_index=mi
 ob=bpy.data.objects.new('OSM supplement | '+c['id']+' | '+c['tags'].get('name','building'),me);bpy.context.collection.objects.link(ob)
 ob['building_id']=c['id'];ob['height_basis']=c['height_basis'];ob['geometry_fidelity']='OSM footprint; estimated height and procedural facade baseline';ob['source']='osm_buildings.json';ob['source_url']='https://www.openstreetmap.org/'+c['id'].replace('-','/');return ob
for c in D['buildings']:building(c)
scene=bpy.context.scene;scene['attribution']=D['attribution'];scene['limitations']=D['limitations'];scene['coordinate_frame']=D['coordinate_frame']
R.joinpath('output').mkdir(exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(R/'output/buildings_supplement.blend'),compress=False)
bpy.ops.export_scene.gltf(filepath=str(R/'output/buildings_supplement.glb'),export_format='GLB',export_extras=True,export_yup=True)
# Independent import of exported artifact and numerical bounds/material checks.
expected={o['building_id']:(len(o.data.polygons),[min((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)],[max((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)]) for o in scene.objects if o.type=='MESH'}
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);bpy.ops.import_scene.gltf(filepath=str(R/'output/buildings_supplement.glb'))
seen=set();maxerr=0
for o in scene.objects:
 if o.type!='MESH':continue
 key=o.get('building_id');assert key in expected;seen.add(key);assert len(o.data.materials)>0
 lo=[min((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)];hi=[max((o.matrix_world@v.co)[i] for v in o.data.vertices) for i in range(3)]
 maxerr=max(maxerr,max(abs(a-b) for a,b in zip(lo+hi,expected[key][1]+expected[key][2])))
assert seen==set(expected);assert maxerr<.002
json.dump({'count':len(seen),'bounds_roundtrip_max_error_m':maxerr,'numerical_pass':True,'visual_reviewed':False,'scope':'Supplement only; source model preserved'},open(R/'reports/export_check.json','w'),indent=2)
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True;scene.world.color=(.8,.8,.8);scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
camd=bpy.data.cameras.new('Review');cam=bpy.data.objects.new('Review',camd);scene.collection.objects.link(cam);scene.camera=cam;camd.type='ORTHO';camd.clip_end=10000
for name,pos,target,scale in [('overview',(0,-1800,3000),(0,0,0),2900),('queens_gate',(900,-900,700),(580,-300,0),700),('montrose',(1200,-160,230),(900,65,10),220),('roof',(900,65,400),(900,65,0),170),('rear',(660,170,180),(900,65,10),240)]:
 cam.location=pos;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();camd.ortho_scale=scale;scene.render.filepath=str(R/'reports'/f'{name}.png');bpy.ops.render.render(write_still=True)
