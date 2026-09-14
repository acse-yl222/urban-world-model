"""27 Princes Gate: full mapped ring, context-informed townhouse and estimated attic.
No downloaded textures; no global scene mutation. Image-led context is CC BY-SA.
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
    materials=dict(materials);materials['masonry']=materials['trim']  # pale stucco from inspected streetscape context, not target identification
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
        shared.append({**seg,'policy':'Retain full wall; null neighbour height conservatively suppresses all target-wall apertures without claiming neighbour measurement'})
    if not shared:raise ValueError('Expected normalized shared-wall segments for this target')
    split=H/levels
    floor_bounds=[i*H/levels for i in range(levels+1)]
    for ei,(a,b,L,u,n) in enumerate(edges):
        def at(s,d,z):return (a[0]+u[0]*s+n[0]*d,a[1]+u[1]*s+n[1]*d,z0+z)
        def panel(g,m,l,r,lo,hi,d=-.18,t=.36):block(g,m,at((l+r)/2,d,(lo+hi)/2),(r-l,t,hi-lo),u,n)
        # Long street wall gets differentiated workshop bays; short return faces remain complete.
        count=3 if ei==4 else max(1,int(L/4.3)) if L>2.5 else 0
        centers=[(i+.5)*L/count for i in range(count)] if count else []
        entry_s=((ep[0]-a[0])*u[0]+(ep[1]-a[1])*u[1]) if ep and ei==entry_edge else L*.5
        for level,(low,high) in enumerate(zip(floor_bounds,floor_bounds[1:])):
            holes=[]
            for bi,s in enumerate(centers):
                w=min((1.30 if level in (1,2) else 1.08) if ei==4 else 1.08,L/count-.8)
                bot=low+(.30 if ei==4 and level==1 else .60);top=high-(.40 if level in (1,2) else .58)
                if level==0 and ei==entry_edge and abs(s-entry_s)<(w/2+1):continue
                holes.append((s-w/2,s+w/2,bot,top,False,bi))
            if level==0 and ei==entry_edge:
                w=float(entry.get('clear_width_m',1.3))+.16
                s=entry_s
                if not w/2<s<L-w/2:raise ValueError('Entry aperture outside mapped edge')
                holes=[h for h in holes if h[1]<s-w/2-.2 or h[0]>s+w/2+.2]
                holes.append((s-w/2,s+w/2,0,min(2.7,split-.3),True,-1))
            for interface in shared:
                if interface['edge']==ei:
                    lo,hi=interface.get('height_interval') or (z0,z0+H)
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
                panel('recessed door' if door else 'recessed glazing','door' if door else 'glass',l+.07,r-.07,bot+(0 if door else .07),top-.07,-.30,.055)
                for xx in [l+.035,r-.035]:panel('painted joinery','trim',xx-.035,xx+.035,bot,top,-.22,.09)
                for zz in ([top-.035] if door else [bot+.035,top-.035]):panel('painted joinery','trim',l,r,zz-.035,zz+.035,-.22,.09)
                panel('lintels','trim',l-.11,r+.11,top+.03,top+.18,.015,.11)
                if not door:
                    panel('projecting sills','trim',l-.09,r+.09,bot-.11,bot-.035,.035,.21)
                    for xx in ([s-(r-l)/6,s+(r-l)/6] if level==0 else [s]):panel('window mullions','trim',xx-.023,xx+.023,bot,top,-.21,.07)
                    panel('window transoms','trim',l,r,top-.60,top-.55,-.21,.07)
                    # Upper sash has a finer six-light pattern, not a repeated studio grille.
                    if level>0:
                        panel('upper sash meeting rail','trim',l,r,(bot+top)/2-.026,(bot+top)/2+.026,-.19,.055)
                else:
                    panel('door transom','trim',l,r,top-.44,top-.37,-.20,.07)
                    panel('door glass fanlight','glass',l+.08,r-.08,top-.36,top-.08,-.27,.035)
                    panel('threshold','trim',l-.10,r+.10,-.006,0,-.22,.44)
                    block('door handle','metal',at(r-.2,-.20,1.1),(.025,.055,.24),u,n)
                    entrance={'threshold_xyz':list(at(s,0,0)),'outward_normal':[n[0],n[1],0],'clear_width_m':r-l-.16,'door_leaf_xyz':list(at(s,-.30,(top+bot)/2)),'stair_treads':[],'ramp':'none; supporting ground retained by coordinator','surface_owner':'coordinator','basis':'retained baseline entry projected to mapped wall; aperture artistic'}
                openings.append({'edge':ei,'floor':level,'bay':bi,'type':'door' if door else 'window','width_m':r-l,'height_m':top-bot,'recess_m':.30,'basis':'licensed nearby terrace context; target detail artistic'})
        if ei==4:
            # Three-bay composition informed by nearby numbered terraces. All
            # target spacing and simplified decoration remain artistic.
            for zz in [split,2*split,4*split,H-.25]:panel('front cornice','trim',.10,L-.10,zz-.07,zz+.08,.08,.20)
            for ss in [.18,L-.18]:
                panel('outer shallow pilasters','trim',ss-.09,ss+.09,split+.06,2*split-.10,.045,.12)
            for bi,ss in enumerate(centers):
                if bi in (0,1,2):
                    for xx in (ss-.83,ss+.83):
                        panel('first floor pilaster shafts','trim',xx-.055,xx+.055,split+.28,2*split-.28,.05,.15)
                        panel('simplified first floor capitals','trim',xx-.12,xx+.12,2*split-.32,2*split-.16,.07,.19)
                if bi==1:
                    zz=2*split-.10
                    vs=[at(ss-.95,.02,zz),at(ss+.95,.02,zz),at(ss,.02,zz+.36),at(ss-.95,.20,zz),at(ss+.95,.20,zz),at(ss,.20,zz+.36)]
                    meshpart('central first floor pediment','trim',vs,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)])
                # Separate metal Juliet rails, not the neighbouring embassy's
                # continuous ornate stone balcony or double-column porch.
                for level in (1,2):
                    bot=level*split+.60
                    panel('Juliet sill decks','trim',ss-.72,ss+.72,bot-.13,bot-.04,.19,.43)
                    panel('Juliet top rails','metal',ss-.72,ss+.72,bot+.71,bot+.75,.33,.045)
                    for k in range(9):block('Juliet vertical bars','metal',at(ss-.65+k*.1625,.33,bot+.33),(.026,.03,.72),u,n)
            for j in range(17):block('front cornice dentils','trim',at(.22+j*(L-.44)/16,.12,H-.18),(.11,.23,.17),u,n)
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
    band('inward eaves','trim',H-.15,H+.02,-.15,.25)
    band('low parapet','masonry',H-.005,H+.26,-.14,.28)
    band('mitred coping','trim',H+.255,H+.34,-.21,.36)
    # OSM roof:levels=1 supports an attic count, not shape or dimensions.
    # A complete mapped base cap underlies a fully inset, editable 1.8m attic.
    def cap(rr,z,name):
        vv=[Vector((x,y,z0+z)) for x,y in rr];vs=[];fs=[]
        for tri in tessellate_polygon([vv]):
            off=len(vs);vs.extend(tuple(vv[v] if isinstance(v,int) else v) for v in tri);fs.append((off,off+1,off+2))
        meshpart(name,'roof',vs,fs)
    # 8mm above main wall top; distinct from eaves top H+.020.
    cap(ring,H+.008,'full mapped roof base cap')
    attic=offset(-1.05);AH=1.80
    for ei,(a,b) in enumerate(zip(attic,attic[1:]+attic[:1])):
        L=math.dist(a,b);u=((b[0]-a[0])/L,(b[1]-a[1])/L);n=(u[1],-u[0])
        def ap(l,r,lo,hi,d=-.11,t=.22,mat='roof',group='inset attic solid walls'):
            block(group,mat,(a[0]+u[0]*(l+r)/2+n[0]*d,a[1]+u[1]*(l+r)/2+n[1]*d,z0+H+(lo+hi)/2),(r-l,t,hi-lo),u,n)
        holes=[(L*(j+.5)/3-.38,L*(j+.5)/3+.38) for j in range(3)] if ei==4 else []
        cuts=sorted({0,L,*[v for h in holes for v in h]})
        for l,r in zip(cuts,cuts[1:]):
            if any(hl<(l+r)/2<hr for hl,hr in holes):ap(l,r,0,.40);ap(l,r,1.48,AH)
            else:ap(l,r,0,AH)
        for l,r in holes:
            ap(l+.055,r-.055,.45,1.43,-.15,.045,'glass','recessed attic glazing')
            for x in (l+.026,r-.026):ap(x-.026,x+.026,.40,1.48,-.08,.08,'trim','attic frame jambs')
            for z in (.425,1.455):ap(l,r,z-.025,z+.025,-.08,.08,'trim','attic frame rails')
    # One mitred solid ring shares exact corner vertices: edge blocks would
    # overlap on coplanar top faces at corners. Cover wall tops with 4mm
    # outer overhang and 5mm vertical embed, keeping all geometry inset.
    band('attic continuous mitred top rim','roof',H+AH-.005,H+AH+.10,-1.160,.228)
    # The deck intersects the closed rim sides 25mm above their bottom,
    # leaving 75mm upstand; no coincident cap/rim top faces.
    cap(attic,H+AH+.025,'complete attic flat roof')
    created=[]
    for (g,m),(vs,fs) in groups.items():
        if not fs:continue
        name='27 Princes Gate | '+g;mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update()
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
        ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;ob['evidence_status']='Mapped five-level townhouse plus OSM attic count; actual exact facade unresolved, licensed-context artistic detail';created.append(ob.name)
    return {'created':created,'parameters':{'height_m':H,'base_z':z0,'levels':levels,'opening_count':len(openings),'wall_thickness_m':.36,'roof_max_z':z0+H+1.90,'eaves_height_m':H,'roof_levels':1,'attic_height_m':1.80,'attic_inset_m':1.05},'interfaces':{'entrance':entrance,'additional_entrances':[],'additional_supports':[],'shared_walls':shared,'shared_wall_policy':'All mapped boundary walls retained; no unverified party-wall deletions'},'openings':openings,'evidence_source_ids':['osm-640097053','context23-25-2017','neighbour28-2024','neighbour28-2025','neighbour28-other','reading-27-history'],'uncertainty':['Exact27 facade is not securely identified; numbered28 photos and23-25 are context, not target architectural measurements','Five main levels and one roof level are OSM tags; original16.3015m eaves retained as procedural estimate','Inset1.8m attic with front windows is artistic roof completion, not photo-observed roof; all5 mapped corners retained under complete roofcap','Three normalized shared segments retained; absent28 source mesh leaves neighbour height null, conservatively opaque full target wall without inventing neighbour dimensions','Original source entry lateral position and threshold preserved; external finite approach belongs to coordinator; no guessed porch, basement excavation or second entrance']}
