"""25 Kensington Gore: OSM plan / Historic England architecture / estimates.
Authoring only. build(feature, materials) -> JSON-serializable report.
"""
import math

def build(feature, materials):
    import bpy
    from mathutils import Vector
    from mathutils.geometry import tessellate_polygon
    ring=[tuple(map(float,p)) for p in feature['ring']]
    if ring[0]==ring[-1]:ring.pop()
    area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1]))/2
    if area<=0:raise ValueError('CCW ring required to retain facade indexing')
    z0=float(feature.get('base_z',.05));H=float(feature.get('height_m',10));E=feature.get('entry') or {}
    entry_edge=int(E.get('edge_index',5));groups={};openings=[];entry_out=None
    def part(group,mat,v,f):
        vv,ff=groups.setdefault((group,mat),([],[]));off=len(vv);vv.extend(v);ff.extend(tuple(off+i for i in face) for face in f)
    def box(group,mat,c,size,u=(1.,0.),n=(0.,1.)):
        if min(size)<1e-6:return
        x,y,z=c;w,d,h=[x/2 for x in size]
        v=[(x+i*w*u[0]+j*d*n[0],y+i*w*u[1]+j*d*n[1],z+k*h) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        part(group,mat,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    def offset(distance):
        out=[]
        for i,b in enumerate(ring):
            a=ring[i-1];c=ring[(i+1)%len(ring)];l=math.dist(a,b);m=math.dist(b,c)
            n1=((b[1]-a[1])/l,-(b[0]-a[0])/l);n2=((c[1]-b[1])/m,-(c[0]-b[0])/m)
            den=1+n1[0]*n2[0]+n1[1]*n2[1]
            out.append((b[0]+distance*(n1[0]+n2[0])/den,b[1]+distance*(n1[1]+n2[1])/den))
        return out
    def continuous_band(group,mat,inner,outer,low,high):
        a=offset(inner);b=offset(outer);N=len(ring)
        v=[(x,y,z0+z) for z in [low,high] for rr in [a,b] for x,y in rr];f=[]
        for i in range(N):
            j=(i+1)%N
            f.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
        part(group,mat,v,f)
    def cap(group,mat,rr,z):
        vv=[Vector((x,y,z0+z)) for x,y in rr]
        triangles=tessellate_polygon([vv])
        for tri in triangles:part(group,mat,[tuple(vv[v] if isinstance(v,int) else v) for v in tri],[(0,1,2)])
    def column(group,xy,bottom,top,radius=.115):
        # Turned shaft, foot and capital: all geometric, directly on portico slab.
        profile=[(bottom,radius*1.45),(bottom+.1,radius*1.45),(bottom+.15,radius*1.1),(bottom+.25,radius),(top-.3,radius*.88),(top-.20,radius*1.2),(top-.1,radius*1.55),(top,radius*1.55)]
        v=[(xy[0]+r*math.cos(2*math.pi*k/16),xy[1]+r*math.sin(2*math.pi*k/16),z0+z) for z,r in profile for k in range(16)];f=[]
        for j in range(len(profile)-1):
            for k in range(16):q=(k+1)%16;f.append((j*16+k,j*16+q,(j+1)*16+q,(j+1)*16+k))
        f.extend([tuple(range(15,-1,-1)),tuple((len(profile)-1)*16+k for k in range(16))]);part(group,'trim',v,f)
    floors=[0,H*.37,H*.70,H]
    # Eight principal north bays distributed over the mapped bay/corner returns.
    fixed={0:[],1:[.5],2:[.5],3:[.5],4:[],5:[.2,.65],6:[.5],7:[],8:[.5],9:[.5],10:[.5],11:[],12:[.5],13:[],14:[.5],15:[.5],16:[],17:[.25,.72],18:[],19:[.5],20:[],21:[.5],22:[],23:[],24:[],25:[]}
    for ei,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
        L=math.dist(a,b);u=((b[0]-a[0])/L,(b[1]-a[1])/L);n=(u[1],-u[0])
        def at(s,d,z):return (a[0]+s*u[0]+d*n[0],a[1]+s*u[1]+d*n[1],z0+z)
        def panel(group,mat,left,right,bottom,top,d=-.20,t=.40):box(group,mat,at((left+right)/2,d,(bottom+top)/2),(right-left,t,top-bottom),u,n)
        positions=fixed.get(ei,[])
        for lev,(lo,hi) in enumerate(zip(floors,floors[1:])):
            holes=[]
            for bi,fraction in enumerate(positions):
                s=L*fraction;w=min(1.25 if lev==0 else 1.15,L-.62)
                if ei==5 and bi==0:w=.90
                door=ei==entry_edge and lev==0 and bi==1
                if door:
                    xy=E.get('center_xy',[a[0]+s*u[0],a[1]+s*u[1]])
                    s=(xy[0]-a[0])*u[0]+(xy[1]-a[1])*u[1];w=float(E.get('clear_width_m',1.05))+.15
                bottom=0 if door else lo+(.62 if lev!=1 else .42)
                top=min(2.85,hi-.40) if door else hi-(.40 if lev==0 else .52)
                if s-w/2<.12 or s+w/2>L-.12:continue
                holes.append((s-w/2,s+w/2,bottom,top,door))
            cuts=sorted({0,L,*[s for h in holes for s in h[:2]]})
            for left,right in zip(cuts,cuts[1:]):
                hole=next((h for h in holes if h[0]-1e-8<=(left+right)/2<=h[1]+1e-8),None)
                if hole:
                    panel('pierced stucco envelope','masonry',left,right,lo,hole[2]);panel('pierced stucco envelope','masonry',left,right,hole[3],hi)
                else:panel('pierced stucco envelope','masonry',left,right,lo,hi)
            for left,right,bottom,top,door in holes:
                s=(left+right)/2;w=right-left
                panel('recessed door leaves' if door else 'recessed glazing','door' if door else 'glass',left+.075,right-.075,bottom+.03,top-.075,-.34,.06)
                for xx in [left+.04,right-.04]:panel('black sash frames','metal',xx-.04,xx+.04,bottom,top,-.27,.075)
                for zz in ([top-.04] if door else [bottom+.04,top-.04,(bottom+top)/2]):panel('door head frame' if door else 'black sash frames','metal',left,right,zz-.035,zz+.035,-.255,.08)
                if not door:panel('black sash frames','metal',s-.024,s+.024,bottom,top,-.255,.08)
                for xx in [left-.075,right+.075]:panel('dressed architraves','trim',xx-.06,xx+.06,bottom-.06,top+.1,.025,.17)
                panel('dressed architraves','trim',left-.17,right+.17,top,top+.16,.09,.22)
                if not door:panel('projecting sills','trim',left-.17,right+.17,bottom-.1,bottom-.025,.09,.24)
                if ei<18 and lev in [1,2]:
                    # Pediment silhouette (triangular or segmental approximation), not a flat texture.
                    z=top+.19
                    if lev==2:
                        p=[at(left-.2,.12,z),at(right+.2,.12,z),at(s,.12,z+.37),at(left-.2,.24,z),at(right+.2,.24,z),at(s,.24,z+.37)]
                        part('pedimented window hoods','trim',p,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)])
                    else:
                        for k in range(14):
                            t0=math.pi*k/14;t1=math.pi*(k+1)/14
                            rr=w/2+.18;pts=[]
                            for depth in [.09,.23]:
                                for rad,t in [(rr,t0),(rr,t1),(rr+.10,t1),(rr+.10,t0)]:pts.append(at(s+rad*math.cos(t),depth,z+.32*math.sin(t)+(rad-rr)*.4))
                            part('segmental window hoods','trim',pts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7)])
                if door:
                    threshold=float(E.get('threshold_z',z0));panel('portico threshold','trim',left-.28,right+.28,threshold-z0-.006,threshold-z0,-.10,.42)
                    # Slight projection scaled to the inherited apron; columns grounded on finite slab.
                    panel('porch slab','trim',left-.5,right+.5,-.006,0,.34,.68)
                    for side in [-1,1]:
                        for delta in [-.13,.13]:
                            xy=at(s+side*(w/2+.25)+delta,.55,0)
                            column('coupled Ionic-inspired porch columns',xy[:2],0,2.83,.085)
                    panel('porch entablature','trim',left-.65,right+.65,2.83,3.08,.3,1.05)
                    entry_out={**E,'center_xy':list(E.get('center_xy',at(s,0,0)[:2])),'threshold_xyz':[*E.get('center_xy',at(s,0,0)[:2]),threshold],'threshold_z':threshold,'outward_normal_xy':list(n),'clear_width_m':w-.15,'porch_projection_m':.85,'support_owner':'coordinator; check ground beneath new finite slab','door_leaf_xyz':list(at(s,-.34,1.4))}
                openings.append({'edge':ei,'floor':lev,'type':'door' if door else 'window','width_m':w,'height_m':top-bottom,'recess_m':.34})
        if ei<18:
            # Vertical quoin blocks and corbels rhythm tied to mapped corners, not random windows.
            for z in [i*.44+.22 for i in range(int(H/.44))]:
                panel('corner quoins','trim',.035,min(.36,L-.035),z-.17,z+.17,.025,.14)
            for s in [L*.25,L*.75] if L>3 else [L*.5]:
                panel('cornice brackets','trim',s-.1,s+.1,H-.39,H-.03,.16,.30)
    # Continuous mitered courses: shared vertex loops, no isolated edge-box gaps.
    for height,outer,th in [(H*.37,.20,.16),(H*.70,.12,.12),(H-.14,.22,.18),(H+.03,.30,.14)]:
        continuous_band('continuous mitred cornices','trim',-.08,outer,height-th/2,height+th/2)
    # Full concave footprint roof shell; inset loop preserves every concavity.
    inset=offset(-.9);cap('attic interior ceiling','roof',ring,H)
    cap('slate upper roof','roof',inset,H+2.3)
    for i,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
        j=(i+1)%len(ring)
        part('mansard perimeter','roof',[(a[0],a[1],z0+H+.05),(b[0],b[1],z0+H+.05),(inset[j][0],inset[j][1],z0+H+2.3),(inset[i][0],inset[i][1],z0+H+2.3)],[(0,1,2,3)])
    # Dormers sit outside mansard plane, recessed leaf in a genuine opening;
    # their backing is forward of roof slope, preventing coplanar painted windows.
    for ei in [2,5,8,12,14,17]:
        a=ring[ei];b=ring[(ei+1)%len(ring)];L=math.dist(a,b);u=((b[0]-a[0])/L,(b[1]-a[1])/L);n=(u[1],-u[0]);s=L/2
        def dbox(group,mat,cx,dep,zz,w,th,h):box(group,mat,(a[0]+u[0]*cx+n[0]*dep,a[1]+u[1]*cx+n[1]*dep,z0+zz),(w,th,h),u,n)
        for ds in [-.57,.57]:dbox('dormer masonry jambs','trim',s+ds,-.1,H+1.05,.14,.45,1.35)
        for zz in [H+.4,H+1.68]:dbox('dormer masonry lintel sill','trim',s,-.1,zz,1.28,.45,.14)
        dbox('dormer recessed glazing','glass',s,-.13,H+1.04,.94,.04,1.12)
        for ds in [-.49,0,.49]:dbox('dormer sash','metal',s+ds,-.04,H+1.04,.05,.07,1.17)
        for zz in [H+.49,H+1.05,H+1.60]:dbox('dormer sash','metal',s,-.04,zz,1.03,.07,.05)
        c=(a[0]+u[0]*s,a[1]+u[1]*s)
        pts=[]
        for dep in [.17,-.8]:
            for xx,zz in [(-.72,H+1.77),(.72,H+1.77),(0,H+2.09)]:pts.append((c[0]+u[0]*xx+n[0]*dep,c[1]+u[1]*xx+n[1]*dep,z0+zz))
        part('pedimented dormer roofs','trim',pts,[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)])
    # First-floor balustrade follows front and corner bay, with clear space between posts.
    for ei in [1,2,3,5,6,8,9,10,12]:
        a=ring[ei];b=ring[(ei+1)%len(ring)];L=math.dist(a,b);u=((b[0]-a[0])/L,(b[1]-a[1])/L);n=(u[1],-u[0]);z=H*.37+.12
        box('balcony support slabs','trim',((a[0]+b[0])/2+n[0]*.15,(a[1]+b[1])/2+n[1]*.15,z0+z-.11),(L,.65,.18),u,n)
        for t in range(max(2,int(L/.36))):
            q=(t+.5)*L/max(2,int(L/.36));xy=(a[0]+u[0]*q+n[0]*.34,a[1]+u[1]*q+n[1]*.34)
            column('turned balcony balusters',xy,z,z+.60,.045)
        for zz in [z-.04,z+.66]:box('balcony handrail','trim',((a[0]+b[0])/2+n[0]*.34,(a[1]+b[1])/2+n[1]*.34,z0+zz),(L,.20,.12),u,n)
    # Two modest chimney stacks; location estimated; full volume confined to roof.
    for x,y in [(487,99),(496,104)]:
        box('estimated chimney stacks','masonry',(x,y,z0+H+2.5),(.65,.95,1.15));box('chimney caps','trim',(x,y,z0+H+3.10),(.82,1.10,.14))
    created=[]
    for (group,mat),(v,f) in groups.items():
        if not f:continue
        name='25 Kensington Gore | '+group;mesh=bpy.data.meshes.new(name);mesh.from_pydata(v,[],f);mesh.update();
        import bmesh
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
        obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);mesh.materials.append(materials[mat]);obj['building_id']=feature['id'];obj['research_object_id']=feature['id']+'::'+group;obj['evidence_status']='HE architectural description and open-photo contextual inspection; dimensions and unseen details estimated';created.append(obj.name)
    return {'created':created,'parameters':{'main_wall_height_m':H,'attic_height_m':2.3,'mapped_footprint_area_m2':area,'storeys':3,'opening_count':len(openings)},'interfaces':{'entry':entry_out,'shared_walls':'All mapped walls retained; east edge 25 left solid conservatively, not deleted'},'observations':['HE1275267: three storeys, attic, stucco, slate, canted bay, polygonal corner, coupled Ionic porch, first-floor balcony, pedimented dormers','2025 Mike Peel photographs: pale ornate stucco, dark frames, continuous cornices and balustrades in corner ensemble; image includes neighbours'],'evidence_source_ids':['osm-117417421','he-1275267','commons-165200481','commons-165200486'],'uncertainty':['Dimensions, roof slopes, rear facade, chimney locations and detailed ornaments artistically completed','Photos encompass adjoining property; exact decorative assignment is interpretation','No surveyed elevation, basement excavation or interior generated','Source-reported eight principal front bays distributed over mapped irregular bay returns; exact pier spacing estimated']}
