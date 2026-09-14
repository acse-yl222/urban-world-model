"""24 Princes Gate: mapped five-storey townhouse, exact licensed street evidence and estimated hidden roof.
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
    z0=float(feature['base_z']);H=float(feature['height_m']);levels=max(1,int(feature.get("levels",4)));pitch=H/levels
    groups={};openings=[];entrance=None;roof_parts=[];additional=[];supports=[]
    materials=dict(materials);materials["masonry"]=materials["trim"] # exact pale-stucco facade
    bounds=[H*t for t in (0,.23,.48,.69,.87,1)]
    if levels!=5:raise ValueError("Five-storey evidence contract required")
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
        count=(3 if ei==3 else max(1,round(L/4.0))) if L>2.8 else 0
        centers=[L*(k+.5)/count for k in range(count)]
        door_info=entry if ei==entry_edge else feature.get('photo_front_entry') if ei==3 else None
        door_xy=door_info.get('center_xy') if door_info else None
        door_s=sum((door_xy[k]-a[k])*u[k] for k in range(2)) if door_xy else L/2
        for floor in range(levels):
            low=bounds[floor];high=bounds[floor+1];holes=[]
            for bi,s in enumerate(centers):
                w=min((1.82 if floor<4 else 1.28) if ei==3 else 1.20,L/count-.8);bot=low+(.30 if floor==1 else .52);top=high-(.76 if floor==1 else .42)
                if floor==0 and door_info and abs(s-door_s)<1.75:continue
                if blocked(ei,s-w/2,s+w/2,bot,top):continue
                holes.append((s-w/2,s+w/2,bot,top,False,bi))
            if floor==0 and door_info:
                w=float(door_info.get('clear_width_m',1.05))+.16
                holes.append((door_s-w/2,door_s+w/2,0,min(3.15,high-.20),True,-1))
            cuts=sorted(set([0,L]+[v for h in holes for v in h[:2]]))
            for l,r in zip(cuts,cuts[1:]):
                h=next((h for h in holes if h[0]<(l+r)/2<h[1]),None)
                if h:panel('pierced muted masonry facades','masonry',l,r,low,h[2]);panel('pierced muted masonry facades','masonry',l,r,h[3],high)
                else:panel('pierced muted masonry facades','masonry',l,r,low,high)
            for l,r,bot,top,door,bi in holes:
                s=(l+r)/2;w=r-l
                panel('entrance leaves' if door else 'recessed townhouse sash glazing','door' if door else 'glass',l+.065,r-.065,bot if door else bot+.06,top-.06,-.34,.06)
                for xx in (l+.035,r-.035):panel('painted sash frames','trim',xx-.035,xx+.035,bot,top,-.26,.11)
                for zz in ((top-.035,) if door else (bot+.035,top-.035)):panel('painted sash frames','trim',l+.07,r-.07,zz-.035,zz+.035,-.26,.11)
                if not door:
                    for frac in (.5,):panel('plain sash mullions','trim',l+w*frac-.02,l+w*frac+.02,bot+.07,top-.07,-.245,.055)
                    for frac in (.5,):
                        zz=bot+(top-bot)*frac
                        for xa,xb in ((l+.07,s-.02),(s+.02,r-.07)):panel('plain sash transoms','trim',xa,xb,zz-.021,zz+.021,-.245,.055)
                    panel('stone window sills','trim',l-.09,r+.09,bot-.105,bot-.025,.035,.21)
                    panel('subtle brick headers','masonry',l-.06,r+.06,top+.015,top+.13,.025,.12)
                else:
                    for xx in (l-.105,r+.105):panel('plain entrance jambs','trim',xx-.07,xx+.07,0,top,.025,.18)
                    panel('plain entrance lintel','trim',l-.19,r+.19,top,top+.14,.025,.18)
                    panel('entry transom','trim',l,r,top-.6,top-.53,-.25,.11)
                    panel('door recessed lower panel','door',l+.16,r-.16,.3,1.12,-.295,.045)
                    panel('door recessed upper panel','door',l+.16,r-.16,1.3,top-.75,-.295,.045)
                    box('door hardware','metal',at(s+.28,-.19,1.1),(.035,.08,.24),u,n)
                    panel('flush threshold','trim',l-.12,r+.12,-.006,0,-.17,.40)
                    this_entry={'threshold_xyz':list(at(s,0,0)),'outward_normal':[n[0],n[1],0],'clear_width_m':w-.16,'door_leaf_xyz':list(at(s,-.34,top/2)),'stair_treads':[],'ramp':'none authored','surface_owner':'coordinator','basis':door_info.get('basis','preserved baseline entry'), 'edge':ei}
                    if ei==entry_edge:entrance=this_entry
                    else:
                        this_entry['audited_ground_z']=door_info['audited_ground_z'];additional.append(this_entry)
                openings.append({'edge':ei,'floor':floor,'bay':bi,'type':'door' if door else 'window','width_m':w,'height_m':top-bot,'recess_m':.34,'basis':'exact-photo three-bay rectangular north facade; metric arrangement and hidden facades estimated'})
        # Pale stone ground-floor base skirt; above openings sill height.
        if not door_info:panel('plain brick plinth','masonry',0,L,.02,.32,.015,.10)
        else:
            panel('plain brick plinth','masonry',0,max(0,door_s-.78),.02,.32,.015,.1);panel('plain brick plinth','masonry',min(L,door_s+.78),L,.02,.32,.015,.1)
        if ei==3:
            # Shallow ground-floor channels skip every aperture, avoiding strips
            # laid across glazing or the photo-supported doorway.
            for zz in (.32,.71,1.10,1.49,1.88,2.27,2.66,3.05):
                intervals=[(0,L)]
                masks=[(cs-.94,cs+.94) for cs in centers if abs(cs-door_s)>=1.75]+[(door_s-.78,door_s+.78)]
                for ml,mr in masks:
                    intervals=[p for lo,hi in intervals for p in ((lo,min(hi,ml)),(max(lo,mr),hi)) if p[1]-p[0]>.02]
                for lo,hi in intervals:panel('ground rustication arrises','trim',lo,hi,zz,zz+.035,.012,.06)
            # Three-bay first-floor order; shaft/capital junctions have no
            # overlapping front planes. Ionic porch is independent below.
            for cs in centers:
                for ss in (cs-1.08,cs+1.08):
                    panel('Corinthian simplified pilaster bases','trim',ss-.11,ss+.11,bounds[1]+.12,bounds[1]+.28,.055,.22)
                    panel('Corinthian pilaster shafts','trim',ss-.075,ss+.075,bounds[1]+.28,bounds[2]-.97,.06,.15)
                    panel('Corinthian simplified capitals','trim',ss-.15,ss+.15,bounds[2]-.97,bounds[2]-.78,.075,.26)
                    for dx in (-.09,0,.09):box('capital leaf blocks','trim',at(ss+dx,.235,bounds[2]-.85),(.045,.06,.11),u,n)
                panel('first order window entablature','trim',cs-1.30,cs+1.30,bounds[2]-.76,bounds[2]-.56,.07,.30)
                for k in range(10):box('window entablature dentils','trim',at(cs-1.17+k*.26,.22,bounds[2]-.78),(.09,.11,.08),u,n)
                panel('second-floor window hood','trim',cs-1.06,cs+1.06,bounds[3]-.36,bounds[3]-.23,.07,.24)
            cs=centers[1];zz=bounds[2]-.55
            vs=[at(cs+x,d,zz+y) for d in (.015,.255) for x,y in [(-1.30,0),(1.30,0),(0,.43)]]
            mesh('central triangular pediment','trim',vs,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)])
            # Broad continuous stone balcony observed across first floor.
            balcony=bounds[1]+.10
            panel('continuous stone balcony deck','trim',.08,L-.08,balcony-.15,balcony,.43,1.12)
            panel('continuous stone balcony handrail','trim',.08,L-.08,balcony+.81,balcony+.91,.87,.24)
            def turned(ss,dd,profile,name):
                N=16;v=[at(ss+rad*math.cos(2*math.pi*k/N),dd+rad*math.sin(2*math.pi*k/N),zz) for zz,rad in profile for k in range(N)];F=len(profile)
                faces=[tuple(range(N-1,-1,-1)),tuple(range((F-1)*N,F*N))]
                for j in range(F-1):
                    for k in range(N):faces.append((j*N+k,j*N+(k+1)%N,(j+1)*N+(k+1)%N,(j+1)*N+k))
                mesh(name,'trim',v,faces)
            for k in range(30):
                ss=.23+k*(L-.46)/29
                turned(ss,.87,[(balcony,.060),(balcony+.09,.080),(balcony+.25,.055),(balcony+.48,.075),(balcony+.70,.038),(balcony+.81,.060)],'stone turned balcony balusters')
            for ss in (.13,L-.13):panel('stone balcony end piers','trim',ss-.10,ss+.10,balcony,balcony+.81,.87,.26)
            # Projecting Ionic porch, approximate proportions; bases must meet
            # coordinator-supplied finite support at exactly the feature datum.
            ph=float(door_info['porch_half_width_m']);cd=float(door_info['column_outward_m']);cs_off=float(door_info['column_lateral_offset_m'])
            for ss in (door_s-cs_off,door_s+cs_off):
                box('Ionic porch plinth','trim',at(ss,cd,.05),(.44,.44,.10),u,n)
                turned(ss,cd,[(.10,.19),(.20,.17),(3.14,.145),(3.24,.20)],'Ionic porch shafts')
                box('Ionic porch abacus','trim',at(ss,cd,3.30),(.44,.44,.12),u,n)
                # Paired scroll disks, simplified rather than literal sculpture.
                for dx in (-.16,.16):
                    N=16;vv=[at(ss+dx+.10*math.cos(k*2*math.pi/N),d,3.22+.10*math.sin(k*2*math.pi/N)) for d in (cd+.16,cd+.24) for k in range(N)]
                    ff=[tuple(range(N-1,-1,-1)),tuple(range(N,2*N))]+[(k,(k+1)%N,(k+1)%N+N,k+N) for k in range(N)]
                    mesh('Ionic capital volutes','trim',vv,ff)
            panel('Ionic porch entablature','trim',door_s-(ph-.06),door_s+(ph-.06),3.36,balcony-.15,.43,1.18)
            supports.append({'polygon_xy':[list(at(door_s+x,d,0)[:2]) for x,d in [(-ph,door_info['porch_support_depth_interval_m'][0]),(ph,door_info['porch_support_depth_interval_m'][0]),(ph,door_info['porch_support_depth_interval_m'][1]),(-ph,door_info['porch_support_depth_interval_m'][1])]],'top_z':z0,'basis':'Estimated Ionic porch feet support; coordinator owns ground'})
            # Corner quoins and plain fifth-storey cornice, without a sixth tier.
            for zz in (bounds[1]+.25,bounds[1]+.68,bounds[1]+1.11,bounds[1]+1.54,bounds[1]+1.97,bounds[1]+2.40):
                for lo,hi in ((0,.30),(L-.30,L)):panel('end terrace rusticated quoins','trim',lo,hi,zz,zz+.23,.035,.12)
            # Exact24 has a plainer top cornice than25, plus visible slim
            # upper-window railings. No25's dense eaves brackets copied here.
            panel('plain fifth-storey front cornice','trim',.03,L-.03,H-.26,H-.13,.065,.22)
            for fl in (2,3):
                zb=bounds[fl]+.52
                for cs in centers:
                    panel('upper Juliet top rail','metal',cs-.81,cs+.81,zb+.69,zb+.735,.20,.045)
                    for k in range(9):box('upper Juliet vertical bars','metal',at(cs-.75+k*.1875,.20,zb+.34),(.023,.028,.68),u,n)

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
    for zz,th,dep in [(bounds[1],.12,.015),(bounds[2],.10,.015),(H-.12,.17,.025)]:band('plain eaves and floor course','trim',zz-th/2,zz+th/2,dep,.22)
    band('low hidden roof parapet','masonry',H-.005,H+.24,-.18,.34);band('shallow parapet coping','trim',H+.235,H+.31,-.18,.37)
    vv=[Vector((x,y,z0+H+.008)) for x,y in ring];v=[];f=[]
    for tri in tessellate_polygon([vv]):
        off=len(v);v.extend(tuple(vv[q] if isinstance(q,int) else q) for q in tri);f.append((off,off+1,off+2))
    mesh('complete four-point roof deck','roof',v,f)
    roof_parts.append({'type':'complete_polygon_flat_deck','z':z0+H+.008,'footprint':ring,'basis':'artistic roof completion; exact roof unconfirmed'})
    roof_parts.append({'type':'continuous_mitred_parapet_and_coping','max_z':z0+H+.31,'basis':'artistic low parapet'})
    if entrance:entrance["additional_supports"]=supports
    created=[]
    for (g,m),(v,f) in groups.items():
        if not f:continue
        name='24 Princes Gate | '+g;me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;ob['evidence_status']='OSM full concave plan; HE1265482 five levels and exact licensed no24 facade; hidden geometry estimated';created.append(ob.name)
    return {'created':created,'parameters':{'height_m':H,'eaves_height_m':H,'base_z':z0,'levels':levels,'roof_levels':0,'roof_max_z':z0+H+.31,'opening_count':len(openings),'wall_thickness_m':.4,'floor_bounds_m':bounds,'front_edge':3},'interfaces':{'entrance':entrance,'additional_entrances':additional,'shared_walls':common},'openings':openings,'roof_parts':roof_parts,'evidence_source_ids':['osm-640097056','he-1265482','front23-25-2017'],'uncertainty':['HE1265482 and exact numbered2017photo support five storeys; metric H16.299562m remains inherited estimate','Short fifth tier is included in five levels, no additional attic storey','North front Ionic porch and three-bay order follow exact24photo, plain top cornice and upper Juliet rails distinguish24 from25; positions and dimensions estimated','Full four-point roof is artistically completed behind low parapet; hidden rear facades and roof equipment unverified','Both normalized common walls against25 and23 retained opaque over supplied height intervals','Original south entrance retained primary; added north photo door and porch support by coordinator; no basement excavation or terrain survey claim']}
