# final table: same 4 seeds x 3 motions as run4 (cached ideal references), chosen fix + remaining alternatives
import tipstudy2 as S2, tipstudy as S, json, contextlib, io, patterns
S.OFFS.update(patterns.P)
M = [('sq4in4 k4 gL2.0 (fix)', 'sq4in4', 'post', 4.0, 2.0, 'line'), ('cur8+ax4 (12) stencil', 'cur8+ax4', 'stencil', 0, 2.5),
     ('cur8 post k1.33 gR', 'cur8', 'post', 4 / 3, 2.5, 'ring'), ('sq4in4 stencil (ring only)', 'sq4in4', 'stencil', 0, 5.0)]
with contextlib.redirect_stdout(io.StringIO()): acc = S2.run(M)
json.dump(acc, open('run6.json', 'w'), indent=1)
a4 = json.load(open('run4.json'))
acc2 = {k: [tuple(x) for x in v] for k, v in a4.items()}; acc2.update(acc)
S2.summary(acc2)
for mo in ('sub', 'rot', 'mix'):
    print('-- motion', mo); S2.summary({k: [x for x in v if x[0] == mo] for k, v in acc2.items()})
