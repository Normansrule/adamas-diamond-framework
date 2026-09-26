export * from 'three';
import * as T from 'three';
const noop = () => {};
export class WebGLRenderer {
  constructor() { return new Proxy(this, { get: (t, k) => {
    if (k === 'getSize' || k === 'getDrawingBufferSize') return v => v.set(800, 420);
    if (k === 'getPixelRatio') return () => 1;
    if (k === 'setAnimationLoop') return cb => { let n = 0; const tick = () => { if (n++ < 600) { cb(); setTimeout(tick, 2); } }; if (cb) setTimeout(tick, 2); };
    if (k === 'capabilities') return { isWebGL2: true };
    if (k === 'domElement') return globalThis.document.createElement('canvas');
    if (k in t) return t[k];
    return noop; } }); }
}
