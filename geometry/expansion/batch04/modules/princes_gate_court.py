"""Princes Gate Court: mapped six-storey mansion block with photo-informed courtyard.
Authoring only; no global scene mutation, external data retrieval or export.
"""
import math

def build(feature, materials):
    import bpy,bmesh
    from mathutils import Vector
    from mathutils.geometry import tessellate_polygon
    ring=[tuple(map(float,p[:2])) for p in feature['ring']]
    if ring[0]==ring[-1]:ring.pop()
    if sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1]))<0:raise ValueError('CCW ring required to preserve edge contract')
    z0=float(feature.get('base_z',.05));H=float(feature['height_m']);levels=6;pitch=H/levels
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
    for ei,(a,L,u,n) in enumerate(edges):
        def at(s,d,z):return(a[0]+u[0]*s+n[0]*d,a[1]+u[1]*s+n[1]*d,z0+z)
        def panel(g,m,l,r,lo,hi,d=-.2,t=.4):box(g,m,at((l+r)/2,d,(lo+hi)/2),(r-l,t,hi-lo),u,n)
        count=max(1,round(L/3.1)) if L>2.0 else 0
        centers=[L*(k+.5)/count for k in range(count)]
        door_s=sum((exy[k]-a[k])*u[k] for k in range(2)) if exy and ei==entry_edge else L/2
        for floor in range(levels):
            low=pitch*floor;high=pitch*(floor+1);holes=[]
            for bi,s in enumerate(centers):
                w=min(1.42,L/count-.7);bot=low+(.85 if floor==0 else .65);top=high-.48
                if floor==0 and ei==entry_edge and abs(s-door_s)<1.75:continue
                if blocked(ei,s-w/2,s+w/2,bot,top):continue
                holes.append((s-w/2,s+w/2,bot,top,False,bi))
            if floor==0 and ei==entry_edge:
                w=float(entry.get('clear_width_m',1.05))+.16
                holes.append((door_s-w/2,door_s+w/2,0,min(3,high-.12),True,-1))
            cuts=sorted(set([0,L]+[v for h in holes for v in h[:2]]))
            for l,r in zip(cuts,cuts[1:]):
                h=next((h for h in holes if h[0]<(l+r)/2<h[1]),None)
                if h:panel('pierced red brick facades','masonry',l,r,low,h[2]);panel('pierced red brick facades','masonry',l,r,h[3],high)
                else:panel('pierced red brick facades','masonry',l,r,low,high)
            for l,r,bot,top,door,bi in holes:
                s=(l+r)/2;w=r-l
                panel('entrance leaves' if door else 'recessed courtyard sashes','door' if door else 'glass',l+.065,r-.065,bot if door else bot+.06,top-.06,-.34,.06)
                for xx in (l+.035,r-.035):panel('white sash frames','trim',xx-.035,xx+.035,bot,top,-.26,.11)
                for zz in ((top-.035,) if door else (bot+.035,top-.035)):panel('white sash frames','trim',l,r,zz-.035,zz+.035,-.26,.11)
                if not door:
                    for frac in (1/3,2/3):panel('small pane glazing bars','trim',l+w*frac-.02,l+w*frac+.02,bot,top,-.245,.055)
                    for frac in (.25,.5,.75):panel('small pane glazing bars','trim',l,r,bot+(top-bot)*frac-.021,bot+(top-bot)*frac+.021,-.245,.055)
                    panel('stone window sills','trim',l-.09,r+.09,bot-.105,bot-.025,.035,.21)
                    panel('subtle brick headers','masonry',l-.06,r+.06,top+.015,top+.13,.025,.12)
                    if ei in (15,19) and bi==0:
                        # Photo shows a vertical dressed-stone bay at the courtyard return.
                        for xx in (l-.16,r+.16):panel('courtyard stone vertical bays','trim',xx-.095,xx+.095,low,high,.065,.17)
                        panel('courtyard stone vertical bays','trim',l-.25,r+.25,low,bot-.02,.065,.17)
                        panel('courtyard stone vertical bays','trim',l-.25,r+.25,top+.02,high,.065,.17)
                else:
                    for xx in (l-.17,r+.17):panel('stone entrance jambs','trim',xx-.12,xx+.12,0,top+.30,.08,.28)
                    panel('stone entrance entablature','trim',l-.36,r+.36,top+.13,top+.36,.11,.40)
                    panel('entry transom','trim',l,r,top-.6,top-.53,-.25,.11)
                    panel('door central stile','trim',s-.025,s+.025,0,top-.6,-.25,.10)
                    box('door hardware','metal',at(s+.28,-.19,1.1),(.035,.08,.24),u,n)
                    panel('flush threshold','trim',l-.12,r+.12,-.006,0,-.17,.40)
                    entrance={'threshold_xyz':list(at(s,0,0)),'outward_normal':[n[0],n[1],0],'clear_width_m':w-.16,'door_leaf_xyz':list(at(s,-.34,top/2)),'stair_treads':[],'ramp':'none authored','surface_owner':'coordinator','basis':'preserved baseline lateral position; threshold projected to wall'}
                openings.append({'edge':ei,'floor':floor,'bay':bi,'type':'door' if door else 'window','width_m':w,'height_m':top-bot,'recess_m':.34,'basis':'photo-informed architectural vocabulary; dimensions estimated'})
        # Pale stone ground-floor base skirt; above openings sill height.
        if ei!=entry_edge:panel('pale stone plinth','trim',0,L,.02,.72,.015,.10)
        else:
            panel('pale stone plinth','trim',0,max(0,door_s-.78),.02,.72,.015,.1);panel('pale stone plinth','trim',min(L,door_s+.78),L,.02,.72,.015,.1)
    def offset(d):
        out=[]
        for i,p in enumerate(ring):
            na=edges[i-1][3];nb=edges[i][3];den=1+sum(na[k]*nb[k] for k in range(2));v=d/max(.08,den);out.append((p[0]+v*(na[0]+nb[0]),p[1]+v*(na[1]+nb[1])))
        return out
    def band(g,m,lo,hi,dep,th):
        inner=offset(dep-th/2);outer=offset(dep+th/2);N=len(ring);v=[(x,y,z0+z) for z in (lo,hi) for c in (inner,outer) for x,y in c];f=[]
        for i in range(N):
            j=(i+1)%N;f.extend([(i,j,N+j,N+i),(2*N+i,3*N+i,3*N+j,2*N+j),(i,2*N+i,2*N+j,j),(N+i,N+j,3*N+j,3*N+i)])
        mesh(g,m,v,f)
    for zz,th,dep in [(4*pitch,.15,.04),(5*pitch,.22,.08),(H-.12,.26,.14)]:band('upper stone string courses','trim',zz-th/2,zz+th/2,dep,.22)
    band('red brick roof parapet','masonry',H,H+.37,-.17,.34);band('stone parapet coping','trim',H+.37,H+.47,-.15,.4)
    vv=[Vector((x,y,z0+H-.06)) for x,y in ring];v=[];f=[]
    for tri in tessellate_polygon([vv]):
        off=len(v);v.extend(tuple(vv[q] if isinstance(q,int) else q) for q in tri);f.append((off,off+1,off+2))
    mesh('complete concave roof deck','roof',v,f)
    def inside(p):
        hit=False
        for a,b in zip(ring,ring[1:]+ring[:1]):
            if (a[1]>p[1])!=(b[1]>p[1]) and p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]:hit=not hit
        return hit
    for ei,(a,L,u,n) in enumerate(edges):
        if L<7:continue
        def at(s,d,z):return(a[0]+u[0]*s+n[0]*d,a[1]+u[1]*s+n[1]*d,z0+z)
        left,right=.65,L-.65;deep=2.3
        if not all(inside(at(left+(right-left)*j/12,-.5-(deep-.5)*k/5,0)[:2]) for j in range(13) for k in range(6)):continue
        # Short sloping perimeter roof ranges coexist with mapped flat central decks.
        v=[at(left,-.5,H+.10),at(right,-.5,H+.10),at(right,-deep,H+2.35),at(left,-deep,H+2.35),at(left,-deep,H-.06),at(right,-deep,H-.06)]
        mesh('inset sloping roof ranges','roof',v,[(0,1,2,3),(0,3,4),(1,5,2),(2,5,4,3)])
        roof_parts.append({'edge':ei,'length_m':right-left,'inset_m':deep,'rise_m':2.35,'basis':'2007 photograph and 2017 planning description support dormered pitch; exact plan estimated'})
        count=max(1,int((right-left)/6))
        for k in range(count):
            s=left+(right-left)*(k+.5)/count
            # Front glass sits ahead of lower sloped roof, so the opening is real.
            for xx in (-.73,.73):box('white dormer cheek walls','trim',at(s+xx,-1.25,H+1.17),(.16,1.0,2.46),u,n)
            box('dormer rear closure','trim',at(s,-1.70,H+1.17),(1.62,.1,2.46),u,n)
            box('dormer front sill','trim',at(s,-.80,H+.28),(1.62,.10,.68),u,n)
            box('dormer cap','roof',at(s,-1.25,H+2.45),(1.8,1.15,.14),u,n)
            box('recessed dormer glass','glass',at(s,-.80,H+1.45),(1.28,.055,1.65),u,n)
            for xx in (-.68,0,.68):box('white dormer joinery','trim',at(s+xx,-.745,H+1.45),(.06,.08,1.80),u,n)
            for zz in (.56,1.15,1.75,2.34):box('white dormer joinery','trim',at(s,-.745,H+zz),(1.42,.08,.055),u,n)
    created=[]
    for (g,m),(v,f) in groups.items():
        if not f:continue
        name='Princes Gate Court | '+g;me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(materials[m]);ob['building_id']=feature['id'];ob['research_object_id']=feature['id']+'::'+g;ob['evidence_status']='Mapped plan and levels; licensed courtyard photograph-informed interpretation';created.append(ob.name)
    return {'created':created,'parameters':{'height_m':H,'eaves_height_m':H,'base_z':z0,'levels':levels,'roof_levels':1,'roof_max_z':z0+H+2.52,'opening_count':len(openings),'wall_thickness_m':.4},'interfaces':{'entrance':entrance,'additional_entrances':[],'shared_walls':common},'openings':openings,'roof_parts':roof_parts,'evidence_source_ids':['osm-20260912','geograph-396643','westminster-2017-princes-gate-court'],'uncertainty':['Six main levels and original estimated eaves preserved; not a surveyed height','The 2007 courtyard photo supports facade language, not all rear apertures or current roof alterations','Flat OSM roof tag conflicts with visible dormered roof margins; complete flat deck plus estimated sloping perimeter segments reconcile sources explicitly','Exact stone corner-panel positions and hidden roof services are unknown; no invented mechanical equipment','Footprint courtyard and concave returns retained; shared wall windows suppressed only over audited common height intervals']}
