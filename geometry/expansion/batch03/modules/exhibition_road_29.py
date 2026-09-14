"""29 Exhibition Road. OSM plan + HE facts + inspected CC BY-SA photo.
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
    entry_edge=min(range(len(edges)),key=lambda i:dist_edge(edges[i])) if exy else 6
    for ei,(a,L,u,n) in enumerate(edges):
        def at(s,d,z):return (a[0]+s*u[0]+d*n[0],a[1]+s*u[1]+d*n[1],z0+z)
        def panel(g,m,l,r,lo,hi,d=-.2,t=.4):box(g,m,at((l+r)/2,d,(lo+hi)/2),(r-l,t,hi-lo),u,n)
        count=0 if ei==6 else max(1,round(L/3.3)) if L>2.7 else 0
        centers=[(i+.5)*L/count for i in range(count)]
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
                    # Balcony over entrance with individually modelled balusters.
                    panel('entrance balcony slab','trim',l-.65,r+.65,high+.02,high+.22,.3,.9)
                    for k in range(12):
                        x=l-.6+(w+1.2)*k/11
                        panel('entrance balcony balusters','masonry',x-.055,x+.055,high+.22,high+1.05,.70,.12)
                    panel('entrance balcony handrail','trim',l-.7,r+.7,high+1.05,high+1.17,.70,.22)
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
    # Corrected asset association: this northern wing has no duplicate south
    # twin-gabled portico frontage. Roof arrangement remains an estimated rear roof.
    a,L,u,n=edges[6]
    cx,cy=849.9,12.0;w,d=7.0,10.5;rise=2.1
    def p(x,y,z):return(cx+x*u[0]+y*n[0],cy+x*u[1]+y*n[1],z0+z)
    v=[p(-w/2,-d/2,E),p(w/2,-d/2,E),p(w/2,d/2,E),p(-w/2,d/2,E),p(0,-d/2+2,E+rise),p(0,d/2-2,E+rise)]
    mesh('estimated northern hipped roof','roof',v,[(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5)])
    box('rear chimney stack','masonry',p(-2,2,E+1.3),(.8,.85,2.6),u,n)
    box('rear chimney cap','masonry',p(-2,2,E+2.67),(1,1.05,.18),u,n)
    created=[]
    for (g,m),(v,f) in groups.items():
        if not f:continue
        name='29 Exhibition Road | '+g;me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update()
        bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
        ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;ob['evidence_status']='Mapped footprint; licensed photo-informed architectural interpretation';created.append(ob.name)
    return {'created':created,'parameters':{'height_m':H,'base_z':z0,'eaves_height_m':E,'levels':3,'attic':False,'opening_count':len(openings),'roof_max_z':z0+E+2.76,'wall_thickness_m':.4},'interfaces':{'entrance':next((q for q in entrances if q['basis']=='preserved baseline entry'),entrance),'additional_entrances':[q for q in entrances if q['basis']!='preserved baseline entry'],'shared_walls':[{'edge':6,'polyline':[list(ring[6]),list(ring[7])],'height_interval':[z0,z0+E],'openings':[],'neighbour':'way-641603104','basis':'exact shared line; no new door or window apertures'}]},'openings':openings,'evidence_source_ids':['osm-20260912','he-1211833','geograph-6577545'],'uncertainty':['Batch03 correction: photo southern double-gabled frontage belongs to adjoining Jamaican High Commission polygon, not this northern wing','Southern shared edge6 is retained as blind wall and former additional south entrance removed','Northern wing facade and hipped roof are explicitly artistic estimates based on the listed-pair brick vocabulary','Source GLB eaves retained; northern entry threshold projected onto wall preserving lateral location','No basement or new terrain cut; coordinator owns ground support']}
