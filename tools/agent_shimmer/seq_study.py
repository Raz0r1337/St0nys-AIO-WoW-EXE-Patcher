# seq_study.py - temporal stability of the glow for the whole figure under small motions.
# Sequences: sub-pixel x (0.25 px steps), generic sub-pixel diagonal (0.25, 0.1), 1 px steps x,
# rotation (0.1 deg steps), scale (0.2 % steps). Rings: 'bin' (no MSAA), 'ms4' (4x MSAA).
# For every frame pair (k, k+1), at fixed screen pixels that show glow in both frames:
#   total    = A[k+1] - A[k]                  (what the eye sees change)
#   motion   = I[k+1] - I[k]                  (I = ideal: own pipeline phase-averaged over the 2x2 grid, analytic ring coverage)
#   artifact = total - motion                 (grid parity + 8-bit quantisation + ring aliasing)
# all in 8-bit LSB of glow alpha (composite opacity). Also the motion-compensated residual for exact 1 px shifts
# A[k+1](x+1) - A[k](x) (zero for a shift-invariant pipeline) and the energy (sum of visible glow) modulation.
import os, sys, json, numpy as np
import glowlib as G

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, 'cache'); os.makedirs(CACHE, exist_ok=True)

SEQS = {
    'sub_x':    [dict(tx=k / 4.0) for k in range(17)],
    'sub_diag': [dict(tx=0.25 * k, ty=0.1 * k) for k in range(17)],
    'px1_x':    [dict(tx=float(k)) for k in range(6)],
    'px1_y':    [dict(ty=float(k)) for k in range(6)],
    'rot':      [dict(rot_deg=0.1 * k) for k in range(-5, 6)],
    'scale':    [dict(scale=1.0 + 0.002 * k) for k in range(11)],
}

def frames(seq, pat):
    fn = os.path.join(CACHE, '%s_%s.npz' % (seq, pat))
    if os.path.exists(fn):
        z = np.load(fn); return z['F'], z['R']
    Fs, Rs = [], []
    for tf in SEQS[seq]:
        F, R = G.scene(pat, **tf); Fs.append(F.astype(np.float32)); Rs.append(R.astype(np.float32))
    np.savez_compressed(fn, F=np.array(Fs), R=np.array(Rs)); return np.array(Fs), np.array(Rs)

VARIANTS = {
    'current':                 dict(down='box'),
    'a tent':                  dict(down='tent'),
    'b full-res 9tap':         dict(down='full', full_sigma=3.6),
    'c gain3':                 dict(down='box', gain=3.0),
    'c soft':                  dict(down='box', curve_mode='soft'),
    'a+c tent soft':           dict(down='tent', curve_mode='soft'),
    'e tent+gainInV':          dict(down='tent', vgain=True),
    'e tent+bspline':          dict(down='tent', up='bspline'),
    'e tent+vfused':           dict(down='tent', up='vfused'),
}

def ideal_of(Ri, kw):
    base = {k: v for k, v in kw.items() if k in ('down', 'up', 'full_sigma')}
    return G.curve(G.phase_avg(Ri, **base), kw.get('curve_mode', 'hard'), kw.get('gain', 4.0))

