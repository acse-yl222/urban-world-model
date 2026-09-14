"""4 Princes Gate Mews OSM-ID-specific two-storey interpretation.
Only contextual CC street imagery; exact facade and roof remain artistic estimates.
"""
import math

def build(feature, materials):
    import bpy,bmesh
    from mathutils import Vector
    from mathutils.geometry import tessellate_polygon
    ring=[tuple(map(float,p[:2])) for p in feature['ring']]
    if ring[0]==ring[-1]:ring.pop()
    if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1]))<0:raise ValueError('CCW ring required to preserve edge contract')
    z0=float(feature['base_z']);H=float(feature['height_m']);levels=max(1,int(feature.get("levels",2)));pitch=H/levels
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
    for seg in feature.get('audit',{}).get('normalized_shared_wall_segments',[]):
        ei=int(seg['edge']);a,L,u,n=edges[ei];line=seg['polyline']
        spans=sorted(sum((v[k]-a[k])*u[k] for k in range(2)) for v in line)
        common.append({'edge':ei,'s_interval':[max(0,spans[0]),min(L,spans[-1])],
                       'height_interval':list(seg['height_interval']),'polyline':line,
                       'neighbour':seg['neighbour'],'openings':[]})
    def blocked(ei,l,r,bot,top):return any(c['edge']==ei and l<c['s_interval'][1] and r>c['s_interval'][0] and z0+bot<c['height_interval'][1] and z0+top>c['height_interval'][0] for c in common)
    # Planned apertures differ between the mews front, rear and short return walls.
    # Three upper front sashes and two ground casements sit beside the offset
    # original entry. Rear openings follow the complete target5pointplan.
    floor_positions={4:{0:[1.65,3.75],1:[1.40,3.88,6.36]},
                     2:{0:[1.28,3.90],1:[1.35,3.85]},
                     1:{0:[],1:[1.27]}}
    for ei,(a,L,u,n) in enumerate(edges):
        def at(s,d,z):return(a[0]+u[0]*s+n[0]*d,a[1]+u[1]*s+n[1]*d,z0+z)
        def panel(g,m,l,r,lo,hi,d=-.20,t=.40):
            if r-l>1e-6 and hi-lo>1e-6:box(g,m,at((l+r)/2,d,(lo+hi)/2),(r-l,t,hi-lo),u,n)
        door_s=sum((exy[k]-a[k])*u[k] for k in[0,1]) if exy and ei==entry_edge else None
        for floor in range(levels):
            low=pitch*floor;high=pitch*(floor+1);holes=[]
            for bi,s in enumerate(floor_positions.get(ei,{}).get(floor,[])):
                # Larger ground casements; smaller upper sashes, not duplicated rows.
                w=(1.45 if ei==4 else 1.15) if floor==0 else 1.18
                bot=low+(.77 if floor==0 else .67);top=high-(.65 if floor==0 else .52)
                if s-w/2<.32 or s+w/2>L-.32:continue
                if floor==0 and door_s is not None and abs(s-door_s)<w/2+.85:continue
                if blocked(ei,s-w/2,s+w/2,bot,top):continue
                holes.append((s-w/2,s+w/2,bot,top,False,bi))
            if floor==0 and door_s is not None:
                w=entry['clear_width_m']+.14
                holes.append((door_s-w/2,door_s+w/2,entry['threshold_z']-z0,2.62,True,-1))
            holes.sort();cursor=0
            for l,r,bot,top,door,bi in holes:
                panel('pierced wall piers','masonry',cursor,l,low,high)
                panel('wall below recessed apertures','masonry',l,r,low,bot)
                panel('solid wall lintels','masonry',l,r,top,high)
                s=(l+r)/2;w=r-l
                panel('painted entrance leaf' if door else 'deep inset glazing','door' if door else 'glass',l+.05,r-.05,bot if door else bot+.045,top-.045,-.34,.055)
                for x in[l+.028,r-.028]:panel('door jamb' if door else 'recessed window outer sash','trim',x-.028,x+.028,bot,top,-.105,.14)
                panel('door head frame' if door else 'recessed window outer sash','trim',l+.056,r-.056,top-.055,top,-.105,.14)
                if not door:
                    panel('recessed window bottom sash','trim',l+.056,r-.056,bot,bot+.055,-.105,.14)
                    if floor==0:
                        for frac in[1/3,2/3]:
                            x=l+w*frac;panel('tripartite mews casement mullions','trim',x-.025,x+.025,bot+.055,top-.055,-.10,.12)
                        panel('ground transom rail','trim',l+.056,r-.056,top-.48,top-.43,-.09,.12)
                    else:
                        panel('upper sash meeting rail','trim',l+.056,r-.056,(bot+top)/2-.034,(bot+top)/2+.034,-.10,.12)
                        panel('upper sash glazing bars','trim',s-.018,s+.018,bot+.055,top-.055,-.085,.10)
                    panel('deep projecting stone sill','trim',l-.12,r+.12,bot-.115,bot+.005,.075,.32)
                    panel('simple stone window lintel','trim',l-.10,r+.10,top+.045,top+.155,.045,.22)
                    # Distinct soldier-course brick headers, no fanciful classical pediments.
                    if floor==0:
                        for j in range(max(4,round((w+.2)/.18))):
                            N=max(4,round((w+.2)/.18));xl=l-.10+j*(w+.20)/N
                            panel('soldier-course header blocks','masonry',xl+.009,xl+(w+.20)/N-.009,top+.155,top+.32,.027,.11)
                else:
                    # Leaf panels remain behind the opening; no bottom-frame threshold obstruction.
                    for zz in[.50,1.23,2.00]:panel('inset door panels','door',l+.16,r-.16,zz-.20,zz+.20,-.303,.026)
                    panel('door transom glazing','glass',l+.095,r-.095,2.27,2.54,-.305,.025)
                    for zz in[2.23,2.57]:panel('door transom frame','trim',l+.075,r-.075,zz-.025,zz+.025,-.30,.055)
                    panel('simple entrance lintel','trim',l-.18,r+.18,top+.055,top+.23,.065,.29)
                    for x in[l-.095,r+.095]:panel('entrance stone jamb surround','trim',x-.065,x+.065,0,top+.055,.06,.22)
                    entrance={'threshold_xyz':[exy[0],exy[1],entry['threshold_z']],
                              'outward_normal':[n[0],n[1],0],'door_leaf_xyz':list(at(s,-.34,top/2)),
                              'clear_width_m':entry['clear_width_m'],'clear_height_m':top,
                              'leaf_recess_m':.34,'stair_treads':[],'additional_supports':[],
                              'ramp':'none authored','surface_owner':'coordinator',
                              'basis':'Projected old door position and near-zero threshold retained; finite ground support supplied separately'}
                openings.append({'edge':ei,'floor':floor,'s_interval':[l,r],'z_interval':[z0+bot,z0+top],'door':door})
                cursor=r
            panel('pierced wall piers','masonry',cursor,L,low,high)
        # Low plinth is split around source entrance and cannot cross its threshold.
        spans=[(0,L)] if door_s is None else [(0,door_s-.76),(door_s+.76,L)]
        for l,r in (spans if ei in [2,4] else []):panel('segmented low plinth','masonry',l,r,.01,.33,.012,.10)
        # Estimated downpipe on select return corners; attached within rear facade extents.
        if ei==2:
            box('estimated rear rainwater pipe','metal',at(.32,.13,H/2),(.075,.075,H-.20),u,n)
            for z in[1.0,3.0,5.0]:box('pipe fixing collars','metal',at(.32,.13,z),(.11,.10,.045),u,n)
    def offset(d):
        out=[]
        for i,p in enumerate(ring):
            na=edges[i-1][3];nb=edges[i][3];den=1+sum(na[k]*nb[k] for k in[0,1])
            if den<.08:raise ValueError('Unstable mitre requires explicit corner review')
            out.append((p[0]+d*(na[0]+nb[0])/den,p[1]+d*(na[1]+nb[1])/den))
        return out
    def band(g,m,lo,hi,inner,outer,free_only=False):
        aa=offset(inner);bb=offset(outer);N=len(ring)
        v=[(x,y,z0+z) for z in[lo,hi] for rr in[aa,bb] for x,y in rr];faces=[]
        selected=[2,4] if free_only else list(range(N))
        for i in selected:
            j=(i+1)%N
            faces.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),
                          (i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
            if free_only:
                # Cap only exposed ends of each selected contiguous run.
                # Adjacent segments share their mitre; a second opposing cap
                # there is an internal duplicate face removed by GLB import.
                if (i-1)%N not in selected:
                    faces.append((i,N+i,3*N+i,2*N+i))
                if j not in selected:
                    faces.append((j,2*N+j,3*N+j,N+j))
        mesh(g,m,v,faces)
    # Mitred eaves remain within plan; selected front/rear courses have capped ends.
    band('front and rear intermediate course','trim',pitch-.10,pitch+.015,-.16,-.005,True)
    band('contained continuous mitred eaves','trim',H-.16,H-.015,-.18,-.005)
    # Exact4loft-redesign planning history motivates an estimated inset tier,
    # not a claim that the basement or sunken terrace was constructed. Main shared walls stop at H.
    rise=float(feature['roof_tier']['rise_m']);inset=float(feature['roof_tier']['inset_m'])
    upper=offset(-inset);N=len(ring);upper_openings=[]
    def capmesh(name,rr,z):
        vv=[Vector((x,y,z0+z)) for x,y in rr]
        # Resolve only against tessellator Vector inputs; keep source doubles.
        original=[(x,y,z0+z) for x,y in rr];ff=[]
        for tri in tessellate_polygon([vv]):
            ff.append(tuple(q if isinstance(q,int) else vv.index(q) for q in tri))
        mesh(name,'roof',original,ff)
    capmesh('complete six point original footprint deck',ring,H+.008)
    for ei,(a,b) in enumerate(zip(upper,upper[1:]+upper[:1])):
        L=math.dist(a,b);u=((b[0]-a[0])/L,(b[1]-a[1])/L);n=(u[1],-u[0])
        def up(l,r,lo,hi,g='inset upper tier solid walls',m='roof',d=-.11,depth=.22):
            if r>l and hi>lo:
                box(g,m,(a[0]+u[0]*(l+r)/2+n[0]*d,a[1]+u[1]*(l+r)/2+n[1]*d,z0+H+(lo+hi)/2),(r-l,depth,hi-lo),u,n)
        positions=[L*.28,L*.72] if ei==4 else [L*.50] if ei==2 else []
        holes=[(c-.47,c+.47,.43,rise-.43) for c in positions if c-.47>.25 and c+.47<L-.25]
        cursor=0
        for l,r,lo,hi in holes:
            up(cursor,l,.008,rise-.025);up(l,r,.008,lo);up(l,r,hi,rise-.025)
            up(l+.04,r-.04,lo+.04,hi-.04,'inset upper tier recessed glazing','glass',-.16,.045)
            for x in[l+.025,r-.025]:up(x-.025,x+.025,lo,hi,'upper window stiles','trim',-.045,.10)
            for z in[lo,hi-.05]:up(l+.05,r-.05,z,z+.05,'upper window head sill frames','trim',-.045,.10)
            up(l+.05,r-.05,(lo+hi)/2-.025,(lo+hi)/2+.025,'upper window meeting rail','trim',-.035,.10)
            upper_openings.append({'inset_edge':ei,'s_interval':[l,r],'z_interval':[z0+H+lo,z0+H+hi],'inset_m':inset,'basis':'Estimated upper-tier glazing, not photographed dormers'})
            cursor=r
        up(cursor,L,.008,rise-.025)
    # A finite-thickness top slab embeds into the tier walls; no coplanar cap
    # over wall-box tops. Top and bottom caps share slab vertex indices.
    rv=[(x,y,z0+H+z) for z in[rise-.055,rise] for x,y in upper]
    rf=[(i,(i+1)%N,N+(i+1)%N,N+i) for i in range(N)]
    for off,reverse in [(0,True),(N,False)]:
        vv=[Vector(v) for v in rv[off:off+N]]
        for tri in tessellate_polygon([vv]):
            ii=[off+(q if isinstance(q,int) else vv.index(q)) for q in tri]
            rf.append(tuple(reversed(ii)) if reverse else tuple(ii))
    mesh('closed upper roof slab','roof',rv,rf)
    roof_parts.extend([{'name':'full original six point footprint deck','z':z0+H+.008,'full_footprint':True},
                       {'name':'estimated inset loft tier','count':1,'inset_m':inset,'rise_m':rise,
                        'max_z':z0+H+rise,'glazing':upper_openings,'boundary_shared_height_increased':False,
                        'basis':'Exact4loft-redesign text motivates artistic tier; no claim currentform or sunken terrace constructed'}])
    created=[]
    for (group,mat),(vertices,faces) in groups.items():
        if not faces:continue
        # Partial-edge bands allocate the full mitre ring. Remove unused ring
        # corners before export so Blender and GLB bounds describe the same faces.
        used=sorted({index for face in faces for index in face})
        remap={old:new for new,old in enumerate(used)}
        vertices=[vertices[index] for index in used]
        faces=[tuple(remap[index] for index in face) for face in faces]
        name='4 Princes Gate Mews | '+group;m=bpy.data.meshes.new(name);m.from_pydata(vertices,[],faces);m.update()
        bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
        o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);m.materials.append(materials[mat]);o['building_id']=feature['id'];o['research_object_id']=feature['id']+'::'+group;o['evidence_status']='OSM two-storey plan; CC street context only; unobserved facade and roof artistically completed';created.append(o.name)
    if entrance is None:raise ValueError('Original entrance not generated')
    return {'created':created,'parameters':{'base_z':z0,'height_m':H,'main_wall_height_m':H,'eaves_height_m':H,'levels':levels,'roof_levels':1,'authored_total_visible_tiers':3,'roof_levels_semantics':'Estimated loft tier motivated by exact4planning text; not surveyed','roof_max_z':z0+H+rise,'wall_thickness_m':.40,'opening_count':len(openings),'inset_upper_opening_count':len(upper_openings),'total_authored_apertures':len(openings)+len(upper_openings)},
            'interfaces':{'entrance':entrance,'additional_entrances':[],'shared_walls':common},'openings':openings,'roof_parts':roof_parts,
            'evidence_source_ids':['osm-851362838','mews-east-2023','rbkc-4pgm-loft2021-2023'],
            'observations':['Licensed street view shows pale divided windows and sloped slate roofs on unidentified neighbours; exact4 is not identified','Exact4PP21/06281loft-redesign record supports roof-level history, not current shape or implementation'],
            'uncertainty':['Facade bays, window dimensions, rear apertures, inset roof-tier detail and rainwater pipe are artistic completion, not mapped observations',
                           'Two main levels retained fromOSM;exact4loft history informs estimated roof tier;6.850406060m is the retained source estimate, not a measured eaves height',
                           'All three normalized shared segments retain walls and suppress overlapping openings; no neighbour walls are removed',
                           'No inferred garage, basement, roof terrace, extra entry or imported1PrincesGateMews ramp',
                           'Original projected entrance and near-zero threshold preserved; coordinator supplies finite support to originalground-.05',
                           'Blender rendering and integration validation are pending coordinator']}
