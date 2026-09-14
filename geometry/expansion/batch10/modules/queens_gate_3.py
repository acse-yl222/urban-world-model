"""3 Queens Gate: OSM six-storey narrow terrace with HE group description; precise facade and roof remain uncertain.
Authoring only; no global scene mutation, external data retrieval or export.
"""
import math

def build(feature, materials):
    import bpy,bmesh
    from mathutils import Vector
    from mathutils.geometry import tessellate_polygon
    ring=[tuple(map(float,p[:2])) for p in feature['ring']]
    if ring[0]==ring[-1]:ring.pop()
    if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1]))<0:raise ValueError('CCW ring required to preserve edge contract')
    z0=float(feature.get('base_z',.05));H=float(feature['height_m']);levels=max(1,int(feature.get("levels",6)));pitch=H/levels
    groups={};openings=[];entrance=None;roof_parts=[]
    def mesh(g,m,v,f):
        vs,fs=groups.setdefault((g,m),([],[]));o=len(vs);vs.extend(v);fs.extend(tuple(o+i for i in face) for face in f)
    def box(g,m,c,size,u=(1,0),n=(0,1)):
        if min(size)<1e-6:return
        x,y,z=c;w,d,h=[s/2 for s in size]
        v=[(x+i*w*u[0]+j*d*n[0],y+i*w*u[1]+j*d*n[1],z+k*h) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        mesh(g,m,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    edges=[]
    for a,b in zip(ring,ring[1:]+ring[:1]):
        L=math.dist(a,b);u=((b[0]-a[0])/L,(b[1]-a[1])/L);edges.append((a,L,u,(u[1],-u[0])))
    entry=feature.get('entry') or {};exy=entry.get('center_xy')
    def distance(i):
        a,L,u,n=edges[i];s=max(0,min(L,sum((exy[k]-a[k])*u[k] for k in range(2))));return math.dist(exy,[a[k]+s*u[k] for k in range(2)])
    entry_edge=min(range(len(edges)),key=distance) if exy else max(range(len(edges)),key=lambda i:edges[i][1])
    # Translate exact coordinator adjacency polylines to edge intervals. Only
    # common wall heights suppress apertures; whole walls are never removed.
    common=[]
    for adj in feature.get('audit',{}).get('adjacent_or_detailed_neighbours_within_35m',[]):
        geo=adj.get('shared_boundary_geometry') or {};zz=adj.get('shared_wall_potential_height_interval_m')
        if not zz:continue
        lines=[geo.get('coordinates',[])] if geo.get('type')=='LineString' else geo.get('coordinates',[]) if geo.get('type')=='MultiLineString' else []
        for line in lines:
            for p,q in zip(line,line[1:]):
                for ei,(a,L,u,n) in enumerate(edges):
                    if max(abs(sum((v[k]-a[k])*n[k] for k in range(2))) for v in (p,q))>.03:continue
                    spans=sorted(sum((v[k]-a[k])*u[k] for k in range(2)) for v in (p,q));lo=max(0,spans[0]);hi=min(L,spans[1])
                    if hi-lo>.03:common.append({'edge':ei,'s_interval':[lo,hi],'height_interval':zz,'polyline':[p,q],'neighbour':adj['id'],'openings':[]})
    def blocked(ei,l,r,bot,top):return any(c['edge']==ei and l<c['s_interval'][1] and r>c['s_interval'][0] and z0+bot<c['height_interval'][1] and z0+top>c['height_interval'][0] for c in common)
    for ei,(a,L,u,n) in enumerate(edges):
        def at(s,d,z):return(a[0]+u[0]*s+n[0]*d,a[1]+u[1]*s+n[1]*d,z0+z)
        def panel(g,m,l,r,lo,hi,d=-.2,t=.4):box(g,m,at((l+r)/2,d,(lo+hi)/2),(r-l,t,hi-lo),u,n)
        count=3 if ei==6 else max(1,round(L/3.4)) if L>2.8 else 0
        centers=[L*(k+.5)/count for k in range(count)]
        door_s=sum((exy[k]-a[k])*u[k] for k in range(2)) if exy and ei==entry_edge else L/2
        for floor in range(levels):
            low=pitch*floor;high=pitch*(floor+1);holes=[]
            for bi,s in enumerate(centers):
                w=min(1.38 if floor<4 else 1.18,L/count-.76);bot=low+(.68 if floor<4 else .92);top=high-(.45 if floor<4 else .70)
                if floor==0 and ei==entry_edge and abs(s-door_s)<1.75:continue
                if blocked(ei,s-w/2,s+w/2,bot,top):continue
                holes.append((s-w/2,s+w/2,bot,top,False,bi))
            if floor==0 and ei==entry_edge:
                w=float(entry.get('clear_width_m',1.05))+.16
                holes.append((door_s-w/2,door_s+w/2,0,min(3,high-.12),True,-1))
            cuts=sorted(set([0,L]+[v for h in holes for v in h[:2]]))
            for l,r in zip(cuts,cuts[1:]):
                h=next((h for h in holes if h[0]<(l+r)/2<h[1]),None)
                if h:panel('pierced stucco elevations','masonry',l,r,low,h[2]);panel('pierced stucco elevations','masonry',l,r,h[3],high)
                else:panel('pierced stucco elevations','masonry',l,r,low,high)
            for l,r,bot,top,door,bi in holes:
                s=(l+r)/2;w=r-l
                panel('entrance leaves' if door else 'recessed townhouse sash glazing','door' if door else 'glass',l+.065,r-.065,bot if door else bot+.06,top-.06,-.34,.06)
                for xx in (l+.035,r-.035):panel('painted sash frames','trim',xx-.035,xx+.035,bot,top,-.26,.11)
                for zz in ((top-.035,) if door else (bot+.035,top-.035)):panel('painted sash frames','trim',l,r,zz-.035,zz+.035,-.26,.11)
                if not door:
                    for frac in (.5,):panel('sash glazing bars','trim',l+w*frac-.02,l+w*frac+.02,bot,top,-.245,.055)
                    for frac in (.5,):panel('sash meeting rails','trim',l,r,bot+(top-bot)*frac-.021,bot+(top-bot)*frac+.021,-.245,.055)
                    panel('stone window sills','trim',l-.09,r+.09,bot-.105,bot-.025,.035,.21)
                    
                    if floor!=3 or ei!=6:panel('moulded window hood','trim',l-.14,r+.14,top+.035,top+.18,.06,.22)
                    for xx in (l-.065,r+.065):panel('window architrave sides','trim',xx-.055,xx+.055,bot-.08,top+.12,.015,.12)
                    if floor in (1,2) and ei==6:
                        for xx in (l-.10,r+.10):panel('hood console blocks','trim',xx-.07,xx+.07,top-.14,top+.07,.10,.25)
                else:
                    for xx in (l-.17,r+.17):panel('stone entrance jambs','trim',xx-.12,xx+.12,0,top+.30,.08,.28)
                    panel('stone entrance entablature','trim',l-.36,r+.36,top+.13,top+.36,.11,.40)
                    panel('entry transom','trim',l,r,top-.6,top-.53,-.25,.11)
                    panel('door central stile','trim',s-.025,s+.025,0,top-.6,-.25,.10)
                    box('door hardware','metal',at(s+.28,-.19,1.1),(.035,.08,.24),u,n)
                    panel('flush threshold','trim',l-.12,r+.12,-.006,0,-.17,.40)
                    entrance={'threshold_xyz':list(at(s,0,0)),'outward_normal':[n[0],n[1],0],'clear_width_m':w-.16,'door_leaf_xyz':list(at(s,-.34,top/2)),'stair_treads':[],'ramp':'none authored','surface_owner':'coordinator','basis':'preserved baseline lateral position; threshold projected to wall'}
                if not door and floor==3 and ei==6:
                    # Exact segment endpoints shared between arch band and solid spandrel.
                    spring=top-w/2;N=20
                    for k in range(N):
                        t0=math.pi*k/N;t1=math.pi*(k+1)/N
                        x0=s+math.cos(t0)*w/2;x1=s+math.cos(t1)*w/2
                        h0=spring+math.sin(t0)*w/2;h1=spring+math.sin(t1)*w/2
                        pts=[(x0,h0),(x1,h1),(x1,top),(x0,top)]
                        # At the crown a strip is triangular, not a quad with
                        # coincident vertices. Extrude its actual polygon so
                        # neither cap nor depth side contains zero-area faces.
                        clean=[]
                        for pt in pts:
                            if not clean or math.dist(pt,clean[-1])>1e-9:clean.append(pt)
                        if len(clean)>1 and math.dist(clean[0],clean[-1])<1e-9:clean.pop()
                        countp=len(clean)
                        vv=[at(x,d,z) for d in (-.4,0) for x,z in clean]
                        ff=[tuple(range(countp-1,-1,-1)),tuple(range(countp,2*countp))]
                        ff.extend((j,(j+1)%countp,(j+1)%countp+countp,j+countp) for j in range(countp))
                        mesh('arched window solid spandrels','masonry',vv,ff)
                        rr=w/2+.09
                        pts=[(x0,h0),(x1,h1),(s+math.cos(t1)*rr,spring+math.sin(t1)*rr),(s+math.cos(t0)*rr,spring+math.sin(t0)*rr)]
                        vv=[at(x,d,z) for d in (-.025,.11) for x,z in pts]
                        mesh('third floor curved arch surrounds','trim',vv,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
                openings.append({'edge':ei,'floor':floor,'bay':bi,'type':'door' if door else 'window','width_m':w,'height_m':top-bot,'recess_m':.34,'basis':'artistic townhouse completion; exact current facade unconfirmed'})
        if ei==6:
            # Narrow three-bay street front, contrasted with plain rear return.
            for ss in (.28,L-.28):
                for floor in (1,2):
                    bot=floor*pitch+.05;top=(floor+1)*pitch-.05
                    panel('street order pilaster shafts','trim',ss-.11,ss+.11,bot,top-.20,.025,.16)
                    panel('street order capital abaci','trim',ss-.22,ss+.22,top-.20,top,.055,.22)
                    panel('street order base mouldings','trim',ss-.17,ss+.17,bot,bot+.15,.06,.24)
            # A shallow balcony has closed slab and three guarded bay sections.
            panel('street first floor balcony slab','trim',.15,L-.15,pitch-.15,pitch+.03,.23,.65)
            for zz in (pitch+.12,pitch+.93):panel('street balcony rails','trim',.22,L-.22,zz,zz+.10,.53,.12)
            for j in range(21):
                ss=.27+(L-.54)*j/20
                panel('street balcony balusters','trim',ss-.045,ss+.045,pitch+.20,pitch+.94,.53,.10)
        # Pale ground-floor base skirt stays below openings.
        if ei!=entry_edge:panel('plain brick plinth','masonry',0,L,.02,.50,.015,.10)
        else:
            panel('plain brick plinth','masonry',0,max(0,door_s-.78),.02,.50,.015,.1);panel('plain brick plinth','masonry',min(L,door_s+.78),L,.02,.50,.015,.1)
    def offset(d):
        out=[]
        for i,p in enumerate(ring):
            na=edges[i-1][3];nb=edges[i][3];den=1+sum(na[k]*nb[k] for k in range(2));v=d/max(.08,den);out.append((p[0]+v*(na[0]+nb[0]),p[1]+v*(na[1]+nb[1])))
        return out
    def band(g,m,lo,hi,dep,th):
        inner=offset(dep-th/2);outer=offset(dep+th/2);N=len(ring);v=[(x,y,z0+z) for z in (lo,hi) for c in (inner,outer) for x,y in c];f=[]
        for i in range(N):
            j=(i+1)%N;f.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
        mesh(g,m,v,f)
    for zz,th,dep in [(pitch,.18,.015),(pitch*2,.12,.01),(H-.30,.20,.06),(H-.08,.13,.12)]:band('plain eaves and floor course','trim',zz-th/2,zz+th/2,dep,.22)
    band('stucco attic parapet','masonry',H,H+.37,-.17,.34);band('stone parapet coping','trim',H+.37,H+.47,-.15,.4)
    vv=[Vector((x,y,z0+H-.06)) for x,y in ring];v=[];f=[]
    for tri in tessellate_polygon([vv]):
        off=len(v);v.extend(tuple(vv[q] if isinstance(q,int) else q) for q in tri);f.append((off,off+1,off+2))
    mesh('complete concave roof deck','roof',v,f)
    created=[]
    for (g,m),(v,f) in groups.items():
        if not f:continue
        name='3 Queens Gate | '+g;me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;ob['evidence_status']='HE1-19 group description; number3 exact facade photo unresolved, six OSM levels retained with conflict noted';created.append(ob.name)
    return {'created':created,'parameters':{'height_m':H,'eaves_height_m':H,'base_z':z0,'levels':levels,'roof_levels':0,'roof_max_z':z0+H+.47,'opening_count':len(openings),'wall_thickness_m':.4},'interfaces':{'entrance':entrance,'additional_entrances':[],'shared_walls':common},'openings':openings,'roof_parts':roof_parts,'evidence_source_ids':['osm-809238783','he-1226082','commons-neighbour2-2019'],'uncertainty':['OSM six levels conflicts with HE legacy group five-storey description; retained source19.4513533813m eaves pending exact current building evidence','No exact number3 licensed street view identified; neighbour number2 portico photo is group context only and not copied to rear doorway','Three street-front bays, classical middle pilasters and third-floor arches follow group description with estimated dimensions; sixth tier and rear openings follow source interpretation','Full seven-point footprint and flat parapet roof retain original massing; actual roof and attic form unresolved','North shared wall opaque through1-2QueensGate model eaves16.29944445m; south shared wall opaque through4QueensGate19.44981459m, whole walls retained','Rear source entrance near0 remains, external ground at-.05 requires coordinator finite support; no platform authored']}
