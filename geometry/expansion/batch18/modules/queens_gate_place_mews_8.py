"""8 Queens Gate Place Mews: full mapped ring; Residential mews from OSM; individual facade estimated.
No downloaded textures; no global scene mutation. The 2010 photo is street context only,
with author public-domain dedication recorded by Commons (PD-author-FlickrPDM).
"""
import math


def build(feature, materials):
    import bpy
    import bmesh
    from mathutils import Vector
    from mathutils.geometry import tessellate_polygon
    ring = [tuple(map(float, p[:2])) for p in feature['ring']]
    if ring[0] == ring[-1]: ring.pop()
    if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1])) <= 0:
        raise ValueError('Expected CCW ring')
    z0 = float(feature.get('base_z', .05)); H = float(feature['height_m'])
    levels = max(1, int(feature.get('levels', 2)))
    materials=dict(materials); materials['masonry']=materials['trim']  # pale painted street-context completion, not measured colour
    groups = {}; openings = []; entrance = None
    entry = feature.get('entry') or {}
    edges = []
    for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
        L=math.dist(a,b);u=((b[0]-a[0])/L,(b[1]-a[1])/L);n=(u[1],-u[0])
        edges.append((a,b,L,u,n))
    ep = entry.get('center_xy')
    if ep:
        def distance(e):
            a,b,L,u,n=e;s=max(0,min(L,(ep[0]-a[0])*u[0]+(ep[1]-a[1])*u[1]))
            return math.dist(ep,(a[0]+s*u[0],a[1]+s*u[1]))
        entry_edge=min(range(len(edges)),key=lambda i:distance(edges[i]))
    else: entry_edge=4
    def meshpart(group,mat,vs,fs):
        v,f=groups.setdefault((group,mat),([],[]));off=len(v);v.extend(vs);f.extend(tuple(off+i for i in face) for face in fs)
    def block(group,mat,center,size,u=(1.,0.),n=(0.,1.)):
        if min(size)<=1e-7:return
        x,y,z=center;w,d,h=[s/2 for s in size]
        vs=[(x+a*w*u[0]+b*d*n[0],y+a*w*u[1]+b*d*n[1],z+c*h) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        meshpart(group,mat,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    shared=[]
    for seg in feature.get('audit',{}).get('normalized_shared_wall_segments',[]):
        if seg.get('height_interval'):
            shared.append({**seg,'policy':'Retain full wall; all normalized disconnected common-height segments opaque'})
    if not shared:raise ValueError('Expected normalized shared-wall segments for this target')
    split=H/levels
    floor_bounds=[i*H/levels for i in range(levels+1)]
    for ei,(a,b,L,u,n) in enumerate(edges):
        def at(s,d,z):return (a[0]+u[0]*s+n[0]*d,a[1]+u[1]*s+n[1]*d,z0+z)
        def panel(g,m,l,r,lo,hi,d=-.18,t=.36):block(g,m,at((l+r)/2,d,(lo+hi)/2),(r-l,t,hi-lo),u,n)
        # Long street wall gets differentiated workshop bays; short return faces remain complete.
        count=3 if ei==2 else 2 if ei==4 else 1 if ei==1 else 0
        centers=[(i+.5)*L/count for i in range(count)] if count else []
        entry_s=((ep[0]-a[0])*u[0]+(ep[1]-a[1])*u[1]) if ep and ei==entry_edge else L*.5
        for level,(low,high) in enumerate(zip(floor_bounds,floor_bounds[1:])):
            holes=[]
            for bi,s in enumerate(centers):
                w=min(.94 if ei==2 else 1.02,L/count-.65)
                bot=low+.66;top=high-.55
                if level==0 and ei==entry_edge and abs(s-entry_s)<(w/2+1):continue
                holes.append((s-w/2,s+w/2,bot,top,False,bi))
            if level==0 and ei==entry_edge:
                w=float(entry.get('clear_width_m',1.3))+.16
                s=entry_s
                if not w/2<s<L-w/2:raise ValueError('Retained entry outside edge')
                holes=[h for h in holes if h[1]<s-w/2-.2 or h[0]>s+w/2+.2]
                holes.append((s-w/2,s+w/2,0,min(2.7,split-.3),True,-1))
            for interface in shared:
                if interface['edge']==ei:
                    lo,hi=interface['height_interval']
                    coords=interface['polyline'];pp=[(q[0]-a[0])*u[0]+(q[1]-a[1])*u[1] for q in coords];sl,sr=min(pp),max(pp)
                    holes=[h for h in holes if h[4] or h[1]<=sl or h[0]>=sr or z0+h[3]<=lo or z0+h[2]>=hi]
            cuts=sorted({0.,L,*[q for h in holes for q in h[:2]]})
            for l,r in zip(cuts,cuts[1:]):
                hole=next((h for h in holes if h[0]-1e-7<=(l+r)/2<=h[1]+1e-7),None)
                if hole:
                    panel('pierced masonry','masonry',l,r,low,hole[2]);panel('pierced masonry','masonry',l,r,hole[3],high)
                else:panel('pierced masonry','masonry',l,r,low,high)
            for l,r,bot,top,door,bi in holes:
                s=(l+r)/2
                # Rails and jambs meet at endpoints, never overlay front faces.
                if door:
                    panel('recessed door','door',l+.07,r-.07,bot,top-.44,-.30,.055)
                else:panel('recessed glazing','glass',l+.07,r-.07,bot+.07,top-.07,-.30,.055)
                for xx in [l+.035,r-.035]:panel('frame jambs','trim',xx-.035,xx+.035,bot+(0 if door else .07),top-.07,-.22,.09)
                panel('frame head','trim',l,r,top-.07,top,-.22,.09)
                if not door:panel('frame sill rail','trim',l,r,bot,bot+.07,-.22,.09)
                panel('lintels','trim',l-.11,r+.11,top+.03,top+.18,.015,.11)
                if not door:
                    panel('projecting sills','trim',l-.09,r+.09,bot-.11,bot-.035,.035,.21)
                    # Narrow sash windows: horizontal meeting rail only below;
                    # short upper glazing bar ends at that rail, never overlays it.
                    mid=bot+(top-bot)*(.62 if level==0 else .50)
                    panel('sash meeting rail','trim',l+.07,r-.07,mid-.027,mid+.027,-.22,.09)
                    if level==1:
                        panel('upper sash vertical bar','trim',s-.022,s+.022,mid+.027,top-.07,-.22,.09)
                else:
                    panel('door transom','trim',l+.07,r-.07,top-.44,top-.37,-.22,.09)
                    panel('door glass fanlight','glass',l+.07,r-.07,top-.37,top-.07,-.30,.055)
                    panel('threshold','trim',l-.10,r+.10,-.006,0,-.22,.44)
                    block('door handle','metal',at(r-.2,-.20,1.1),(.025,.055,.24),u,n)
                    entrance={'threshold_xyz':list(at(s,0,0)),'outward_normal':[n[0],n[1],0],'clear_width_m':r-l-.16,'door_leaf_xyz':list(at(s,-.30,(top+bot)/2)),'stair_treads':[],'ramp':'none; supporting ground retained by coordinator','surface_owner':'coordinator','basis':'retained baseline entry projected to mapped wall; aperture artistic'}
                openings.append({'edge':ei,'floor':level,'bay':bi,'type':'door' if door else 'window','width_m':r-l,'height_m':top-bot,'recess_m':.30,'basis':'OSM house with individual street-context window layout; artistic proportions'})
        if ei==2:
            panel('plain first floor stringcourse','trim',.08,L-.08,split-.09,split+.035,.025,.09)
            for j in range(11):
                ss=.18+j*(L-.36)/10
                panel('small brick eaves dentils','trim',ss-.045,ss+.045,H-.20,H-.10,.04,.12)
            # Shallow horizontal masonry joints are authored only between
            # openings by the actual pierced wall; do not place slabs over doors.
            for ss in [.17,L-.17]:
                panel('corner brick piers','masonry',ss-.09,ss+.09,0,H-.12,.012,.055)
        if ei in (1,2,4):
            panel('front rear eaves','trim',.04,L-.04,H-.10,H-.025,.035,.12)
    def offset(d):
        out=[]
        for i,p in enumerate(ring):
            a=ring[i-1];b=ring[(i+1)%len(ring)];la=math.dist(a,p);lb=math.dist(p,b)
            na=((p[1]-a[1])/la,-(p[0]-a[0])/la);nb=((b[1]-p[1])/lb,-(b[0]-p[0])/lb)
            k=d/(1+na[0]*nb[0]+na[1]*nb[1]);out.append((p[0]+k*(na[0]+nb[0]),p[1]+k*(na[1]+nb[1])))
        return out
    def band(group,mat,lo,hi,d,t):
        inner=offset(d-t/2);outer=offset(d+t/2);N=len(ring)
        vs=[(x,y,z0+z) for z in (lo,hi) for rr in (inner,outer) for x,y in rr];fs=[]
        for i in range(N):
            j=(i+1)%N;fs.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
        meshpart(group,mat,vs,fs)
    # Continuous inward mitred rim has no duplicated per-edge caps. It is
    # wholly inside mapped plan, including the near-collinear fifth corner.
    band('inward parapet','trim',H-.10,H+.24,-.15,.24)
    def cap(rr,z,name):
        original=[(x,y,z0+z) for x,y in rr]
        vv=[Vector(q) for q in original]
        lookup={tuple(v):i for i,v in enumerate(vv)}
        faces=[]
        for tri in tessellate_polygon([vv]):
            ids=tuple(v if isinstance(v,int) else lookup[tuple(v)] for v in tri)
            faces.append(ids)
        meshpart(name,'roof',original,faces)
    # The full plan cap is independent of the inner visible membrane. Different
    # elevations avoid a coplanar overlap while retaining every original corner.
    cap(ring,H-.025,'full polygon roof basecap')
    cap(offset(-.255),H+.04,'estimated flat roof membrane')
    created=[]
    for (g,m),(vs,fs) in groups.items():
        if not fs:continue
        used=sorted({i for face in fs for i in face}); remap={j:i for i,j in enumerate(used)}; vs=[vs[i] for i in used]; fs=[tuple(remap[i] for i in face) for face in fs]
        name='8 Queens Gate Place Mews | '+g;mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update()
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
        ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;ob['evidence_status']='Mapped footprint; OSM house and two levels; nearby licensed street context; exact facade unverified';created.append(ob.name)
    return {'created':created,'parameters':{'height_m':H,'base_z':z0,'levels':levels,'opening_count':len(openings),'wall_thickness_m':.36,'roof_max_z':z0+H+.24},'interfaces':{'entrance':entrance,'additional_entrances':[],'additional_supports':[],'shared_walls':shared,'shared_wall_policy':'Every normalized common-height segment retained blind; full footprint preserved'},'openings':openings, 'evidence_source_ids':['osm-810633522','mews2010'],'uncertainty':['OSM identifies no8 as house, not neighbouring no14 motor showroom; exact present use not independently confirmed','No licensed photo securely identifies no8; pale masonry, narrow sash windows and modest dentils are street-context artistic completion','OSM two levels and original estimated eaves retained; no evidence justifies adding other houses dormer storeys','Complete original five-corner plan and estimated flat membrane/inward parapet retained; rear windows and roof are unmeasured artistic details','All normalized shared-wall segments retained blind; only original offset east rear door interface, no invented garage entrance','Source ground-.05 and original threshold retained; coordinator owns finite support']}
