"""71–72 Princes Gate: licensed entrance observation, official terrace form.
Metric heights, hidden elevations and mansard profile remain explicit estimates.
"""
import math

def build(feature, materials):
    import bpy,bmesh
    from mathutils import Vector
    from mathutils.geometry import tessellate_polygon
    ring=[tuple(map(float,p[:2])) for p in feature['ring']]
    if ring[0]==ring[-1]:ring.pop()
    area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1]))/2
    if area<=0:raise ValueError('CCW ring required')
    z0=float(feature['base_z']);H=float(feature['height_m']);E=feature['entry']
    floors=[H*q for q in[0,.225,.455,.655,.835,1]]
    groups={};openings=[];entrance=None
    def mesh(g,m,v,f):
        vs,fs=groups.setdefault((g,m),([],[]));off=len(vs);vs.extend(v);fs.extend(tuple(off+i for i in face)for face in f)
    def box(g,m,c,size,u=(1,0),n=(0,1)):
        if min(size)<=1e-7:return
        x,y,z=c;w,d,h=[v/2 for v in size]
        vv=[(x+i*w*u[0]+j*d*n[0],y+i*w*u[1]+j*d*n[1],z+k*h)for i,j,k in[(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        mesh(g,m,vv,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    edges=[]
    for a,b in zip(ring,ring[1:]+ring[:1]):
        L=math.dist(a,b);u=((b[0]-a[0])/L,(b[1]-a[1])/L);edges.append((a,L,u,(u[1],-u[0])))
    def at(e,s,d,z):
        a,L,u,n=edges[e];return(a[0]+u[0]*s+n[0]*d,a[1]+u[1]*s+n[1]*d,z0+z)
    def panel(e,g,m,l,r,b,t,d=-.22,depth=.44):
        if r-l>1e-7 and t-b>1e-7:box(g,m,at(e,(l+r)/2,d,(b+t)/2),(r-l,depth,t-b),edges[e][2],edges[e][3])
    def column(g,xy,low,high,r):
        prof=[(low,r*1.40),(low+.08,r*1.40),(low+.16,r),(high-.18,r*.88),(high-.10,r*1.2),(high,r*1.5)]
        vv=[(xy[0]+rr*math.cos(k*math.pi/8),xy[1]+rr*math.sin(k*math.pi/8),z0+z)for z,rr in prof for k in range(16)];ff=[]
        for j in range(len(prof)-1):
            for k in range(16):q=(k+1)%16;ff.append((j*16+k,j*16+q,(j+1)*16+q,(j+1)*16+k))
        ff.extend([tuple(range(15,-1,-1)),tuple((len(prof)-1)*16+k for k in range(16))]);mesh(g,'trim',vv,ff)
    # One contract for every normalized disjoint segment, never the first line only.
    common=[]
    for seg in feature['audit']['normalized_shared_wall_segments']:
        ei=int(seg['edge']);a,L,u,n=edges[ei];line=seg['polyline']
        span=sorted(sum((p[k]-a[k])*u[k]for k in[0,1])for p in[line[0],line[-1]])
        zz=[max(z0,seg['height_interval'][0]),min(z0+H,seg['height_interval'][1])]
        if span[1]-span[0]<=1e-6 or zz[1]<=zz[0]:raise ValueError('Invalid shared segment')
        common.append({'edge':ei,'s_interval':[max(0,span[0]),min(L,span[1])],'height_interval':zz,'polyline':line,'neighbour':seg['neighbour'],'openings':[]})
    def blocked(e,l,r,b,t):return any(c['edge']==e and l<c['s_interval'][1]+.08 and r>c['s_interval'][0]-.08 and z0+b<c['height_interval'][1]+.15 and z0+t>c['height_interval'][0]for c in common)
    ee=E['edge_index'];ea,EL,eu,en=edges[ee];es=sum((E['center_xy'][k]-ea[k])*eu[k]for k in[0,1])
    # Six front bays: two historic three-window-wide houses, not six arbitrary units.
    for ei,(a,L,u,n) in enumerate(edges):
        if ei==0:positions=[L*(i+.5)/6 for i in range(6)]
        elif ei in[1,3,5,10,12]:positions=[]  # Narrow inset return cheeks stay solid.
        else:
            count=max(1,int(L/3.3));positions=[L*(i+.5)/count for i in range(count)]
        for floor,(lo,hi)in enumerate(zip(floors,floors[1:])):
            holes=[]
            for bi,s in enumerate(positions):
                w=1.38 if ei==0 and floor==1 else 1.24 if ei==0 else 1.12
                bot=lo+(.62 if floor!=1 else .32);top=hi-(.65 if floor<4 else .48)
                if s-w/2<.26 or s+w/2>L-.26:continue
                if floor==0 and ei==ee and abs(s-es)<w/2+.86:continue
                if blocked(ei,s-w/2,s+w/2,bot,top):continue
                holes.append((s-w/2,s+w/2,bot,top,False,bi))
            if floor==0 and ei==ee:
                w=E['clear_width_m']+.14;bot=E['threshold_z']-z0
                if blocked(ei,es-w/2,es+w/2,bot,2.88):raise ValueError('Source entrance conflicts shared wall')
                holes.append((es-w/2,es+w/2,bot,2.88,True,-1))
            holes.sort();cursor=0
            for l,r,bot,top,door,bi in holes:
                panel(ei,'pierced wall piers','masonry',cursor,l,lo,hi)
                panel(ei,'pierced wall sill infill','masonry',l,r,lo,bot)
                panel(ei,'pierced wall lintel infill','masonry',l,r,top,hi)
                mid=(l+r)/2
                panel(ei,'wood entrance leaf'if door else'recessed sash glazing','door'if door else'glass',l+.05,r-.05,bot if door else bot+.04,top-.04,-.35,.05)
                for x in[l+.028,r-.028]:panel(ei,'entrance jamb'if door else'timber sash side frames','trim',x-.028,x+.028,bot,top,-.10,.12)
                panel(ei,'entrance head frame'if door else'timber sash upper rail','trim',l,r,top-.055,top,-.10,.12)
                if door:
                    for zz in[.6,1.45,2.15]:panel(ei,'door leaf panel mouldings','door',l+.16,r-.16,zz-.22,zz+.22,-.317,.025)
                    panel(ei,'entrance glazed transom','glass',l+.08,r-.08,2.40,2.78,-.317,.025)
                    panel(ei,'door leaf transom rail','door',l+.07,r-.07,2.35,2.41,-.29,.06)
                    for x in[l-.10,r+.10]:panel(ei,'entrance stone surrounds','trim',x-.07,x+.07,bot,top+.12,.04,.18)
                    panel(ei,'entrance stone head','trim',l-.17,r+.17,top,top+.14,.04,.18)
                    entrance={'threshold_xyz':[*E['center_xy'],E['threshold_z']],'outward_normal':[*n,0.0],'door_leaf_xyz':list(at(ei,mid,-.35,(bot+top)/2)),'clear_width_m':E['clear_width_m'],'clear_height_m':top-bot,'leaf_recess_m':.35,'stair_treads':[],'ramp':'none authored','surface_owner':'coordinator','additional_supports':[],'basis':'Coordinator raised threshold .074 above visible source paving .068, original tangent location retained'}
                else:
                    for zz in[bot+.03,(bot+top)/2]:panel(ei,'sash meeting and bottom rails','trim',l,r,zz-.025,zz+.025,-.10,.11)
                    if floor==1:panel(ei,'first floor French casement mullion','trim',mid-.025,mid+.025,bot,top,-.095,.11)
                    panel(ei,'projecting stone sill','trim',l-.12,r+.12,bot-.11,bot+.01,.06,.30)
                    for x in[l-.06,r+.06]:panel(ei,'architrave upright','trim',x-.045,x+.045,bot-.01,top+.09,.015,.13)
                    panel(ei,'architrave head','trim',l-.105,r+.105,top+.02,top+.13,.025,.16)
                    if ei==0:
                        if floor==1:
                            for x in[l-.21,r+.21]:
                                column('first floor Corinthian shafts',at(0,x,.18,0)[:2],bot-.1,top+.10,.070)
                                for k in[-1,0,1]:box('simplified Corinthian leaf blocks','trim',at(0,x+k*.058,.21,top+.065),(.065,.17,.13),u,n)
                        elif floor in[2,3]:
                            panel(0,'cornice window hoods','trim',l-.20,r+.20,top+.15,top+.28,.12,.34)
                            for x in[l-.10,r+.10]:panel(0,'window hood corbels','trim',x-.06,x+.06,top+.025,top+.15,.13,.27)
                            if floor==2 and bi in[1,4]:
                                # Closed triangular pediment prism, not floating rods.
                                pts=[(l-.22,top+.28),(r+.22,top+.28),(mid,top+.61)]
                                vv=[at(0,x,d,z)for d in[.01,.26]for x,z in pts]
                                mesh('central second floor pediment','trim',vv,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)])
                            if floor==2:
                                panel(0,'second floor balcony sill','trim',l-.18,r+.18,bot-.10,bot+.02,.20,.62)
                                for j in range(6):column('second floor bottle balusters',at(0,l+(r-l)*j/5,.45,0)[:2],bot+.02,bot+.64,.045)
                                panel(0,'second floor balcony rail','trim',l-.18,r+.18,bot+.64,bot+.74,.45,.18)
                openings.append({'edge':ei,'floor':floor,'s_interval':[l,r],'z_interval':[z0+bot,z0+top],'door':door})
                cursor=r
            panel(ei,'pierced wall piers','masonry',cursor,L,lo,hi)
        # Fine positive channel strips avoid every aperture and the entry threshold.
        if ei==0:
            for zz in[.28+j*.39 for j in range(int((floors[1]-.35)/.39))]:
                cuts=sorted((o['s_interval'][0]-.13,o['s_interval'][1]+.13)for o in openings if o['edge']==ei and o['z_interval'][0]-.08<=z0+zz<=o['z_interval'][1]+.08);cur=0
                for l,r in cuts:panel(ei,'ground stucco channel courses','trim',cur,max(cur,l),zz,zz+.025,.009,.026);cur=max(cur,r)
                panel(ei,'ground stucco channel courses','trim',cur,L,zz,zz+.025,.009,.026)
    def offset(d):
        out=[]
        for i,p in enumerate(ring):
            a=edges[i-1][3];b=edges[i][3];den=1+a[0]*b[0]+a[1]*b[1]
            if den<.08:raise ValueError('Unstable mitre')
            out.append(tuple(p[k]+d*(a[k]+b[k])/den for k in[0,1]))
        return out
    def band(g,m,lo,hi,inner,outer):
        aa=offset(inner);bb=offset(outer);N=len(ring);vv=[(x,y,z0+z)for z in[lo,hi]for rr in[aa,bb]for x,y in rr];ff=[]
        for i in range(N):
            j=(i+1)%N;ff.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
        mesh(g,m,vv,ff)
    def cap(g,rr,z):
        vv=[Vector((x,y,z0+z))for x,y in rr]
        for tri in tessellate_polygon([vv]):mesh(g,'roof',[tuple(vv[q]if isinstance(q,int)else q)for q in tri],[(0,1,2)])
    # Contained continuous mitred cornice. Rich projection is only on the free front.
    for z,h in[(floors[1]-.1,.16),(floors[2]-.09,.12),(H-.34,.16),(H-.12,.12)]:band('continuous mitred contained stringcourse','trim',z,z+h,-.26,0)
    panel(0,'front bracketed frieze','trim',.18,edges[0][1]-.18,H-.43,H-.16,.09,.26)
    panel(0,'front projecting cornice','trim',.18,edges[0][1]-.18,H-.17,H+.035,.15,.40)
    for j in range(32):
        ss=.4+j*(edges[0][1]-.8)/31;panel(0,'cornice modillions','trim',ss-.06,ss+.06,H-.44,H-.18,.16,.32)
    cap('complete concave mapped roof deck',ring,H)
    lower=offset(-.30);upper=offset(-1.20);N=len(ring)
    vv=[(x,y,z0+zz)for rr,zz in[(lower,H),(upper,H+1.8)]for x,y in rr]
    mesh('estimated concave mansard slopes','roof',vv,[(i,(i+1)%N,(i+1)%N+N,i+N)for i in range(N)])
    cap('estimated concave mansard upper deck',upper,H+1.8)
    # No raised party-wall parapet and no speculative roof equipment/dormers.
    F=floors[1];L=edges[0][1]
    panel(0,'continuous first floor balcony deck','trim',.30,L-.30,F-.10,F+.07,.44,1.12)
    for j in range(43):column('first floor bottle balusters',at(0,.47+j*(L-.94)/42,.92,0)[:2],F+.07,F+.78,.045)
    panel(0,'continuous first floor balustrade rail','trim',.30,L-.30,F+.78,F+.90,.92,.21)
    # Existing single source entrance only; observed paired porch translated onto it.
    for s in[es-1.00,es+1.00]:column('Doric porch columns',at(ee,s,.83,0)[:2],0,F-.22,.16)
    panel(ee,'Doric porch entablature','trim',es-1.35,es+1.35,F-.24,F+.02,.53,1.30)
    for j in range(9):
        ss=es-1.16+j*.29;panel(ee,'Doric triglyphs','trim',ss-.042,ss+.042,F-.20,F-.04,1.185,.045)
    if entrance is None:raise ValueError('Missing source entry')
    entrance['additional_supports']=[{'polygon_xy':[list(at(ee,es+s,d,0)[:2])for s,d in[(-1.30,-.1),(1.30,-.1),(1.30,1.14),(-1.30,1.14)]],'top_z':z0,'basis':'Finite coordinator support for paired Doric column feet, r.224m at outward.83; module authors no ground slab'}]
    # Two simplified wall lanterns seen in the licensed entrance photograph.
    for s in[es-.91,es+.91]:
        box('entrance lantern casing','metal',at(ee,s,.17,2.29),(.19,.20,.37),edges[ee][2],edges[ee][3])
        box('entrance lantern glazing','glass',at(ee,s,.28,2.29),(.12,.022,.25),edges[ee][2],edges[ee][3])
    created=[]
    for (g,m),(vv,ff)in groups.items():
        if not ff:continue
        name='71-72 Princes Gate | '+g;me=bpy.data.meshes.new(name);me.from_pydata(vv,[],ff);me.update()
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
        ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;ob['evidence_status']='CC BY-SA3.0 observed entrance, OGL terrace description; hidden form and metric heights estimated';created.append(ob.name)
    return {'created':created,'parameters':{'base_z':z0,'main_wall_height_m':H,'height_m':H,'eaves_height_m':H,'levels':5,'roof_levels':1,'roof_max_z':z0+H+1.8,'footprint_area_m2':area,'wall_thickness_m':.44,'opening_count':len(openings)},'interfaces':{'entrance':entrance,'additional_entrances':[],'shared_walls':common},'openings':openings,'roof_parts':[{'name':'full concave roof deck','z':z0+H},{'name':'estimated later mansard','lower_inset_m':.30,'upper_inset_m':1.20,'max_z':z0+H+1.8}], 'evidence_source_ids':['osm-851362855','commons-76458224','he-1266085','rbkc-queensgate-3.32'],'observations':['Licensed same-building entrance image shows Doric porch, white channelled stucco, sash windows, wood panel door/transom and two lanterns','Official text supplies five main storeys, three bays per historic house and later mansard additions'],'uncertainty':['Main height16.3011778m and mansard1.8m rise are estimates, not survey','Six front bays informed by two historic houses; exact spacing and rear openings estimated','No complete licensed roof view; concave mansard extents estimated, no invented dormers or equipment','Original below-paving datum explicitly superseded by coordinator+.074 base; no copied photo stairs or basement excavation','Four disjoint normalized shared segments retained and blocked, neighbour heights estimated','No Blender integration or visual validation claimed by author']}
