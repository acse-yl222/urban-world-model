import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'output/buildings_supplement.blend'))
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_cavity=True;s.render.resolution_x=1600;s.render.resolution_y=1200;s.render.resolution_percentage=100
ob=next(o for o in s.objects if o.get('building_id')=='way-810194066');vs=[o for o in ob.data.vertices];lo=Vector([min(v.co[i] for v in vs) for i in range(3)]);hi=Vector([max(v.co[i] for v in vs) for i in range(3)]);center=(lo+hi)/2
camd=bpy.data.cameras.new('Review camera');cam=bpy.data.objects.new('Review camera',camd);s.collection.objects.link(cam);s.camera=cam;camd.type='ORTHO';camd.clip_end=10000
for name,offset,scale in [('front',(100,-140,90),180),('roof',(0,-.01,300),160),('rear',(-110,130,90),180)]:
 cam.location=center+Vector(offset);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();camd.ortho_scale=scale;s.render.filepath=str(R/'reports'/f'{name}.png');bpy.ops.render.render(write_still=True)
