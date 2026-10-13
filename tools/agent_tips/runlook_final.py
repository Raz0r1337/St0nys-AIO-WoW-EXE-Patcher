# look of the final fix vs current on thick shapes (analytic coverage): line thickness by angle, glow mass by angle,
# disc (R 8 / 20) line thickness min/mean/max, glow profile along the normal of a vertical edge
import numpy as np, json, lookstudy as LS, tipstudy as S, patterns
OF = dict(S.OFFS); OF.update(patterns.P)
ANG = (0, 11.25, 22.5, 33.75, 45)
out = {}
for name, ok, line, k, gk, gs in (('current', 'cur8', 'stencil', 0, 2.5, 'ring'), ('fix sq4in4 k4 gL2.0', 'sq4in4', 'post', 4, 2.0, 'line'),
                                  ('fallback (GLFAIL) = current ring', 'cur8', 'stencil', 0, 2.5, 'ring')):
    m = (name, OF[ok], line, k, gk, gs)
    Lid = []; Gid = []
    for a in ANG:
        L, G, C = LS.profile(m, 'ideal', a, 4); Lid.append(float(L.mean())); Gid.append(float(G.mean()))
    d8 = LS.disc_thickness(m, 8.0); d20 = LS.disc_thickness(m, 20.0); gp = LS.glow_profile(m)
    out[name] = dict(line=Lid, glow=Gid, d8=[float(x) for x in d8], d20=[float(x) for x in d20], gprof=[float(gp[b][1]) for b in range(0, 10)], lprof=[float(gp[b][0]) for b in range(-1, 4)])
    print('%-32s line %s (mean %.2f) | glow %s (mean %.2f) | disc8 %.2f/%.2f/%.2f disc20 %.2f/%.2f/%.2f' % (name, ' '.join('%.2f' % x for x in Lid), np.mean(Lid),
          ' '.join('%.2f' % x for x in Gid), np.mean(Gid), *d8, *d20))
    print('%-32s glow profile d=0..9: %s | line profile d=-1..3: %s' % ('', ' '.join('%.2f' % x for x in out[name]['gprof']), ' '.join('%.2f' % x for x in out[name]['lprof'])))
json.dump(out, open('runlook_final.json', 'w'), indent=1)
