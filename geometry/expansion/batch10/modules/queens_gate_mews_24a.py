"""24a Queen's Gate Mews OSM-ID-specific two-storey interpretation.
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
    for adj in feature.get('audit',{}).get('adjacent_or_detailed_neighbours_within_35m',[]):
        geo=adj.get('shared_boundary_geometry') or {};zz=adj.get('shared_wall_potential_height_interval_m')
        if not zz:continue
        lines=[geo.get('coordinates',[])] if geo.get('type')=='LineString' else geo.get('coordinates',[]) if geo.get('type')=='MultiLineString' else []
        for line in lines:
            for p,q in zip(line,line[1:]):
                for ei,(a,L,u,n) in enumerate(edges):
                    if max(abs(sum((v[k]-a[k])*n[k] for k in range(2))) for v in (p,q))>.03:continue
                    spans=sorted(sum((v[k]-a[k])*u[k] for k in range(2)) for v in (p,q));lo=max(0,spans[0]);hi=min(L,spans[1])
                    if hi-lo>.03:common.append({'edge':ei,'s_interval':[lo,hi],'height_interval':zz,'polyline':[p,q],'neighbour':adj['id'],'openings':[]})
    def blocked(ei,l,r,bot,top):return any(c['edge']==ei and l<c['s_interval'][1] and r>c['s_interval'][0] and z0+bot<c['height_interval'][1] and z0+top>c['height_interval'][0] for c in common)
    # Planned apertures differ between the mews front, rear and short return walls.
    floor_positions={0:{0:[3.05,6.35,12.45,15.80],1:[2.25,5.75,9.20,12.65,16.10]},
                     1:{0:[3.05,8.50],1:[2.6,5.95,9.3]},
                     2:{0:[2.65],1:[2.65]},3:{0:[],1:[]},4:{0:[],1:[]},
                     5:{0:[4.05],1:[2.55,5.75]},6:{0:[3.15,8.85],1:[2.55,6.25,10.05]}}
    for ei,(a,L,u,n) in enumerate(edges):
        def at(s,d,z):return(a[0]+u[0]*s+n[0]*d,a[1]+u[1]*s+n[1]*d,z0+z)
        def panel(g,m,l,r,lo,hi,d=-.20,t=.40):
            if r-l>1e-6 and hi-lo>1e-6:box(g,m,at((l+r)/2,d,(lo+hi)/2),(r-l,t,hi-lo),u,n)
        door_s=sum((exy[k]-a[k])*u[k] for k in[0,1]) if exy and ei==entry_edge else None
        for floor in range(levels):
            low=pitch*floor;high=pitch*(floor+1);holes=[]
            for bi,s in enumerate(floor_positions.get(ei,{}).get(floor,[])):
                # Larger ground casements; smaller upper sashes, not duplicated rows.
                w=(1.80 if ei==0 else 1.55) if floor==0 else 1.18
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
                panel('full thickness masonry piers','masonry',cursor,l,low,high)
                panel('wall below recessed apertures','masonry',l,r,low,bot)
                panel('solid wall lintels','masonry',l,r,top,high)
                s=(l+r)/2;w=r-l
                panel('painted entrance leaf' if door else 'deep inset glazing','door' if door else 'glass',l+.05,r-.05,bot if door else bot+.045,top-.045,-.34,.055)
                for x in[l+.028,r-.028]:panel('door jamb' if door else 'recessed window outer sash','trim',x-.028,x+.028,bot,top,-.105,.14)
                panel('door head frame' if door else 'recessed window outer sash','trim',l,r,top-.055,top,-.105,.14)
                if not door:
                    panel('recessed window bottom sash','trim',l,r,bot,bot+.055,-.105,.14)
                    if floor==0:
                        for frac in[1/3,2/3]:
                            x=l+w*frac;panel('tripartite mews casement mullions','trim',x-.025,x+.025,bot+.045,top-.04,-.10,.12)
                        panel('ground transom rail','trim',l,r,top-.48,top-.43,-.10,.12)
                    else:
                        panel('upper sash meeting rail','trim',l,r,(bot+top)/2-.034,(bot+top)/2+.034,-.10,.12)
                        panel('upper sash glazing bars','trim',s-.018,s+.018,bot+.05,top-.05,-.105,.08)
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
            panel('full thickness masonry piers','masonry',cursor,L,low,high)
        # Low plinth is split around source entrance and cannot cross its threshold.
        spans=[(0,L)] if door_s is None else [(0,door_s-.76),(door_s+.76,L)]
        for l,r in spans:panel('segmented low plinth','masonry',l,r,.01,.33,.012,.10)
        # Estimated downpipe on select return corners; attached within rear facade extents.
        if ei in[1,6]:
            box('estimated rear rainwater pipe','metal',at(.32,.13,H/2),(.075,.075,H-.20),u,n)
            for z in[1.0,3.0,5.0]:box('pipe fixing collars','metal',at(.32,.13,z),(.11,.10,.045),u,n)
    def offset(d):
        out=[]
        for i,p in enumerate(ring):
            na=edges[i-1][3];nb=edges[i][3];den=1+sum(na[k]*nb[k] for k in[0,1])
            if den<.08:raise ValueError('Unstable mitre requires explicit corner review')
            out.append((p[0]+d*(na[0]+nb[0])/den,p[1]+d*(na[1]+nb[1])/den))
        return out
    def band(g,m,lo,hi,inner,outer,skip_shared=False):
        aa=offset(inner);bb=offset(outer);N=len(ring);v=[(x,y,z0+z) for z in[lo,hi] for rr in[aa,bb] for x,y in rr];faces=[]
        for i in range(N):
            if skip_shared and i==4:continue
            j=(i+1)%N;faces.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
        if skip_shared:
            for k in[4,5]:faces.append((k,N+k,3*N+k,2*N+k))
        mesh(g,m,v,faces)
    band('continuous mitred intermediate sill course','trim',pitch-.12,pitch+.02,-.06,.11)
    band('continuous mitred modest eaves','trim',H-.18,H+.02,-.12,.22)
    band('roof upstand excluding attached edge4','masonry',H,H+.28,-.25,.00,True)
    band('stone coping excluding attached edge4','trim',H+.28,H+.38,-.30,.00,True)
    vv=[Vector((x,y,z0+H)) for x,y in ring]
    for tri in tessellate_polygon([vv]):mesh('full concave roof surface','roof',[tuple(vv[q] if isinstance(q,int) else q) for q in tri],[(0,1,2)])
    roof_parts.append({'name':'full mapped footprint flat roof','z':z0+H,'basis':'Retained full OSM roof plane, form estimated; no dormer or rooftop equipment evidence'})
    created=[]
    for (group,mat),(vertices,faces) in groups.items():
        if not faces:continue
        name='24a Queens Gate Mews | '+group;m=bpy.data.meshes.new(name);m.from_pydata(vertices,[],faces);m.update()
        bm=bmesh.new();bm.from_mesh(m);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(m);bm.free();m.update()
        o=bpy.data.objects.new(name,m);bpy.context.collection.objects.link(o);m.materials.append(materials[mat]);o['building_id']=feature['id'];o['research_object_id']=feature['id']+'::'+group;o['evidence_status']='OSM two-storey plan; CC street context only; unobserved facade and roof artistically completed';created.append(o.name)
    if entrance is None:raise ValueError('Original entrance not generated')
    return {'created':created,'parameters':{'base_z':z0,'height_m':H,'main_wall_height_m':H,'eaves_height_m':H,'levels':levels,'roof_levels':0,'roof_max_z':z0+H+.38,'wall_thickness_m':.40,'opening_count':len(openings)},
            'interfaces':{'entrance':entrance,'additional_entrances':[],'shared_walls':common},'openings':openings,'roof_parts':roof_parts,
            'evidence_source_ids':['osm-809238780','geograph-3860949-context'],
            'uncertainty':['Exact24a facade not identified in licensed imagery; source address/postcode unresolved against similarly named listings','Two levels from OSM;6.84986794m retained estimated wall height, not survey','Aperture layout, tripartite ground windows, soldier headers, roof parapet and rainwater pipes are artistic completion','Context photo is another view alongQueensGateMews, not evidence for this building or a garage','Full7-point footprint retained; sharededge4 blocked over full actual target interval; no basement, terrace, rooftop plant or stairs inferred','Finite support between sourceground-.05 and originalthreshold near0 belongs to coordinator; no Blender validation claimed']}
