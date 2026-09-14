#!/usr/bin/env python3
"""Prepare full mapped footprints and audited interfaces from local sources only.
No Blender, downloads, module generation or source-scene mutation. Writes only
batch features/manifest/reports. Target syntax: ID:slug:display name.
"""
import argparse, json, math, hashlib, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];PROJECT=ROOT.parent
sys.path.insert(0,str(PROJECT/'geometry/completion/.deps'))

def main():
    from pyproj import Transformer
    from shapely.geometry import Polygon,LineString,Point,mapping
    from shapely.geometry.polygon import orient
    from shapely.ops import polygonize,unary_union
    from shapely import make_valid
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--batch',required=True);ap.add_argument('--target',action='append',required=True);ap.add_argument('--context',type=Path,default=ROOT/'batch03/reports/context.json');args=ap.parse_args()
    if not args.batch.isdigit():ap.error('batch must be digits')
    targets=[s.split(':',2) for s in args.target]
    if any(len(t)!=3 for t in targets):ap.error('target syntax ID:slug:name')
    R=ROOT/('batch'+args.batch);(R/'features').mkdir(parents=True,exist_ok=True);(R/'reports').mkdir(exist_ok=True)
    source=json.load(open(PROJECT/'geometry/completion/sources/osm_buildings.json'))['elements'];assets={b['id']:b for b in json.load(open(ROOT/'asset_index.json'))['buildings']};ctx=json.load(open(args.context));ctxby={}
    for o in ctx['objects']:ctxby.setdefault(o['id'],[]).append(o)
    tf=Transformer.from_crs(4326,32630,always_xy=True);origin=[695238.304719173,5709236.965026026]
    def xy(g):return [(x-origin[0],y-origin[1]) for x,y in [tf.transform(v['lon'],v['lat']) for v in g]]
    polygons={};elements={};relation_count=0
    for e in source:
        bid=e['type']+'-'+str(e['id']);elements[bid]=e;p=None
        if len(e.get('geometry',[]))>=4:p=Polygon(xy(e['geometry']))
        elif e['type']=='relation':
            outer=[];inner=[]
            for m in e.get('members',[]):
                if len(m.get('geometry',[]))>=2:(inner if m.get('role')=='inner' else outer).append(LineString(xy(m['geometry'])))
            if outer:
                p=unary_union([make_valid(x) for x in polygonize(outer)]).difference(unary_union([make_valid(x) for x in polygonize(inner)]));relation_count+=1
        if p is not None and p.is_valid and not p.is_empty:polygons[bid]=p
    # Newest delivered geometry reports override stale core008 wall/roof bounds.
    latest={};delivered_reports=[]
    for report in sorted((ROOT/'output').glob('*/verification.json'),key=lambda p:p.stat().st_mtime):
        d=json.load(open(report))
        if not d.get('delivered'):continue
        delivered_reports.append(str(report.relative_to(PROJECT)))
        for bid,result in d.get('module_results',{}).items():
            bounds=[v['bounds'] for k,v in d.get('expected',{}).items() if k.startswith(bid+'::')]
            pars=result.get('parameters',{});bz=pars.get('base_z')
            if bz is None and bounds:bz=min(b[2] for b in bounds)
            ht=pars.get('eaves_height_m',pars.get('main_wall_height_m',pars.get('height_m')))
            wall_top=bz+ht if bz is not None and ht is not None else None
            # An explicitly flush attic continues the party wall above main eaves.
            # Do not use roof/parapet maxima or extend an inset mansard to the boundary.
            if wall_top is not None and pars.get('attic_inset_m')==0 and pars.get('attic_height_m',0)>0:
                wall_top=pars.get('attic_wall_top_z',wall_top+pars['attic_height_m'])
            latest[bid]={'report':str(report.relative_to(PROJECT)),'base_z':bz,'wall_top_z':wall_top,'geometry_z_bounds':[min(b[2] for b in bounds),max(b[5] for b in bounds)] if bounds else None,'parameters':pars,'interfaces':result.get('interfaces',{})}
    def pts(o):return [o['positions'][i:i+3] for i in range(0,len(o['positions']),3)]
    def original_heights(bid):
        oo=ctxby.get(bid,[]);roofs=[p[2] for o in oo if any('slate grey roof' in m for m in o['materials']) for p in pts(o)];doors=[p[2] for o in oo if any('painted entrance' in m for m in o['materials']) for p in pts(o)];zs=[p[2] for o in oo if o.get('extras',{}).get('semantic_type')!='entry_support' for p in pts(o)]
        return {'base_z':min(doors) if doors else (min(zs) if zs else None),'wall_top_z':sum(roofs)/len(roofs) if roofs else None,'geometry_z_bounds':[min(zs),max(zs)] if zs else None,'report':'original decoded GLB; estimates'}
    features=[];required=set();entry_checks=[]
    for bid,slug,name in targets:
        p=orient(polygons[bid],sign=1);ring=list(p.exterior.coords)[:-1]
        if p.geom_type!='Polygon' or len(p.interiors):raise ValueError('Requires explicit multi-part/hole contract: '+bid)
        oo=ctxby.get(bid,[])
        if not oo:raise ValueError('Target missing from decoded context: '+bid)
        edges=[LineString([a,b]) for a,b in zip(ring,ring[1:]+ring[:1])]
        h=original_heights(bid);tags=elements[bid].get('tags',{})
        door=next((o for o in oo if 'Detailed | painted entrance' in o['materials']),None)
        support=next((o for o in oo if o.get('extras',{}).get('semantic_type')=='entry_support'),None)
        if door:
            dp=pts(door);base=min(q[2] for q in dp);leaf=[sum(q[k] for q in dp)/len(dp) for k in [0,1]]
            ei=min(range(len(edges)),key=lambda i:edges[i].distance(Point(leaf)));a,b=ring[ei],ring[(ei+1)%len(ring)];L=math.dist(a,b);u=((b[0]-a[0])/L,(b[1]-a[1])/L);n=(u[1],-u[0]);signed=sum((leaf[k]-a[k])*n[k] for k in [0,1]);facade=[leaf[k]-signed*n[k] for k in [0,1]];projs=[sum(q[k]*u[k] for k in [0,1]) for q in dp];width=max(projs)-min(projs);supportz=sum(q[2] for q in pts(support))/len(pts(support)) if support else None
            entry={'edge_index':ei,'center_xy':facade,'center_semantics':'wall-plane projected aperture/threshold centre','original_leaf_center_xy':leaf,'original_leaf_recess_m':-signed,'outward_normal_xy':n,'threshold_z':base,'existing_support_z':supportz,'clear_width_m':width,'basis':'Original recessed leaf projected onto mapped wall plane; preserve tangent location and threshold z'}
        else:
            base=h['base_z'];entry=None;ei=None
        height=h['wall_top_z']-base
        audit_neighbours=[];overlaps=[]
        for oid,q in polygons.items():
            if oid==bid:continue
            dist=p.distance(q)
            if dist>.0001 and dist>35:continue
            inter=p.intersection(q)
            if inter.area>.01:overlaps.append({'id':oid,'area_m2':inter.area,'target_fraction':inter.area/p.area})
            statuses=assets.get(oid,{}).get('statuses',[]);detailed=oid in latest or any('source-informed' in s or 'inherited Phase4' in s for s in statuses)
            shared=p.boundary.intersection(q.boundary)
            if dist>.01 and not detailed:continue
            names=[v for v in assets.get(oid,{}).get('names',[]) if v!='Entry approaches'];nh=latest.get(oid,original_heights(oid));lo=nh.get('base_z');hi=nh.get('wall_top_z');interval=[max(base,lo),min(base+height,hi)] if shared.length>.01 and lo is not None and hi is not None else None
            audit_neighbours.append({'id':oid,'name':elements[oid].get('tags',{}).get('name') or (names[0] if names else oid),'distance_m':dist,'overlap_area_m2':inter.area,'shared_boundary_length_m':shared.length,'shared_boundary_geometry':mapping(shared) if shared.length>.01 else None,'target_shared_edge_indices':[i for i,edge in enumerate(edges) if edge.intersection(shared).length>.01],'shared_wall_potential_height_interval_m':interval,'neighbour_height_basis':nh,'neighbour_latest_delivered':oid in latest,'interface_rule':'Keep complete walls; common-height shared intervals default opaque unless actual openings verified. Above-neighbour portions remain available. Do not equate roof/chimney maximum with shared wall top.'})
        audit_neighbours.sort(key=lambda x:(x['distance_m'],-x['shared_boundary_length_m']))
        parents=[{'id':eid,'role':m.get('role')} for eid,e in elements.items() if e['type']=='relation' for m in e.get('members',[]) if m.get('type')=='way' and m.get('ref')==int(bid[4:])]
        aliases=[{'asset_id':aid,'node_index':node['node_index']} for aid,asset in assets.items() for node in asset['nodes'] if bid in node.get('extras',{}).get('source_part_ids',[])]
        feature={'id':bid,'slug':slug,'name':name,'ring':ring,'center_xy':[p.centroid.x,p.centroid.y],'area_m2':p.area,'tags':tags,'base_z':base,'levels':int(tags['building:levels'].split(';')[0]) if 'building:levels' in tags else max(1,round((height-.55)/3.15)),'levels_basis':'OSM levels' if 'building:levels' in tags else 'Inferred from retained procedural eaves using baseline 3.15m pitch + 0.55m allowance; not observed or OSM source-reported','height_m':height,'height_basis':'Retained original GLB flat roof plane minus original leaf threshold; estimated eaves, not survey','entry':entry,'entry_status':'original leaf decoded' if door else 'No door or entry-support mesh in original asset; entrance unknown, do not invent a mapped entrance','small_solid_outbuilding':door is None and int(tags.get('building:levels','1'))==1,'coordinate_contract':'EPSG:32630 minus [695238.304719173,5709236.965026026]; Blender east/north/up','user_authorized_artistic_completion':True,'material_keys':{'masonry':next(o['materials'][0] for o in oo if any('urban masonry' in m for m in o['materials'])),'trim':'Detailed | limestone trim','glass':'Detailed | recessed blue grey glazing','door':'Detailed | painted entrance','roof':'Detailed | slate grey roof','metal':'Detailed | Stevens black coated window metal'},'audit':{'polygon_valid':True,'ring_ccw':True,'holes_count':0,'positive_area_overlaps':overlaps,'source_parent_relations':parents,'asset_parent_part_aliases':aliases,'relation_geometries_checked':relation_count,'adjacent_or_detailed_neighbours_within_35m':audit_neighbours,'source_asset_nodes':assets[bid]['nodes'],'source_assets_preserved':True}}
        if tags.get('building')=='roof':
            feature.update({'semantic_type':'roof_only_mapped_feature','levels':None,'levels_basis':'building=roof; layer is not a floor count','base_z':None,'height_m':None,'height_basis':'No real-world roof support/underside elevation supplied by OSM; old generic extrusion is not evidence','entry':None,'entry_status':'Roof feature has no source door; no entry inferred','small_solid_outbuilding':False,'platform_elevation_m':None,'roof_surface_z_m':None,'source_baseline_geometry':{'base_z':base,'generic_extrusion_height_m':height,'flat_roof_plane_z':h['wall_top_z'],'geometry_z_bounds':h['geometry_z_bounds'],'basis':'Retained original GLB typology estimate only, not measured canopy height'},'authoring_constraint':'Treat as roof/canopy feature; do not create enclosing walls or infer storeys from layer=1. Resolve roof support/intersection using neighbouring geometry/evidence; unknown elevations remain estimated.'})
            for neighbour in audit_neighbours:
                neighbour['shared_wall_potential_height_interval_m']=None
                neighbour['interface_rule']='Roof adjacency/overlap only. No target wall-height interval is established; resolve roof support and neighbouring building intersections explicitly.'
        (R/'features'/f'{slug}.json').write_text(json.dumps(feature,ensure_ascii=False,indent=2)+'\n');features.append(feature);required.add(bid);required.update(n['id'] for n in audit_neighbours)
        entry_checks.append({'id':bid,'wall_center_edge_distance_m':edges[ei].distance(Point(facade)),'original_leaf_edge_distance_m':-signed,'threshold_above_support_m':base-supportz if supportz is not None else None} if door else {'id':bid,'entry_status':'absent from original asset; unknown, not automatically created'})
        print(slug,'READY',len(ring),'vertices','eaves',height,'entry',ei)
    counts={bid:len(ctxby.get(bid,[])) for bid in sorted(required)};missing=[bid for bid,count in counts.items() if not count]
    manifest={'batch':args.batch,'scope':'Complete explicitly selected next frontier footprints; latest delivered neighbour heights override original context','features':features};(R/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    coverage={'copied_from':str(args.context),'source_sha256':hashlib.sha256(args.context.read_bytes()).hexdigest(),'required_building_object_counts':counts,'missing_ids':missing,'latest_delivered_reports_used':delivered_reports,'important':'Original context mesh positions remain source GLB. Current delivered overlays must replace corresponding objects before current-geometry QA; feature neighbour heights already use delivered reports.'}
    coverage['upstream_context_provenance']=ctx.get('reuse_basis',{});ctx['reuse_basis']=coverage;(R/'reports/context.json').write_text(json.dumps(ctx,separators=(',',':'))+'\n');(R/'reports/preparation_audit.json').write_text(json.dumps({'entry_checks':entry_checks,'context_coverage':coverage,'feature_count':len(features),'geometry_modified':False},indent=2)+'\n')
    if missing:raise RuntimeError('Context missing required neighbours; acquire bounded decode: '+','.join(missing))

if __name__=='__main__':main()
