"""Index existing GLB asset identities without modifying geometry."""
import json, struct, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
source = ROOT / "south_kensington_core008_web.glb"
with source.open("rb") as f:
    magic, version, size = struct.unpack("<III", f.read(12))
    assert magic == 0x46546C67 and version == 2
    length, kind = struct.unpack("<II", f.read(8))
    assert kind == 0x4E4F534A
    data = json.loads(f.read(length))
groups = {}
unassigned = []
for index, node in enumerate(data["nodes"]):
    extra = node.get("extras", {})
    raw = extra.get("building_id") or extra.get("osm_id")
    identity = str(raw) if raw is not None else None
    # Only explicit typed identities are grouped. Unqualified IDs need review.
    if not identity or not re.fullmatch(r"(?:way|relation|node)-[0-9]+", identity):
        if "mesh" in node:
            unassigned.append({"node_index": index, "name": node.get("name"), "raw_identity": raw})
        continue
    group = groups.setdefault(identity, {"id": identity, "names": [], "statuses": [], "nodes": []})
    label = extra.get("building") or node.get("name", "").split(" | ")[0]
    if label not in group["names"]: group["names"].append(label)
    status = extra.get("expansion_status") or extra.get("geometry_fidelity")
    if status and status not in group["statuses"]: group["statuses"].append(status)
    materials = sorted({p["material"] for p in data.get("meshes", [])[node["mesh"]]["primitives"] if "material" in p}) if "mesh" in node else []
    group["nodes"].append({"node_index": index, "name": node.get("name"), "mesh_index": node.get("mesh"), "materials": [{"index": m, "name": data["materials"][m].get("name")} for m in materials], "extras": extra})
result = {"source": source.name, "source_size_bytes": source.stat().st_size, "method": "Explicit typed building_id or osm_id from GLB extras; labels and detail status are inherited metadata, not independent verification. Node/mesh indices are specific to this file version.", "building_count": len(groups), "mapped_node_count": sum(len(g["nodes"]) for g in groups.values()), "buildings": sorted(groups.values(), key=lambda g: g["id"]), "unassigned_mesh_nodes": unassigned}
out = ROOT / "geometry_expansion" / "asset_index.json"
out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
print(json.dumps({k:result[k] for k in ("building_count", "mapped_node_count")}))
print("unassigned_mesh_nodes", len(unassigned))
for identity in ("way-110085215", "way-205276847", "way-438951124", "way-117417431"):
    g = groups[identity]
    print(identity, len(g["nodes"]), g["statuses"])
