"""8 Queens Gate: full mapped ring; individually completed stucco terrace exterior.
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
    materials=dict(materials);materials['masonry']=materials['trim']  # HE stucco terrace, pale painted completion
    groups = {}; openings = []; entrance = None; additional_entrances=[];additional_supports=[]
    entry = feature.get('entry') or {}
    front = feature['estimated_front_entry']
    front_edge = int(front['edge_index'])
    if front_edge != 5: raise ValueError('Expected approved street edge5')
    if abs(float(front['threshold_z'])-z0)>1e-8: raise ValueError('Front threshold must match approved source base')
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
    shared=[{**seg,'policy':'Retain whole common-height segment opaque'} for seg in feature['audit']['normalized_shared_wall_segments']]
    if len(shared)!=3:raise ValueError('Expected three normalized party-wall segments for no8')
    split=H/levels
    if levels!=5:raise ValueError('Coordinator approved five visible tiers required')
    floor_bounds=[H*f for f in (0,.22,.44,.66,.86,1.)]
    f1,f2,f3,f4=floor_bounds[1:5]
    for ei,(a,b,L,u,n) in enumerate(edges):
        def at(s,d,z):return (a[0]+u[0]*s+n[0]*d,a[1]+u[1]*s+n[1]*d,z0+z)
        def panel(g,m,l,r,lo,hi,d=-.18,t=.36):block(g,m,at((l+r)/2,d,(lo+hi)/2),(r-l,t,hi-lo),u,n)
        # Three street bays follow the listed terrace description; rear wing is independently laid out.
        count=3 if ei==5 else 2 if ei==2 else 1 if ei in (1,3) else 0
        centers=[(i+.5)*L/count for i in range(count)] if count else []
        entry_s=((ep[0]-a[0])*u[0]+(ep[1]-a[1])*u[1]) if ep and ei==entry_edge else sum((front['center_xy'][k]-a[k])*u[k] for k in (0,1)) if ei==front_edge else L*.5
        for level,(low,high) in enumerate(zip(floor_bounds,floor_bounds[1:])):
            holes=[]
            for bi,s in enumerate(centers):
                w=min((1.42 if level in (1,2) else 1.16) if ei==5 else 1.0,L/count-.8)
                bot=low+(.52 if level==0 else .48 if level==4 else .68);top=high-(.42 if level==4 else .45)
                if level==0 and ei==entry_edge and abs(s-entry_s)<(w/2+1):continue
                holes.append((s-w/2,s+w/2,bot,top,False,bi))
            if level==0 and ei in (entry_edge,5):
                w=(float(entry.get('clear_width_m',1.3)) if ei==entry_edge else float(front['clear_width_m']))+.16
                s=entry_s
                if not w/2<s<L-w/2:raise ValueError('Source entry outside mapped street edge')
                holes=[h for h in holes if h[1]<s-w/2-.2 or h[0]>s+w/2+.2]
                holes.append((s-w/2,s+w/2,0,min(2.7,split-.3),True,-1))
            for interface in shared:
                if interface['edge']==ei:
                    lo,hi=interface['height_interval']
                    pp=[(q[0]-a[0])*u[0]+(q[1]-a[1])*u[1] for q in interface['polyline']];sl,sr=min(pp),max(pp)
                    holes=[h for h in holes if h[4] or h[1]<=sl or h[0]>=sr or z0+h[3]<=lo or z0+h[2]>=hi]
            cuts=sorted({0.,L,*[q for h in holes for q in h[:2]]})
            for l,r in zip(cuts,cuts[1:]):
                hole=next((h for h in holes if h[0]-1e-7<=(l+r)/2<=h[1]+1e-7),None)
                if hole:
                    panel('pierced masonry','masonry',l,r,low,hole[2])
                    if ei==5 and level==3 and not hole[4]:
                        # Real semicircular head: spandrel mesh follows crown and
                        # keeps space below empty instead of a painted arch.
                        hl,hr,bot,top,_,_=hole;rad=(hr-hl)/2;mid=(hl+hr)/2;spring=top-rad
                        stations=[mid-rad*math.cos(math.pi*j/24) for j in range(25)]
                        for x,y in zip(stations,stations[1:]):
                            za=spring+math.sqrt(max(0,rad*rad-(x-mid)**2));zb=spring+math.sqrt(max(0,rad*rad-(y-mid)**2))
                            vs=[at(ss,dd,zz) for dd in [-.36,0] for ss,zz in [(x,za),(y,zb),(y,high),(x,high)]]
                            meshpart('arched window spandrel','masonry',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
                    else:panel('pierced masonry','masonry',l,r,hole[3],high)
                else:panel('pierced masonry','masonry',l,r,low,high)
            for l,r,bot,top,door,bi in holes:
                s=(l+r)/2
                if ei==5 and level==3 and not door:
                    rad=(r-l)/2;spring=top-rad
                    panel('recessed arched glazing','glass',l+.07,r-.07,bot+.07,spring,-.30,.055)
                    vs=[at(s,-.30,spring)]+[at(s+(rad-.07)*math.cos(math.pi*j/24),-.30,spring+(rad-.07)*math.sin(math.pi*j/24)) for j in range(25)]
                    meshpart('recessed arched glazing','glass',vs,[(0,j+1,j+2) for j in range(24)])
                    for j in range(24):
                        aa=math.pi*j/24;bb=math.pi*(j+1)/24
                        vs=[at(s+rr*math.cos(q),dd,spring+rr*math.sin(q)) for dd in [-.245,-.17] for rr,q in [(rad-.065,aa),(rad-.065,bb),(rad+.065,bb),(rad+.065,aa)]]
                        meshpart('arched frame','trim',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
                else:panel('recessed door' if door else 'recessed glazing','door' if door else 'glass',l+.07,r-.07,bot+(0 if door else .07),top-(.44 if door else .07),-.30,.055)
                for xx in [l+.035,r-.035]:panel('painted joinery','trim',xx-.035,xx+.035,bot+(0 if door else .07),(top-(r-l)/2 if ei==5 and level==3 and not door else top-.07),-.22,.09)
                for zz in ([top-.035] if door else [bot+.035] if ei==5 and level==3 else [bot+.035,top-.035]):panel('painted joinery','trim',l,r,zz-.035,zz+.035,-.22,.09)
                panel('lintels','trim',l-.11,r+.11,top+.03,top+.18,.015,.11)
                if not door:
                    panel('projecting sills','trim',l-.09,r+.09,bot-.11,bot-.035,.035,.21)
                    # Rails span only the clear frame interior. Mullions are
                    # partitioned at every rail, so their front faces never overlap.
                    arched = ei == 5 and level == 3
                    inner_l, inner_r = l+.07, r-.07
                    transom_bottom = min(top-.60, spring-.10) if arched else top-.60
                    rails = [(transom_bottom, transom_bottom+.05,
                              'window transoms', -.21, .07)]
                    if level > 0:
                        rails.append(((bot+top)/2-.026, (bot+top)/2+.026,
                                      'upper sash meeting rail', -.19, .055))
                    rails.sort()
                    for rail_bot, rail_top, label, depth, thickness in rails:
                        panel(label, 'trim', inner_l, inner_r,
                              rail_bot, rail_top, depth, thickness)
                    for xx in ([s-(r-l)/6,s+(r-l)/6] if level==0 else [s]):
                        # The entire finite-width mullion stays inside the inner
                        # arch profile, including its outermost top corner.
                        if arched:
                            inner_radius = rad-.065
                            far_x = max(abs(xx-.023-s), abs(xx+.023-s))
                            mullion_top = spring + math.sqrt(max(0., inner_radius**2-far_x**2))
                        else:
                            mullion_top = top-.07
                        cursor = bot+.07
                        for rail_bot, rail_top, _, _, _ in rails:
                            if rail_bot > cursor:
                                panel('window mullions', 'trim', xx-.023, xx+.023,
                                      cursor, min(rail_bot,mullion_top), -.21, .07)
                            cursor = max(cursor,rail_top)
                        if cursor < mullion_top:
                            panel('window mullions', 'trim', xx-.023, xx+.023,
                                  cursor, mullion_top, -.21, .07)
                else:
                    panel('door transom','trim',l+.07,r-.07,top-.44,top-.37,-.22,.09)
                    panel('door glass fanlight','glass',l+.08,r-.08,top-.37,top-.07,-.30,.055)
                    panel('threshold','trim',l-.10,r+.10,-.006,0,-.22,.44)
                    block('door handle','metal',at(r-.2,-.20,1.1),(.025,.055,.24),u,n)
                    interface={'threshold_xyz':list(at(s,0,0)),'outward_normal':[n[0],n[1],0],'clear_width_m':r-l-.16,'door_leaf_xyz':list(at(s,-.30,(top+bot)/2)),'stair_treads':[],'ramp':'none; supporting ground retained by coordinator','surface_owner':'coordinator','basis':'retained baseline entry projected to mapped wall; aperture artistic'}
                    if ei==entry_edge:entrance=interface
                    else:
                        interface['basis']=front['basis'];interface['audited_ground_z']=float(front['audited_ground_z']);additional_entrances.append(interface)
                openings.append({'edge':ei,'floor':level,'bay':bi,'type':'door' if door else 'window','width_m':r-l,'height_m':top-bot,'recess_m':.30,'basis':'HE group character with individual artistic completion'})
        if ei==5:
            # Text-led group character, individually simplified; no special no1 colonnade.
            for zz in [f1,f3,f4,H-.30]:panel('street cornice','trim',.05,L-.05,zz-.10,zz+.08,.09,.24)
            for ss in [.30,L/3,2*L/3,L-.30]:
                panel('middle storey pilasters','trim',ss-.11,ss+.11,f1+.20,f3-.20,.07,.16)
                for zz in [f1+.22,f2-.16,f3-.18]:panel('simplified capitals','trim',ss-.20,ss+.20,zz,zz+.16,.12,.24)
            panel('first floor balcony deck','trim',.12,L-.12,f1-.18,f1-.03,.45,.92)
            panel('balcony upper rail','trim',.15,L-.15,f1+.90,f1+1.02,.87,.12)
            for j in range(27):
                ss=.24+j*(L-.48)/26
                block('balcony balusters','trim',at(ss,.87,f1+.44),(.065,.065,.82),u,n)
            for ss in [L/6,L/2,5*L/6]:
                for xx in [ss-.52,ss+.52]:
                    panel('individual window consoles','trim',xx-.065,xx+.065,f3-.26,f3-.05,.09,.20)
            for j in range(19):
                ss=.20+j*(L-.40)/18
                panel('upper cornice consoles','trim',ss-.045,ss+.045,H-.27,H-.12,.08,.19)
            es=entry_s
            # Estimated additional street door and grouped Doric portico; original rear doorway remains separate.
            # Original source ground is -.05 through one metre outward; the
            # coordinator closes the finite 2.4m by1.06m support polygon below.
            ph=float(front['porch_half_width_m']); col=float(front['column_lateral_offset_m']); cd=float(front['column_outward_m'])
            for ss in [es-col,es+col]:
                panel('Doric column square plinths','trim',ss-.17,ss+.17,0,.17,cd,.34)
                profile=[(.17,.132),(.24,.120),(1.35,.115),(2.49,.102),(2.54,.102),(2.64,.155)]
                vs=[];fs=[];N=24
                for zz,rad in profile:
                    for j in range(N):
                        q=2*math.pi*j/N;vs.append(at(ss+rad*math.cos(q),cd+rad*math.sin(q),zz))
                fs.append(tuple(range(N-1,-1,-1)));fs.append(tuple(range((len(profile)-1)*N,len(profile)*N)))
                for k in range(len(profile)-1):
                    for j in range(N):fs.append((k*N+j,k*N+(j+1)%N,(k+1)*N+(j+1)%N,(k+1)*N+j))
                meshpart('tapered Doric shafts and echinus','trim',vs,fs)
                panel('Doric column abaci','trim',ss-.18,ss+.18,2.64,2.78,cd,.36)
            panel('projecting portico architrave','trim',es-ph+.05,es+ph-.05,2.78,2.94,.43,1.02)
            panel('projecting portico cornice','trim',es-ph,es+ph,2.94,3.04,.45,1.04)
            support={'polygon_xy':[list(at(es+x,d,0)[:2]) for x,d in [(-ph,front['support_depth_interval_m'][0]),(ph,front['support_depth_interval_m'][0]),(ph,front['support_depth_interval_m'][1]),(-ph,front['support_depth_interval_m'][1])]],'top_z':z0,'basis':'Estimated freestanding Doric column feet support at estimated additional street entry; coordinator owns closed finite slab'}
            additional_supports.append(support)
            if entrance:entrance['additional_supports']=[support]
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
    for zz in floor_bounds[1:-1]:band('flush floor course','trim',zz-.045,zz+.045,-.065,.12)
    band('inward eaves','trim',H-.16,H+.02,-.12,.22)
    band('low parapet','masonry',H,H+.3,-.14,.28)
    band('mitred coping','trim',H+.3,H+.38,-.21,.36)
    # Exact concave triangulation with 5.2 integer-index compatibility; no invented roof equipment.
    def roofcap(rr,z,name):
        vertices=[(x,y,z0+z) for x,y in rr]
        vv=[Vector(v) for v in vertices];lookup={tuple(v):i for i,v in enumerate(vv)}
        fs=[tuple(v if isinstance(v,int) else lookup[tuple(v)] for v in tri) for tri in tessellate_polygon([vv])]
        meshpart(name,'roof',vertices,fs)
    roofcap(offset(-.27),H-.04,'concave roof membrane')
    roofcap(ring,H-.07,'complete mapped roof basecap')
    created=[]
    for (g,m),(vs,fs) in groups.items():
        if not fs:continue
        used=sorted({i for face in fs for i in face});remap={old:i for i,old in enumerate(used)};vs=[vs[i] for i in used];fs=[tuple(remap[i] for i in face) for face in fs]
        name='8 Queens Gate | '+g;mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update()
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
        ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;ob['evidence_status']='Mapped footprint; five visible tiers perHE1226082 including shorter top attic; original estimated envelope height retained';created.append(ob.name)
    return {'created':created,'parameters':{'height_m':H,'base_z':z0,'levels':levels,'visible_tier_count':5,'tier_height_ratios':[.22,.22,.22,.20,.14],'source_osm_levels':6,'opening_count':len(openings),'wall_thickness_m':.36,'roof_max_z':z0+H+.38},'interfaces':{'entrance':entrance,'additional_entrances':additional_entrances,'additional_supports':additional_supports,'shared_walls':shared,'shared_wall_policy':'All mapped boundary walls retained; no unverified party-wall deletions'},'openings':openings,'evidence_source_ids':['osm-809238788','he-1226082','number2-context-2019'],'uncertainty':['Exact number8 facade not confirmed in licensed images; number2 is only group context; retained rear entry and approved estimated additional street door/Doric portico are unverified in real appearance','HE five visible storeys includes top attic; sourceOSM6 archived by coordinator, not explained as basement count. Source19.450444m envelope retained and redistributed, not measured','Five tiers include shorter14percent top attic, with complete flat roof and parapet artistic; sourcetotalheight retained, no basement excavation or rooftop plant inferred','Three normalized shared segments on edges0/3/4 opaque at common height; complete walls preserved; rear wing windows artistic']}
