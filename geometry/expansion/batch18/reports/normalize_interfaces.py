"""Batch18 only: normalize exact mapped shared segments and annotate evidence limits."""
import json,sys,hashlib
from pathlib import Path
sys.path.insert(0,str(Path('geometry/completion/.deps').resolve()))
from shapely.geometry import shape,LineString
R=Path('geometry/expansion/batch18');a=json.load(open('geometry/expansion/asset_index.json'));assets={b['id']:b for b in a['buildings']};protected={bid for bid,b in assets.items() if any('source-informed' in s or 'inherited Phase4' in s for s in b.get('statuses',[]))};assert len(protected)==74
ground=json.load(open(R/'reports/source_ground_audit.json'));manifest=json.load(open(R/'manifest.json'));out=[]
for f in manifest['features']:
 audit=f['audit'];statuses=assets[f['id']].get('statuses',[]);audit['protected_core_exclusion']={'target_is_protected':f['id'] in protected,'protected_inventory_count':74,'target_asset_statuses':statuses,'parent_and_part_aliases_empty':not audit['source_parent_relations'] and not audit['asset_parent_part_aliases'],'no_positive_mapped_overlap':not audit['positive_area_overlaps']};assert not audit['protected_core_exclusion']['target_is_protected']
 normalized=[]
 for n in audit['adjacent_or_detailed_neighbours_within_35m']:
  n['neighbour_is_protected_core']=n['id'] in protected;n['neighbour_asset_statuses']=assets.get(n['id'],{}).get('statuses',[])
  if not n['shared_boundary_geometry']:continue
  g=shape(n['shared_boundary_geometry'])
  for ei,(p,q) in enumerate(zip(f['ring'],f['ring'][1:]+f['ring'][:1])):
   inter=LineString([p,q]).intersection(g)
   lines=[inter] if inter.geom_type=='LineString' else list(inter.geoms) if hasattr(inter,'geoms') else []
   for line in lines:
    if line.geom_type!='LineString' or line.length<=.01:continue
    unknown=n['shared_wall_potential_height_interval_m'] is None
    normalized.append({'edge':ei,'neighbour':n['id'],'polyline':list(line.coords),'height_interval':n['shared_wall_potential_height_interval_m'],'basis':'Exact mapped shared segment; neighbour absent from source geometry, height unknown' if unknown else 'Exact mapped shared segment; neighbour wall-height estimate from source scene, not measurement','aperture_policy':'Conservatively opaque over full target height pending coordinator decision; this is not an inferred neighbour height' if unknown else 'Suppress apertures within common-height interval; preserve complete wall'})
 audit['normalized_shared_wall_segments']=normalized
 profile=[]
 for d in [0,.5,1]:
  hits=[{'object_name':o['name'],**h} for o in ground['objects'] for h in o['hits'] if h['id']==f['id'] and h['sample_outward_m']==d];highest=max((h['z'] for h in hits),default=None);profile.append({'outward_m':d,'all_surface_hits':hits,'highest_source_surface_z':highest,'threshold_minus_highest_surface_m':None if highest is None else f['base_z']-highest})
 f['entry']['source_ground_profile']=profile;f['entry']['support_status']='No original entry support. Actual barycentric triangle hits find site ground -0.05 at threshold/.5/1m; coordinator owns finite approach/datum decision. No base changed by preparation.'
 f['authoring_constraint']='Preserve all mapped corners, original entry tangent and documented source datum until coordinator resolves ground. Consume every normalized shared segment. Unknown neighbour height is not permission to omit wall or invent a measured interval. Protected74/source aliases excluded.'
 (R/'features'/f"{f['slug']}.json").write_text(json.dumps(f,indent=2)+'\n');out.append({'id':f['id'],'vertices':len(f['ring']),'base_z':f['base_z'],'levels':f['levels'],'height_m':f['height_m'],'shared_segments':len(normalized),'unknown_shared_neighbours':[s['neighbour'] for s in normalized if s['height_interval'] is None],'protected':f['id'] in protected})
(R/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(R/'reports/normalized_interface_audit.json').write_text(json.dumps({'targets':out,'protected_inventory_count':74,'protected_inventory_basis':'asset_index statuses source-informed or inherited Phase4','original_source_sha256':hashlib.sha256(Path('geometry/expansion/asset_index.json').read_bytes()).hexdigest(),'geometry_modified':False,'only_batch18_written':True},indent=2)+'\n');print(json.dumps(out,indent=2))
