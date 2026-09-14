"""Refined ancillary shell; unknown openings and use deliberately remain unknown."""
import math


def build(feature, materials):
    import bpy
    import bmesh
    from mathutils import Vector
    from mathutils.geometry import tessellate_polygon
    ring=[tuple(map(float,p[:2])) for p in feature['ring']]
    if ring[0]==ring[-1]:ring.pop()
    if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1]))<=0:raise ValueError('CCW required')
    z0=float(feature['base_z']);H=float(feature['height_m']);groups={}
    def part(name,mat,verts,faces):
        v,f=groups.setdefault((name,mat),([],[]));o=len(v);v.extend(verts);f.extend(tuple(o+i for i in x) for x in faces)
    def offset(d):
        out=[]
        for i,p in enumerate(ring):
            a=ring[i-1];b=ring[(i+1)%len(ring)];la=math.dist(a,p);lb=math.dist(p,b);na=((p[1]-a[1])/la,-(p[0]-a[0])/la);nb=((b[1]-p[1])/lb,-(b[0]-p[0])/lb);k=d/(1+na[0]*nb[0]+na[1]*nb[1]);out.append((p[0]+k*(na[0]+nb[0]),p[1]+k*(na[1]+nb[1])))
        return out
    def band(name,mat,lo,hi,inner,outer):
        N=len(ring);vs=[(x,y,z0+z) for z in (lo,hi) for r in (offset(inner),offset(outer)) for x,y in r];fs=[]
        for i in range(N):
            j=(i+1)%N;fs.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
        part(name,mat,vs,fs)
    def slab(name,mat,lo,hi):
        N=len(ring);vs=[(x,y,z0+z) for z in (lo,hi) for x,y in ring];fs=[]
        vv=[Vector((x,y,0)) for x,y in ring]
        for tri in tessellate_polygon([vv]):
            ids=[t if isinstance(t,int) else min(range(N),key=lambda k:(vv[k]-t).length) for t in tri];fs.extend([tuple(reversed(ids)),tuple(i+N for i in ids)])
        for i in range(N):j=(i+1)%N;fs.append((i,j,N+j,N+i))
        part(name,mat,vs,fs)
    band('continuous closed masonry perimeter','masonry',0,H,-.28,0)
    slab('closed bottom slab','masonry',0,.045)
    band('inset masonry base trim','trim',.03,.18,-.29,-.005)
    band('simple inward eaves fascia','trim',H-.15,H+.035,-.30,-.005)
    slab('complete thin roof slab','roof',H-.06,H+.04)
    band('low roof weather upstand','masonry',H+.04,H+.16,-.24,-.015)
    band('mitred coping','trim',H+.16,H+.22,-.27,-.005)
    # Inward corner closure strips express editable masonry joints without adding openings.
    for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
        L=math.dist(a,b);u=((b[0]-a[0])/L,(b[1]-a[1])/L);n=(u[1],-u[0]);vs=[]
        for z in (.18,H-.15):
            for s,d in [(.015,-.03),(.105,-.03),(.105,-.001),(.015,-.001)]:vs.append((a[0]+u[0]*s+n[0]*d,a[1]+u[1]*s+n[1]*d,z0+z))
        part('corner boundary strips','trim',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    created=[]
    for (group,mat),(vs,fs) in groups.items():
        name='Mews outbuilding1154608369 | '+group;me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[mat]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+group;ob['evidence_status']='Refined ancillary shell; mapped one floor, unknown openings, estimated heights';created.append(ob.name)
    return {'created':created,'parameters':{'height_m':H,'base_z':z0,'levels':1,'opening_count':0,'wall_thickness_m':.28,'roof_max_z':z0+H+.22,'small_solid_outbuilding':True,'refinement_class':'refined ancillary shell'},'interfaces':{'entrance':None,'entrance_status':'No source entry; opening locations unknown, none invented','shared_walls':[],'shared_wall_policy':'All original edges retained; no exact shared line in audit'},'openings':[],'evidence_source_ids':['osm-1154608369','outbuilding-mews-context'],'uncertainty':['Exact building use and entrances unknown; no source door/window mesh and no confirmed target photograph','OSM one floor retained; source eaves estimated, not measured','Coping, thin slab and masonry trim are artistic weatherproofing details; this is refined ancillary shell, not survey-accurate facade']}
