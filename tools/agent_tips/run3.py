import tipstudy as S, json, sys, math
def circ(r, a0, n=8): return [(r * math.cos(math.radians(a0 + 360.0 * i / n)), r * math.sin(math.radians(a0 + 360.0 * i / n))) for i in range(n)]
S.OFFS.update({'c1a': circ(1.0, 22.5), 'c1.2': circ(1.2, 22.5), 'c1.4': circ(1.4, 22.5), 'c1.4b': circ(1.4, 0),
               'pin8': [(1, .5), (1, -.5), (-1, .5), (-1, -.5), (.5, 1), (-.5, 1), (.5, -1), (-.5, -1)],
               'pin4': [(1, .5), (-.5, 1), (-1, -.5), (.5, -1)], 'c1.2x4': circ(1.2, 22.5, 4)[:4],
               'c2a': circ(2.0, 22.5)})
M = [m for m in S.METHODS if m[0] in ('current: cur8 stencil', 'circ8 stencil')]
M += [('r1x8 post k4 gL', 'r1x8', 'post', 4.0, 1.7, 'line')]
for nm in ('c1a', 'c1.2', 'c1.4', 'c1.4b', 'pin8', 'pin4', 'c1.2x4'):
    for k in ((3.0, 4.0) if nm != 'c1.4' else (2.5, 3.5)):
        M.append(('%s post k%g gR' % (nm, k), nm, 'post', k, 4.5, 'ring'))
        M.append(('%s post k%g gL' % (nm, k), nm, 'post', k, 1.7, 'line'))
M.append(('c2a stencil', 'c2a', 'stencil', 0, 2.5))
out = S.run(M)
json.dump(out, open('run3.json', 'w'), indent=1)
