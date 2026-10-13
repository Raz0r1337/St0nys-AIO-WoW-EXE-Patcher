# gen_frames2.py - frames.bin for tips_test.exe: thin-feature scenes of tipstudy2 (seeds 1-4 x sub/rot/mix x 30 frames)
# and straight edges (half-planes at 0, 26.57, 45 deg, 8 sub-pixel phases), fan-triangulated, D3D9 screen coordinates
# (pixel centre at integer => coord - 0.5). Layout: int32 nframes, per frame int32 ntri, float32[ntri*3*2]. frames.json: meta.
import os, sys, json, struct, math, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import tiplib as T, tipstudy2 as S2
W, H = 170, 120
def tris(polys):
    out = []
    for p in polys:
        p = T.ccw(p)
        for k in range(1, len(p) - 1): out += [p[0], p[k], p[k + 1]]
    return np.array(out) - 0.5
def halfplane(theta, phase):
    a = math.radians(theta); n = np.array([math.cos(a), math.sin(a)]); t = np.array([-n[1], n[0]]); c = np.array([W / 2, H / 2]) + n * phase
    return [np.array([c + t * 300, c - t * 300, c - t * 300 - n * 300, c + t * 300 - n * 300])]
FRAMES = []
for seed in (1, 2, 3, 4):
    for mo in ('sub', 'rot', 'mix'):
        fn = S2.scene_fn(seed, mo)
        for k in range(30): FRAMES.append(dict(kind='thin', seed=seed, motion=mo, k=k, polys=fn(k)))
for th in (0.0, 26.57, 45.0):
    for ph in range(8): FRAMES.append(dict(kind='edge', theta=th, phase=ph / 8 + 0.0371, polys=halfplane(th, ph / 8 + 0.0371)))
if __name__ == '__main__':
    blob = []
    for f in FRAMES:
        t = tris(f['polys']).astype(np.float32); blob.append(struct.pack('<i', len(t) // 3) + t.tobytes())
    with open(os.path.join(HERE, 'frames.bin'), 'wb') as fo:
        fo.write(struct.pack('<i', len(blob))); fo.write(b''.join(blob))
    json.dump(dict(W=W, H=H, frames=[{k: v for k, v in f.items() if k != 'polys'} for f in FRAMES]), open(os.path.join(HERE, 'frames.json'), 'w'))
    print('frames', len(FRAMES))
