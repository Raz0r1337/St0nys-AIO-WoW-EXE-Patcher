# lookstudy.py - look of the outline per method on thick shapes: line thickness (line mass per unit edge length) vs edge
# angle, glow mass/profile outside the figure, and the straight-edge stability (variation over sub-pixel phases).
# Straight edges: half-plane through the canvas centre, angle 0..45 deg, 8 sub-pixel phases each, 'ideal' / 'bin' / 'ms4'.
import sys, math, json, numpy as np
import tiplib as T

N = 72; WIN = (20, 52)
def halfplane(theta_deg, phase):
    a = math.radians(theta_deg); n = np.array([math.cos(a), math.sin(a)]); t = np.array([-n[1], n[0]])
    c = np.array([N / 2, N / 2]) + n * phase
    # figure = {x: (x - c).n < 0}
    P = [c + t * 300, c - t * 300, c - t * 300 - n * 300, c + t * 300 - n * 300]
    return [T.ccw(np.array(P))]

def seglen(theta_deg, phase):
    # length of the edge line inside the window square, numerically
    a = math.radians(theta_deg); n = np.array([math.cos(a), math.sin(a)]); t = np.array([-n[1], n[0]])
    c = np.array([N / 2, N / 2]) + n * phase
    s = np.linspace(-100, 100, 200001); p = c[None] + s[:, None] * t[None]
    inside = (p[:, 0] >= WIN[0]) & (p[:, 0] <= WIN[1]) & (p[:, 1] >= WIN[0]) & (p[:, 1] <= WIN[1])
    return inside.sum() * (s[1] - s[0])

def profile(m, pat, theta, phases=8):
    name, offs, line, k, gk, gs = m
    Lm, Gm, Cm = [], [], []
    for ph in range(phases):
        phase = ph / phases + 0.0371
        P = halfplane(theta, phase)
        f, L, Gl, C = T.frame(P, offs, pat, N, N, line, k, gk, gsrc=gs)
        w = np.zeros((N, N)); w[WIN[0]:WIN[1], WIN[0]:WIN[1]] = 1
        ln = seglen(theta, phase)
        Lm.append((L * w).sum() / ln); Gm.append((Gl * w).sum() / ln); Cm.append((C * w).sum() / ln)
    return np.array(Lm), np.array(Gm), np.array(Cm)

def glow_profile(m, theta=0.0, pat='ideal'):
    """mean glow / line along the normal (distance bins of 1 px) for a straight edge"""
    name, offs, line, k, gk, gs = m
    acc = {};
    for ph in range(8):
        phase = ph / 8 + 0.0371
        d = T.frame(halfplane(theta, phase), offs, pat, N, N, line, k, gk, want=True, gsrc=gs)
        jj, ii = np.mgrid[0:N, 0:N] + 0.5
        a = math.radians(theta); dist = (ii - N / 2) * math.cos(a) + (jj - N / 2) * math.sin(a) - phase
        win = (ii > WIN[0]) & (ii < WIN[1]) & (jj > WIN[0]) & (jj < WIN[1])
        for b in range(-1, 12):
            sel = win & (dist >= b) & (dist < b + 1)
            if sel.any(): acc.setdefault(b, []).append((d['L'][sel].mean(), d['g'][sel].mean(), d['C'][sel].mean()))
    return {b: tuple(np.mean(v, 0)) for b, v in sorted(acc.items())}

def disc_thickness(m, R=20.0, pat='ideal'):
    name, offs, line, k, gk, gs = m
    n = 2 * R + 20; n = int(n) + (int(n) & 1)
    P = [T.disc(n / 2 + 0.31, n / 2 + 0.17, R, 400)]
    d = T.frame(P, offs, pat, n, n, line, k, gk, want=True, gsrc=gs)
    th = []
    for deg in np.arange(0, 360, 3):
        t = 0; a = math.radians(deg)
        for s in np.arange(R - 1, R + 6, 0.05):
            x = n / 2 + 0.31 + s * math.cos(a); y = n / 2 + 0.17 + s * math.sin(a)
            t += 0.05 * d['L'][int(y), int(x)]
        th.append(t)
    th = np.array(th)
    return th.min(), th.mean(), th.max()

if __name__ == '__main__':
    import run3
