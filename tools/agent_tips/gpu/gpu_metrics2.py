# gpu_metrics2.py - metrics on the Wine/wined3d renders of tips_test.exe (gpu/out/<variant>_ms<m>/bb.raw)
#  model check : mean |GPU - simulation| of the composite (G channel), same sampling ('bin' / 'ms4'), per variant
#  thin scenes : like tipstudy2 (ROI = 7 px around the thin parts, not near the head): own = |d(M - A)| with A = simulation of
#                the same variant on analytic coverage; out = only pixels outside the figure in both frames; pops = |d| >= 32 LSB
#  edges       : straight edges at 0 / 26.57 / 45 deg, 8 sub-pixel phases: std/mean of the composite sum in a window (pumping)
import os, sys, json, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import tiplib as T, tipstudy as S, tipstudy2 as S2, patterns, gen_frames2 as GF
T.LC = 1.0; T.GC = 1.0
S.OFFS.update(patterns.P)
VAR = {'old': ('cur8', 'stencil', 0, 2.5, 'ring'), 'new': ('r1x8', 'post', 4.0, 2.0, 'line'), 'nsq': ('sq4in4', 'post', 4.0, 2.0, 'line')}
W, H = GF.W, GF.H
def load(run):
    a = np.fromfile(os.path.join(HERE, 'out', run, 'bb.raw'), np.uint8).reshape(-1, H, W, 4).astype(np.float64) / 255
    B, G, R = a[..., 0], a[..., 1], a[..., 2]
    return np.clip(R - B, 0, 1), G
def simframe(v, polys, pat):
    ok, line, k, gk, gs = VAR[v]
    return T.frame(polys, S.OFFS[ok], pat, H, W, line, k, gk, gsrc=gs)
runs = sys.argv[1:] or ['old_ms0', 'new_ms0', 'nsq_ms0', 'old_ms4', 'new_ms4', 'nsq_ms4']
FR = GF.FRAMES
res = {}
for run in runs:
    v, ms = run.split('_'); pat = 'bin' if ms == 'ms0' else 'ms4'
    Fg, Cg = load(run); r = {}
    # model check on a subset (every 5th thin frame + all edge frames)
    dif = []
    for i in list(range(0, 360, 5)) + list(range(360, 384)):
        f, L, Gl, C = simframe(v, FR[i]['polys'], pat)
        dif.append(np.abs(Cg[i] - C).mean() * 255)
    r['model_mean_abs_LSB'] = float(np.mean(dif)); r['model_max_frame'] = float(np.max(dif))
    # thin scenes
    own_all, out_all, pops_all = [], [], []
    for seed in (1, 2, 3, 4):
        for mo in ('sub', 'rot', 'mix'):
            idx = [i for i, f in enumerate(FR) if f['kind'] == 'thin' and f['seed'] == seed and f['motion'] == mo]
            roi, _ = S.roi_mask([FR[i]['polys'] for i in idx]) if False else (None, None)
            S.H, S.W = H, W
            roi, _ = S.roi_mask([FR[i]['polys'] for i in idx])
            A = [simframe(v, FR[i]['polys'], 'ideal') for i in idx]
            for j in range(len(idx) - 1):
                a, b = idx[j], idx[j + 1]
                d = (Cg[b] - Cg[a]) - (A[j + 1][3] - A[j][3])
                outside = roi & (Fg[a] < 0.01) & (Fg[b] < 0.01) & (A[j][0] < 0.02) & (A[j + 1][0] < 0.02)
                own_all.append(np.abs(d)[roi].mean() * 255); out_all.append(np.abs(d)[outside].sum() * 255 / roi.sum())
                pops_all.append(int((np.abs(d)[outside] * 255 >= 32).sum()))
    r['thin_own'] = float(np.mean(own_all)); r['thin_out'] = float(np.mean(out_all)); r['thin_pops32'] = float(np.mean(pops_all))
    # edges
    pump = {}
    for th in (0.0, 26.57, 45.0):
        idx = [i for i, f in enumerate(FR) if f['kind'] == 'edge' and f['theta'] == th]
        s = np.array([Cg[i][20:100, 45:125].sum() for i in idx]); pump[str(th)] = float(100 * s.std() / s.mean())
    r['edge_pump_pct'] = pump
    res[run] = r
    print('%-8s model |GPU-sim| %.2f LSB (max frame %.2f) | thin C own %.2f out %.2f pops>=32 %.1f/frame | edge pumping %% 0: %.2f 26.6: %.2f 45: %.2f' % (
        run, r['model_mean_abs_LSB'], r['model_max_frame'], r['thin_own'], r['thin_out'], r['thin_pops32'], pump['0.0'], pump['26.57'], pump['45.0']), flush=True)
json.dump(res, open(os.path.join(HERE, 'gpu_metrics2.json'), 'w'), indent=1)
