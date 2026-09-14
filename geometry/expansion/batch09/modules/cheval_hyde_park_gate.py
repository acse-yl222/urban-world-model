"""Cheval Hyde Park Gate: mapped plan, HE1080596 architecture, estimated dimensions.
No scene/global operations. build(feature, materials) returns objects/interfaces.
"""
import math

def build(feature, materials):
    import bpy, bmesh
    from mathutils import Vector
    from mathutils.geometry import tessellate_polygon
    ring=[tuple(map(float,p)) for p in feature['ring']]
    area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(ring,ring[1:]+ring[:1]))/2
    if area<=0:raise ValueError('CCW full footprint required')
    z0=float(feature['base_z']);H=float(feature.get('height_m',21.5))  # Coordinator visual estimate, not survey.
    if H<19: raise ValueError('Coordinated north-group height feature required')
    E=feature['entry'];groups={};openings=[];entry_out=None
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
    # Distinct seven-bay north composition; rear spacing remains an explicit estimate.
    fronts={7:[2.25,5.6,8.9,12.9,16.4,19.7,23.1],4:[2.3,6.1,10.,14.,18.,21.3],1:[2.8],5:[1.4],8:[.86]}
    shared={0:13.1500305619,2:9.9995345733,6:H+z0}
    for nb in feature.get('audit',{}).get('adjacent_or_detailed_neighbours_within_35m',[]):
        ht=nb.get('neighbour_height_basis',{}).get('wall_top_z')
        for ei in nb.get('target_shared_edge_indices',[]):
            if ht is not None:shared[ei]=max(shared.get(ei,-1e10),ht)
    levels=[H*f for f in [0,.224,.451,.647,.825,1.0]]
    F=levels[1]
    entry_edge=E['edge_index']
    for ei,(a,b) in enumerate(zip(ring,ring[1:]+ring[:1])):
        L=math.dist(a,b);u=((b[0]-a[0])/L,(b[1]-a[1])/L);n=(u[1],-u[0])
        def at(s,d,z):return(a[0]+u[0]*s+n[0]*d,a[1]+u[1]*s+n[1]*d,z0+z)
        def panel(group,mat,l,r,lo,hi,d=-.22,t=.44):
            if r-l>1e-5 and hi-lo>1e-5:box(group,mat,at((l+r)/2,d,(lo+hi)/2),(r-l,t,hi-lo),u,n)
        def beam(group,mat,s1,z1,s2,z2,d=.12,thick=.10):
            length=math.hypot(s2-s1,z2-z1);ds=-(z2-z1)/length*thick/2;dz=(s2-s1)/length*thick/2
            v=[at(s+q*ds,dep,z+q*dz) for dep in[d-.08,d+.08] for s,z in[(s1,z1),(s2,z2)] for q in[-1,1]]
            part(group,mat,v,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)])
        positions=fronts.get(ei,[])
        for li,(lo,hi) in enumerate(zip(levels,levels[1:])):
            holes=[]
            for si,s in enumerate(positions):
                if L<2 and li<1:continue
                w=min(1.35 if li==0 else (1.55 if li==1 else 1.35),L-.45)
                bottom=lo+(.72 if li==0 else .55);top=hi-(.68 if li<3 else .45)
                if ei in shared and z0+bottom<shared[ei]+.35:continue
                door=ei==entry_edge and li==0 and abs(s-12.9)<.1
                if door:
                    s=sum((E['center_xy'][k]-a[k])*u[k] for k in[0,1]);w=E['clear_width_m']+.12;bottom=E['threshold_z']-z0;top=2.8
                if s-w/2<.15 or s+w/2>L-.15:continue
                holes.append((s-w/2,s+w/2,bottom,top,door))
            holes.sort();cursor=0
            for left,right,bottom,top,door in holes:
                panel('full depth wall piers','masonry',cursor,left,lo,hi)
                panel('wall below apertures','masonry',left,right,lo,bottom)
                # Subdivide a shallow curved head on ground windows, with true reveal.
                rise=.23 if li==0 and not door else 0
                if rise:
                    for q in range(12):
                        xl=left+(right-left)*q/12;xr=left+(right-left)*(q+1)/12
                        zl=top+rise*math.sin(math.pi*q/12);zr=top+rise*math.sin(math.pi*(q+1)/12)
                        v=[at(x,d,z) for d in[-.44,0] for x,z in[(xl,zl),(xr,zr),(xr,hi),(xl,hi)]]
                        part('curved window head masonry','masonry',v,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(3,7,6,2),(0,4,7,3),(1,2,6,5)])
                        beam('segmental ground archivolts','trim',xl,zl+.055,xr,zr+.055,.08,.12)
                else:panel('wall lintels','masonry',left,right,top,hi)
                mid=(left+right)/2;w=right-left
                # Deep glazing / leaf and reveal trims; no face covering the aperture plane.
                panel('entrance leaf' if door else 'recessed glazing','door' if door else 'glass',left+.045,right-.045,bottom+.015,top-.035,d=-.37,t=.045)
                for x in[left+.025,right-.025]:panel('door jamb' if door else 'sash jamb','trim' if door else 'metal',x-.025,x+.025,bottom,top,d=-.12,t=.10)
                if not door:
                    for z in[bottom+.03,(bottom+top)/2,top-.03]:panel('window sash rails','metal',left+.03,right-.03,z-.024,z+.024,d=-.115,t=.09)
                    panel('sash central mullion','metal',mid-.022,mid+.022,bottom,top,d=-.115,t=.09)
                    panel('projecting window sill','trim',left-.12,right+.12,bottom-.10,bottom+.02,d=.11,t=.40)
                else:
                    panel('door lintel frame','trim',left-.06,right+.06,top,top+.10,d=.03,t=.18)
                    for z in[.55,1.65,2.35]:panel('door leaf raised panels','door',left+.17,right-.17,z-.20,z+.20,d=-.335,t=.025)
                    entry_out={'center_xy':list(E['center_xy']),'threshold_xy':list(E['center_xy']),'threshold_z':E['threshold_z'],'outward_normal_xy':list(n),'clear_width_m':E['clear_width_m'],'clear_height_m':top-bottom,'leaf_recess_m':.37,'leaf_center_xy':[at(mid,-.37,0)[k] for k in[0,1]],'existing_support_z':E.get('existing_support_z'),'ground_owner':'coordinator'}
                for x in[left-.08,right+.08]:panel('aperture stone surround','trim',x-.055,x+.055,bottom-.02,top+.08,d=.055,t=.18)
                if ei==7 and not door:
                    if li==1:
                        for x in[left-.21,right+.21]:column('first floor Ionic shafts',at(x,.19,0)[:2],bottom-.08,top+.04,.073)
                        for x in[left-.24,right+.24]:
                            box('Ionic capital volute blocks','trim',at(x,.19,top+.02),(.22,.20,.11),u,n)
                        beam('triangular first floor pediments','trim',left-.32,top+.22,mid,top+.67,.14,.14)
                        beam('triangular first floor pediments','trim',mid,top+.67,right+.32,top+.22,.14,.14)
                    elif li==2:
                        for q in range(16):
                            x1=left-.18+(w+.36)*q/16;x2=left-.18+(w+.36)*(q+1)/16
                            zz=lambda q:top+.15+.24*math.sin(math.pi*q/16)
                            beam('second floor curved pediments','trim',x1,zz(q),x2,zz(q+1),.15,.11)
                    elif li==4:
                        for x in[left-.29,right+.29]:
                            panel('top floor giant consoles','trim',x-.12,x+.12,lo+.25,hi-.12,d=.12,t=.38)
                            box('stylised bearded mask blocks estimated','trim',at(x,.35,hi-.65),(.22,.17,.28),u,n)
                openings.append({'edge':ei,'level':li,'left':left,'right':right,'bottom':z0+bottom,'top':z0+top+rise,'door':door})
                cursor=right
            panel('full depth wall piers','masonry',cursor,L,lo,hi)
        # Ground rustication is segmented around true holes, including doorway.
        for z in[.35+i*.45 for i in range(int((F-.65)/.45))]:
            cuts=[(o['left']-.10,o['right']+.10) for o in openings if o['edge']==ei and o['bottom']-.06<=z0+z<=o['top']+.06];left=0
            for cl,cr in sorted(cuts):
                panel('rusticated stucco course edges','trim',left,max(left,cl),z,z+.025,d=.012,t=.04);left=max(left,cr)
            panel('rusticated stucco course edges','trim',left,L,z,z+.025,d=.012,t=.04)
    # Continuous mitred bands preserve every concave footprint vertex.
    for z,dep,h in[(levels[1]-.10,.22,.16),(levels[2]-.07,.12,.11),(levels[3]-.07,.20,.15),(H-.30,.30,.18),(H-.08,.42,.16)]:
        continuous_band('continuous mitred cornices','trim',-.06,dep,z,z+h)
    cap('full concave footprint roof','roof',ring,H)
    # Five floors plus explicit estimated recessed attic; convex-hull never used.
    a,b=ring[7],ring[8];L=math.dist(a,b);u=((b[0]-a[0])/L,(b[1]-a[1])/L);n=(u[1],-u[0])
    def front(s,d,z):return(a[0]+u[0]*s+n[0]*d,a[1]+u[1]*s+n[1]*d,z0+z)
    low=[front(s,d,H+.04) for s,d in[(1.5,-1.5),(L-1.5,-1.5),(L-1.5,-11),(1.5,-11)]]
    high=[front(s,d,H+2.5) for s,d in[(2.5,-2.5),(L-2.5,-2.5),(L-2.5,-10),(2.5,-10)]]
    part('estimated recessed attic mansard','roof',low+high,[(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)])
    # Photograph-supported rounded dormers; spacing and dimensions remain estimates.
    # Front roof slope is partitioned around actual apertures, never behind glass.
    def slope(s,z):return front(s,-1.5-(z-.04)/2.46,H+z)
    def roofpatch(sl,sr,bl,br,tl,tr):
        part('mansard front pierced roof','roof',[slope(sl,bl),slope(sr,br),slope(sr,tr),slope(sl,tl)],[(0,1,2,3)])
    # End triangles account for the upper rectangle's one-metre lateral inset.
    part('mansard front end slopes','roof',[low[0],slope(2.5,.04),high[0]],[(0,1,2)])
    part('mansard front end slopes','roof',[slope(L-2.5,.04),low[1],high[1]],[(0,1,2)])
    cursor=2.5
    for ds in [3.4+i*(L-6.8)/6 for i in range(7)]:
        le,ri=ds-.55,ds+.55;bot,top=.45,2.08
        roofpatch(cursor,le,.04,.04,2.5,2.5)
        roofpatch(le,ri,.04,.04,bot,bot);roofpatch(le,ri,top,top,2.5,2.5)
        # Projected vertical face with genuinely arched opening and full side cheeks.
        for x in [le,ri]:
            part('dormer side cheeks','roof',[front(x,-1.5,H+bot),slope(x,bot),slope(x,top),front(x,-1.5,H+top)],[(0,1,2,3)])
        box('dormer recessed glass','glass',front(ds,-1.62,H+1.18),(1.0,.035,1.39),u,n)
        for x in[le+.025,ri-.025]:box('dormer jambs','trim',front(x,-1.48,H+1.05),(.08,.18,1.2),u,n)
        for k in range(16):
            x1=le+1.1*k/16;x2=le+1.1*(k+1)/16
            z1=1.5+.48*math.sin(math.pi*k/16);z2=1.5+.48*math.sin(math.pi*(k+1)/16)
            part('rounded dormer heads','trim',[front(x1,-1.49,H+z1),front(x2,-1.49,H+z2),front(x2,-1.49,H+top),front(x1,-1.49,H+top)],[(0,1,2,3)])
        part('dormer top flashing','roof',[front(le,-1.5,H+top),front(ri,-1.5,H+top),slope(ri,top),slope(le,top)],[(0,1,2,3)])
        box('dormer sill','trim',front(ds,-1.5,H+bot),(1.16,.22,.09),u,n)
        box('dormer central sash','metal',front(ds,-1.46,H+1.14),(.045,.07,1.36),u,n)
        cursor=ri
    roofpatch(cursor,L-2.5,.04,.04,2.5,2.5)
    # Front balcony / Doric porch; column bases require coordinator support at z0.
    box('first floor balcony deck','trim',front(L/2,.48,F+.07),(L-.65,1.18,.20),u,n)
    for s in[.7+i*(L-1.4)/68 for i in range(69)]:column('balcony turned balusters',front(s,.95,0)[:2],F+.18,F+.88,.043)
    box('balcony cap rail','trim',front(L/2,.95,F+.94),(L-.65,.22,.12),u,n)
    es=sum((E['center_xy'][k]-a[k])*u[k] for k in[0,1])
    for s in[es-1.02,es+1.02]:
        column('Doric entrance porch columns',front(s,.69,0)[:2],0,F-.32,.15)
    box('Doric porch entablature','trim',front(es,.47,F-.22),(2.65,1.15,.27),u,n)
    for s in[es-1.12+i*.28 for i in range(9)]:box('porch triglyph blocks','trim',front(s,1.06,F-.19),(.10,.065,.18),u,n)
    # Roof parapet finish and distinctive spiked globes from official description.
    continuous_band('parapet continuous upstand','trim',-.12,.08,H+.08,H+.38)
    for s in[1.2,L/2,L-1.2]:
        column('parapet finial plinths',front(s,.03,0)[:2],H+.38,H+.64,.10)
        # Lathed sphere profile with narrow pointed cap, stylised not sculptural survey.
        xy=front(s,.03,0)[:2];v=[];faces=[]
        prof=[(H+.64,.03),(H+.70,.14),(H+.82,.19),(H+.95,.14),(H+1.01,.035),(H+1.27,.005)]
        for z,rad in prof:
            v.extend((xy[0]+rad*math.cos(2*math.pi*k/16),xy[1]+rad*math.sin(2*math.pi*k/16),z0+z) for k in range(16))
        for j in range(len(prof)-1):
            for k in range(16):q=(k+1)%16;faces.append((j*16+k,j*16+q,(j+1)*16+q,(j+1)*16+k))
        part('stylised spiked globes','trim',v,faces)
    # Generic coordinator contract; geometry and source threshold are unchanged.
    if entry_out is None:raise ValueError('Expected source entrance was not authored')
    entrance={
        'threshold_xyz':[*entry_out['threshold_xy'],entry_out['threshold_z']],
        'outward_normal':[*entry_out['outward_normal_xy'],0.0],
        'door_leaf_xyz':[*entry_out['leaf_center_xy'],entry_out['threshold_z']+entry_out['clear_height_m']/2],
        'clear_width_m':entry_out['clear_width_m'],
        'clear_height_m':entry_out['clear_height_m'],
        'leaf_recess_m':entry_out['leaf_recess_m'],
        'stair_treads':[], 'ramp':'none authored', 'surface_owner':'coordinator',
        'basis':'Original projected aperture and threshold retained; leaf geometry recess .37m',
        'additional_supports':[{
            'polygon_xy':[list(front(es+ss,dd,0)[:2]) for ss,dd in[(-1.35,-.10),(1.35,-.10),(1.35,1.05),(-1.35,1.05)]],
            'top_z':z0,
            'basis':'Estimated finite porch support requested from coordinator; covers both Doric column bases including .2175m foot radius, not a slab authored in this module'
        }]
    }
    common=[]
    for adj in feature.get('audit',{}).get('adjacent_or_detailed_neighbours_within_35m',[]):
        geo=adj.get('shared_boundary_geometry') or {};interval=adj.get('shared_wall_potential_height_interval_m')
        if not interval:continue
        lines=[geo.get('coordinates',[])] if geo.get('type')=='LineString' else geo.get('coordinates',[]) if geo.get('type')=='MultiLineString' else []
        for line in lines:
            for p,q in zip(line,line[1:]):
                for ei,(aa,bb) in enumerate(zip(ring,ring[1:]+ring[:1])):
                    ll=math.dist(aa,bb);uu=[(bb[k]-aa[k])/ll for k in[0,1]];nn=[uu[1],-uu[0]]
                    if max(abs(sum((v[k]-aa[k])*nn[k] for k in[0,1])) for v in[p,q])>.03:continue
                    span=sorted(sum((v[k]-aa[k])*uu[k] for k in[0,1]) for v in[p,q]);lo=max(0,span[0]);hi=min(ll,span[1])
                    if hi-lo>.03:
                        zz=[max(z0,interval[0]),min(z0+H,interval[1])]
                        if zz[1]>zz[0]:common.append({'edge':ei,'s_interval':[lo,hi],'height_interval':zz,'polyline':[p,q],'neighbour':adj['id'],'openings':[]})
    created=[]
    for (group,mat),(vertices,faces) in groups.items():
        if not faces:continue
        name='Cheval Hyde Park Gate | '+group;mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update()
        obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);mesh.materials.append(materials[mat]);obj['building_id']=feature['id'];obj['research_object_id']=feature['id']+'::'+group;obj['evidence_status']='HE architectural description; dimensions and hidden elevations estimated';created.append(obj.name)
    return {'created':created,'parameters':{'base_z':z0,'main_wall_height_m':H,'storeys':5,'attic_height_m':2.5,'roof_max_z':z0+H+2.5,'mapped_footprint_area_m2':area,'opening_count':len(openings)},'interfaces':{'entrance':entrance,'additional_entrances':[],'shared_walls':common,'shared_wall_top_estimates':shared,'attic_setback_m':1.5,'attic_footprint_xy':[list(p[:2]) for p in low],'openings':openings},'evidence_source_ids':['he-1080596','cheval-about','osm-809238777','geograph-5416380-context','commons-123701629','rbkc-queensgate-3.24'],'observations':['Official HE group description supports five storeys, attic, stucco, Doric porch, Ionic first-floor windows, curved second-floor pediments and parapet spiked globes','CC group-context photograph confirms pale stucco, balustrade and projecting window surrounds, with major tree occlusion'],'uncertainty':['Seven front bays and all dimensions are artistic estimates; source group description is not a complete current as-built elevation','2022 licensed north-corner photograph supports five floors and rounded dormers; main21.5m is a visual estimate, attic2.5m and bay spacing remain estimated; rear openings and attic extent estimated','Basement exists in official text but no ground excavation or basement windows created; ground interface belongs to coordinator','Not yet Blender-integrated or visually verified']}
