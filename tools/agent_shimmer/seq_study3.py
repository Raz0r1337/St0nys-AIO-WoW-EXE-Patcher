# seq_study3.py - curve applied in the vertical blur pass (TEX1 holds final alpha, composite gain 1):
# reference = phase average of the complete float pipeline (curve before upsample), the variant's own look.
import json, os, numpy as np, glowlib as G, seq_study as Q
def ideal_full(R, kw):
    acc = 0
    for sx in (0, 1):
        for sy in (0, 1):
            acc = acc + np.roll(G.pipe(np.roll(R, (sy, sx), (0, 1)), quant=False, **kw), (-sy, -sx), (0, 1))
    return acc / 4
Q.ideal_of = lambda Ri, kw: ideal_full(Ri, kw) if kw.get('vgain') else G.curve(G.phase_avg(Ri, **{k: v for k, v in kw.items() if k in ('down', 'up', 'full_sigma')}), kw.get('curve_mode', 'hard'), kw.get('gain', 4.0))
Q.VARIANTS.update({'tent+hardInV x4': dict(down='tent', vgain=True, curve_mode='hard', gain=4.0),
                   'tent+softInV k2.5': dict(down='tent', vgain=True, curve_mode='soft', gain=5.0),
                   'box+hardInV x4': dict(down='box', vgain=True, curve_mode='hard', gain=4.0)})
if __name__ == '__main__':
    res = Q.run(list(Q.SEQS), ['bin', 'ms4'], ['tent+hardInV x4', 'tent+softInV k2.5', 'box+hardInV x4'])
    json.dump({'variants': {'|'.join(k): v for k, v in res.items()}, 'decomp': {}}, open(os.path.join(Q.HERE, 'seq_results3.json'), 'w'), indent=1)
    print('ok')
