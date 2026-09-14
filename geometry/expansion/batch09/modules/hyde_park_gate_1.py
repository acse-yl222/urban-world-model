"""1 Hyde Park Gate: OSM five-storey address independently corroborated; elevations and roof artistically completed.
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
    z0=float(feature.get('base_z',.05));H=float(feature['height_m']);levels=max(1,int(feature.get("levels",5)));pitch=H/levels
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
        # HE1080596-informed coordinator correction: Cheval main body now
        # reaches five storeys; old 13.15m neighbour interval is superseded.
        # Retain complete wall and conservatively exclude openings to target eaves.
        if adj.get('id')=='way-809238777':zz=[z0,z0+H]
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
        count=max(1,round(L/3.15)) if L>2.8 else 0
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
                    panel('moulded window hood','trim',l-.14,r+.14,top+.035,top+.18,.06,.22)
                    for xx in (l-.065,r+.065):panel('window architrave sides','trim',xx-.055,xx+.055,bot-.08,top+.12,.015,.12)
                    if floor in (1,2):
                        for xx in (l-.10,r+.10):panel('hood console blocks','trim',xx-.07,xx+.07,top-.14,top+.07,.10,.25)
                else:
                    for xx in (l-.17,r+.17):panel('stone entrance jambs','trim',xx-.12,xx+.12,0,top+.30,.08,.28)
                    panel('stone entrance entablature','trim',l-.36,r+.36,top+.13,top+.36,.11,.40)
                    panel('entry transom','trim',l,r,top-.6,top-.53,-.25,.11)
                    panel('door central stile','trim',s-.025,s+.025,0,top-.6,-.25,.10)
                    box('door hardware','metal',at(s+.28,-.19,1.1),(.035,.08,.24),u,n)
                    panel('flush threshold','trim',l-.12,r+.12,-.006,0,-.17,.40)
                    entrance={'threshold_xyz':list(at(s,0,0)),'outward_normal':[n[0],n[1],0],'clear_width_m':w-.16,'door_leaf_xyz':list(at(s,-.34,top/2)),'stair_treads':[],'ramp':'none authored','surface_owner':'coordinator','basis':'preserved baseline lateral position; threshold projected to wall'}
                openings.append({'edge':ei,'floor':floor,'bay':bi,'type':'door' if door else 'window','width_m':w,'height_m':top-bot,'recess_m':.34,'basis':'artistic townhouse completion; exact current facade unconfirmed'})
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
    # Evidence revision: parameterised mansard and local 1a Queen's Gate tower.
    # H remains the coordinator's common main-eaves parameter, never mesh scaling.
    attic=2.50; tower_top=30.0
    lower=offset(-.15);upper=offset(-1.60)
    def prism(g,m,pts,d0,d1,point):
        clean=[]
        for pt in pts:
            if not clean or math.dist(pt,clean[-1])>1e-9:clean.append(pt)
        if len(clean)>1 and math.dist(clean[0],clean[-1])<1e-9:clean.pop()
        nn=len(clean)
        if nn<3:return
        vv=[point(x,d,z) for d in (d0,d1) for x,z in clean]
        ff=[tuple(range(nn-1,-1,-1)),tuple(range(nn,2*nn))]
        ff.extend((j,(j+1)%nn,(j+1)%nn+nn,j+nn) for j in range(nn))
        mesh(g,m,vv,ff)
    def archfill(g,point,center,width,spring,ceiling,d0,d1,mat):
        R=width/2
        for k in range(20):
            t0=math.pi*k/20;t1=math.pi*(k+1)/20
            x0=center+R*math.cos(t0);x1=center+R*math.cos(t1)
            h0=spring+R*math.sin(t0);h1=spring+R*math.sin(t1)
            prism(g,mat,[(x0,h0),(x1,h1),(x1,ceiling),(x0,ceiling)],d0,d1,point)
    def archband(g,point,center,width,spring,d0,d1):
        R=width/2
        for k in range(20):
            t0=math.pi*k/20;t1=math.pi*(k+1)/20
            pts=[(center+rr*math.cos(t),spring+rr*math.sin(t)) for rr,t in [(R,t0),(R,t1),(R+.075,t1),(R+.075,t0)]]
            prism(g,'metal',pts,d0,d1,point)
    # Sloping roof skin broken at actual dormer openings; no sheet behind glass.
    for ei,(a,L,u,n) in enumerate(edges):
        def pt(ss,dd,zz):return(a[0]+u[0]*ss+n[0]*dd,a[1]+u[1]*ss+n[1]*dd,z0+zz)
        centers=[L*(j+.5)/max(1,round(L/3.1)) for j in range(max(1,round(L/3.1)))] if ei in (4,5) else []
        centers=[cc for cc in centers if not(ei==4 and 3.1<cc<10.9)]
        intervals=[(cc-.66,cc+.66,cc) for cc in centers if 2.40<cc<L-2.40]
        cuts=sorted(set([0,L]+[q for l,r,c in intervals for q in (l,r)]))
        # Clip the actual mitred hip trapezoid at constant edge-s values.
        # Former proportional interpolation shifted top cuts laterally, leaving
        # triangular wedges beside rectangular dormer cheeks.
        j=(ei+1)%len(ring)
        def local(q,zz):return(sum((q[k]-a[k])*u[k] for k in range(2)),sum((q[k]-a[k])*n[k] for k in range(2)),zz)
        full=[local(lower[ei],H+.15),local(lower[j],H+.15),local(upper[j],H+attic),local(upper[ei],H+attic)]
        def clip(poly,bound,keepgreater):
            out=[]
            for aa,bb in zip(poly,poly[1:]+poly[:1]):
                ia=aa[0]>=bound-1e-10 if keepgreater else aa[0]<=bound+1e-10
                ib=bb[0]>=bound-1e-10 if keepgreater else bb[0]<=bound+1e-10
                if ia:out.append(aa)
                if ia!=ib:
                    t=(bound-aa[0])/(bb[0]-aa[0]);out.append(tuple(aa[k]+t*(bb[k]-aa[k]) for k in range(3)))
            clean=[]
            for q in out:
                if not clean or math.dist(q,clean[-1])>1e-9:clean.append(q)
            if len(clean)>1 and math.dist(clean[0],clean[-1])<1e-9:clean.pop()
            return clean
        cuts=sorted(set([min(q[0] for q in full),max(q[0] for q in full)]+[q for l,r,c in intervals for q in (l,r)]))
        for l,r in zip(cuts,cuts[1:]):
            if any(ll<(l+r)/2<rr for ll,rr,c in intervals):continue
            poly=clip(clip(full,l,True),r,False)
            if len(poly)<3:continue
            vv=[pt(ss,dd,zz) for ss,dd,zz in poly]
            mesh('observed mansard sloping skin','roof',vv,[(0,k,k+1) for k in range(1,len(vv)-1)])
        for l,r,cc in intervals:
            bot=H+.35;spring=H+1.73;top=H+attic;w=1.10
            # Closed cheeks/back and a top cap; glass recess opens into dormer.
            for xx in (l+.045,r-.045):box('mansard dormer closed cheeks','roof',pt(xx,-.98,(H+.15+top)/2),(.09,1.66,top-H-.15),u,n)
            box('mansard dormer closed back','roof',pt(cc,-1.79,(H+.15+top)/2),(r-l,.12,top-H-.15),u,n)
            box('mansard dormer closed top','roof',pt(cc,-.98,top),(r-l,1.78,.10),u,n)
            box('mansard dormer lower apron','roof',pt(cc,-.20,(H+.15+bot)/2),(r-l,.14,bot-H-.15),u,n)
            for xx in (cc-w/2-.055,cc+w/2+.055):box('mansard dormer upright frames','metal',pt(xx,-.20,(bot+top)/2),(.11,.14,top-bot),u,n)
            box('mansard recessed glazing','glass',pt(cc,-.27,(bot+spring+w/2)/2),(w,.05,spring+w/2-bot),u,n)
            archfill('mansard curved head solid closure',pt,cc,w,spring,top,-.28,-.14,'roof')
            archband('mansard rounded arch frames',pt,cc,w,spring,-.14,-.06)
            box('mansard sash mullion','metal',pt(cc,-.15,(bot+spring)/2),(.035,.05,spring-bot),u,n)
            box('mansard sash transom','metal',pt(cc,-.15,bot+.65),(w,.05,.035),u,n)
    topvv=[Vector((x,y,z0+H+attic)) for x,y in upper];v=[];f=[]
    for tri in tessellate_polygon([topvv]):
        off=len(v);v.extend(tuple(topvv[q] if isinstance(q,int) else q) for q in tri);f.append((off,off+1,off+2))
    mesh('complete inset mansard top','roof',v,f)
    # Audit-estimated tower base: edge4 s=7m, inward3.4m, six-metre square.
    a,L,u,n=edges[4]
    def tp(ss,dd,zz):return(a[0]+u[0]*ss+n[0]*dd,a[1]+u[1]*ss+n[1]*dd,z0+zz)
    tr=[tp(4,-.4,0)[:2],tp(10,-.4,0)[:2],tp(10,-6.4,0)[:2],tp(4,-6.4,0)[:2]]
    if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(tr,tr[1:]+tr[:1]))<0:tr.reverse()
    for ta,tb in zip(tr,tr[1:]+tr[:1]):
        TL=math.dist(ta,tb);tu=((tb[0]-ta[0])/TL,(tb[1]-ta[1])/TL);tn=(tu[1],-tu[0])
        def pt(ss,dd,zz):return(ta[0]+tu[0]*ss+tn[0]*dd,ta[1]+tu[1]*ss+tn[1]*dd,z0+zz)
        def panel(g,m,l,r,lo,hi,dd=-.16,depth=.32):box(g,m,pt((l+r)/2,dd,(lo+hi)/2),(r-l,depth,hi-lo),tu,tn)
        floor=H-.08;bot=25.0;spring=27.05;W=.95;ceiling=29.20
        bays=[TL*.28,TL*.50,TL*.72];cuts=sorted([0,TL]+[ss+sign*W/2 for ss in bays for sign in (-1,1)])
        for l,r in zip(cuts,cuts[1:]):
            cc=next((ss for ss in bays if ss-W/2<(l+r)/2<ss+W/2),None)
            if cc is None:panel('tower pierced upper walls','masonry',l,r,floor,ceiling)
            else:
                panel('tower pierced upper walls','masonry',l,r,floor,bot)
                archfill('tower arch spandrels',pt,cc,W,spring,ceiling,-.32,0,'masonry')
                panel('tower recessed arched glazing','glass',l,r,bot,spring+W/2,-.24,.05)
                archband('tower rounded window heads',pt,cc,W,spring,.025,.12)
                for xx in (l-.045,r+.045):panel('tower window jamb trim','trim',xx-.045,xx+.045,bot,spring,.05,.14)
                panel('tower window sill','trim',l-.12,r+.12,bot-.14,bot-.035,.08,.20)
        for xx in (.16,TL-.16):panel('tower corner pilasters','trim',xx-.15,xx+.15,H,28.42,.025,.13)
        for zz,th,dep in [(H+.12,.18,.04),(24.55,.20,.07),(28.45,.30,.13),(28.83,.20,.22)]:panel('tower layered cornice','trim',-.12,TL+.12,zz,zz+th,dep,.30)
        panel('tower parapet solid plinth','trim',.18,TL-.18,29.03,29.20,0,.26)
        panel('tower parapet handrail','trim',.18,TL-.18,29.86,30.0,0,.30)
        for k in range(17):
            xx=.40+(TL-.80)*k/16;panel('tower parapet balusters','trim',xx-.055,xx+.055,29.18,29.88,0,.12)
    for tx,ty in tr:box('single tower corner parapet pier','trim',(tx,ty,z0+29.50),(.36,.36,1.0),u,n)
    towerroof=[(x,y,z0+29.14) for x,y in tr]
    mesh('tower closed flat roof','roof',towerroof,[(0,1,2,3)])
    roof_parts.extend([{'type':'mansard','height_above_eaves_m':attic,'basis':'2022 photograph; dimensions estimated'},{'type':'local tower','ring':tr,'roof_max_z':z0+tower_top,'basis':'RBKC30m1aQueenGate tower; audit attribution to778, six-metre base location estimated'}])
    created=[]
    for (g,m),(v,f) in groups.items():
        if not f:continue
        name='1 Hyde Park Gate | '+g;me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;ob['evidence_status']='Corner2022 licensed photograph and RBKC3.24 tower/mansard evidence; main height visually calibrated, tower base estimated';created.append(ob.name)
    return {'created':created,'parameters':{'height_m':H,'eaves_height_m':H,'base_z':z0,'levels':levels,'roof_levels':1,'roof_max_z':z0+tower_top,'opening_count':len(openings),'wall_thickness_m':.4},'interfaces':{'entrance':entrance,'additional_entrances':[],'shared_walls':common},'openings':openings,'roof_parts':roof_parts,'evidence_source_ids':['osm-809238778','gallery1957-address-2022','geograph-4338348','commons-corner-2022','rbkc-queensgate-3-24'],'uncertainty':['Address corroborated by Gallery1957 official exhibition document; no assertion of whole-building ownership or current occupancy','Five main levels regenerated at coordinator21.5m main eaves, visual calibration midpoint20–23m using official30m tower; not measured, no nonuniform mesh scaling','Viewed Geograph street photo identifies nearby26HydeParkGate, not this building; pale sash/trim vocabulary is context only, target bays and roof are artistic','2022 north-corner photograph supports mansard rounded dormers and local tower; RBKC names30m tower at1aQueensGate, audit places estimated6m base inside eastern-return778; exact base and main eaves remain estimates','West shared wall to Cheval retained opaque across full target height following coordinator HE1080596 height correction; prior four-storey neighbour estimate is superseded, attic inset handled by Cheval author','Original entrance threshold near0 retained; no inherited .05 platform or external support authored']}
