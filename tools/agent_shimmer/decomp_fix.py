# decomp_fix.py - error sources added one by one, current pipeline vs fix (tent + soft curve in V pass, gain 1)
import json, numpy as np, glowlib as G, seq_study as Q, seq_study3 as S3
CFG = {'current': dict(down='box'), 'fix': dict(down='tent', vgain=True, curve_mode='soft', gain=5.0)}
out = {}
for seq in ('sub_x', 'sub_diag', 'rot', 'scale'):
    Fi, Ri = Q.frames(seq, 'ideal'); Vi = np.clip(1 - Fi - Ri, 0, 1)
    for nm, kw in CFG.items():
        I = np.array([S3.ideal_full(r, kw) if kw.get('vgain') else Q.ideal_of(r, kw) for r in Ri])
        steps = [('grid only (analytic ring, float)', Ri, Vi, False), ('grid + 8-bit (analytic ring)', Ri, Vi, True)]
        for pat in ('ms4', 'bin'):
            F, R = Q.frames(seq, pat); steps.append(('+ ring %s (= game)' % pat, R, np.clip(1 - F - R, 0, 1), True))
        for sn, RR, VV, q in steps:
            A = np.array([G.pipe(r, quant=q, **kw) for r in RR])
            out['%s|%s|%s' % (seq, nm, sn)] = Q.metrics(A, I, VV)
json.dump(out, open('decomp_fix.json', 'w'), indent=1)
print('%-9s %-8s %-36s %6s %6s %6s' % ('seq', 'pipe', 'error sources', 'rms', 'p99', 'max'))
for k, r in out.items():
    s, p, n = k.split('|'); print('%-9s %-8s %-36s %6.2f %6.1f %6.1f' % (s, p, n, r['art_rms'], r['art_p99'], r['art_max']))
