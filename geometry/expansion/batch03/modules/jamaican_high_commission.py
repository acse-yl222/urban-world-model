"""Jamaican High Commission. OSM plan + HE facts + inspected CC BY-SA photo.
Author-generated measured-looking detail is estimated, not a survey.
"""
import math

def build(feature, materials):
    import bpy, bmesh
    from mathutils import Vector
    from mathutils.geometry import tessellate_polygon
    ring=[tuple(map(float,p[:2])) for p in feature['ring']]
    if ring[0]==ring[-1]: ring.pop()
    if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1]))<0: ring.reverse()
    # feature.height_m is the inherited wall/eaves estimate, not roof-ridge height.
    z0=float(feature.get('base_z',.05)); H=float(feature.get('height_m',13.15)); E=H
    entry=feature.get('entry') or {}; groups={}; openings=[]; entrance=None; entrances=[]
    def mesh(group,mat,v,f):
        vs,fs=groups.setdefault((group,mat),([],[])); o=len(vs);vs.extend(v);fs.extend(tuple(o+i for i in face) for face in f)
    def box(group,mat,c,size,u=(1,0),n=(0,1)):
        if min(size)<1e-6:return
        w,d,h=[q/2 for q in size];x,y,z=c
        v=[(x+i*w*u[0]+j*d*n[0],y+i*w*u[1]+j*d*n[1],z+k*h) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        mesh(group,mat,v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    edges=[]
    for a,b in zip(ring,ring[1:]+ring[:1]):
        L=math.dist(a,b);u=((b[0]-a[0])/L,(b[1]-a[1])/L);edges.append((a,L,u,(u[1],-u[0])))
    exy=entry.get('center_xy')
    def dist_edge(edge):
        a,L,u,n=edge;s=max(0,min(L,(exy[0]-a[0])*u[0]+(exy[1]-a[1])*u[1]));return math.dist(exy,(a[0]+s*u[0],a[1]+s*u[1]))
    entry_edge=min(range(len(edges)),key=lambda i:dist_edge(edges[i])) if exy else max(range(len(edges)),key=lambda i:edges[i][1])
    for ei,(a,L,u,n) in enumerate(edges):
        def at(s,d,z):return (a[0]+s*u[0]+d*n[0],a[1]+s*u[1]+d*n[1],z0+z)
        def panel(g,m,l,r,lo,hi,d=-.2,t=.4):box(g,m,at((l+r)/2,d,(lo+hi)/2),(r-l,t,hi-lo),u,n)
        count=0 if ei==1 else (6 if ei==7 else max(1,round(L/3.3)) if L>2.7 else 0)
        centers=[L*f for f in (.12,.24,.43,.57,.76,.88)] if ei==7 else [(i+.5)*L/count for i in range(count)]
        door_s=((exy[0]-a[0])*u[0]+(exy[1]-a[1])*u[1]) if exy and ei==entry_edge else L*.44
        if ei==entry_edge:
            door_s=max(.8,min(L-.8,door_s))
        for floor in range(3):
            low=E*floor/3;high=E*(floor+1)/3
            holes=[]
            for bi,s in enumerate(centers):
                w=min(1.35,L/count-.8);bottom=low+(.85 if floor==0 else .55);top=high-.48
                if floor==0 and ei==entry_edge and abs(s-door_s)<1.8:continue
                holes.append((s-w/2,s+w/2,bottom,top,False,bi))
            if floor==0 and ei==entry_edge:
                w=float(entry.get('clear_width_m',1.15))+.16;holes.append((door_s-w/2,door_s+w/2,0,min(3.1,high-.25),True,-1))
            cuts=sorted(set([0,L]+[v for h in holes for v in h[:2]]))
            for l,r in zip(cuts,cuts[1:]):
                ho=next((h for h in holes if h[0]<(l+r)/2<h[1]),None)
                if ho:
                    panel('pierced brick walls','masonry',l,r,low,ho[2]);panel('pierced brick walls','masonry',l,r,ho[3],high)
                else:panel('pierced brick walls','masonry',l,r,low,high)
            for l,r,bot,top,door,bi in holes:
                s=(l+r)/2;w=r-l
                panel('door leaves' if door else 'recessed sashes','door' if door else 'glass',l+.065,r-.065,bot if door else bot+.04,top-.06,-.34,.06)
                for xx in (l+.035,r-.035):panel('timber sash frames','trim',xx-.035,xx+.035,bot,top,-.265,.10)
                for zz in ((top-.035,) if door else (bot+.035,top-.035)):panel('timber sash frames','trim',l,r,zz-.035,zz+.035,-.265,.10)
                if not door:
                    for f in (1/3,2/3):panel('small pane glazing bars','trim',l+w*f-.019,l+w*f+.019,bot,top,-.25,.045)
                    for f in (.25,.5,.75):panel('small pane glazing bars','trim',l,r,bot+(top-bot)*f-.023,bot+(top-bot)*f+.023,-.25,.045)
                    panel('brick sills','masonry',l-.12,r+.12,bot-.15,bot-.035,.045,.22)
                # Segmental ground-floor brick arch; no solid wall behind glass.
                if floor==0:
                    spring=top-.22
                    for k in range(16):
                        x1=l+k*w/16;x2=l+(k+1)*w/16;dx=((x1+x2)/2-s)/(w/2)
                        arch=spring+.22*math.sqrt(max(0,1-dx*dx))
                        panel('segmental arch infill','masonry',x1,x2,arch,top)
                        panel('radiating brick arch','masonry',x1-.002,x2+.002,arch,arch+.15,.045,.16)
                else:
                    panel('cut brick heads','masonry',l-.16,r+.16,top+.02,top+.17,.04,.18)
                    if floor==2:
                        # Split pediments are deliberately abstracted brick relief.
                        for side in (-1,1):
                            for k in range(5):
                                x=s+side*(.2+k*.12)
                                panel('split brick pediments','masonry',x-.073,x+.073,top+.26-k*.035,top+.34-k*.035,.09,.22)
                if door:
                    panel('door transom','trim',l,r,top-.59,top-.52,-.25,.1)
                    panel('door center stile','trim',s-.028,s+.028,bot,top-.59,-.25,.09)
                    box('brass door hardware','metal',at(s+.3,-.18,1.1),(.035,.09,.22),u,n)
                    panel('entry threshold','trim',l-.08,r+.08,-.005,0.0,-.15,.4)
                    entrance={'threshold_xyz':[*at(s,0,0)[:2],float(entry.get('threshold_z',z0))], 'outward_normal':[n[0],n[1],0], 'clear_width_m':w-.16,'door_leaf_xyz':list(at(s,-.34,(bot+top)/2)), 'stair_treads':[], 'ramp':'none authored','surface_owner':'coordinator','basis':'preserved baseline entry' if ei==entry_edge else 'south entrance supported by listing; exact opening and terrace estimated'}
                    entrances.append(entrance)
                openings.append({'edge':ei,'floor':floor,'bay':bi,'type':'door' if door else 'window','width_m':w,'height_m':top-bot,'recess_m':.34,'basis':'photo-informed estimated spacing'})
        # Sparse cut-brick vertical pilasters vary long facades from domestic terrace template.
        if L>6:
            for s in (.22,L-.22):panel('corner brick pilasters','masonry',s-.13,s+.13,.15,E,.04,.18)
    def band(g,m,lo,hi,dep,th):
        def offset(d):
            out=[]
            for i,p in enumerate(ring):
                na=edges[i-1][3];nb=edges[i][3];k=d/(1+na[0]*nb[0]+na[1]*nb[1]);out.append((p[0]+k*(na[0]+nb[0]),p[1]+k*(na[1]+nb[1])))
            return out
        inner=offset(dep-th/2);outer=offset(dep+th/2);N=len(ring)
        v=[(x,y,z0+z) for z in (lo,hi) for c in (inner,outer) for x,y in c];f=[]
        for i in range(N):
            j=(i+1)%N;f.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
        mesh(g,m,v,f)
    for z,t,d in [(E/3,.12,.04),(2*E/3,.24,.08),(E-.12,.22,.08)]:band('continuous cut brick cornices','masonry',z-t/2,z+t/2,d,.30)
    # Cover overlapping wall-box top faces at convex corners with one continuous cap.
    band('continuous roof edge flashing','roof',E-.01,E+.025,-.12,.70)
    vv=[Vector((x,y,z0+E-.06)) for x,y in ring];vs=[];fs=[]
    for tri in tessellate_polygon([vv]):
        k=len(vs);vs.extend(tuple(vv[v] if isinstance(v,int) else v) for v in tri);fs.append((k,k+1,k+2))
    mesh('exact concave roof deck','roof',vs,fs)
    # South frontage geometry is located against edge 7; unlike the northern
    # mapped asset, this is the photographed twin-gabled Prince Consort facade.
    a,L,u,n=edges[7]
    def at(s,d,z):return(a[0]+s*u[0]+d*n[0],a[1]+s*u[1]+d*n[1],z0+z)
    def frontbox(g,m,s,d,z,w,depth,h):box(g,m,at(s,d,z),(w,depth,h),u,n)
    # Open double arched portico: three piers and discrete arch wedges, no bottom rail.
    center=(entry['center_xy'][0]-a[0])*u[0]+(entry['center_xy'][1]-a[1])*u[1] if entry.get('center_xy') else L*.5
    aw=3.5; spring=2.55; rise=.95; portico=center+aw/2
    frontbox('finite portico supporting slab','trim',portico,.775,-.003,aw*2+.5,1.55,.006)
    for ss in (portico-aw,portico,portico+aw):
        frontbox('portico brick piers','masonry',ss,.75,spring/2,.24,1.35,spring)
        frontbox('portico pier capitals','trim',ss,.75,spring,.36,1.48,.16)
    for ac in (portico-aw/2,portico+aw/2):
        for k in range(24):
            t1=math.pi*k/24;t2=math.pi*(k+1)/24
            v=[]
            for dep in (.12,1.4):
                for radius,height,t in [(aw/2-.12,rise,t1),(aw/2-.12,rise,t2),(aw/2+.12,rise+.27,t2),(aw/2+.12,rise+.27,t1)]:v.append(at(ac+radius*math.cos(t),dep,spring+height*math.sin(t)))
            mesh('twin portico brick arches','masonry',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    balcony_z=E/3
    # The lower spandrel edge shares the exact sampled outer arch vertices.
    # No midpoint rectangle approximation: continuous prism faces meet voussoirs.
    for ac in (portico-aw/2,portico+aw/2):
        for k in range(24):
            t1=math.pi*k/24;t2=math.pi*(k+1)/24
            x1=ac+(aw/2+.12)*math.cos(t1); x2=ac+(aw/2+.12)*math.cos(t2)
            z1=spring+(rise+.27)*math.sin(t1); z2=spring+(rise+.27)*math.sin(t2)
            hi=balcony_z-.11
            v=[at(xx,dep,zz) for dep in (.12,1.4) for xx,zz in ((x1,z1),(x2,z2),(x2,hi),(x1,hi))]
            mesh('portico arch spandrels','masonry',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    frontbox('central balcony slab','trim',portico,.70,balcony_z,aw*2+.45,1.65,.22)
    for k in range(28):
        ss=portico-aw+(aw*2)*k/27
        frontbox('central stone balustrade','trim',ss,1.42,balcony_z+.57,.075,.13,.93)
        frontbox('baluster necks','trim',ss,1.42,balcony_z+.6,.13,.18,.26)
    frontbox('balustrade top rail','trim',portico,1.42,balcony_z+1.08,aw*2+.3,.25,.14)
    # Main gabled ranges stay over safely interior subrectangles.
    roofrise=min(3.7,H*.28)
    def range_roof(s,w,depth,rise):
        def p(x,y,z):return at(s+x,-.18-y,z)
        v=[p(-w/2,0,E),p(w/2,0,E),p(w/2,depth,E),p(-w/2,depth,E),p(0,0,E+rise),p(0,depth,E+rise)]
        mesh('paired steep red tiled roofs','roof',v,[(0,4,5,3),(1,2,5,4)])
        for yy in (0,depth):
            half=.62; bot=.55; top=2.10; shoulder=w/2*(1-top/rise)
            sections=[[(-w/2,0),(w/2,0),(w/2*(1-bot/rise),bot),(-w/2*(1-bot/rise),bot)],[(-w/2*(1-bot/rise),bot),(-half,bot),(-half,top),(-shoulder,top)],[(half,bot),(w/2*(1-bot/rise),bot),(shoulder,top),(half,top)],[(-shoulder,top),(shoulder,top),(0,rise)]]
            for sec in sections:mesh('pierced triangular attic gables','masonry',[p(x,yy,E+zz) for x,zz in sec],[tuple(range(len(sec)))])
            # Transparent sash fills actual gable aperture; joinery independent.
            box('attic sash glazing','glass',p(0,yy,E+(bot+top)/2),(1.12,.07,top-bot-.1),u,n)
            for xx in (-half,half):box('attic sash frames','trim',p(xx,yy-.045,E+(bot+top)/2),(.07,.10,top-bot+.08),u,n)
            for zz in (bot,bot+.52,bot+1.03,top):box('attic sash frames','trim',p(0,yy-.045,E+zz),(1.32,.10,.055),u,n)
        box('roof ridge tiles','roof',p(0,depth/2,E+rise+.04),(.16,depth,.14),u,n)
    range_roof(L*.20,8.5,5.7,roofrise)
    range_roof(L*.80,8.5,10.5,roofrise)
    # The middle low roof and twin roof-light dormers are photo informed estimates.
    frontbox('central linking roof','roof',center,-3.6,E+.185,9.2,6.4,.49)
    for ss in (center-1.9,center+1.9):
        frontbox('central dormer back panels','masonry',ss,-1.52,E+1.0,1.58,.10,1.65)
        frontbox('central dormer side jambs','masonry',ss-.7,-1.15,E+1.0,.18,.8,1.65)
        frontbox('central dormer side jambs','masonry',ss+.7,-1.15,E+1.0,.18,.8,1.65)
        frontbox('central dormer glazing','glass',ss,-.87,E+1.0,1.18,.06,1.45)
        for xx in (-.62,0,.62):frontbox('central dormer joinery','trim',ss+xx,-.81,E+1.0,.055,.08,1.56)
        for zz in (.24,.63,1.03,1.43,1.78):frontbox('central dormer joinery','trim',ss,-.81,E+zz,1.3,.08,.055)
        frontbox('central dormer lintels','masonry',ss,-1.1,E+1.84,1.64,1.02,.18)
    for ss in (L*.35,L*.65):
        frontbox('tall chimney stacks','masonry',ss,-4.3,E+roofrise*.62,.95,.94,roofrise*1.7)
        frontbox('chimney corbel caps','masonry',ss,-4.3,E+roofrise*1.47,1.14,1.13,.18)
        for off in (-.25,.25):frontbox('chimney pots','roof',ss+off,-4.3,E+roofrise*1.47+.24,.2,.2,.3)
    created=[]
    for (g,m),(v,f) in groups.items():
        if not f:continue
        name='Jamaican High Commission | '+g;me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update()
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;ob['evidence_status']='Mapped footprint; licensed photo-informed architectural interpretation';created.append(ob.name)
    return {'created':created,'parameters':{'height_m':H,'base_z':z0,'eaves_height_m':E,'levels':3,'attic':True,'opening_count':len(openings),'roof_max_z':z0+E+roofrise*1.47+.39,'wall_thickness_m':.4},'interfaces':{'entrance':next((q for q in entrances if q['basis']=='preserved baseline entry'),entrance),'additional_entrances':[q for q in entrances if q['basis']!='preserved baseline entry'],'shared_walls':[{'edge':1,'polyline':[list(ring[1]),list(ring[2])],'height_interval':[z0,z0+E],'openings':[],'neighbour':'way-641757059','basis':'exact shared boundary from coordinator audit; full wall retained'}]},'openings':openings,'evidence_source_ids':['osm-20260912','he-1211833','geograph-6577546'],'uncertainty':['Photo-informed southern Prince Consort facade matches this asset; exact dimensions and roof intersections remain interpreted','Mapped eaves height retained; three main storeys plus attic are source supported','All mapped concavities and shared north wall retained; north shared wall has no new speculative openings','Existing entrance threshold retained at ground level; photograph shows a raised historic terrace, so vertical doorway composition is deliberately simplified for scene connectivity','No basement or outer stairs excavated; coordinator owns supporting ground','Rear elevations and small roof details are artistically completed']}
