"""Retain the two unaffected batch12 assets without changing mesh buffers."""
import hashlib
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'output/batch12_v1/replacement.glb'
target = ROOT / 'output/princes_gate_27_v2/retained_batch12.glb'
raw = source.read_bytes()
magic, version, length = struct.unpack_from('<III', raw)
assert magic == 0x46546C67 and version == 2 and length == len(raw)
json_length, kind = struct.unpack_from('<II', raw, 12)
assert kind == 0x4E4F534A
doc = json.loads(raw[20:20 + json_length])
tail = raw[20 + json_length:]
keep_ids = {'way-640808103', 'way-810633525'}
nodes = doc['nodes']
assert all(not n.get('children') and 'skin' not in n for n in nodes)
assert not doc.get('animations') and not doc.get('skins')
keep = [i for i, n in enumerate(nodes) if n.get('extras', {}).get('building_id') in keep_ids]
assert {nodes[i]['extras']['building_id'] for i in keep} == keep_ids
remap = {old: new for new, old in enumerate(keep)}
for scene in doc['scenes']:
    scene['nodes'] = [remap[i] for i in scene.get('nodes', []) if i in remap]
doc['nodes'] = [nodes[i] for i in keep]
encoded = json.dumps(doc, separators=(',', ':')).encode()
encoded += b' ' * (-len(encoded) % 4)
result = struct.pack('<III', magic, version, 20 + len(encoded) + len(tail))
result += struct.pack('<II', len(encoded), kind) + encoded + tail
if target.exists():
    assert target.read_bytes() == result, 'Refuse changing an existing retained asset'
else:
    target.write_bytes(result)
sha = lambda b: hashlib.sha256(b).hexdigest()
audit = {'source': str(source.relative_to(ROOT)), 'source_sha256': sha(raw),
         'output': str(target.relative_to(ROOT)), 'output_sha256': sha(result),
         'retained_ids': sorted(keep_ids), 'retained_nodes': len(keep),
         'source_nodes': len(nodes), 'binary_chunks_sha256': sha(tail),
         'geometry_preserved': 'All mesh/accessor/material records and binary chunks unchanged; only flat scene nodes filtered and root indices remapped.'}
(ROOT / 'revision27/reports/retained_batch12.json').write_text(json.dumps(audit, indent=2))
print(json.dumps(audit))
