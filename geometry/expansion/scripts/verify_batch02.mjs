// Decode an isolated review copy. Original GLB bytes are never modified.
import fs from 'node:fs';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'three/addons/libs/meshopt_decoder.module.js';
import * as THREE from 'three';
const raw=fs.readFileSync('south_kensington_core008_web.glb');
const n=raw.readUInt32LE(12), data=JSON.parse(raw.subarray(20,20+n));
// Context preview uses the original scalar PBR values; texture maps are omitted
// only in this diagnostic copy so it can be decoded without a browser image API.
function omitTextures(o){for(const k of Object.keys(o)){if(/Texture$/.test(k))delete o[k];else if(o[k]&&typeof o[k]==='object')omitTextures(o[k]);}}
for(const m of data.materials??[])omitTextures(m);
data.images=[];data.textures=[];
const j=Buffer.from(JSON.stringify(data)), pad=(4-j.length%4)%4;
const bin=raw.subarray(20+n);
const out=Buffer.alloc(20+j.length+pad+bin.length);
out.writeUInt32LE(0x46546c67,0);out.writeUInt32LE(2,4);out.writeUInt32LE(out.length,8);
out.writeUInt32LE(j.length+pad,12);out.writeUInt32LE(0x4e4f534a,16);
j.copy(out,20);out.fill(32,20+j.length,20+j.length+pad);bin.copy(out,20+j.length+pad);
const loader=new GLTFLoader();loader.setMeshoptDecoder(MeshoptDecoder);
const gltf=await loader.parseAsync(out.buffer.slice(out.byteOffset,out.byteOffset+out.byteLength),'');
gltf.scene.updateMatrixWorld(true);

const {EXPANSION_BATCHES,installExpansion}=await import('../../viewer/3d/expansion.js');
const assert=(v,msg)=>{if(!v)throw new Error(msg);};
const results=[];
for(const batch of EXPANSION_BATCHES){
 const bytes=fs.readFileSync(new URL(batch.url,new URL('../../viewer/3d/',import.meta.url)));
 const replacement=await loader.parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
 let before=0;replacement.scene.traverse(o=>{if(o.isMesh)before+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;});
 const support=[];gltf.scene.traverse(o=>{if(batch.ids.includes(o.userData.building_id)&&o.userData.semantic_type==='entry_support')support.push(o);});
 const installed=await installExpansion(gltf.scene,replacement.scene,batch.ids,batch.projectionM);
 assert(installed.originals.length===batch.ids.length,'Missing original IDs');
 assert(installed.originals.every(o=>!o.visible),'Source exterior not hidden before batching');
 let after=0;installed.object.traverseVisible(o=>{if(o.isMesh)after+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;});
 assert(before===after,'Triangle loss in batching');
 installed.setEnabled(false);assert(!installed.object.visible&&installed.originals.every(o=>o.visible),'Original comparison failed');
 installed.setEnabled(true);assert(installed.object.visible&&installed.originals.every(o=>!o.visible),'Refined comparison failed');
 assert(support.length===batch.ids.length&&support.every(o=>o.visible),'Original entry supports lost');
 results.push({ids:batch.ids,triangles:before,originals_hidden_before_batch:true,entry_supports_retained:support.length,comparison_passed:true});
}
fs.writeFileSync('geometry/expansion/batch02/reports/viewer_check.json',JSON.stringify({passed:true,total_buildings:results.reduce((a,b)=>a+b.ids.length,0),batches:results,scope:'Actual source GLB decode and Three.js loader/batching; no live browser screenshot'},null,2));
console.log(results);
