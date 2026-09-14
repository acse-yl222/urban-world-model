import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]/'output/batch02_v1'
bpy.ops.wm.open_mainfile(filepath=str(R/'master.blend'));s=bpy.context.scene;c=s.camera
v=json.load(open(R/'verification.json'));entry=v['module_results']['way-641757059']['interfaces']['additional_entrances'][0];x,y,z=entry['threshold_xyz'];nx,ny,_=entry['outward_normal']
shots=[('exhibition_road_29_context_southeast',(887,-45,80),(844.5,11.6,8),105,True),('exhibition_road_29_context_overhead',(860,-5,130),(844.5,11.6,0),75,True),('exhibition_road_29_south_entrance',(x+nx*12,y+ny*12,4.5),(x,y,1.5),7,False)]
for name,pos,target,scale,context in shots:
 for o in s.objects:
  if o.get('context_only'):o.hide_render=not context
  elif o.type=='MESH' and o.get('building_id'):o.hide_render=not context and o['building_id']!='way-641757059'
 c.location=pos;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale;s.render.filepath=str(R/(name+'.png'));bpy.ops.render.render(write_still=True)