def metrics(A, I, V, mc=False):
    out = {}
    tot, mot, art, art_b = [], [], [], {'bright': [], 'mid': [], 'faint': []}
    for k in range(len(A) - 1):
        m = (np.minimum(V[k], V[k + 1]) > 0.999) & ((I[k] > 0.5 / 255) | (I[k + 1] > 0.5 / 255) | (A[k] > 0.5 / 255) | (A[k + 1] > 0.5 / 255))
        dA = (A[k + 1] - A[k]) * 255; dI = (I[k + 1] - I[k]) * 255; dE = dA - dI
        tot.append(dA[m]); mot.append(dI[m]); art.append(dE[m])
        lev = np.maximum(I[k], I[k + 1])[m]
        art_b['bright'].append(dE[m][lev >= 0.5]); art_b['mid'].append(dE[m][(lev >= 0.15) & (lev < 0.5)]); art_b['faint'].append(dE[m][lev < 0.15])
    c = np.concatenate
    rms = lambda x: float(np.sqrt((x ** 2).mean())) if len(x) else float('nan')
    out['total_rms'] = rms(c(tot)); out['motion_rms'] = rms(c(mot)); out['art_rms'] = rms(c(art))
    a = np.abs(c(art)); out['art_p99'] = float(np.percentile(a, 99)); out['art_max'] = float(a.max())
    out['art_px_ge4'] = float((a >= 4).mean() * 100)                   # % of glow pixels per frame with artifact >= 4 LSB
    for b in art_b: out['art_rms_' + b] = rms(c(art_b[b]))
    e = (A * V).sum((1, 2)); ei = (I * V).sum((1, 2))
    out['energy_mod_pct'] = float((e / ei).std() * 100)               # brightness pumping of the whole glow vs ideal
    if mc:   # exact 1 px shifts along x or y: residual vs shifted previous frame
        res = []
        for k in range(len(A) - 1):
            ax = mc
            if ax == 'x': d = (A[k + 1][:, 1:] - A[k][:, :-1]) * 255; m = np.minimum(V[k + 1][:, 1:], V[k][:, :-1]) > 0.999
            else: d = (A[k + 1][1:, :] - A[k][:-1, :]) * 255; m = np.minimum(V[k + 1][1:, :], V[k][:-1, :]) > 0.999
            m &= (A[k + 1][:, 1:] if ax == 'x' else A[k + 1][1:, :]) > 0.5 / 255
            res.append(d[m])
        r = np.abs(c(res)); out['mc_rms'] = rms(r); out['mc_max'] = float(r.max()); out['mc_p99'] = float(np.percentile(r, 99))
    return out

def run(seqs, pats, variants, quant=True):
    R_all = {}
    for seq in seqs:
        Fi, Ri = frames(seq, 'ideal')
        for pat in pats:
            F, R = frames(seq, pat)
            V = np.clip(1 - F - R, 0, 1)
            for vn in variants:
                kw = VARIANTS[vn]
                A = np.array([G.pipe(r, quant=quant, **kw) for r in R])
                I = np.array([ideal_of(r, kw) for r in Ri])
                R_all[(seq, pat, vn)] = metrics(A, I, V, mc={'px1_x': 'x', 'px1_y': 'y'}.get(seq, False))
                if vn == 'current':
                    sat = np.array([G.pipe(r, quant=False, linear_out=True, **kw) for r in R]) * 4 >= 1
                    glowpx = (np.array([G.pipe(r, quant=False, **kw) for r in R]) > 0.5 / 255) & (V > 0.999)
                    R_all[(seq, pat, vn)]['sat_pct'] = float((sat & glowpx).sum() / glowpx.sum() * 100)
    return R_all

def decompose(seqs, pats):
    """current pipeline: add the error sources one by one (artifact rms / p99 / max, LSB)"""
    out = {}
    kw = VARIANTS['current']
    for seq in seqs:
        Fi, Ri = frames(seq, 'ideal'); Vi = np.clip(1 - Fi - Ri, 0, 1)
        I = np.array([ideal_of(r, kw) for r in Ri])
        steps = [('grid only (analytic ring, float)', Ri, Vi, False),
                 ('grid + 8-bit (analytic ring)', Ri, Vi, True)]
        for pat in pats:
            F, R = frames(seq, pat); V = np.clip(1 - F - R, 0, 1)
            steps.append(('ring %s, float' % pat, R, V, False))
            steps.append(('ring %s, 8-bit (= game)' % pat, R, V, True))
        for nm, RR, VV, q in steps:
            A = np.array([G.pipe(r, quant=q, **kw) for r in RR])
            out[(seq, nm)] = metrics(A, I, VV)
        # grid artifact on the actual ring: actual pipeline vs its own phase average on the SAME ring
        for pat in pats:
            F, R = frames(seq, pat); V = np.clip(1 - F - R, 0, 1)
            A = np.array([G.pipe(r, quant=False, **kw) for r in R]); I2 = np.array([ideal_of(r, kw) for r in R])
            out[(seq, 'grid only on ring %s (vs phase-avg of same ring)' % pat)] = metrics(A, I2, V)
    return out

if __name__ == '__main__':
    pats = ['bin', 'ms4']
    seqs = list(SEQS)
    res = run(seqs, pats, list(VARIANTS))
    dec = decompose(['sub_x', 'sub_diag', 'rot', 'scale'], pats)
    js = {'variants': {'|'.join(k): v for k, v in res.items()}, 'decomp': {'|'.join(k): v for k, v in dec.items()}}
    json.dump(js, open(os.path.join(HERE, 'seq_results.json'), 'w'), indent=1)
    print('wrote seq_results.json')
