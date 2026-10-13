import tipstudy as S, json, sys
M = [m for m in S.METHODS if m[0] in ('current: cur8 stencil', 'circ8 stencil', 'disc12 stencil', 'r1x8 post k4', 'r1x4 post k4')]
M += [('r1x8 post k4 gL', 'r1x8', 'post', 4.0, 1.7, 'line'), ('r1x8 post k3 gL', 'r1x8', 'post', 3.0, 1.8, 'line'),
      ('r1x4 post k4 gL', 'r1x4', 'post', 4.0, 1.7, 'line'), ('r1x4 post k6 gL', 'r1x4', 'post', 6.0, 1.7, 'line')]
out = S.run(M)
json.dump(out, open('run2.json', 'w'), indent=1)
