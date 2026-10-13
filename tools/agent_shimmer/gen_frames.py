# gen_frames.py - writes frames.bin for shimmer_test.exe: the polygon figure of glowlib (same transforms as
# seq_study.SEQS), fan-triangulated, in D3D9 screen coordinates (pixel centre at integer => coord - 0.5).
# Layout: int32 nframes, then per frame int32 ntri, float32[ntri*3*2]. frames.json lists (seq, index, transform).
import os, json, struct, numpy as np
import glowlib as G
from seq_study import SEQS

HERE = os.path.dirname(os.path.abspath(__file__))
ORDER = ['sub_x', 'sub_diag', 'px1_x', 'px1_y', 'rot', 'scale']

def tris(polys):
    out = []
    for p in polys:
        for k in range(1, len(p) - 1): out += [p[0], p[k], p[k + 1]]
    return np.array(out) - 0.5

if __name__ == '__main__':
    meta = []; blob = []
    for seq in ORDER:
        for i, tf in enumerate(SEQS[seq]):
            t = tris(G.transform(G.POLYS, **tf)).astype(np.float32)
            blob.append(struct.pack('<i', len(t) // 3) + t.tobytes()); meta.append(dict(seq=seq, i=i, tf=tf))
    with open(os.path.join(HERE, 'frames.bin'), 'wb') as f:
        f.write(struct.pack('<i', len(blob))); f.write(b''.join(blob))
    json.dump(dict(W=G.W, H=G.H, frames=meta), open(os.path.join(HERE, 'frames.json'), 'w'), indent=0)
    print('frames', len(meta), 'tris/frame', len(t) // 3)
