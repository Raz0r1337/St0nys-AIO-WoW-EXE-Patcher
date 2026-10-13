# viewseq.py - zoomed crops of consecutive frames (rows = methods, columns = frames) -> PNG
import sys, numpy as np, tipstudy as S, tiplib as T
from PIL import Image
def crop_frames(methods, pat, frames, box, comp="C", z=12):
    y0, y1, x0, x1 = box; rows = []
    for name, ok, line, k, gk in methods:
        row = []
        for i in frames:
            d = T.frame(S.scene_polys(i), S.OFFS[ok], pat, S.H, S.W, line, k, gk, want=True)
            img = (d['C'] + 0.30 * d['f']) if comp == 'C' else d[comp]
            row.append(np.pad(img[y0:y1, x0:x1], 1, constant_values=0.25))
        rows.append(np.concatenate(row, 1))
    im = np.concatenate(rows, 0)
    return Image.fromarray((np.clip(im, 0, 1) * 255).astype(np.uint8)).resize((im.shape[1] * z, im.shape[0] * z), Image.NEAREST)
if __name__ == '__main__':
    ms = [m for m in S.METHODS if m[0] in sys.argv[3].split(',')] if len(sys.argv) > 3 else S.METHODS[:1]
    box = tuple(int(v) for v in sys.argv[4].split(',')) if len(sys.argv) > 4 else (30, 66, 30, 70)
    crop_frames(ms, sys.argv[1], range(0, 6), box, sys.argv[5] if len(sys.argv) > 5 else 'C').save(sys.argv[2])
