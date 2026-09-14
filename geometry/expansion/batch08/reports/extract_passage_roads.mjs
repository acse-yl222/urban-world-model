// Bounded identity extraction: source bytes untouched; scalar-PBR diagnostic only.
import fs from 'node:fs';
import path from 'node:path';
import {GLTFLoader} from 'file:///Users/yl222/Desktop/UrbanWorldModelVisualizer/agents/demo_rev02/vendor/three/examples/jsm/loaders/GLTFLoader.js';
import {MeshoptDecoder} from 'file:///Users/yl222/Desktop/UrbanWorldModelVisualizer/agents/demo_rev02/vendor/three/examples/jsm/libs/meshopt_decoder.module.js';
import * as THREE from 'file:///Users/yl222/Desktop/UrbanWorldModelVisualizer/agents/demo_rev02/vendor/three/build/three.module.js';
const loader=new GLTFLoader();loader.setMeshoptDecoder(MeshoptDecoder);
let objects=[];const materials={},replacements=[];
function omitTextures(o){for(const k of Object.keys(o)){if(/Texture$/.test(k))delete o[k];else if(o[k]&&typeof o[k]==='object')omitTextures(o[k]);}}

 const raw=fs.readFileSync('south_kensington_core008_web.glb'),n=raw.readUInt32LE(12),data=JSON.parse(raw.subarray(20,20+n));
 for(const m of data.materials??[])omitTextures(m);data.images=[];data.textures=[];
 const j=Buffer.from(JSON.stringify(data)),pad=(4-j.length%4)%4,bin=raw.subarray(20+n),out=Buffer.alloc(20+j.length+pad+bin.length);
 out.writeUInt32LE(0x46546c67,0);out.writeUInt32LE(2,4);out.writeUInt32LE(out.length,8);out.writeUInt32LE(j.length+pad,12);out.writeUInt32LE(0x4e4f534a,16);j.copy(out,20);out.fill(32,20+j.length,20+j.length+pad);bin.copy(out,20+j.length+pad);
 const gltf=await loader.parseAsync(out.buffer.slice(out.byteOffset,out.byteOffset+out.byteLength),'');gltf.scene.updateMatrixWorld(true);

const ids=new Set([4907924,699773493,699773494]);gltf.scene.traverse(o=>{if(!o.isMesh||!ids.has(Number(o.userData.osm_id)))return;const ps=o.geometry.attributes.position,positions=[],v=new THREE.Vector3();for(let i=0;i<ps.count;i++){v.fromBufferAttribute(ps,i).applyMatrix4(o.matrixWorld);positions.push(v.x,-v.z,v.y);}const mm=Array.isArray(o.material)?o.material:[o.material];for(const m of mm)materials[m.name]={name:m.name,color:m.color.toArray(),roughness:m.roughness,metalness:m.metalness,opacity:m.opacity,transparent:m.transparent};objects.push({name:o.name,id:'road-'+o.userData.osm_id,positions,indices:o.geometry.index?Array.from(o.geometry.index.array):Array.from({length:ps.count},(_,i)=>i),materials:mm.map(m=>m.name),groups:o.geometry.groups,extras:o.userData,context_source:'south_kensington_core008_web.glb'});});if(objects.length!==3)throw Error('Expected exactly 3 road meshes, got '+objects.length);fs.writeFileSync('geometry/expansion/batch08/reports/passage_road_context.json',JSON.stringify({source:'south_kensington_core008_web.glb',axes:'Blender east north up',limitation:'Original traffic road display geometry at z=.25; not survey; full decoded triangles, no textures',materials,objects}));console.log(objects.map(o=>({name:o.name,vertices:o.positions.length/3,triangles:o.indices.length/3})));
