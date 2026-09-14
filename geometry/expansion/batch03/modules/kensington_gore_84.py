"""84 Kensington Gore: full mapped ring; two-storey red brick office/mews with estimated quadruple saltbox roof.
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
        count=max(1,int(L/2.85)) if L>2.5 else 0
        centers=[(i+.5)*L/count for i in range(count)] if count else []
        entry_s=((ep[0]-a[0])*u[0]+(ep[1]-a[1])*u[1]) if ep and ei==entry_edge else L*.5
        for level,(low,high) in enumerate(zip(floor_bounds,floor_bounds[1:])):
            holes=[]
            for bi,s in enumerate(centers):
                w=min(1.25 if level==0 else 1.10,L/count-.8)
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
                    panel('pierced masonry','masonry',l,r,low,hole[2]);panel('pierced masonry','masonry',l,r,hole[3],high)
                else:panel('pierced masonry','masonry',l,r,low,high)
            for l,r,bot,top,door,bi in holes:
                s=(l+r)/2
                panel('recessed door' if door else 'recessed glazing','door' if door else 'glass',l+.07,r-.07,bot+(0 if door else .07),top-.07,-.30,.055)
                for xx in [l+.035,r-.035]:panel('painted joinery','trim',xx-.035,xx+.035,bot,top,-.22,.09)
                for zz in ([top-.035] if door else [bot+.035,top-.035]):panel('painted joinery','trim',l,r,zz-.035,zz+.035,-.22,.09)
                # Segmental masonry arch made from discrete solid wedge voussoirs.
                rise=.22; radius=((r-l)/2)**2/(2*rise)+rise/2; cy=top+rise-radius
                theta=math.asin((r-l)/2/radius)
                for k in range(9):
                    angles=[-theta+2*theta*(k+.035)/9,-theta+2*theta*(k+.965)/9]
                    pts=[]
                    for depth in [.005,.16]:
                        for rr,ang in [(radius,angles[0]),(radius,angles[1]),(radius+.17,angles[1]),(radius+.17,angles[0])]:
                            pts.append(at(s+rr*math.sin(ang),depth,cy+rr*math.cos(ang)))
                    meshpart('segmental brick arch heads','masonry',pts,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
                if not door:
                    panel('projecting sills','trim',l-.09,r+.09,bot-.11,bot-.035,.035,.21)
                    for xx in ([s-(r-l)/6,s+(r-l)/6] if level==0 else [s]):panel('window mullions','trim',xx-.023,xx+.023,bot,top,-.21,.07)
                    panel('window transoms','trim',l,r,(top+bot)/2-.025,(top+bot)/2+.025,-.21,.07)
                    # Upper sash has a finer six-light pattern, not a repeated studio grille.
                    if level>0:
                        for xx in [s-(r-l)/6,s+(r-l)/6]:panel('fine sash bars','trim',xx-.013,xx+.013,bot,top,-.20,.045)
                else:
                    panel('door transom','trim',l,r,top-.44,top-.37,-.20,.07)
                    panel('door glass fanlight','glass',l+.08,r-.08,top-.36,top-.08,-.27,.035)
                    panel('threshold','trim',l-.10,r+.10,-.006,0,-.22,.44)
                    block('door handle','metal',at(r-.2,-.20,1.1),(.025,.055,.24),u,n)
                    entrance={'threshold_xyz':list(at(s,0,0)),'outward_normal':[n[0],n[1],0],'clear_width_m':r-l-.16,'door_leaf_xyz':list(at(s,-.30,(top+bot)/2)),'stair_treads':[],'ramp':'none; supporting ground retained by coordinator','surface_owner':'coordinator','basis':'retained baseline entry projected to mapped wall; aperture artistic'}
                openings.append({'edge':ei,'floor':level,'bay':bi,'type':'door' if door else 'window','width_m':r-l,'height_m':top-bot,'recess_m':.30,'basis':'artistic mews completion'})
        if L>5 and not any(q['edge']==ei for q in shared):
            for s in [.32,L-.32]:
                block('rainwater downpipes','metal',at(s,.085,H/2),(.085,.085,H),u,n)
                for zz in [1.,3.1,5.7]:block('pipe brackets','metal',at(s,.04,zz),(.17,.18,.055),u,n)
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
    for zz in floor_bounds[1:-1]:band('flush storey trim','trim',zz-.055,zz+.055,-.065,.12)
    band('inward eaves fascia','trim',H-.13,H+.02,-.10,.18)
    
    # Exact concave triangulation with 5.2 integer-index compatibility; no invented roof equipment.
    roofring=ring;vv=[Vector((x,y,z0+H-.04)) for x,y in roofring]
    vs=[];fs=[]
    for tri in tessellate_polygon([vv]):
        off=len(vs);vs.extend(tuple(vv[v] if isinstance(v,int) else v) for v in tri);fs.append((off,off+1,off+2))
    meshpart('complete mapped roof base cap','roof',vs,fs)
    # Clip each base triangle in long-axis coordinates: exact nonconvex coverage.
    # Four asymmetric ridges are an artistic interpretation of OSM quadruple_saltbox.
    a0=ring[0];a1=ring[3];ll=math.dist(a0,a1);axis=((a1[0]-a0[0])/ll,(a1[1]-a0[1])/ll)
    def station(p):return (p[0]-a0[0])*axis[0]+(p[1]-a0[1])*axis[1]
    station_min=min(station(p) for p in ring);station_max=max(station(p) for p in ring)
    pitch=(station_max-station_min)/4
    def clip(poly,t,keep_high):
        out=[]
        for p,q in zip(poly,poly[1:]+poly[:1]):
            dp=station(p)-t;dq=station(q)-t;ip=dp>=-1e-8 if keep_high else dp<=1e-8;iq=dq>=-1e-8 if keep_high else dq<=1e-8
            if ip:out.append(p)
            if ip!=iq:
                alpha=dp/(dp-dq);out.append((p[0]+alpha*(q[0]-p[0]),p[1]+alpha*(q[1]-p[1])))
        return out
    for strip in range(4):
        start=station_min+strip*pitch;end=start+pitch;ridge=start+.34*pitch
        for lower,upper,ascending in [(start,ridge,True),(ridge,end,False)]:
            def zz(p):
                t=station(p);fraction=(t-start)/(ridge-start) if ascending else (end-t)/(end-ridge)
                return z0+H+max(0,min(1,fraction))*1.6
            for face in fs:
                poly=[vs[i][:2] for i in face];poly=clip(clip(poly,lower,True),upper,False)
                if len(poly)<3:continue
                verts=[(p[0],p[1],zz(p)) for p in poly]
                meshpart('four asymmetric saltbox roof slopes','roof',verts,[(0,i,i+1) for i in range(1,len(verts)-1)])
            # Close vertical perimeter infill under the varying roof profile.
            for aa,bb in zip(ring,ring[1:]+ring[:1]):
                ta=station(aa);tb=station(bb)
                if abs(tb-ta)<1e-8:continue
                f0=max(0,min(1,(lower-ta)/(tb-ta)));f1=max(0,min(1,(upper-ta)/(tb-ta)))
                f0,f1=sorted((f0,f1))
                if f1-f0<1e-8:continue
                pa=(aa[0]+(bb[0]-aa[0])*f0,aa[1]+(bb[1]-aa[1])*f0);pb=(aa[0]+(bb[0]-aa[0])*f1,aa[1]+(bb[1]-aa[1])*f1)
                za,zb=zz(pa),zz(pb)
                verts=[(*pa,z0+H),(*pb,z0+H),(*pb,zb),(*pa,za)]
                # Triangle fan omits zero area faces at valley endpoints.
                faces=[]
                if zb>z0+H+1e-7:faces.append((0,1,2))
                if za>z0+H+1e-7:faces.append((0,2,3))
                meshpart('saltbox perimeter infill','masonry',verts,faces)
    created=[]
    for (g,m),(vs,fs) in groups.items():
        if not fs:continue
        name='84 Kensington Gore | '+g;mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.update()
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
        ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;ob['evidence_status']='Mapped footprint; OSM two levels and estimated quadruple saltbox roof; artistic terraced facade completion';created.append(ob.name)
    return {'created':created,'parameters':{'height_m':H,'base_z':z0,'levels':levels,'opening_count':len(openings),'wall_thickness_m':.36,'roof_max_z':z0+H+1.6},'interfaces':{'entrance':entrance,'shared_walls':shared,'shared_wall_policy':'All mapped boundary walls retained; no unverified party-wall deletions'},'openings':openings,'evidence_source_ids':['osm-492431542','84-office-description','84-mews-context'],'uncertainty':['Exact 84 Kensington Gore facade not confirmed in licensed images; all bay positions and window sizes artistically completed','OSM residential and brochure office use differ; no occupancy signage modelled','Four asymmetric roof strips artistically interpret OSM quadruple_saltbox; ridge organisation and height unobserved; existing eaves retained','Shared-wall adjacency unknown; full walls preserved']}
