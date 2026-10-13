# gpu_load.py - loads shimmer_test.exe output (gpu/<variant>_ms<m>/) as float arrays
import os, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
META = json.load(open(os.path.join(HERE, 'frames.json')))
W, H = META['W'], META['H']; NF = len(META['frames'])
def load(run):
    d = os.path.join(HERE, 'gpu', run)
    bb = np.fromfile(os.path.join(d, 'bb.raw'), np.uint8).reshape(NF, H, W, 4)[..., [2, 1, 0, 3]].astype(np.float64)
    ta = np.fromfile(os.path.join(d, 'tex0a.raw'), np.uint8).reshape(NF, H, W).astype(np.float64) / 255
    R = bb[..., 2] / 94.0                         # thin line light(green) has B = 0x5E: ring coverage
    F = np.clip((bb[..., 0] - 94.0 * R) / 255.0, 0, 1)
    A = bb[..., 1] / 255.0                         # glow alpha where R = B = 0
    clean = (bb[..., 0] == 0) & (bb[..., 2] == 0)  # no figure / ring sample in this pixel
    return dict(bb=bb, tex0a=ta, R=R, F=F, A=A, clean=clean)
def seq_index(seq):
    return [k for k, f in enumerate(META['frames']) if f['seq'] == seq]
