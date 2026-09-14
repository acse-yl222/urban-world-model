#!/usr/bin/env python3
"""Rank the explicit remaining frontier without building or marking completion.

Authoritative completed IDs come only from remaining_frontier.json. Optional
--staging-id values exclude in-flight work and act as provisional anchors; they
are never promoted to completed IDs. Reads local GIS, updates only queue output.
"""
import argparse
import datetime
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
sys.path.insert(0, str(PROJECT / 'geometry/completion/.deps'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--frontier', type=Path, default=ROOT / 'remaining_frontier.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'continuation_queue.json')
    parser.add_argument('--staging-id', action='append', default=[], help='In-flight footprint excluded from pending; provisional anchor only')
    args = parser.parse_args()
    from pyproj import Transformer
    from shapely.geometry import Polygon, LineString
    from shapely.ops import polygonize, unary_union
    frontier = json.loads(args.frontier.read_text())
    previous = json.loads(args.output.read_text()) if args.output.exists() else {}
    previous_by_id = {x['id']: x for x in previous.get('queue', [])}
    completed = sorted(set(frontier.get('completed_ids', [])))
    pending_ids = {x['id'] for x in frontier.get('pending', [])}
    pending_records = {x['id']: x for x in frontier.get('pending', [])}
    staging = sorted(set(args.staging_id) - set(completed))
    unknown = set(staging) - pending_ids
    if unknown:
        parser.error('Staging IDs must be in authoritative pending frontier: ' + ', '.join(sorted(unknown)))
    source_path = PROJECT / 'geometry/completion/sources/osm_buildings.json'
    source = json.loads(source_path.read_text())
    transform = Transformer.from_crs(4326, 32630, always_xy=True)
    origin = [695238.304719173, 5709236.965026026]
    wanted = pending_ids | set(completed) | set(staging)
    geometry = {}
    elements = {}
    def ring(g):
        return [(x-origin[0], y-origin[1]) for x,y in [transform.transform(p['lon'],p['lat']) for p in g]]
    for item in source['elements']:
        bid = item['type'] + '-' + str(item['id'])
        if bid not in wanted:
            continue
        elements[bid] = item
        shape = None
        if item.get('geometry') and len(item['geometry']) >= 4:
            shape = Polygon(ring(item['geometry']))
        elif item['type'] == 'relation':
            outer, inner = [], []
            for member in item.get('members', []):
                if len(member.get('geometry', [])) >= 2:
                    (inner if member.get('role') == 'inner' else outer).append(LineString(ring(member['geometry'])))
            if outer:
                shape = unary_union(list(polygonize(outer))).difference(unary_union(list(polygonize(inner))))
        if shape is not None and not shape.is_empty and shape.is_valid:
            geometry[bid] = shape
    anchors = [(bid, geometry[bid]) for bid in completed + staging if bid in geometry]
    allowed_states = ['pending', 'evidence', 'module', 'validated', 'integrated']
    queue = []
    for candidate in frontier.get('pending', []):
        bid = candidate['id']
        if bid in completed or bid in staging:
            continue
        p = geometry.get(bid)
        tags = elements.get(bid, {}).get('tags', {})
        name = tags.get('name') or next((n for n in candidate.get('names', []) if n != 'Entry approaches'), bid)
        roof_or_service = tags.get('building') in ['roof','service','shed','garage','garages'] or name.startswith(('roof ', 'service '))
        distances = sorted((p.boundary.distance(q.boundary), aid) for aid,q in anchors) if p is not None else []
        prev = previous_by_id.get(bid, {})
        state = prev.get('state', 'pending')
        if state not in allowed_states:
            state = 'pending'
        # A planner never validates or integrates; retained coordinator state is
        # informational until authoritative completed_ids removes the candidate.
        queue.append({
            'id': bid, 'name': name, 'state': state,
            'state_basis': prev.get('state_basis', 'pending; no stage completion asserted by planner'),
            'report_refs': prev.get('report_refs', []),
            'tags': tags, 'footprint_area_m2': p.area if p is not None else None,
            'polygon_valid': p is not None,
            'distance_to_anchor_boundary_m': distances[0][0] if distances else None,
            'nearest_anchor_id': distances[0][1] if distances else None,
            'nearest_anchor_status': ('staging_unconfirmed' if distances and distances[0][1] in staging else 'authoritative_completed') if distances else None,
            'roof_or_service_review_required': roof_or_service,
            'planning_eligible': p is not None and not roof_or_service and not pending_records[bid].get('status', '').startswith('deferred'),
            'coordinator_status': pending_records[bid].get('status', 'pending'),
            'deferral_reason': pending_records[bid].get('reason') if pending_records[bid].get('status', '').startswith('deferred') else None,
            'delivery_ready': False,
            'next_action': 'Resolve feature identity and roof/service scope before authoring' if roof_or_service else 'Inspect building-specific permitted references and interfaces; label unknowns as estimates',
            'gates': ['evidence inspected and attributed', 'module authored', 'numerical and visual validation reports', 'coordinator integration confirmation'],
        })
    queue.sort(key=lambda q: (q['distance_to_anchor_boundary_m'] is None, q['distance_to_anchor_boundary_m'] or 0, q['id']))
    for rank, candidate in enumerate(queue, 1):
        candidate['rank'] = rank
    next_candidate = next((q['id'] for q in queue if q['planning_eligible']), None)
    output = {
        'schema_version': 1,
        'updated_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'basis': 'Local OSM footprint-boundary distance to completed and explicitly staged anchors; bounded explicit pending-refinement inventory, not whole-city completeness',
        'authoritative_frontier': str(args.frontier.relative_to(PROJECT)) if args.frontier.is_relative_to(PROJECT) else str(args.frontier),
        'authoritative_completed_ids': completed,
        'staging_ids': staging,
        'staging_is_not_completion': True,
        'anchor_count': len(anchors),
        'missing_anchor_geometry': sorted((set(completed)|set(staging))-set(geometry)),
        'pending_count': len(queue),
        'next_candidate': next_candidate,
        'next_candidate_is_planning_only': True,
        'state_order': allowed_states,
        'transition_policy': 'Planner never advances states or marks completion. Coordinator must cite actual evidence/module/validation/integration reports. Missing imagery or roof/service ambiguity cannot be delivered automatically.',
        'source_osm_sha256': hashlib.sha256(source_path.read_bytes()).hexdigest(),
        'coordinate_contract': {'crs':'EPSG:32630','projected_origin_m':origin,'axes':'X east Y north, metres'},
        'queue': queue,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'completed':len(completed),'staging':len(staging),'anchors':len(anchors),'pending':len(queue),'next_candidate':next_candidate,'states_advanced':False}))


if __name__ == '__main__':
    main()
