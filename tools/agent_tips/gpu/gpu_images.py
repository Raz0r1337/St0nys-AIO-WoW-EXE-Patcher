# gpu_images.py - zoomed crops of consecutive GPU frames: rows old/nsq x no MSAA/4x, columns = frames (seed, motion)
import os, sys, numpy as np, json
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 170, 120
meta = json.load(open(os.path.join(HERE, 'frames.json')))['frames']
def load(run): return np.fromfile(os.path.join(HERE, 'out', run, 'bb.raw'), np.uint8).reshape(-1, H, W, 4)[..., [2, 1, 0]]
def strip(seed, motion, box, frames, out, z=8):
    idx = [i for i, f in enumerate(meta) if f['kind'] == 'thin' and f['seed'] == seed and f['motion'] == motion]
    y0, y1, x0, x1 = box; rows = []
    for run in ('old_ms0', 'nsq_ms0', 'old_ms4', 'nsq_ms4'):
        a = load(run); row = []
        for k in frames: row.append(np.pad(a[idx[k]][y0:y1, x0:x1], ((1, 1), (1, 1), (0, 0)), constant_values=60))
        rows.append(np.concatenate(row, 1))
    im = np.concatenate(rows, 0)
    Image.fromarray(im).resize((im.shape[1] * z, im.shape[0] * z), Image.NEAREST).save(os.path.join(HERE, out))
if __name__ == '__main__':
    a = load('old_ms0'); idx = [i for i, f in enumerate(meta) if f['kind'] == 'thin' and f['seed'] == 1 and f['motion'] == 'sub']
    Image.fromarray(a[idx[0]]).resize((W * 4, H * 4), Image.NEAREST).save(os.path.join(HERE, 'overview_seed1.png'))
