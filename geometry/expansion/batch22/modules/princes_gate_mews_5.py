"""5 Princes Gate Mews OSM-ID-specific two-storey interpretation.
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
    # Broad paired front casements flank original central entry; rear opens only
    # above the low neighbour. All exact bay proportions are artistic estimates.
    floor_positions={3:{0:[2.40,8.20],1:[2.10,5.30,8.50]},
                     1:{0:[],1:[2.25,5.30,8.30]}}
    for ei,(a,L,u,n) in enumerate(edges):
        def at(s,d,z):return(a[0]+u[0]*s+n[0]*d,a[1]+u[1]*s+n[1]*d,z0+z)
        def panel(g,m,l,r,lo,hi,d=-.20,t=.40):
            if r-l>1e-6 and hi-lo>1e-6:box(g,m,at((l+r)/2,d,(lo+hi)/2),(r-l,t,hi-lo),u,n)
        door_s=sum((exy[k]-a[k])*u[k] for k in[0,1]) if exy and ei==entry_edge else None
        for floor in range(levels):
            low=pitch*floor;high=pitch*(floor+1);holes=[]
            for bi,s in enumerate(floor_positions.get(ei,{}).get(floor,[])):
                # Larger ground casements; smaller upper sashes, not duplicated rows.
                w=(1.85 if ei==3 else 1.15) if floor==0 else 1.45
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
        for l,r in (spans if ei in [3] else []):panel('segmented low plinth','masonry',l,r,.01,.33,.012,.10)
        # Estimated downpipe on select return corners; attached within rear facade extents.
        if ei==3:
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
        selected=[3] if free_only else list(range(N))
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
    # Exact5 monitored mansard completion motivates an estimated contained tier,
    # basement is not authored. Main shared walls stop at H.
    rise=float(feature['roof_tier']['height_m']);inset=float(feature['roof_tier']['inset_m'])
    lower=offset(-inset);upper=offset(-(inset+.55));N=len(ring);upper_openings=[]
    def capmesh(name,rr,z):
        vv=[Vector((x,y,z0+z)) for x,y in rr]
        # Resolve only against tessellator Vector inputs; keep source doubles.
        original=[(x,y,z0+z) for x,y in rr];ff=[]
        for tri in tessellate_polygon([vv]):
            ff.append(tuple(q if isinstance(q,int) else vv.index(q) for q in tri))
        mesh(name,'roof',original,ff)
    capmesh('complete four point original footprint deck',ring,H+.008)
    # Sloped mansard shell with actual apertures, not windows pasted onto roof.
    # Lower ring uses contracted inset; upper ring retreats another .55m.
    for ei in range(N):
        jj=(ei+1)%N;L=math.dist(lower[ei],lower[jj]);normal=edges[ei][3]
        def pt(t,z,d):
            f=z/rise
            lo=[lower[ei][k]*(1-t)+lower[jj][k]*t for k in [0,1]]
            hi=[upper[ei][k]*(1-t)+upper[jj][k]*t for k in [0,1]]
            return (lo[0]*(1-f)+hi[0]*f+normal[0]*d,lo[1]*(1-f)+hi[1]*f+normal[1]*d,z0+H+z)
        def up(l,r,bot,top,g='pierced mansard slope',mat='roof',outer=0,inner=-.18):
            if r<=l or top<=bot:return
            vs=[pt(t,z,d) for d in [inner,outer] for t,z in [(l,bot),(r,bot),(r,top),(l,top)]]
            mesh(g,mat,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
        positions=[.28,.72] if ei in [1,3] else []
        holes=[(t-.56/L,t+.56/L,.45,rise-.45) for t in positions]
        cursor=0
        for l,r,bot,top in holes:
            up(cursor,l,-.005,rise-.025);up(l,r,-.005,bot);up(l,r,top,rise-.025)
            w=.055/L
            up(l+w,r-w,bot+.045,top-.045,'deep mansard recessed glazing','glass',-.11,-.15)
            for aa,bb in [(l,l+w),(r-w,r)]:up(aa,bb,bot,top,'mansard frame stiles','trim',.025,-.04)
            for zz in [bot,top-.055]:up(l+w,r-w,zz,zz+.055,'mansard frame rails','trim',.025,-.04)
            upper_openings.append({'inset_edge':ei,'s_interval':[l*L,r*L],'z_interval':[z0+H+bot,z0+H+top],'inset_m':inset,'basis':'Artistic recessed roof casement in actual sloped opening; no exact dormer count evidence'})
            cursor=r
        up(cursor,1,-.005,rise-.025)
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
    roof_parts.extend([{'name':'full original four point footprint deck','z':z0+H+.008,'full_footprint':True},
                       {'name':'estimated contained mansard tier','count':1,'inset_m':inset,'upper_inset_m':inset+.55,'rise_m':rise,
                        'max_z':z0+H+rise,'glazing':upper_openings,'boundary_shared_height_increased':False,
                        'basis':'Exact5 AMR monitored completion includes mansard; rise/setback/openings are artistic estimates'}])
    created=[]
    for (group,mat),(vertices,faces) in groups.items():
        if not faces:continue
        # Partial-edge bands allocate the full mitre ring. Remove unused ring
        # corners before export so Blender and GLB bounds describe the same faces.
        used=sorted({index for face in faces for index in face})
        remap={old:new for new,old in enumerate(used)}
        vertices=[vertices[index] for index in used]
        faces=[tuple(remap[index] for index in face) for face in faces]
        name='5 Princes Gate Mews | '+group;m=bpy.data.meshes.new(name);m.from_pydata(vertices,[],faces);m.update()
        bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
        o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);m.materials.append(materials[mat]);o['building_id']=feature['id'];o['research_object_id']=feature['id']+'::'+group;o['evidence_status']='OSM two main levels; exact5 completed mansard typology; roof dimensions and facade artistically completed';created.append(o.name)
    if entrance is None:raise ValueError('Original entrance not generated')
    return {'created':created,'parameters':{'base_z':z0,'height_m':H,'main_wall_height_m':H,'eaves_height_m':H,'levels':levels,'roof_levels':1,'authored_total_visible_tiers':3,'roof_levels_semantics':'Two main plus one mansard interpretation of completed four-storey scheme including basement; dimensions estimated','roof_max_z':z0+H+rise,'wall_thickness_m':.40,'opening_count':len(openings),'inset_upper_opening_count':len(upper_openings),'total_authored_apertures':len(openings)+len(upper_openings)},
            'interfaces':{'entrance':entrance,'additional_entrances':[],'shared_walls':common},'openings':openings,'roof_parts':roof_parts,
            'evidence_source_ids':['osm-851362840','rbkc-5-permission2016','rbkc-5-completion2019','rbkc-5-ctmp2017','agent-5-current-description','mews-east-2023-context'],
            'observations':['Exact5 PP16/04150 occurs in official2019HousingCompletions table, includes mansard and basement',
                            'Four total storeys interpreted as two main plus roof plus basement, not four full aboveground levels',
                            'Licensed street image contextual only; no secure5door or roof attribution'],
            'uncertainty':['All front/rear bays, sash details, mansard .65m lower setback and2.1m rise are artistic estimates',
                           'Upper ring retreats an additional .55m; four recessed roof casements are not observed dormer count',
                           'All three normalizedshared segments preserved with no common-height apertures',
                           'Reported garage remains unlocated; no garage aperture, basement, lightwell, wintergarden or newentry authored',
                           'Source nearzero entry datum retained; coordinator supplies finiteground approach',
                           'Blender/export/render verification pending root']}
