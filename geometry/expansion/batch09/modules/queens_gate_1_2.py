"""1–2 Queens Gate: Licensed number2 entrance photographs and Historic England terrace description; roof and rear estimated.
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
        count=max(1,round(L/3.6)) if L>2.8 else 0
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
                    
                    if floor!=3 or ei not in (0,16,17):panel('moulded window hood','trim',l-.14,r+.14,top+.035,top+.18,.06,.22)
                    for xx in (l-.065,r+.065):panel('window architrave sides','trim',xx-.055,xx+.055,bot-.08,top+.12,.015,.12)
                    if floor in (1,2) and ei in (0,16,17):
                        for xx in (l-.10,r+.10):panel('hood console blocks','trim',xx-.07,xx+.07,top-.14,top+.07,.10,.25)
                else:
                    for xx in (l-.17,r+.17):panel('stone entrance jambs','trim',xx-.12,xx+.12,0,top+.30,.08,.28)
                    panel('stone entrance entablature','trim',l-.36,r+.36,top+.13,top+.36,.11,.40)
                    panel('entry transom','trim',l,r,top-.6,top-.53,-.25,.11)
                    panel('door central stile','trim',s-.025,s+.025,0,top-.6,-.25,.10)
                    box('door hardware','metal',at(s+.28,-.19,1.1),(.035,.08,.24),u,n)
                    panel('flush threshold','trim',l-.12,r+.12,-.006,0,-.17,.40)
                    entrance={'threshold_xyz':list(at(s,0,0)),'outward_normal':[n[0],n[1],0],'clear_width_m':w-.16,'door_leaf_xyz':list(at(s,-.34,top/2)),'stair_treads':[],'ramp':'none authored','surface_owner':'coordinator','basis':'preserved baseline lateral position; threshold projected to wall'}
                if not door and floor==3 and ei in (0,16,17):
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
        if ei==entry_edge:
            def turned(g,ss,dd,profile):
                N=20;vv=[at(ss+rad*math.cos(2*math.pi*k/N),dd+rad*math.sin(2*math.pi*k/N),zz) for zz,rad in profile for k in range(N)];ff=[tuple(range(N-1,-1,-1)),tuple((len(profile)-1)*N+k for k in range(N))]
                for j in range(len(profile)-1):
                    for k in range(N):ff.append((j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k))
                mesh(g,'trim',vv,ff)
            canopy=pitch-.05
            for delta in (-1.78,-1.20,1.20,1.78):
                ss=door_s+delta
                panel('Doric portico plinth','trim',ss-.27,ss+.27,0,.12,.92,.54)
                turned('paired Doric entrance columns',ss,.92,[(.12,.25),(.20,.26),(.29,.205),(.37,.175),(canopy-.37,.155),(canopy-.28,.21),(canopy-.17,.245),(canopy-.10,.245)])
                panel('Doric square abacus','trim',ss-.27,ss+.27,canopy-.11,canopy+.01,.92,.54)
            panel('portico entablature closed canopy','trim',door_s-2.15,door_s+2.15,canopy,canopy+.27,.48,1.50)
            panel('portico upper moulding','trim',door_s-2.21,door_s+2.21,canopy+.27,canopy+.39,.48,1.58)
            for j in range(13):
                ss=door_s-1.95+j*3.90/12
                turned('balcony turned balusters',ss,1.20,[(canopy+.39,.065),(canopy+.47,.07),(canopy+.59,.055),(canopy+.71,.085),(canopy+.80,.05),(canopy+.95,.04),(canopy+1.01,.07)])
            panel('balustrade handrail','trim',door_s-2.12,door_s+2.12,canopy+.99,canopy+1.10,1.20,.23)
            entrance['additional_supports']=[{'polygon_xy':[list(at(door_s+ss,dd,0)[:2]) for ss,dd in [(-2.2,-.25),(2.2,-.25),(2.2,1.30),(-2.2,1.30)]],'top_z':z0,'basis':'estimated porch-column approach support; coordinator owns ground'}]
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
        name='1–2 Queens Gate | '+g;me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;ob['evidence_status']='Licensed exact number2 portico photos and HE terrace description; positioning, proportions and roof estimated';created.append(ob.name)
    return {'created':created,'parameters':{'height_m':H,'eaves_height_m':H,'base_z':z0,'levels':levels,'roof_levels':0,'roof_max_z':z0+H+.47,'opening_count':len(openings),'wall_thickness_m':.4},'interfaces':{'entrance':entrance,'additional_entrances':[],'shared_walls':common},'openings':openings,'roof_parts':roof_parts,'evidence_source_ids':['osm-809238779','commons-number2-2019','commons-entrance-2023','he-1226082'],'uncertainty':['Five storeys including attic supported by OSM and HE terrace description; 16.2994496043m eaves is model estimate','Two licensed photos show number2 paired Doric portico, pale stucco and balustrades; source entry on edge0 retained rather than inferring uncalibrated photographic door coordinates','Third-floor arches and classical mid-floor consoles derive from HE description, dimensions and bay layout artistically completed','Complete eighteen-point footprint and flat roof retained; actual roof/back elevations not visible in acquired photos','Shared edge15 fully opaque to taller3QueensGate; edge3 opaque only below estimated24aMews wall top6.849527m','No photographed steps or raised datum copied; original threshold near0 and coordinator ground support required']}
