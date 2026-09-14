import {pathToFileURL} from 'node:url';
import {resolve as pathResolve} from 'node:path';
export async function resolve(specifier, context, nextResolve) {
 if(specifier==='three') return {url:pathToFileURL(pathResolve('vendor/three/build/three.module.js')).href,shortCircuit:true};
 if(specifier.startsWith('three/addons/')) return {url:pathToFileURL(pathResolve('vendor/three/examples/jsm',specifier.slice(13))).href,shortCircuit:true};
 return nextResolve(specifier,context);
}
