"""1 Princes Gate Mews: mapped two-storey house, licensed streetscape-informed artistic detail.
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
    z0=float(feature.get('base_z',.05));H=float(feature['height_m']);levels=max(1,int(feature.get("levels",4)));pitch=H/levels
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
    # Consume every coordinator-normalized segment, including partial edges.
    common=[]
    for seg in feature.get('audit',{}).get('normalized_shared_wall_segments',[]):
        ei=int(seg['edge']);a,L,u,n=edges[ei];line=seg['polyline']
        spans=sorted(sum((v[k]-a[k])*u[k] for k in range(2)) for v in line)
        lo=max(0,spans[0]);hi=min(L,spans[-1]);zz=seg.get('height_interval') or [z0,z0+H]
        if hi-lo>.001:common.append({'edge':ei,'s_interval':[lo,hi],'height_interval':zz,'polyline':line,'neighbour':seg['neighbour'],'openings':[],'basis':seg.get('basis','audited shared segment')})
    def blocked(ei,l,r,bot,top):return any(c['edge']==ei and l<c['s_interval'][1] and r>c['s_interval'][0] and z0+bot<c['height_interval'][1] and z0+top>c['height_interval'][0] for c in common)
    for ei,(a,L,u,n) in enumerate(edges):
        def at(s,d,z):return(a[0]+u[0]*s+n[0]*d,a[1]+u[1]*s+n[1]*d,z0+z)
        def panel(g,m,l,r,lo,hi,d=-.2,t=.4):box(g,m,at((l+r)/2,d,(lo+hi)/2),(r-l,t,hi-lo),u,n)
        count=(3 if ei==entry_edge else max(1,round(L/3.1))) if L>2.0 else 0
        centers=[L*(k+.5)/count for k in range(count)]
        door_s=sum((exy[k]-a[k])*u[k] for k in range(2)) if exy and ei==entry_edge else L/2
        for floor in range(levels):
            low=pitch*floor;high=pitch*(floor+1);holes=[]
            for bi,s in enumerate(centers):
                w=min(1.62 if floor==0 else 1.24,L/count-.7);bot=low+(.72 if floor==0 else .83);top=high-.60
                if floor==0 and ei==entry_edge and abs(s-door_s)<1.75:continue
                if blocked(ei,s-w/2,s+w/2,bot,top):continue
                holes.append((s-w/2,s+w/2,bot,top,False,bi))
            if floor==0 and ei==entry_edge:
                w=float(entry.get('clear_width_m',1.05))+.16
                holes.append((door_s-w/2,door_s+w/2,0,min(3,high-.12),True,-1))
            cuts=sorted(set([0,L]+[v for h in holes for v in h[:2]]))
            for l,r in zip(cuts,cuts[1:]):
                h=next((h for h in holes if h[0]<(l+r)/2<h[1]),None)
                if h:panel('pierced muted masonry facades','masonry',l,r,low,h[2]);panel('pierced muted masonry facades','masonry',l,r,h[3],high)
                else:panel('pierced muted masonry facades','masonry',l,r,low,high)
            for l,r,bot,top,door,bi in holes:
                s=(l+r)/2;w=r-l
                panel('entrance leaves' if door else 'recessed mews sash glazing','door' if door else 'glass',l+.065,r-.065,bot if door else bot+.06,top-.06,-.34,.06)
                for xx in (l+.035,r-.035):panel('painted sash frames','trim',xx-.035,xx+.035,bot,top,-.26,.11)
                for zz in ((top-.035,) if door else (bot+.035,top-.035)):panel('painted sash frames','trim',l,r,zz-.035,zz+.035,-.26,.11)
                if not door:
                    for frac in (1/3,2/3):panel('plain sash mullions','trim',l+w*frac-.02,l+w*frac+.02,bot,top,-.245,.055)
                    for frac in (.5,):panel('plain sash transoms','trim',l,r,bot+(top-bot)*frac-.021,bot+(top-bot)*frac+.021,-.245,.055)
                    panel('stone window sills','trim',l-.09,r+.09,bot-.105,bot-.025,.035,.21)
                    panel('subtle brick headers','masonry',l-.06,r+.06,top+.015,top+.13,.025,.12)
                else:
                    for xx in (l-.105,r+.105):panel('plain entrance jambs','trim',xx-.07,xx+.07,0,top+.12,.025,.18)
                    panel('plain entrance lintel','trim',l-.19,r+.19,top,top+.14,.025,.18)
                    panel('entry transom','trim',l,r,top-.6,top-.53,-.25,.11)
                    panel('door recessed lower panel','door',l+.16,r-.16,.3,1.12,-.295,.045)
                    panel('door recessed upper panel','door',l+.16,r-.16,1.3,top-.75,-.295,.045)
                    box('door hardware','metal',at(s+.28,-.19,1.1),(.035,.08,.24),u,n)
                    panel('flush threshold','trim',l-.12,r+.12,-.006,0,-.17,.40)
                    entrance={'threshold_xyz':list(at(s,0,0)),'outward_normal':[n[0],n[1],0],'clear_width_m':w-.16,'door_leaf_xyz':list(at(s,-.34,top/2)),'stair_treads':[],'ramp':'none authored','surface_owner':'coordinator','basis':'preserved baseline lateral position; threshold projected to wall'}
                openings.append({'edge':ei,'floor':floor,'bay':bi,'type':'door' if door else 'window','width_m':w,'height_m':top-bot,'recess_m':.34,'basis':'artistic mews house arrangement; exact no.1 not identified in licensed views'})
        # Pale stone ground-floor base skirt; above openings sill height.
        if ei!=entry_edge:panel('plain brick plinth','masonry',0,L,.02,.32,.015,.10)
        else:
            panel('plain brick plinth','masonry',0,max(0,door_s-.78),.02,.32,.015,.1);panel('plain brick plinth','masonry',min(L,door_s+.78),L,.02,.32,.015,.1)
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
    for zz,th,dep in [(pitch,.08,.015),(H-.10,.13,.025)]:band('plain eaves and floor course','trim',zz-th/2,zz+th/2,dep,.22)
    band('low mews roof parapet','masonry',H,H+.24,-.17,.34);band('shallow parapet coping','trim',H+.24,H+.31,-.17,.34)
    vv=[Vector((x,y,z0+H-.06)) for x,y in ring];v=[];f=[]
    for tri in tessellate_polygon([vv]):
        off=len(v);v.extend(tuple(vv[q] if isinstance(q,int) else q) for q in tri);f.append((off,off+1,off+2))
    mesh('complete concave roof deck','roof',v,f)
    created=[]
    for (g,m),(v,f) in groups.items():
        if not f:continue
        name='1 Princes Gate Mews | '+g;me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;ob['evidence_status']='OSM-addressed two-storey house; exact-photo identification unresolved; streetscape-informed artistic detail';created.append(ob.name)
    return {'created':created,'parameters':{'height_m':H,'eaves_height_m':H,'base_z':z0,'levels':levels,'roof_levels':0,'roof_max_z':z0+H+.31,'opening_count':len(openings),'wall_thickness_m':.4},'interfaces':{'entrance':entrance,'additional_entrances':[],'shared_walls':common},'openings':openings,'roof_parts':roof_parts,'evidence_source_ids':['osm-851362835','mews-west-2023','mews-east-2023','mews-entry-2015','rbkc-1mews-garage-2012'],'uncertainty':['OSM address and two levels retained; eaves 6.850189m is inherited formula estimate, not survey','Three licensed streetscape photographs inspected but none reliably identifies no.1; muted masonry, pale sash joinery and shallow coping are contextual, opening layout and flat roof artistic','Nearby mansards, roof terraces and garage fronts are not asserted for this property; 2012 garage condition removal establishes history only','Complete five-point roof and walls preserved; two normalized shared intervals remain opaque at audited estimated neighbour heights','Original threshold/base retained; no external ground authored. Raised Traffic-road display geometry is owned by coordinator']}
