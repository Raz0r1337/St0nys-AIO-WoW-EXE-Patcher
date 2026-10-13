import tipstudy2 as S2, tipstudy as S, json, contextlib, io, sys, patterns
S.OFFS.update(patterns.P)
M = [('current: cur8 stencil', 'cur8', 'stencil', 0, 2.5), ('r1x8 k4 gL2.0', 'r1x8', 'post', 4.0, 2.0, 'line')]
for p in ('sq4in4', 'sq4in4d', 'dia4in4', 'sq4in4q'):
    M.append(('%s k4 gL2.0' % p, p, 'post', 4.0, 2.0, 'line'))
M.append(('dia4in4 k5 gL2.0', 'dia4in4', 'post', 5.0, 2.0, 'line'))
with contextlib.redirect_stdout(io.StringIO()): acc = S2.run(M, seeds=(1, 2), motions=('sub', 'rot', 'mix'), nf=30)
json.dump(acc, open('run5.json', 'w'), indent=1)
S2.summary(acc)
