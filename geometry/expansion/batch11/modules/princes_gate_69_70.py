"""69–70 Princes Gate: full mapped ring; individually completed terraced mews exterior.
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
    materials=dict(materials);materials['masonry']=materials['trim']  # text-confirmed stucco
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
        count=6 if ei==0 else max(1,int(L/4.3)) if L>2.5 else 0
        centers=[(i+.5)*L/count for i in range(count)] if count else []
        entry_s=((ep[0]-a[0])*u[0]+(ep[1]-a[1])*u[1]) if ep and ei==entry_edge else L*.5
        for level,(low,high) in enumerate(zip(floor_bounds,floor_bounds[1:])):
            holes=[]
            for bi,s in enumerate(centers):
                w=min((1.30 if level in (1,2) else 1.08) if ei==0 else 1.08,L/count-.8)
                bot=low+(.30 if ei==0 and level==1 else .60);top=high-(.40 if level in (1,2) else .58)
                if level==0 and ei==entry_edge and abs(s-entry_s)<(w/2+1):continue
                holes.append((s-w/2,s+w/2,bot,top,False,bi))
            if level==0 and ei==entry_edge:
                w=float(entry.get('clear_width_m',1.3))+.16
                s=max(w/2+.18,min(L-w/2-.18,entry_s))
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
                openings.append({'edge':ei,'floor':level,'bay':bi,'type':'door' if door else 'window','width_m':r-l,'height_m':top-bot,'recess_m':.30,'basis':'official text-led pair of houses, individual details artistic'})
        if ei==0:
            # Each of the two historic houses has three bays, not six identical
            # unrelated units. Simplified capitals/balustrades are text-led.
            for zz in [split,2*split,4*split,H-.35]:panel('front cornice','trim',.03,L-.03,zz-.08,zz+.09,.09,.22)
            for ss in [.2,L/2,L-.2]:
                panel('paired house pilasters','trim',ss-.10,ss+.10,split+.1,2*split-.15,.06,.16)
                panel('simplified Corinthian capital','trim',ss-.20,ss+.20,2*split-.28,2*split-.07,.12,.28)
                for dx in [-.15,.15]:block('capital volutes','trim',at(ss+dx,.18,2*split-.22),(.08,.13,.08),u,n)
            # Ground channelling divided into solid piers: never cross any opening.
            for zz in [.25,.65,1.05,1.45,1.85,2.25,2.65]:
                for j in range(7):
                    l=.03 if j==0 else centers[j-1]+.63;r=L-.03 if j==6 else centers[j]-.63
                    if r>l:panel('rustication courses','trim',l,r,zz,zz+.025,.012,.025)
            panel('first balcony deck','trim',.15,L-.15,split-.18,split-.045,.37,.78)
            panel('first balcony rail','trim',.15,L-.15,split+.84,split+.97,.70,.15)
            for j in range(45):
                ss=.22+j*(L-.44)/44
                # Bottle outline as a small surface of revolution, not flat alpha texture.
                profile=[(0,.065),(.08,.08),(.16,.04),(.35,.085),(.57,.05),(.70,.04),(.80,.065)]
                vs=[]
                for zz,rad in profile:
                    for k in range(12):
                        aa=2*math.pi*k/12;vs.append(at(ss+rad*math.cos(aa),.70+rad*math.sin(aa),split+zz))
                fs=[tuple(range(11,-1,-1)),tuple(range((len(profile)-1)*12,len(profile)*12))]
                for t in range(len(profile)-1):
                    for k in range(12):fs.append((t*12+k,t*12+(k+1)%12,(t+1)*12+(k+1)%12,(t+1)*12+k))
                meshpart('turned balcony balusters','trim',vs,fs)
            for bi,ss in enumerate(centers):
                # Small individual balconies on second floor, separate from first-floor run.
                panel('second balcony deck','trim',ss-.70,ss+.70,2*split+.45,2*split+.55,.23,.50)
                panel('second balcony rail','trim',ss-.70,ss+.70,2*split+1.20,2*split+1.30,.44,.12)
                for j in range(7):block('second balcony balusters','trim',at(ss-.60+j*.20,.44,2*split+.88),(.055,.055,.70),u,n)
                if bi in (1,4):
                    zz=3*split-.25
                    vs=[at(ss-1.,.02,zz),at(ss+1.,.02,zz),at(ss,.02,zz+.55),at(ss-1.,.20,zz),at(ss+1.,.20,zz),at(ss,.20,zz+.55)]
                    meshpart('central window pediments','trim',vs,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)])
            for j in range(30):
                ss=.20+j*(L-.40)/29;block('eaves brackets','trim',at(ss,.16,H-.23),(.10,.30,.30),u,n)
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
    band('low parapet','masonry',H,H+.26,-.14,.28)
    band('mitred coping','trim',H+.26,H+.34,-.21,.36)
    # Official CAA describes later mansards in this group. Profile dimensions
    # and hidden rear slopes are artistic; exact mapped concavity is retained.
    def cap(rr,z,name):
        vv=[Vector((x,y,z0+z)) for x,y in rr];vs=[];fs=[]
        for tri in tessellate_polygon([vv]):
            off=len(vs);vs.extend(tuple(vv[v] if isinstance(v,int) else v) for v in tri);fs.append((off,off+1,off+2))
        meshpart(name,'roof',vs,fs)
    cap(ring,H,'full polygon roof basecap')
    lower=offset(-.30);upper=offset(-1.20)
    for i in range(len(ring)):
        j=(i+1)%len(ring)
        meshpart('mansard slopes','roof',[(lower[i][0],lower[i][1],z0+H+.15),(lower[j][0],lower[j][1],z0+H+.15),(upper[j][0],upper[j][1],z0+H+1.80),(upper[i][0],upper[i][1],z0+H+1.80)],[(0,1,2,3)])
    cap(upper,H+1.80,'mansard top deck')
    created=[]
    for (g,m),(vs,fs) in groups.items():
        if not fs:continue
        name='69–70 Princes Gate | '+g;mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update()
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
        ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;ob['evidence_status']='Mapped footprint; OSM five levels and official grouped stucco facade; individual proportions estimated';created.append(ob.name)
    return {'created':created,'parameters':{'height_m':H,'base_z':z0,'levels':levels,'opening_count':len(openings),'wall_thickness_m':.36,'roof_max_z':z0+H+1.80},'interfaces':{'entrance':entrance,'additional_entrances':[],'additional_supports':[],'shared_walls':shared,'shared_wall_policy':'All mapped boundary walls retained; no unverified party-wall deletions'},'openings':openings,'evidence_source_ids':['osm-851362854','he-1266085','rbkc-caa-3.32','rbkc-2018-69-70','mews-context2015'],'uncertainty':['No exact-building permitted front photo found; official HE1266085 and RBKC text describe grouped facade; precise proportions artistically completed','69–70 source address supported by official planning text; no historic separate front entrance positions asserted; inherited east rear door retained','Later mansard existence is group-text supported, but 1.8m rise/slopes and rear are artistic; source eaves retained; no dormer or roof plant position claimed','All normalized shared segments processed including disjoint71–72 common walls; neighbouring baseline heights remain estimated']}
