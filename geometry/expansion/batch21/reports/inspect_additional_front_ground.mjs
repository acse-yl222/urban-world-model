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

const manifest=JSON.parse(fs.readFileSync('geometry/expansion/batch21/manifest.json'));
manifest.features=manifest.features.filter(f=>f.estimated_front_entry).map(f=>({...f,entry:f.estimated_front_entry}));
const targets=manifest.features.map(f=>({id:f.id,entry:f.entry,samples:[0,.5,1].map(d=>[f.entry.center_xy[0]+f.entry.outward_normal_xy[0]*d,f.entry.center_xy[1]+f.entry.outward_normal_xy[1]*d])}));
const results=[];
gltf.scene.traverse(o=>{if(!o.isMesh)return;const ex=o.userData;if(!(/ground|terrain|pavement|sidewalk|entry-support|road|path|paving|asphalt/i.test(o.name)||['ground','ground_detail','entry_support'].includes(ex.semantic_type)))return;
 const p=o.geometry.attributes.position,idx=o.geometry.index,vs=[],v=new THREE.Vector3(),min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];
 for(let i=0;i<p.count;i++){v.fromBufferAttribute(p,i).applyMatrix4(o.matrixWorld);const q=[v.x,-v.z,v.y];vs.push(q);for(let k=0;k<3;k++){min[k]=Math.min(min[k],q[k]);max[k]=Math.max(max[k],q[k]);}}
 const hits=[];for(const t of targets)for(let si=0;si<t.samples.length;si++){const [x,y]=t.samples[si];if(x<min[0]||x>max[0]||y<min[1]||y>max[1])continue;
 for(let i=0;i<(idx?idx.count:p.count);i+=3){const [a,b,c]=[0,1,2].map(k=>vs[idx?idx.getX(i+k):i+k]);const det=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1]);if(Math.abs(det)<1e-10)continue;const u=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/det,w=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/det;if(u>=-1e-7&&w>=-1e-7&&u+w<=1+1e-7)hits.push({id:t.id,sample_outward_m:[0,.5,1][si],z:u*a[2]+w*b[2]+(1-u-w)*c[2]});}}
 const distances=targets.map(t=>({id:t.id,bbox_distance_xy_m:Math.hypot(Math.max(min[0]-t.entry.center_xy[0],0,t.entry.center_xy[0]-max[0]),Math.max(min[1]-t.entry.center_xy[1],0,t.entry.center_xy[1]-max[1]))}));
 if(hits.length||distances.some(d=>d.bbox_distance_xy_m<10))results.push({name:o.name,extras:ex,bounds:[...min,...max],hits,distances});});
fs.writeFileSync('geometry/expansion/batch21/reports/additional_front_ground.json',JSON.stringify({source:'south_kensington_core008_web.glb',method:'Decoded original mesh; vertical XY barycentric hits at threshold and .5/1m outward. Bounds distances only for nearby no-hit objects, not exact mesh distances.',targets,objects:results},null,2));console.log(JSON.stringify(results.filter(o=>o.hits.length).map(o=>({name:o.name,hits:o.hits})),null,2));
