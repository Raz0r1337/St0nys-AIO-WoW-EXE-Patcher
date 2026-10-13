import sys, math, json, numpy as np
import lookstudy as LS, tipstudy as S, patterns, tiplib as T
OF = dict(S.OFFS); OF.update(patterns.P)
ANG = (0, 5, 11.25, 18.43, 26.57, 33.75, 40, 45)
for curve, k in (('hard', 4), ('soft', 4), ('soft', 5), ('soft', 6)):
    T.LCURVE = curve
    m = ('sq4in4 %s k%g' % (curve, k), OF['sq4in4'], 'post', k, 2.0, 'line')
    for pat in ('bin', 'ms4'):
        r = []
        for a in ANG:
            L, G, C = LS.profile(m, pat, a, 8); r.append((L.std(), C.std(), C.mean(), L.mean()))
        print('%-18s %s Lmean %s | Cstd%% %s' % (m[0], pat, ' '.join('%.2f' % x[3] for x in r), ' '.join('%.2f' % (100 * x[1] / x[2]) for x in r)), flush=True)
