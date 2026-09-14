import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
r=Path(__file__).resolve().parents[2]/'output/batch17_v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
master_sha=sha(r/'master.blend');glb_sha=sha(r/'replacement.glb')
bpy.ops.wm.open_mainfile(filepath=str(r/'master.blend'))
s=bpy.context.scene;c=s.camera
for o in s.objects:
 if o.type=='MESH':o.hide_render=False
c.location=(945,-285,25);target=Vector((965.4,-269.65,5));c.rotation_euler=(target-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=48
s.render.filepath=str(r/'princes_gate_mews_85_close_context.png');bpy.ops.render.render(write_still=True)
assert sha(r/'master.blend')==master_sha and sha(r/'replacement.glb')==glb_sha
Path(__file__).with_suffix('.json').write_text(json.dumps({'master_sha256':master_sha,'replacement_sha256':glb_sha,'image_sha256':sha(Path(s.render.filepath)),'position':list(c.location),'target':list(target),'scale':48,'scope':'Additional view from closer camera to avoid foreground terrace occlusion; all original master geometry retained, no master saved or asset moved'},indent=2))
