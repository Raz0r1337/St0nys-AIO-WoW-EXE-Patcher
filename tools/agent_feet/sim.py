# Geometric simulation: "nur wo verdeckt" ring at sunk feet and near occluders.
# Unit at origin on flat ground (z=0), camera at horizontal distance D (toward -x) and elevation angle th
# to the unit's FEET. Human: height H, bbox centre at H/2, bounding radius R, body half depth RHO.
import math
H, R, RHO = 2.2, 1.3, 0.3          # assumed human M2 bounds (bbox ~0.8 x 1.2 x 2.2 -> r ~1.3)
KAPPA = 0.001
FOV_V = 1.0; HPX = 1080; ALPHA = FOV_V / HPX   # rad per pixel
P = 1.0                            # ring offset in pixels (glow mode, OFFS diag 1 px)
def setup(dist, th):
    cam = (-dist * math.cos(th), 0.0, dist * math.sin(th))   # camera position; looks at the unit centre
    tgt = (0.0, 0.0, H / 2)
    f = [t - c for t, c in zip(tgt, cam)]; n = math.sqrt(sum(x * x for x in f)); f = [x / n for x in f]
    return cam, f
def depth(cam, f, p): return sum((a - b) * c for a, b, c in zip(p, cam, f))
def ground_delta(dist, th, s, xf=0.0):
    # foot bottom B (sunk by s) at horizontal offset xf; ray through the pixel P px BELOW B on screen
    cam, f = setup(dist, th)
    B = (xf, 0.0, -s)
    v = [b - c for b, c in zip(B, cam)]; L = math.sqrt(sum(x * x for x in v)); v = [x / L for x in v]
    # rotate v downward by P*ALPHA in the vertical plane (x,z)
    a = math.atan2(v[2], v[0]) - P * ALPHA
    v2 = (math.cos(a), 0.0, math.sin(a))
    t = -cam[2] / v2[2]                       # hit ground z=0
    G = [c + t * x for c, x in zip(cam, v2)]
    dB = depth(cam, f, B); dG = depth(cam, f, G)
    dc = depth(cam, f, (0, 0, H / 2))
    return dB, dG, dc
def thr(method, dB, dc):
    df = dc - R
    if method == 'KZ': return KAPPA * dB * dB
    if method == 'SPH': return dB - df
    if method == 'SPH+KZ': return dB - (df - KAPPA * df * df)
def smax(method, dist, th, xf):
    # smallest sinking s that gives a line (bisection on s in [0, 3])
    lo, hi = 0.0, 3.0
    dB, dG, dc = ground_delta(dist, th, 0.0, xf)
    if dB - dG > thr(method, dB, dc): return 0.0
    for _ in range(50):
        m = (lo + hi) / 2; dB, dG, dc = ground_delta(dist, th, m, xf)
        if dB - dG > thr(method, dB, dc): hi = m
        else: lo = m
    return hi
print('Sinking (yd) at which a line appears under the FRONT foot (xf=-0.25), ring 1 px; ">3" = never')
print('dist  angle   KZ(now)  SPH   SPH+KZ')
for dist in (5, 10, 15, 20, 30, 40):
    for deg in (5, 10, 20, 40):
        th = math.radians(deg)
        r = [smax(m, dist, th, -0.25) for m in ('KZ', 'SPH', 'SPH+KZ')]
        print('%4d  %4d°  ' % (dist, deg) + '  '.join(('%5.2f' % x if x < 2.99 else '  >3 ') for x in r))
print()
print('Near occluder (thin wall in front of the body, perpendicular to the view): minimum gap (yd) between')
print('the body front and the wall for the hidden part to get a ring (silhouette at mid-depth, RHO=%.1f, R=%.1f)' % (RHO, R))
print('dist   KZ(now)  SPH   SPH+KZ')
for dist in (5, 10, 15, 20, 30, 40):
    kz = max(0.0, KAPPA * dist * dist - RHO); sp = R - RHO; df = dist - R
    print('%4d   %5.2f   %5.2f  %5.2f' % (dist, kz, sp, sp + KAPPA * df * df))
