"""4 Queens Gate: full mapped ring; individually completed terraced mews exterior.
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
    for neighbour in feature.get('audit',{}).get('adjacent_or_detailed_neighbours_within_35m',[]):
        geom=neighbour.get('shared_boundary_geometry'); interval=neighbour.get('shared_wall_potential_height_interval_m')
        if geom and geom.get('type')=='LineString' and interval:
            coords=geom['coordinates']
            for ei,(a,b,L,u,n) in enumerate(edges):
                if (math.dist(a,coords[0])<.01 and math.dist(b,coords[-1])<.01) or (math.dist(b,coords[0])<.01 and math.dist(a,coords[-1])<.01):
                    shared.append({'edge':ei,'neighbour':neighbour['id'],'polyline':coords,'height_interval':interval,'policy':'retain full wall; suppress overlapping speculative apertures'})
    split=H/levels
    floor_bounds=[i*H/levels for i in range(levels+1)]
    for ei,(a,b,L,u,n) in enumerate(edges):
        def at(s,d,z):return (a[0]+u[0]*s+n[0]*d,a[1]+u[1]*s+n[1]*d,z0+z)
        def panel(g,m,l,r,lo,hi,d=-.18,t=.36):block(g,m,at((l+r)/2,d,(lo+hi)/2),(r-l,t,hi-lo),u,n)
        # Long street wall gets differentiated workshop bays; short return faces remain complete.
        count=3 if ei==6 else max(1,int(L/4.25)) if L>2.5 else 0
        centers=[(i+.5)*L/count for i in range(count)] if count else []
        entry_s=((ep[0]-a[0])*u[0]+(ep[1]-a[1])*u[1]) if ep and ei==entry_edge else L*.5
        for level,(low,high) in enumerate(zip(floor_bounds,floor_bounds[1:])):
            holes=[]
            for bi,s in enumerate(centers):
                w=min((1.45 if level in (1,2) else 1.20) if ei==6 else 1.0,L/count-.8)
                bot=low+(.52 if level==0 else .68);top=high-.45
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
                    holes=[h for h in holes if h[4] or z0+h[3]<=lo or z0+h[2]>=hi]
            cuts=sorted({0.,L,*[q for h in holes for q in h[:2]]})
            for l,r in zip(cuts,cuts[1:]):
                hole=next((h for h in holes if h[0]-1e-7<=(l+r)/2<=h[1]+1e-7),None)
                if hole:
                    panel('pierced masonry','masonry',l,r,low,hole[2])
                    if ei==6 and level==3 and not hole[4]:
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
                if ei==6 and level==3 and not door:
                    rad=(r-l)/2;spring=top-rad
                    panel('recessed arched glazing','glass',l+.07,r-.07,bot+.07,spring,-.30,.055)
                    vs=[at(s,-.30,spring)]+[at(s+(rad-.07)*math.cos(math.pi*j/24),-.30,spring+(rad-.07)*math.sin(math.pi*j/24)) for j in range(25)]
                    meshpart('recessed arched glazing','glass',vs,[(0,j+1,j+2) for j in range(24)])
                    for j in range(24):
                        aa=math.pi*j/24;bb=math.pi*(j+1)/24
                        vs=[at(s+rr*math.cos(q),dd,spring+rr*math.sin(q)) for dd in [-.245,-.17] for rr,q in [(rad-.065,aa),(rad-.065,bb),(rad+.065,bb),(rad+.065,aa)]]
                        meshpart('arched frame','trim',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
                else:panel('recessed door' if door else 'recessed glazing','door' if door else 'glass',l+.07,r-.07,bot+(0 if door else .07),top-.07,-.30,.055)
                for xx in [l+.035,r-.035]:panel('painted joinery','trim',xx-.035,xx+.035,bot,top,-.22,.09)
                for zz in ([top-.035] if door else [bot+.035] if ei==6 and level==3 else [bot+.035,top-.035]):panel('painted joinery','trim',l,r,zz-.035,zz+.035,-.22,.09)
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
                    interface={'threshold_xyz':list(at(s,0,0)),'outward_normal':[n[0],n[1],0],'clear_width_m':r-l-.16,'door_leaf_xyz':list(at(s,-.30,(top+bot)/2)),'stair_treads':[],'ramp':'none; supporting ground retained by coordinator','surface_owner':'coordinator','basis':'retained baseline entry projected to mapped wall; aperture artistic'}
                    if ei==entry_edge:entrance=interface
                    else:
                        interface['basis']='HE group portico, speculative number4 front door position';additional_entrances.append(interface)
                        additional_supports.append({'center_xy':list(at(s,0,0)[:2]),'threshold_xyz':list(at(s,0,0)),'outward_normal':[n[0],n[1],0],'clear_width_m':r-l-.16,'reason':'artistic front portico door; coordinator owns finite support'})
                openings.append({'edge':ei,'floor':level,'bay':bi,'type':'door' if door else 'window','width_m':r-l,'height_m':top-bot,'recess_m':.30,'basis':'HE group character with individual artistic completion'})
        if ei==6:
            # Text-led group character, individually simplified; no special no1 colonnade.
            for zz in [split,3*split,4*split,5*split]:panel('street cornice','trim',.05,L-.05,zz-.10,zz+.08,.09,.24)
            for ss in [.30,L/3,2*L/3,L-.30]:
                panel('middle storey pilasters','trim',ss-.11,ss+.11,split+.20,3*split-.20,.07,.16)
                for zz in [split+.22,2*split-.16,3*split-.18]:panel('simplified capitals','trim',ss-.20,ss+.20,zz,zz+.16,.12,.24)
            panel('first floor balcony deck','trim',.12,L-.12,split-.18,split-.03,.45,.92)
            panel('balcony upper rail','trim',.15,L-.15,split+.90,split+1.02,.87,.12)
            for j in range(28):
                ss=.22+j*(L-.44)/27
                block('balcony balusters','trim',at(ss,.87,split+.44),(.065,.065,.82),u,n)
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
    roofring=offset(-.27);vv=[Vector((x,y,z0+H-.04)) for x,y in roofring]
    vs=[];fs=[]
    for tri in tessellate_polygon([vv]):
        off=len(vs);vs.extend(tuple(vv[v] if isinstance(v,int) else v) for v in tri);fs.append((off,off+1,off+2))
    meshpart('concave roof membrane','roof',vs,fs)
    created=[]
    for (g,m),(vs,fs) in groups.items():
        if not fs:continue
        name='4 Queens Gate | '+g;mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update()
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
        ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;ob['evidence_status']='Mapped footprint; OSM six levels retained; HE group five-storey description disagrees; artistic individual completion';created.append(ob.name)
    return {'created':created,'parameters':{'height_m':H,'base_z':z0,'levels':levels,'opening_count':len(openings),'wall_thickness_m':.36,'roof_max_z':z0+H+.38},'interfaces':{'entrance':entrance,'additional_entrances':additional_entrances,'additional_supports':additional_supports,'shared_walls':shared,'shared_wall_policy':'All mapped boundary walls retained; no unverified party-wall deletions'},'openings':openings,'evidence_source_ids':['osm-809238784','he-1226082','number2-context-2019'],'uncertainty':['Exact number4 facade not confirmed in licensed images; number2 photograph is only same-group context; opening positions artistic','OSM address4 retained; exact current facade not independently identified; HE group five storeys conflicts with OSM six and no metric correction is justified','Flat roof, parapet and door proportions artistically completed; existing eaves height retained exactly; no roof plant inferred','Shared edges0/5 opaque to common eaves, edge3 below6.85m; full walls preserved; upper rear openings artistic']}
