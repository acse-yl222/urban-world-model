"""Museum Lane stone link: editable pierced screen and open vaulted passage.
Mapped outline/eaves retained; two unequal visual zones, not four guessed floors.
"""
import math


def build(feature, materials):
    import bpy
    import bmesh
    from mathutils import Vector
    from mathutils.geometry import tessellate_polygon
    ring=[tuple(p[:2]) for p in feature['ring']]
    if ring[0]==ring[-1]:ring.pop()
    z0=float(feature['base_z']);H=float(feature['height_m']);groups={};openings=[]
    # Northward longitudinal coordinate; cross axis points east through the screen.
    v=(.988690728588,.149968807437);u=(-v[1],v[0])
    origin=(877.196788200119,-347.61190987285227)
    def local(p):return ((p[0]-origin[0])*u[0]+(p[1]-origin[1])*u[1],(p[0]-origin[0])*v[0]+(p[1]-origin[1])*v[1])
    rr=[local(p) for p in ring]
    def world(t,d,z):return (origin[0]+u[0]*t+v[0]*d,origin[1]+u[1]*t+v[1]*d,z0+z)
    def part(g,m,vs,fs):
        a,b=groups.setdefault((g,m),([],[]));off=len(a);a.extend(vs);b.extend(tuple(off+i for i in f) for f in fs)
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    def prism(g,m,xy,low,high):
        if not isinstance(low,(list,tuple)):low=[low]*len(xy)
        if not isinstance(high,(list,tuple)):high=[high]*len(xy)
        n=len(xy);vs=[world(t,d,z) for zs in (low,high) for (t,d),z in zip(xy,zs)]
        fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        part(g,m,vs,fs)
    def box(g,m,t,d,z,w,depth,h):
        if min(w,depth,h)<=1e-7:return
        prism(g,m,[(t-w/2,d-depth/2),(t+w/2,d-depth/2),(t+w/2,d+depth/2),(t-w/2,d+depth/2)],z-h/2,z+h/2)
    passage=feature.get('passage_authoring',{})
    pc=passage.get('center_xy',origin);ct=local(pc)[0]
    W=float(passage.get('clear_width_m',4.0));R=W/2;spring=3.15;rise=1.8
    passage_floor_z=float(passage.get('floor_z',.25));pdz=passage_floor_z-z0
    def arch(t):return pdz+spring+rise*math.sqrt(max(0,1-((t-ct)/R)**2))
    def sides(t):
        hits=[]
        for a,b in zip(rr,rr[1:]+rr[:1]):
            if min(a[0],b[0])-1e-8<=t<=max(a[0],b[0])+1e-8 and abs(b[0]-a[0])>1e-8:
                hits.append(a[1]+(b[1]-a[1])*(t-a[0])/(b[0]-a[0]))
        return min(hits),max(hits)
    entry=feature['entry'];ep=entry['center_xy'];entrance=None
    for ei,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
        L=math.dist(a,b);eu=((b[0]-a[0])/L,(b[1]-a[1])/L);normal=(eu[1],-eu[0]);la,lb=rr[ei],rr[(ei+1)%len(rr)]
        def at(s,d,z):return (a[0]+eu[0]*s+normal[0]*d,a[1]+eu[1]*s+normal[1]*d,z0+z)
        def slab(g,m,l,r,lo,hi,d=-.20,th=.4):
            if r-l<1e-7 or hi-lo<1e-7:return
            vs=[at(s,dd,zz) for zz in (lo,hi) for s,dd in [(l,d-th/2),(r,d-th/2),(r,d+th/2),(l,d+th/2)]];part(g,m,vs,faces)
        def s_of(t):return (t-la[0])*L/(lb[0]-la[0])
        holes=[]
        if ei not in (0,3):
            # Image led sparse arrangement: one tall central upper opening and small flanking low lights.
            for t,w,lo,hi in [(ct,1.65,6.2,9.7),(ct-8,.68,3.3,4.6),(ct+8,.68,3.3,4.6),(ct-8,1.25,1.45,2.05),(ct+8,1.25,1.45,2.05)]:
                if max(min(la[0],lb[0]),t-w/2)<min(max(la[0],lb[0]),t+w/2):
                    ss=sorted([s_of(t-w/2),s_of(t+w/2)]);holes.append((max(0,ss[0]),min(L,ss[1]),lo,hi,'window'))
            if ei==entry['edge_index']:
                s=(ep[0]-a[0])*eu[0]+(ep[1]-a[1])*eu[1];w=entry['clear_width_m']+.14
                # Baseline door is the retained interface. Unobserved rear lights
                # conflicting with its full jamb envelope are omitted entirely.
                holes=[h for h in holes if h[1]<s-w/2-.15 or h[0]>s+w/2+.15]
                holes.insert(0,(s-w/2,s+w/2,0,2.65,'door'))
        cuts={0.,L,*[x for h in holes for x in h[:2]]}
        arc_s=[]
        if ei not in (0,3):
            for j in range(49):
                t=ct+R*math.cos(math.pi*j/48)
                s=s_of(t)
                if 0<s<L:cuts.add(s);arc_s.append(s)
        # Passage crown coincides with mapped vertices on edges1/4. Floating
        # projection can place its cut ~1e-12m before L: snap, then coalesce
        # stations instead of emitting an effectively zero-width spandrel.
        snapped=sorted(0. if abs(x)<1e-7 else L if abs(x-L)<1e-7 else x for x in cuts)
        cuts=[]
        for x in snapped:
            if not cuts or x-cuts[-1]>1e-7:cuts.append(x)
        for l,r in zip(cuts,cuts[1:]):
            t=la[0]+(lb[0]-la[0])*(l+r)/(2*L)
            if ei not in (0,3) and abs(t-ct)<R:
                # Variable arch soffit follows each sampled edge, with real empty aperture below.
                ts=[la[0]+(lb[0]-la[0])*s/L for s in (l,r)]
                lo=[arch(ts[0]),arch(ts[1]),arch(ts[1]),arch(ts[0])]
                xy=[at(s,d,0)[:2] for s,d in [(l,-.4),(r,-.4),(r,0),(l,0)]]
                # Higher central window also pierces this strip.
                hole=next((h for h in holes if h[0]<(l+r)/2<h[1]),None)
                top=hole[2] if hole else H
                vs=[(*p,z0+z) for zs in (lo,[top]*4) for p,z in zip(xy,zs)];part('arched masonry','trim',vs,faces)
                if hole:slab('upper pierced stone','trim',l,r,hole[3],H)
            else:
                hole=next((h for h in holes if h[0]<(l+r)/2<h[1]),None)
                if hole:slab('pierced stone','trim',l,r,0,hole[2]);slab('pierced stone','trim',l,r,hole[3],H)
                else:slab('stone walls','trim',l,r,0,H)
        for l,r,lo,hi,kind in holes:
            slab('recessed '+kind,'door' if kind=='door' else 'glass',l+.055,r-.055,lo+(0 if kind=='door' else .055),hi-.055,-.23,.05)
            for s in [l+.025,r-.025]:slab('dark joinery','metal',s-.025,s+.025,lo,hi,-.18,.075)
            for zz in ([hi] if kind=='door' else [lo,hi,(lo+hi)/2]):slab('dark joinery','metal',l,r,zz-.025,zz+.025,-.18,.075)
            if kind=='door':
                entrance={'threshold_xyz':list(at((l+r)/2,0,0)),'outward_normal':[*normal,0],'clear_width_m':entry['clear_width_m'],'door_leaf_xyz':list(at((l+r)/2,-.23,(lo+hi)/2)),'stair_treads':[],'ramp':'none','basis':'retained baseline door, not photographically observed'}
            openings.append({'edge':ei,'type':kind,'width_m':r-l,'height_m':hi-lo,'basis':'photo-led sparse windows; back and original service door artistic'})
        if ei not in (0,3):
            # Rustication joints are shallow courses above door/passage only, never spanning clear throat.
            for zz in [5.5,5.75,H-.8,H-.5,H-.14]:slab('stone cornice','trim',0,L,zz-.07,zz+.07,.035,.08)
    # Full-depth intrados: pairs of facade intersections sampled along elliptical arch.
    ts=[ct+R*math.cos(math.pi*j/48) for j in range(49)]
    for ta,tb in zip(ts,ts[1:]):
        da=sides(ta);db=sides(tb)
        part('vaulted passage intrados','trim',[world(ta,da[0],arch(ta)),world(ta,da[1],arch(ta)),world(tb,db[1],arch(tb)),world(tb,db[0],arch(tb))],[(0,1,2,3)])
    for t in [ct-R,ct+R]:
        d=sides(t);prism('passage side reveals','trim',[(t-.015,d[0]),(t+.015,d[0]),(t+.015,d[1]),(t-.015,d[1])],pdz,pdz+spring)
    # Reference shows a closed iron gate. Keep independently editable and intentional.
    gd=sides(ct)[1]-.18
    for j in range(23):
        t=ct-R+.12+j*(W-.24)/22;hh=arch(t)-pdz-.20
        box('intentional_gate','metal',t,gd,pdz+hh/2,.035,.075,hh)
    for zz in [.25,2.15,2.85]:box('intentional_gate','metal',ct,gd,pdz+zz,W-.10,.08,.055)
    box('intentional_gate','metal',ct,gd,pdz+spring/2,.075,.10,spring)
    # Simplified upper stone surround and triangular pediment, with no copied insignia.
    for sign in [-1,1]:
        d=sides(ct)[0 if sign<0 else 1]+sign*.045
        for t in [ct-1.02,ct+1.02]:box('upper stone window surround','trim',t,d,7.98,.20,.16,3.92)
        box('upper stone window surround','trim',ct,d,6.04,2.30,.22,.20)
        box('upper stone window surround','trim',ct,d,9.83,2.30,.22,.20)
        part('central triangular pediment','trim',[world(ct-1.3,d,9.95),world(ct+1.3,d,9.95),world(ct,d,10.72),world(ct-1.3,d-sign*.16,9.95),world(ct+1.3,d-sign*.16,9.95),world(ct,d-sign*.16,10.72)],[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)])
    # Complete roof polygon and underside cap above vault, no floor across passage.
    vec=[Vector(world(t,d,H)) for t,d in rr]
    tris=tessellate_polygon([vec]);vs=[];fs=[]
    for tri in tris:
        points=[tuple(vec[i] if isinstance(i,int) else i) for i in tri];off=len(vs);vs.extend(points);fs.append((off,off+1,off+2));off=len(vs);vs.extend((x,y,z-.12) for x,y,z in points);fs.append((off+2,off+1,off))
    part('complete polygon roof','roof',vs,fs)
    for a,b in zip(rr,rr[1:]+rr[:1]):
        part('roof sealed edge','roof',[world(*a,H-.12),world(*b,H-.12),world(*b,H),world(*a,H)],[(0,1,2,3)])
    created=[]
    for (g,m),(vs,fs) in groups.items():
        name='Museum Lane link850528336 | '+g;mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;created.append(ob.name)
    ds=sides(ct);thresholds=[list(world(ct,d,pdz)) for d in ds]
    return {'created':created,'parameters':{'height_m':H,'base_z':z0,'levels':None,'visual_facade_zones':2,'opening_count':len(openings),'roof_max_z':z0+H},'interfaces':{'entrance':entrance,'shared_walls':[{'edge':i,'polyline':[list(ring[i]),list(ring[(i+1)%len(ring)])],'height_interval':[z0,z0+H],'neighbour':'way-24436446' if i==0 else 'way-27765411','interval_basis':'conservative target full height, not measured neighbour eaves','policy':'full height blind; neighbouring eaves unknown'} for i in (0,3)],'passages':[{'start_xyz':thresholds[0],'end_xyz':thresholds[1],'threshold_xyz':thresholds,'axis_direction':[v[0],v[1],0],'clear_width_m':W,'clear_height_m':spring+rise,'spring_height_m':spring,'arch_crown_height_m':spring+rise,'length_m':ds[1]-ds[0],'doorless':False,'gate_state':'closed_reference','gate_object_names':[n for n in created if 'intentional_gate' in n],'basis':'OSM699773494 building_passage axis; width and vertical profile visually estimated'}]},'openings':openings,'evidence_source_ids':['osm-850528336','museum-lane-jpbowen2012','rbkc-nhm-spd2012-4.15','osm-passage-699773494'],'uncertainty':['13.149m eaves retained procedural estimate, not photo measurement','Two unequal stone facade zones and central passage replace unsupported four-storey repetition','Rear windows, door and roof artistic; exact photograph to mapped depth correspondence not surveyed','2012 closed iron gate retained as separate intentional_gate mesh; OSM access private; no public access claim','End shared walls retained blind; no neighbouring height inference from roof maxima']}
