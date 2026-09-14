// Bounded identity extraction: source bytes untouched; scalar-PBR diagnostic only.
import fs from 'node:fs';
import path from 'node:path';
import {GLTFLoader} from 'file:///Users/yl222/Desktop/UrbanWorldModelVisualizer/agents/demo_rev02/vendor/three/examples/jsm/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'file:///Users/yl222/Desktop/UrbanWorldModelVisualizer/agents/demo_rev02/vendor/three/examples/jsm/libs/meshopt_decoder.module.js';
import * as THREE from 'file:///Users/yl222/Desktop/UrbanWorldModelVisualizer/agents/demo_rev02/vendor/three/build/three.module.js';
const batch=process.argv[2];if(!/^\d+$/.test(batch??''))throw Error('Usage: ...extract_prepared_context.mjs 04');
const root=`geometry/expansion/batch${batch}`;
const audit=JSON.parse(fs.readFileSync(`${root}/reports/preparation_audit.json`));
const wanted=new Set(Object.keys(audit.context_coverage.required_building_object_counts));
const inputs=['south_kensington_core008_web.glb'];
for(const reportPath of audit.context_coverage.latest_delivered_reports_used){const glb=path.join(path.dirname(reportPath),'replacement.glb');if(fs.existsSync(glb))inputs.push(glb);}
const loader=new GLTFLoader();loader.setMeshoptDecoder(MeshoptDecoder);
let objects=[];const materials={},replacements=[];
function omitTextures(o){for(const k of Object.keys(o)){if(/Texture$/.test(k))delete o[k];else if(o[k]&&typeof o[k]==='object')omitTextures(o[k]);}}
for(const [sourceIndex,file] of inputs.entries()){
 const raw=fs.readFileSync(file),n=raw.readUInt32LE(12),data=JSON.parse(raw.subarray(20,20+n));
 for(const m of data.materials??[])omitTextures(m);data.images=[];data.textures=[];
 const j=Buffer.from(JSON.stringify(data)),pad=(4-j.length%4)%4,bin=raw.subarray(20+n),out=Buffer.alloc(20+j.length+pad+bin.length);
 out.writeUInt32LE(0x46546c67,0);out.writeUInt32LE(2,4);out.writeUInt32LE(out.length,8);out.writeUInt32LE(j.length+pad,12);out.writeUInt32LE(0x4e4f534a,16);j.copy(out,20);out.fill(32,20+j.length,20+j.length+pad);bin.copy(out,20+j.length+pad);
 const gltf=await loader.parseAsync(out.buffer.slice(out.byteOffset,out.byteOffset+out.byteLength),'');gltf.scene.updateMatrixWorld(true);
 const extracted=[],pt=new THREE.Vector3();
 gltf.scene.traverse(o=>{
  if(!o.isMesh)return;let id=null,extras=o.userData;
  for(let a=o;a;a=a.parent)if(a.userData.building_id){id=a.userData.building_id;extras={...a.userData,...o.userData};break;}
  if(!wanted.has(id))return;
  const pos=o.geometry.attributes.position,coords=[];for(let i=0;i<pos.count;i++){pt.fromBufferAttribute(pos,i).applyMatrix4(o.matrixWorld);coords.push(pt.x,-pt.z,pt.y);}
  const mats=Array.isArray(o.material)?o.material:[o.material];
  for(const m of mats)materials[m.name]={name:m.name,color:m.color.toArray(),roughness:m.roughness,metalness:m.metalness,opacity:m.opacity,transparent:m.transparent};
  extracted.push({name:o.name,id,positions:coords,indices:o.geometry.index?Array.from(o.geometry.index.array):Array.from({length:pos.count},(_,i)=>i),materials:mats.map(m=>m.name),groups:o.geometry.groups,extras,context_source:file});
 });
 if(sourceIndex){const changed=new Set(extracted.map(o=>o.id));objects=objects.filter(o=>!changed.has(o.id)||o.extras.semantic_type==='entry_support');replacements.push({source:file,ids:[...changed]});}
 objects.push(...extracted);gltf.scene.traverse(o=>{if(o.isMesh){o.geometry.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material])m.dispose();}});
 console.log(JSON.stringify({source:file,extracted:extracted.length,ids:new Set(extracted.map(o=>o.id)).size}));
}
const counts=Object.fromEntries([...wanted].map(id=>[id,objects.filter(o=>o.id===id).length]));const missing=Object.entries(counts).filter(([,n])=>!n).map(([id])=>id);if(missing.length)throw Error('Missing required assets '+missing.join(','));
const basis={method:'Decoded original source plus latest delivered replacement overlays in chronological report order; preserved original entry support meshes',inputs,replacements,required_building_object_counts:counts,missing_ids:[]};
// Stream objects to avoid V8's ~512 MB single-string limit on detailed context.
const header={source:inputs,axes:'Blender east north up',limitation:'Scalar PBR diagnostic; no texture maps. Original files unchanged.',materials,reuse_basis:basis};
const fd=fs.openSync(`${root}/reports/context.json`,'w');
fs.writeSync(fd,JSON.stringify(header).slice(0,-1)+',"objects":[');
for(let i=0;i<objects.length;i++)fs.writeSync(fd,(i?',':'')+JSON.stringify(objects[i]));
fs.writeSync(fd,']}');fs.closeSync(fd);
audit.context_coverage=basis;fs.writeFileSync(`${root}/reports/preparation_audit.json`,JSON.stringify(audit,null,2));
console.log(JSON.stringify({complete:true,objects:objects.length,buildings:Object.keys(counts).length}));
