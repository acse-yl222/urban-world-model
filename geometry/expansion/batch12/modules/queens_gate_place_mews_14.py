"""14 Queens Gate Place Mews: full mapped ring; Fiskens showroom identity; individually estimated exterior.
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
    materials=dict(materials)
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
        count=3 if ei==entry_edge else 2 if ei==3 else 0
        centers=[(i+.5)*L/count for i in range(count)] if count else []
        entry_s=((ep[0]-a[0])*u[0]+(ep[1]-a[1])*u[1]) if ep and ei==entry_edge else L*.5
        for level,(low,high) in enumerate(zip(floor_bounds,floor_bounds[1:])):
            holes=[]
            for bi,s in enumerate(centers):
                w=min(1.10,L/count-.7)
                bot=low+.66;top=high-.55
                if level==0 and ei==entry_edge and abs(s-entry_s)<(w/2+1):continue
                holes.append((s-w/2,s+w/2,bot,top,False,bi))
            if level==0 and ei==entry_edge:
                # Fixed display glazing flanks the retained pedestrian leaf.
                # No unobserved vehicle doorway is advertised as an entrance.
                ew=float(entry['clear_width_m'])+.16
                holes=[]
                for bi,(ll,rr) in enumerate([(.35,entry_s-ew/2-.24),(entry_s+ew/2+.24,L-.35)]):
                    if rr-ll>.45: holes.append((ll,rr,.16,2.78,False,bi))
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
                panel('recessed door' if door else 'recessed glazing','glass',l+.07,r-.07,bot+(0 if door else .07),top-.07,-.30,.055)
                for xx in [l+.035,r-.035]:panel('painted joinery','metal',xx-.035,xx+.035,bot,top,-.22,.09)
                for zz in ([top-.035] if door else [bot+.035,top-.035]):panel('painted joinery','metal',l,r,zz-.035,zz+.035,-.22,.09)
                panel('lintels','trim',l-.11,r+.11,top+.03,top+.18,.015,.11)
                if not door:
                    panel('projecting sills','trim',l-.09,r+.09,bot-.11,bot-.035,.035,.21)
                    for xx in ([s-(r-l)/6,s+(r-l)/6] if level==0 else [s]):panel('window mullions','metal',xx-.023,xx+.023,bot,top,-.21,.07)
                    panel('window transoms','metal',l,r,top-.60,top-.55,-.21,.07)
                    # Upper sash has a finer six-light pattern, not a repeated studio grille.
                    if level>0:
                        panel('upper sash meeting rail','metal',l,r,(bot+top)/2-.026,(bot+top)/2+.026,-.19,.055)
                else:
                    panel('door transom','trim',l,r,top-.44,top-.37,-.20,.07)
                    panel('door glass fanlight','glass',l+.08,r-.08,top-.36,top-.08,-.27,.035)
                    panel('threshold','trim',l-.10,r+.10,-.006,0,-.22,.44)
                    block('door handle','metal',at(r-.2,-.20,1.1),(.025,.055,.24),u,n)
                    entrance={'threshold_xyz':list(at(s,0,0)),'outward_normal':[n[0],n[1],0],'clear_width_m':r-l-.16,'door_leaf_xyz':list(at(s,-.30,(top+bot)/2)),'stair_treads':[],'ramp':'none; supporting ground retained by coordinator','surface_owner':'coordinator','basis':'retained baseline entry projected to mapped wall; aperture artistic'}
                openings.append({'edge':ei,'floor':level,'bay':bi,'type':'door' if door else 'window','width_m':r-l,'height_m':top-bot,'recess_m':.30,'basis':'Fiskens showroom identity confirmed by official text; opening proportions artistic'})
        if ei==entry_edge:
            panel('blank showroom fascia','metal',.16,L-.16,2.96,3.20,.045,.10)
            panel('shallow shop cornice','trim',.11,L-.11,3.20,3.30,.07,.14)
            for ss in [.20,L-.20]:panel('showroom end piers','masonry',ss-.12,ss+.12,0,H-.16,-.025,.15)
        if ei in (entry_edge,3):
            panel('front rear eaves','trim',.04,L-.04,H-.18,H,.025,.12)
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
    band('inward eaves','trim',H-.12,H+.03,-.16,.25)
    def cap(rr,z,name):
        vv=[Vector((x,y,z0+z)) for x,y in rr];vs=[];fs=[]
        for tri in tessellate_polygon([vv]):
            off=len(vs);vs.extend(tuple(vv[v] if isinstance(v,int) else v) for v in tri);fs.append((off,off+1,off+2))
        meshpart(name,'roof',vs,fs)
    cap(ring,H+.008,'full polygon roof basecap')
    # Modest hipped roof entirely inside plan; no dormer inferred from other houses.
    rr=offset(-.12);r0=((rr[0][0]+rr[3][0])/2,(rr[0][1]+rr[3][1])/2);r1=((rr[1][0]+rr[2][0])/2,(rr[1][1]+rr[2][1])/2)
    dx,dy=r1[0]-r0[0],r1[1]-r0[1];ll=math.hypot(dx,dy);inset=1.2
    r0=(r0[0]+dx/ll*inset,r0[1]+dy/ll*inset);r1=(r1[0]-dx/ll*inset,r1[1]-dy/ll*inset)
    vs=[(x,y,z0+H+.03) for x,y in rr]+[(r0[0],r0[1],z0+H+1.0),(r1[0],r1[1],z0+H+1.0)]
    meshpart('estimated hipped roof','roof',vs,[(0,1,5,4),(1,2,5),(2,3,4,5),(3,0,4)])
    created=[]
    for (g,m),(vs,fs) in groups.items():
        if not fs:continue
        name='14 Queens Gate Place Mews | '+g;mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update()
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
        ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;ob['evidence_status']='Mapped footprint; OSM two levels; official showroom identity; facade artistic';created.append(ob.name)
    return {'created':created,'parameters':{'height_m':H,'base_z':z0,'levels':levels,'opening_count':len(openings),'wall_thickness_m':.36,'roof_max_z':z0+H+1.0},'interfaces':{'entrance':entrance,'additional_entrances':[],'additional_supports':[],'shared_walls':shared,'shared_wall_policy':'Every normalized common-height segment retained blind; full footprint preserved'},'openings':openings,'evidence_source_ids':['osm-810633525','fiskens-about','fiskens-gregor','mews2010','bentley-context2024'],'uncertainty':['Fiskens identity at 14 confirmed by official text; no exact target facade identified in licensed photos','Dark glazed showroom frontage with retained central pedestrian leaf is artistic, not observed door arrangement; no extra entrance asserted','OSM two levels and original estimated eaves preserved; upper windows, hipped roof rise1m and hidden rear are estimated','Licensed images support street context only; neighbouring garage doors and street arch are not identified as this building','Source ground remains -.05; coordinator owns finite entry support; no building datum altered']}
