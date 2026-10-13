import tipstudy2 as S2, tipstudy as S, json, math, contextlib, io
def circ(r, a0, n=8): return [(r * math.cos(math.radians(a0 + 360.0 * i / n)), r * math.sin(math.radians(a0 + 360.0 * i / n))) for i in range(n)]
S.OFFS['c1.4b'] = circ(1.4, 0)
M = [('current: cur8 stencil', 'cur8', 'stencil', 0, 2.5), ('circ8 stencil', 'circ8', 'stencil', 0, 2.5), ('disc12 stencil', 'disc12', 'stencil', 0, 2.5),
     ('cur8+r1 (16) stencil', 'cur8+r1', 'stencil', 0, 2.5),
     ('r1x8 k4 gL2.0', 'r1x8', 'post', 4.0, 2.0, 'line'), ('r1x8 k4 gR5.0', 'r1x8', 'post', 4.0, 5.0, 'ring'),
     ('c1.4b k3 gL2.0', 'c1.4b', 'post', 3.0, 2.0, 'line')]
with contextlib.redirect_stdout(io.StringIO()): acc = S2.run(M)
json.dump(acc, open('run4.json', 'w'), indent=1)
S2.summary(acc)
for mo in ('sub', 'rot', 'mix'):
    print('-- motion', mo); S2.summary({k: [x for x in v if x[0] == mo] for k, v in acc.items()})
