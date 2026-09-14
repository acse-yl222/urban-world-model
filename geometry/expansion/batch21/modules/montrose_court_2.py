"""2 Montrose Court OSM-ID-specific two-storey interpretation.
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
    # Original west central entrance: paired broad ground windows flank it.
    # Three varied upper lights and two broad rear bays are artistic estimates.
    floor_positions={0:{0:[2.30,8.55],1:[2.30,5.48,8.55]},
                     2:{0:[2.65,8.15],1:[2.65,8.15]}}
    for ei,(a,L,u,n) in enumerate(edges):
        def at(s,d,z):return(a[0]+u[0]*s+n[0]*d,a[1]+u[1]*s+n[1]*d,z0+z)
        def panel(g,m,l,r,lo,hi,d=-.20,t=.40):
            if r-l>1e-6 and hi-lo>1e-6:box(g,m,at((l+r)/2,d,(lo+hi)/2),(r-l,t,hi-lo),u,n)
        door_s=sum((exy[k]-a[k])*u[k] for k in[0,1]) if exy and ei==entry_edge else None
        for floor in range(levels):
            low=pitch*floor;high=pitch*(floor+1);holes=[]
            for bi,s in enumerate(floor_positions.get(ei,{}).get(floor,[])):
                # Widths vary between exposed front and rear facades.
                w=(2.15 if ei==0 else 2.50) if floor==0 else (1.65 if ei==0 else 2.05)
                bot=low+(.82 if floor==0 else .76);top=high-(.73 if floor==0 else .68)
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
                    # Casement stiles are full height; rails stop at their inner faces.
                    # No crossing glazing-bar overlay or classical lintel.
                    x=l+w*(.32 if ei==0 else .50)
                    panel('modern asymmetrical casement stile','metal',x-.025,x+.025,bot+.055,top-.055,-.10,.12)
                    panel('contained simple sill','trim',l-.055,r+.055,bot-.075,bot-.015,.015,.15)
                else:
                    # Flush estimated modern leaf with a narrow recessed vertical panel.
                    panel('plain entrance vertical infill','door',l+.16,r-.16,.18,2.42,-.302,.024)
                    panel('entry pull handle','metal',r-.22,r-.19,1.05,1.38,-.265,.045)
                    panel('simple entrance head surround','trim',l-.12,r+.12,top+.035,top+.14,.01,.15)
                    for x in[l-.075,r+.075]:panel('entrance jamb surround','trim',x-.045,x+.045,0,top+.035,.01,.15)
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
        for l,r in (spans if ei in [0,2] else []):panel('segmented low plinth','masonry',l,r,.01,.33,.012,.10)
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
        selected=[0,2] if free_only else list(range(N))
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
    # Complete source footprint deck is distinct from wall/band top planes.
    vv=[Vector((x,y,z0+H+.008)) for x,y in ring]
    ff=[tuple(q if isinstance(q,int) else vv.index(q) for q in tri) for tri in tessellate_polygon([vv])]
    mesh('complete original four point roof deck','roof',[(x,y,z0+H+.008) for x,y in ring],ff)
    # Low rim only on free edges: no additional shared boundary wall height.
    band('free edge contained low roof rim','masonry',H-.025,H+.24,-.25,-.07,True)
    band('free edge contained roof coping','trim',H+.24,H+.29,-.27,-.05,True)
    roof_parts.append({'name':'complete four point flat deck','z':z0+H+.008,'full_footprint':True,
                       'low_rim_max_z':z0+H+.29,'rim_edges':[0,2],
                       'basis':'Flat roof and contained low rim are artistic estimates, no exact current roof photograph'})
    created=[]
    for (group,mat),(vertices,faces) in groups.items():
        if not faces:continue
        # Partial-edge bands allocate the full mitre ring. Remove unused ring
        # corners before export so Blender and GLB bounds describe the same faces.
        used=sorted({index for face in faces for index in face})
        remap={old:new for new,old in enumerate(used)}
        vertices=[vertices[index] for index in used]
        faces=[tuple(remap[index] for index in face) for face in faces]
        name='2 Montrose Court | '+group;m=bpy.data.meshes.new(name);m.from_pydata(vertices,[],faces);m.update()
        bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
        o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);m.materials.append(materials[mat]);o['building_id']=feature['id'];o['research_object_id']=feature['id']+'::'+group;o['evidence_status']='Historic two-storey estate context; exact2 facade and roof artistic estimates';created.append(o.name)
    if entrance is None:raise ValueError('Original entrance not generated')
    return {'created':created,'parameters':{'base_z':z0,'height_m':H,'main_wall_height_m':H,'eaves_height_m':H,'levels':levels,'roof_levels':0,'roof_max_z':z0+H+.29,'wall_thickness_m':.40,'opening_count':len(openings)},
            'interfaces':{'entrance':entrance,'additional_entrances':[],'shared_walls':common},'openings':openings,'roof_parts':roof_parts,
            'evidence_source_ids':['osm-640457473','montrose-group-judgment','montrose2-official-address','montrose-architect-context','clarke-street-context'],
            'observations':['Official address field identifies2MontroseCourtSW72QH, not a measured building description',
                            'Historical judgment distinguishes two-storey house row from large eight-storey block',
                            'Unnumbered architect estate project describes1950swhite render; no exact2 facade identified'],
            'uncertainty':['Window bays, contemporary casement widths, entry leaf, pipe and flat roof rim are artistic estimates',
                           'Source height6.850345288m is retained estimated eaves, not measurement',
                           'Both normalized shared segments remain complete and opaque at common heights',
                           'Number1extension and entrance relocation history is not transferred; no attic, basement, garage or extra entry',
                           'Original west entry and near-zero datum retained; coordinator supplies finite support to sourceground-.05',
                           'Blender rendering and integration validation pending coordinator']}
