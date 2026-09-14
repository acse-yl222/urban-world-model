"""26 Princes Gate: full mapped ring, context-informed townhouse and estimated attic.
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
    else: entry_edge=5
    def meshpart(group,mat,vs,fs):
        v,f=groups.setdefault((group,mat),([],[]));off=len(v);v.extend(vs);f.extend(tuple(off+i for i in face) for face in fs)
    def block(group,mat,center,size,u=(1.,0.),n=(0.,1.)):
        if min(size)<=1e-7:return
        x,y,z=center;w,d,h=[s/2 for s in size]
        vs=[(x+a*w*u[0]+b*d*n[0],y+a*w*u[1]+b*d*n[1],z+c*h) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        meshpart(group,mat,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    def curved_head(at,l,r,top,rise,group='curved window',front=0.,back=-.36):
        # Exact matching twenty-segment curve; crown duplicates removed before
        # triangulation so endpoints cannot produce zero-area cap faces.
        N=20;s=(l+r)/2;rad=(r-l)/2;spring=top-rise
        curve=[(s-rad*math.cos(math.pi*j/N),spring+rise*math.sin(math.pi*j/N)) for j in range(N+1)]
        for j in range(N):
            pts=[curve[j],curve[j+1],(curve[j+1][0],top),(curve[j][0],top)]
            clean=[]
            for q in pts:
                if not clean or math.dist(q,clean[-1])>1e-8:clean.append(q)
            if len(clean)>1 and math.dist(clean[0],clean[-1])<1e-8:clean.pop()
            if len(clean)<3:continue
            M=len(clean);vs=[at(x,d,z) for d in (back,front) for x,z in clean]
            fs=[]
            for k in range(1,M-1):fs.extend([(0,k+1,k),(M,M+k,M+k+1)])
            fs.extend((k,(k+1)%M,(k+1)%M+M,k+M) for k in range(M))
            meshpart(group+' solid spandrels','masonry',vs,fs)
            aa=math.pi*j/N;bb=math.pi*(j+1)/N
            inner=[(s-(rad-.07)*math.cos(t),spring+(rise-.07)*math.sin(t)) for t in (aa,bb)]
            outline=[curve[j],curve[j+1],inner[1],inner[0]]
            vs=[at(x,d,z) for d in (-.25,-.16) for x,z in outline]
            meshpart(group+' curved trim','trim',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
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
        count=3 if ei==5 else max(1,int(L/4.3)) if L>2.5 else 0
        centers=[(i+.5)*L/count for i in range(count)] if count else []
        entry_s=((ep[0]-a[0])*u[0]+(ep[1]-a[1])*u[1]) if ep and ei==entry_edge else L*.5
        for level,(low,high) in enumerate(zip(floor_bounds,floor_bounds[1:])):
            holes=[]
            for bi,s in enumerate(centers):
                w=min((2.15 if level in (1,2) else 1.85) if ei==5 else 1.08,L/count-.8)
                bot=low+(.30 if ei==5 and level==1 else .60);top=high-(.40 if level in (1,2) else .58)
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
                if not door and ei==5 and level in (2,3):curved_head(at,l,r,top,(r-l)/2 if level==2 else .30)
                openings.append({'edge':ei,'floor':level,'bay':bi,'type':'door' if door else 'window','width_m':r-l,'height_m':top-bot,'recess_m':.30,'basis':'HE1227201 grouped opening types, target metric arrangement estimated'})
        if ei==5:
            # Group-text-supported Doric porch; exact dimensions estimated.
            for ss in (entry_s-1.04,entry_s+1.04):
                block('Doric porch square foot','trim',at(ss,.70,.05),(.44,.44,.10),u,n)
                vs=[];N=20
                for zz,rad in [(.10,.19),(.20,.17),(2.53,.145),(2.63,.20)]:
                    for k in range(N):
                        ang=2*math.pi*k/N;vs.append(at(ss+rad*math.cos(ang),.70+rad*math.sin(ang),zz))
                fs=[tuple(range(N-1,-1,-1)),tuple(range(3*N,4*N))]
                for j in range(3):
                    for k in range(N):fs.append((j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k))
                meshpart('Doric porch shafts','trim',vs,fs)
                block('Doric porch abacus','trim',at(ss,.70,2.68),(.43,.43,.10),u,n)
            panel('Doric porch entablature','trim',entry_s-1.34,entry_s+1.34,2.73,2.94,.40,1.15)
            if entrance:entrance['additional_supports']=[{'polygon_xy':[list(at(entry_s+x,d,0)[:2]) for x,d in [(-1.40,-.12),(1.40,-.12),(1.40,1.12),(-1.40,1.12)]],'top_z':z0,'basis':'Estimated Doric porch column support; finite ground authored by coordinator'}]
            # Three-bay composition informed by nearby numbered terraces. All
            # target spacing and simplified decoration remain artistic.
            for zz in [split,2*split,4*split,H-.25]:panel('front cornice','trim',.10,L-.10,zz-.07,zz+.08,.08,.20)
            for ss in [.18,L-.18]:
                panel('outer shallow pilasters','trim',ss-.09,ss+.09,split+.06,2*split-.10,.045,.12)
            for bi,ss in enumerate(centers):
                if bi in (0,1,2):
                    for xx in (ss-1.24,ss+1.24):
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
                    panel('Juliet sill decks','trim',ss-1.15,ss+1.15,bot-.13,bot-.04,.19,.43)
                    panel('Juliet top rails','metal',ss-1.15,ss+1.15,bot+.71,bot+.75,.33,.045)
                    for k in range(9):block('Juliet vertical bars','metal',at(ss-1.05+k*.2625,.33,bot+.33),(.026,.03,.72),u,n)
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
    # HE1227201 supports four main storeys plus attic; roof profile is not visible.
    # A complete mapped base cap underlies a street-wall-aligned, editable 2.0m attic.
    def cap(rr,z,name):
        vv=[Vector((x,y,z0+z)) for x,y in rr];vs=[];fs=[]
        for tri in tessellate_polygon([vv]):
            off=len(vs);vs.extend(tuple(vv[v] if isinstance(v,int) else v) for v in tri);fs.append((off,off+1,off+2))
        meshpart(name,'roof',vs,fs)
    # 8mm above main wall top; distinct from eaves top H+.020.
    cap(ring,H+.008,'full mapped roof base cap')
    attic=list(ring);AH=2.00
    for ei,(a,b) in enumerate(zip(attic,attic[1:]+attic[:1])):
        L=math.dist(a,b);u=((b[0]-a[0])/L,(b[1]-a[1])/L);n=(u[1],-u[0])
        def ap(l,r,lo,hi,d=-.11,t=.22,mat='masonry',group='flush attic solid walls'):
            block(group,mat,(a[0]+u[0]*(l+r)/2+n[0]*d,a[1]+u[1]*(l+r)/2+n[1]*d,z0+H+(lo+hi)/2),(r-l,t,hi-lo),u,n)
        holes=[(L*(j+.5)/3-.65,L*(j+.5)/3+.65) for j in range(3)] if ei==5 else []
        cuts=sorted({0,L,*[v for h in holes for v in h]})
        for l,r in zip(cuts,cuts[1:]):
            if any(hl<(l+r)/2<hr for hl,hr in holes):ap(l,r,0,.40);ap(l,r,1.48,AH)
            else:ap(l,r,0,AH)
        for l,r in holes:
            def attic_at(x,d,z):return (a[0]+u[0]*x+n[0]*d,a[1]+u[1]*x+n[1]*d,z0+H+z)
            curved_head(attic_at,l,r,1.48,(r-l)/2,'attic round head',0.,-.22)
            ap(l+.055,r-.055,.45,1.43,-.15,.045,'glass','recessed attic glazing')
            for x in (l+.026,r-.026):ap(x-.026,x+.026,.40,1.48,-.08,.08,'trim','attic frame jambs')
            for z in (.425,1.455):ap(l,r,z-.025,z+.025,-.08,.08,'trim','attic frame rails')
    # One mitred solid ring shares exact corner vertices: edge blocks would
    # overlap on coplanar top faces at corners. Avoid wall-face coplanarity with 5mm
    # 5mm vertical embed; outer rim sits 5mm inside mapped footprint.
    band('attic continuous mitred top rim','roof',H+AH-.005,H+AH+.10,-.125,.24)
    # The deck intersects the closed rim sides 25mm above their bottom,
    # leaving 75mm upstand; no coincident cap/rim top faces.
    cap(offset(-.005),H+AH+.025,'complete attic flat roof')
    created=[]
    for (g,m),(vs,fs) in groups.items():
        if not fs:continue
        name='26 Princes Gate | '+g;mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update()
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
        ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;ob['evidence_status']='Mapped footprint, HE four main levels plus attic; metric detail and image-to-parcel assignment estimated';created.append(ob.name)
    return {'created':created,'parameters':{'height_m':H,'base_z':z0,'levels':levels,'opening_count':len(openings),'wall_thickness_m':.36,'roof_max_z':z0+H+2.10,'eaves_height_m':H,'roof_levels':1,'attic_height_m':2.00,'attic_inset_m':0.0,'attic_floor_z':z0+H,'attic_wall_top_z':z0+H+2.00},'interfaces':{'entrance':entrance,'additional_entrances':[],'additional_supports':entrance.get('additional_supports',[]) if entrance else [],'shared_walls':shared,'attic_shared_wall_policy':{'blind_edges':[0,2,3,4],'target_height_interval':[z0+H,z0+H+2.0],'basis':'Conservative full attic-side opacity against27 and25; does not reinterpret old clipped common heights as measurement','openings':[]},'shared_wall_policy':'All mapped boundary walls retained; no unverified party-wall deletions'},'openings':openings,'evidence_source_ids':['osm-640097054','he-1227201','street4203106','street2113153'],'uncertainty':['HE1227201 describes26-31 as four main storeys plus attic and basement; source four-level height estimate agrees with main-storey count but is not measured','Exact26 facade not securely isolated in licensed streetscape views; three-bay grouping and varied arch heads follow official group text, metric widths and ornament artistic','Full six-point concave footprint retained; all five normalized shared segments tested, including three disconnected sides of25','Two-metre street-wall-aligned attic and flat roof are artistic geometry; roof profile is not visible in HE description, no plant or mapped basement inferred','Original source threshold/tangent preserved; finite ground approach belongs to coordinator','Same official listing newly creates a4+attic versus OSM5+roof conflict for delivered27; no batch12 geometry or completion status changed']}
