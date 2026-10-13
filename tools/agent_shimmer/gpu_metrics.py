# gpu_metrics.py - temporal stability measured on the Wine/wined3d renders (gpu/<run>/).
#  mc1px : exact 1 px shifts (px1_x, px1_y): residual A[k+1](x+1) - A[k](x) on pixels with glow only (no figure/ring
#          sample) in both frames. Needs no reference: a shift-invariant pipeline gives 0 (up to GPU rounding).
#  sub-pixel / rotation / scale: total change, ideal motion (python ideal on analytic coverage, own look), artifact.
import sys, json, numpy as np, glowlib as G, gpu_load as L, seq_study as Q, seq_study3 as S3
RUNS = sys.argv[1:] or ['old_ms0', 'tent_ms0', 'old_ms4', 'tent_ms4']
LOOK = {'old': dict(down='box'), 'tent': dict(down='tent'), 'tentsoft': dict(down='tent', curve_mode='soft', gain=5.0),
        'soft': dict(down='box', curve_mode='soft', gain=5.0), 'tsv': dict(down='tent', vgain=True, curve_mode='soft', gain=5.0)}
out = {}
for run in RUNS:
    g = L.load(run); var = run.split('_')[0]; kw = LOOK[var]; r = {}
    for seq, ax in (('px1_x', 'x'), ('px1_y', 'y')):
        idx = L.seq_index(seq); res = []
        for a, b in zip(idx[:-1], idx[1:]):
            A0, A1, c0, c1 = g['A'][a], g['A'][b], g['clean'][a], g['clean'][b]
            if ax == 'x': d = (A1[:, 1:] - A0[:, :-1]); m = c1[:, 1:] & c0[:, :-1] & (np.maximum(A1[:, 1:], A0[:, :-1]) > 0)
            else: d = (A1[1:, :] - A0[:-1, :]); m = c1[1:, :] & c0[:-1, :] & (np.maximum(A1[1:, :], A0[:-1, :]) > 0)
            res.append(np.abs(d[m]) * 255)
        res = np.concatenate(res)
        r['mc_' + seq] = dict(rms=float(np.sqrt((res ** 2).mean())), p99=float(np.percentile(res, 99)), max=float(res.max()), ge4=float((res >= 4).mean() * 100))
    for seq in ('sub_x', 'sub_diag', 'rot', 'scale'):
        idx = L.seq_index(seq); Fi, Ri = Q.frames(seq, 'ideal')
        I = np.array([(S3.ideal_full(x, kw) if kw.get('vgain') else Q.ideal_of(x, kw)) for x in Ri])
        A = g['A'][idx]; C = g['clean'][idx]
        tot, mot, art = [], [], []
        for k in range(len(idx) - 1):
            m = C[k] & C[k + 1] & ((np.maximum(A[k], A[k + 1]) > 0) | (np.maximum(I[k], I[k + 1]) > 0.5 / 255))
            dA = (A[k + 1] - A[k])[m] * 255; dI = (I[k + 1] - I[k])[m] * 255
            tot.append(dA); mot.append(dI); art.append(dA - dI)
        c = np.concatenate; rms = lambda x: float(np.sqrt((x ** 2).mean()))
        a = np.abs(c(art))
        r[seq] = dict(total=rms(c(tot)), motion=rms(c(mot)), art=rms(c(art)), p99=float(np.percentile(a, 99)), max=float(a.max()), ge4=float((a >= 4).mean() * 100))
    out[run] = r
json.dump(out, open('gpu_metrics_%s.json' % '_'.join(RUNS), 'w'), indent=1)
for run, r in out.items():
    print(run)
    for k in ('mc_px1_x', 'mc_px1_y'):
        v = r[k]; print('   %-9s 1px motion-compensated residual: rms %.2f  p99 %.1f  max %.0f  px>=4 LSB %.2f%%' % (k[3:], v['rms'], v['p99'], v['max'], v['ge4']))
    for k in ('sub_x', 'sub_diag', 'rot', 'scale'):
        v = r[k]; print('   %-9s total %.2f  motion %.2f  artifact rms %.2f  p99 %.1f  max %.0f  px>=4 LSB %.2f%%' % (k, v['total'], v['motion'], v['art'], v['p99'], v['max'], v['ge4']))
