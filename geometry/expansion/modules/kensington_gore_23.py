"""23 Kensington Gore: mapped footprint, artistically completed architecture.
No image pixels/textures embedded. build(feature, materials) creates only new objects.
Required material keys: masonry, trim, glass, door, roof, metal.
Feature requires ring of projected east/north points; optional base_z, height_m.
"""
import math

def build(feature, materials):
    import bpy
    from mathutils import Vector
    from mathutils.geometry import tessellate_polygon
    ring = [tuple(map(float, p[:2])) for p in feature['ring']]
    if ring[0] == ring[-1]: ring.pop()
    if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1])) < 0:
        raise ValueError('Expected CCW mapped ring; edge 0 must remain eastern entrance facade')
    z0 = float(feature.get('base_z', 0.05))
    H = float(feature.get('height_m',13.15))
    groups = {}
    openings = []
    entrance = None
    def meshpart(group, mat, vertices, faces):
        v,f = groups.setdefault((group,mat),([],[])); offset=len(v)
        v.extend(vertices);f.extend(tuple(offset+i for i in face) for face in faces)
    def block(group, mat, center, size, u=(1.,0.), n=(0.,1.)):
        if min(size) <= 1e-7: return
        x,y,z=center;w,d,h=[q/2 for q in size]
        pts=[(x+a*w*u[0]+b*d*n[0],y+a*w*u[1]+b*d*n[1],z+c*h) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        meshpart(group,mat,pts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    floor_tops = [0,3.45,6.9,10.1,H]
    for ei,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
        L=math.dist(a,b);u=((b[0]-a[0])/L,(b[1]-a[1])/L);n=(u[1],-u[0])
        def at(s,depth,z):return (a[0]+u[0]*s+n[0]*depth,a[1]+u[1]*s+n[1]*depth,z0+z)
        def panel(group,mat,s0,s1,z1,z2,depth=-.19,thick=.38):
            block(group,mat,at((s0+s1)/2,depth,(z1+z2)/2),(s1-s0,thick,z2-z1),u,n)
        # East = 5 bays with entry, north has three canted bay faces;
        # west shared-wall frontage kept blind pending neighbour inspection.
        is_blind=ei==7 or L<1.3
        count=0 if is_blind else (5 if ei==0 else max(1,int(L/3.1)))
        centers=[(i+.5)*L/count for i in range(count)] if count else []
        for level,(low,high) in enumerate(zip(floor_tops,floor_tops[1:])):
            zbot=low+(0.88 if level==0 else .65)
            ztop=high-.52
            holes=[]
            for bi,s in enumerate(centers):
                width=min(1.45 if level<2 else 1.3,L/count-.65)
                door = ei==0 and level==0 and bi==2
                if door:
                    width=float(feature.get('entry',{}).get('clear_width_m',1.05))+.15
                    entry_xy=feature.get('entry',{}).get('center_xy')
                    if entry_xy: s=(entry_xy[0]-a[0])*u[0]+(entry_xy[1]-a[1])*u[1]
                bottom=0.0 if door else zbot
                top=2.8 if door else ztop
                holes.append((s-width/2,s+width/2,bottom,top,door,bi))
            cuts=sorted(set([0,L]+[q for hole in holes for q in hole[:2]]))
            for left,right in zip(cuts,cuts[1:]):
                hole=next((h for h in holes if h[0]-1e-6<=(left+right)/2<=h[1]+1e-6),None)
                if hole:
                    panel('pierced wall','masonry',left,right,low,hole[2]);panel('pierced wall','masonry',left,right,hole[3],high)
                else:panel('pierced wall','masonry',left,right,low,high)
            for left,right,bottom,top,door,bi in holes:
                s=(left+right)/2;w=right-left;hh=top-bottom
                # No masonry across opening: visible 0.38m jamb depth and recessed leaf/glazing.
                panel('recessed doors' if door else 'recessed glass','door' if door else 'glass',left+.075,right-.075,bottom if door else bottom+.07,top-.07,-.33,.065)
                for xx in [left+.045,right-.045]:panel('joinery','trim',xx-.045,xx+.045,bottom,top,-.24,.1)
                for zz in ([top-.045] if door else [bottom+.045,top-.045]):panel('joinery','trim',left,right,zz-.045,zz+.045,-.24,.1)
                if not door:
                    panel('sash mullions','trim',s-.03,s+.03,bottom,top,-.22,.06)
                    panel('sash mullions','trim',left,right,(bottom+top)/2-.038,(bottom+top)/2+.038,-.22,.06)
                else:
                    panel('door central stile','trim',s-.025,s+.025,bottom,top,-.255,.06)
                    panel('door fanlight transom','trim',left,right,2.24,2.32,-.22,.08)
                    for ds in [-.38,.38]:
                        block('door hardware','metal',at(s+ds,-.19,1.12),(.035,.07,.23),u,n)
                    # Finite threshold fully inside footprint; coordinator owns outside support.
                    panel('entry threshold','trim',left-.12,right+.12,-.006,0.0,-.22,.44)
                    entrance={'threshold_xyz':[*(feature.get('entry',{}).get('center_xy') or at(s,0,0)[:2]),float(feature.get('entry',{}).get('threshold_z',z0))],'outward_normal':[n[0],n[1],0],'clear_width_m':w-.15,'door_leaf_xyz':list(at(s,-.33,1.43)),'stair_treads':[],'ramp':'none authored; match existing ground support','surface_owner':'coordinator','basis':'existing eastern baseline entry vicinity; exact opening artistically completed'}
                # Dressed architraves, stepped lintels and projecting sills.
                for xx in [left-.10,right+.10]:panel('architraves','trim',xx-.065,xx+.065,bottom-.10,top+.14,.015,.10)
                panel('architraves','trim',left-.18,right+.18,top+.04,top+.20,.055,.20)
                panel('sills','trim',left-.15,right+.15,bottom-.12,bottom-.035,.08,.28)
                if level==1 and ei in [0,1,2,3,4,5,6]:
                    panel('hood mouldings','trim',left-.25,right+.25,top+.23,top+.31,.10,.29)
                    # Modest local guard rails, not long invented balconies.
                    for k in range(7):
                        xx=left+(right-left)*k/6
                        panel('window guards','metal',xx-.018,xx+.018,bottom-.03,bottom+.48,.22,.036)
                    panel('window guards','metal',left-.06,right+.06,bottom+.47,bottom+.515,.22,.045)
                openings.append({'edge':ei,'floor':level,'bay':bi,'type':'door' if door else 'window','width_m':w,'height_m':hh,'recess_m':.33,'basis':'artistic completion'})
    # Continuous mitred polygon bands prevent open square gaps at corners.
    def band(group,mat,low,high,depth,thickness):
        def offset(distance):
            points=[]
            for i,p in enumerate(ring):
                a=ring[i-1];b=ring[(i+1)%len(ring)]
                la=math.dist(a,p);lb=math.dist(p,b)
                na=((p[1]-a[1])/la,-(p[0]-a[0])/la)
                nb=((b[1]-p[1])/lb,-(b[0]-p[0])/lb)
                k=distance/(1+na[0]*nb[0]+na[1]*nb[1])
                points.append((p[0]+k*(na[0]+nb[0]),p[1]+k*(na[1]+nb[1])))
            return points
        inner=offset(depth-thickness/2);outer=offset(depth+thickness/2)
        verts=[(x,y,z0+z) for z in (low,high) for contour in (inner,outer) for x,y in contour]
        N=len(ring);faces=[]
        for i in range(N):
            j=(i+1)%N
            faces.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
        meshpart(group,mat,verts,faces)
    for zz,th,dep in [(3.45,.12,.08),(6.9,.10,.055),(10.1,.10,.055),(H-.15,.18,.14),(H+.10,.14,.20)]:
        band('string courses and cornice','trim',zz-th/2,zz+th/2,dep,.15)
    band('roof parapet','masonry',H,H+.47,-.16,.30)
    band('roof coping','trim',H+.47,H+.56,-.12,.40)
    # Exact concave roof cap (not convex hull); no imaginary attic storey.
    vv=[Vector((x,y,z0+H-.07)) for x,y in ring]
    triangles=tessellate_polygon([vv])
    verts=[];faces=[]
    for tri in triangles:
        off=len(verts);verts.extend(tuple(vv[v] if isinstance(v,int) else v) for v in tri);faces.append((off,off+1,off+2))
    meshpart('mapped roof deck','roof',verts,faces)
    # Narrow shallow roof lantern in safely interior rectangle: explicitly artistic.
    x1,x2,y1,y2=507.0,513.5,101.5,110.5
    block('roof lantern curb','trim',((x1+x2)/2,(y1+y2)/2,z0+H+.09),(x2-x1,y2-y1,.30))
    pts=[(x1,y1,z0+H+.25),(x2,y1,z0+H+.25),(x2,y2,z0+H+.25),(x1,y2,z0+H+.25),((x1+x2)/2,y1+.75,z0+H+1.0),((x1+x2)/2,y2-.75,z0+H+1.0)]
    meshpart('estimated shallow hipped roof','roof',pts,[(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5)])
    created=[]
    for (group,mat),(verts,faces) in groups.items():
        if not faces:continue
        name='23 Kensington Gore | '+group
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
        # Wall-local u/outward-normal frames can reverse handedness.
        import bmesh
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
        obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
        obj.data.materials.append(materials[mat]);obj['building_id']=feature['id'];obj['evidence_status']='Mapped footprint and OSM levels; artistic facade and roof completion';obj['geometry_fidelity']='Individual authored apertures, recessed glazing and frames; not survey accurate';obj['research_object_id']=feature['id']+'::'+group
        created.append(obj.name)
    return {'created':created,'parameters':{'height_m':H,'base_z':z0,'levels':4,'opening_count':len(openings),'wall_thickness_m':.38,'roof_max_z':z0+H+1},'interfaces':{'entrance':entrance,'shared_wall':{'edge':7,'polyline':[list(ring[7]),list(ring[8])],'height_interval':[z0,z0+H],'openings':[],'basis':'conservative blind west face pending shared-wall inspection'}},'openings':openings,'evidence_source_ids':['osm-20260912','geograph-2719604','geograph-5276805','he-1275267'],'uncertainty':['No confirmed photo of 23 Kensington Gore; all facade/roof composition artistically completed from neighbourhood context','Height/floor pitch and door position remain estimated','Roof lantern is artistic completion, not observed roof equipment','No basement or invented underground opening created']}
