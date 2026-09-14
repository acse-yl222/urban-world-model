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
const objects=[], materials={}, pt=new THREE.Vector3(), box=new THREE.Box3();
gltf.scene.traverse(o=>{
 if(!o.isMesh)return;
 let id=null;for(let a=o;a;a=a.parent)if(a.userData.building_id){id=a.userData.building_id;break;}
 box.setFromObject(o);const c=box.getCenter(new THREE.Vector3());
 if(!id||Math.hypot(c.x-511.65,c.z+105.24)>100)return;
 const pos=o.geometry.attributes.position, coords=[];
 for(let i=0;i<pos.count;i++){pt.fromBufferAttribute(pos,i).applyMatrix4(o.matrixWorld);coords.push(pt.x,-pt.z,pt.y);}
 const mats=Array.isArray(o.material)?o.material:[o.material];
 for(const m of mats)materials[m.name]={name:m.name,color:m.color.toArray(),roughness:m.roughness,metalness:m.metalness,opacity:m.opacity,transparent:m.transparent};
 objects.push({name:o.name,id,positions:coords,indices:o.geometry.index?Array.from(o.geometry.index.array):Array.from({length:pos.count},(_,i)=>i),materials:mats.map(m=>m.name),groups:o.geometry.groups,extras:o.userData});
});
fs.mkdirSync('geometry/expansion/reports',{recursive:true});
fs.writeFileSync('geometry/expansion/reports/context.json',JSON.stringify({source:'south_kensington_core008_web.glb',axes:'Blender east north up',limitation:'Context render copy omits texture maps; source unchanged',materials,objects}));
console.log(JSON.stringify({objects:objects.length,buildings:new Set(objects.map(o=>o.id)).size,materials:Object.keys(materials)}));
if(process.argv.includes('--verify-expansion')){
 const {installExpansion,EXPANSION_ID}=await import('../../viewer/3d/expansion.js');
 const bytes=fs.readFileSync('geometry/expansion/output/kensington_gore_23_v1/replacement.glb');
 const replacement=await loader.parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
 let before=0;replacement.scene.traverse(o=>{if(o.isMesh)before+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;});
 const support=[];gltf.scene.traverse(o=>{if(o.userData.building_id===EXPANSION_ID&&o.userData.semantic_type==='entry_support')support.push(o);});
 const installed=await installExpansion(gltf.scene,replacement.scene);
 const assert=(condition,message)=>{if(!condition)throw new Error(message);};
 assert(support.length===1&&support[0].visible,'Existing entry support missing');
 assert(installed.originals.length===1&&!installed.originals[0].visible,'Original not excluded before main batching');
 let after=0;installed.object.traverseVisible(o=>{if(o.isMesh)after+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;});
 assert(before===after,'Replacement triangle loss during batching');
 installed.setEnabled(false);assert(!installed.object.visible&&installed.originals[0].visible,'Original comparison failed');
 installed.setEnabled(true);assert(installed.object.visible&&!installed.originals[0].visible,'Refinement comparison failed');
 assert(support[0].visible,'Comparison hid existing entry support');
 const report={passed:true,building_id:EXPANSION_ID,source_exterior_roots:1,entry_support_preserved:true,triangles:before,batching_preserved_triangles:true,comparison_toggle_passed:true,scope:'Actual source GLB decoded by Three.js; scalar-material diagnostic copy. No live browser render.'};
 fs.writeFileSync('geometry/expansion/reports/viewer_check.json',JSON.stringify(report,null,2));console.log(report);
}
