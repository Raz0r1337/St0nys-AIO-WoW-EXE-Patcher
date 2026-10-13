# tipstudy2.py - like tipstudy.py, but several random thin-feature scenes (seeds) and motion types:
#   sub: translation (0.09, 0.05) px per frame; rot: rotation 0.25 deg per frame about the head; mix: both + 0.1 %/frame scale
# prints per method the mean over scenes and motions (and per motion) of the thin-ROI metrics (bin / ms4) and thick-ROI C own.
import sys, os, json, math, numpy as np
import tiplib as T, tipstudy as S
H, W = S.H, S.W
def scene_fn(seed, motion):
    rng = np.random.default_rng(seed)
    cx, cy, r = 70.0 + rng.uniform(-3, 3), 60.0 + rng.uniform(-3, 3), rng.uniform(10, 15)
    parts = []
    for i in range(4):
        ang = rng.uniform(0, 360); base_ang = ang + rng.uniform(-30, 30)
        bx, by = cx + 0.7 * r * math.cos(math.radians(base_ang)), cy + 0.7 * r * math.sin(math.radians(base_ang))
        kind = i % 4
        if kind == 0: parts.append(T.wedge((bx, by), ang, rng.uniform(26, 38), rng.uniform(3, 5)))          # ear
        elif kind == 1: parts.append(T.wedge((bx, by), ang, rng.uniform(22, 32), rng.uniform(1.5, 2.5)))     # thin ear
        elif kind == 2: parts.append(T.wedge((bx, by), ang, rng.uniform(24, 34), rng.uniform(0.9, 1.6), rng.uniform(0.15, 0.4)))  # spike
        else: w_ = rng.uniform(0.4, 1.1); parts.append(T.wedge((bx, by), ang, rng.uniform(22, 32), w_, w_))  # thin bar
    def polys(k):
        P = [T.disc(cx, cy, r)] + parts
        if motion in ('rot', 'mix'): P = T.rot(P, 0.25 * k, (cx, cy))
        if motion == 'mix':
            s = 1 + 0.001 * k; P = [(p - (cx, cy)) * s + (cx, cy) for p in P]
        if motion in ('sub', 'mix'): P = T.tr(P, 0.09 * k, 0.05 * k)
        return P
    return polys
def run(methods, seeds=(1, 2, 3, 4), motions=('sub', 'rot', 'mix'), nf=30, tag='s2'):
    acc = {}
    for seed in seeds:
        for mo in motions:
            fn = scene_fn(seed, mo)
            S.scene_polys = fn
            out = S.run(methods, nf=nf, cache='cache_%s_%d_%s.npz' % (tag, seed, mo), pats=('bin', 'ms4'))
            for name, res in out.items(): acc.setdefault(name, []).append((mo, res))
    return acc
def summary(acc):
    keys = [('bin', 'thinC', 'out'), ('bin', 'thinL', 'out'), ('bin', 'thinG', 'out'), ('bin', 'thinL', 'pops'), ('bin', 'thickC', 'own'),
            ('ms4', 'thinC', 'out'), ('ms4', 'thinL', 'out'), ('ms4', 'thinG', 'out'), ('ms4', 'thinL', 'pops'), ('ms4', 'thickC', 'own')]
    print('%-22s %6s %6s | %-37s | %-37s' % ('method', 'holes', 'mass', 'bin: C out  L out  G out  L pops thickC', 'ms4: C out  L out  G out  L pops thickC'))
    for name, lst in acc.items():
        h = np.mean([r['holes'] for _, r in lst]); m = np.mean([r['mass'] for _, r in lst])
        v = [np.mean([r[p][a][b] for _, r in lst]) for p, a, b in keys]
        print('%-22s %6.3f %6.2f | %6.2f %6.2f %6.2f %6.1f %6.2f | %6.2f %6.2f %6.2f %6.1f %6.2f' % (name, h, m, *v))
