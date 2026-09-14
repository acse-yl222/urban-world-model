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
const selected=JSON.parse(fs.readFileSync('geometry/expansion/batch02/manifest.json')).features;
const objects=[], materials={}, pt=new THREE.Vector3(), box=new THREE.Box3();
gltf.scene.traverse(o=>{
 if(!o.isMesh)return;
 let id=null;for(let a=o;a;a=a.parent)if(a.userData.building_id){id=a.userData.building_id;break;}
 box.setFromObject(o);const c=box.getCenter(new THREE.Vector3());
 if(!id||!selected.some(f=>Math.hypot(c.x-f.center_xy[0],-c.z-f.center_xy[1])<100))return;
 const pos=o.geometry.attributes.position, coords=[];
 for(let i=0;i<pos.count;i++){pt.fromBufferAttribute(pos,i).applyMatrix4(o.matrixWorld);coords.push(pt.x,-pt.z,pt.y);}
 const mats=Array.isArray(o.material)?o.material:[o.material];
 for(const m of mats)materials[m.name]={name:m.name,color:m.color.toArray(),roughness:m.roughness,metalness:m.metalness,opacity:m.opacity,transparent:m.transparent};
 objects.push({name:o.name,id,positions:coords,indices:o.geometry.index?Array.from(o.geometry.index.array):Array.from({length:pos.count},(_,i)=>i),materials:mats.map(m=>m.name),groups:o.geometry.groups,extras:o.userData});
});
fs.mkdirSync('geometry/expansion/batch02/reports',{recursive:true});
fs.writeFileSync('geometry/expansion/batch02/reports/context.json',JSON.stringify({source:'south_kensington_core008_web.glb',axes:'Blender east north up',limitation:'Context render copy omits texture maps; source unchanged',materials,objects}));
console.log(JSON.stringify({objects:objects.length,buildings:new Set(objects.map(o=>o.id)).size,materials:Object.keys(materials)}));
