# gpu_check.py - GPU (Wine) vs Python model for identical frames: ring (TEX0 alpha) and glow alpha.
import numpy as np, glowlib as G, gpu_load as L, seq_study as Q
for run, pat, down in (('old_ms0', 'bin', 'box'), ('tent_ms0', 'bin', 'tent'), ('old_ms4', 'ms4', 'box'), ('tent_ms4', 'ms4', 'tent')):
    g = L.load(run)
    Fs, Rs = Q.frames('sub_x', pat); idx = L.seq_index('sub_x')
    dr = []; da = []; dmax = 0
    for k, fi in enumerate(idx):
        Rg = g['tex0a'][fi]; dr.append(np.abs(Rg - Rs[k]).max() * 255)
        a = G.pipe(Rg, quant=True, down=down)            # python model on the GPU's own ring
        m = g['clean'][fi]
        d = np.abs(g['A'][fi] - a)[m] * 255; da.append(np.sqrt((d ** 2).mean())); dmax = max(dmax, d.max())
    print('%-9s ring: max|TEX0a - sim R| per frame %s LSB | glow: GPU vs model(on GPU ring) rms %.2f LSB, max %.0f LSB' % (run, sorted(set(np.round(dr).astype(int).tolist())), np.mean(da), dmax))
