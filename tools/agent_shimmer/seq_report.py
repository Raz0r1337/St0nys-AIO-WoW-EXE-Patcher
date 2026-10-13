import json, sys
js = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'seq_results.json'))
V = js['variants']; D = js['decomp']
seqs = ['sub_x', 'sub_diag', 'px1_x', 'px1_y', 'rot', 'scale']
print('== decomposition, current pipeline (artifact = change beyond ideal motion; LSB of glow alpha) ==')
print('%-9s %-52s %6s %6s %6s %6s  %6s %6s %6s' % ('seq', 'error sources included', 'rms', 'p99', 'max', '%>=4', 'bright', 'mid', 'faint'))
for k, r in D.items():
    s, nm = k.split('|')
    print('%-9s %-52s %6.2f %6.1f %6.1f %6.2f  %6.2f %6.2f %6.2f' % (s, nm, r['art_rms'], r['art_p99'], r['art_max'], r['art_px_ge4'], r['art_rms_bright'], r['art_rms_mid'], r['art_rms_faint']))
for pat in ('bin', 'ms4'):
    print('\n== variants, ring %s, 8-bit pipeline: total / motion / artifact rms, artifact p99 / max, %%px>=4, energy pumping %%, (1px seqs: motion-compensated residual rms/p99/max) ==' % pat)
    for s in seqs:
        print(' ' + s)
        for k, r in V.items():
            ss, pp, vn = k.split('|')
            if ss != s or pp != pat: continue
            extra = ('  mc %.2f/%.1f/%.0f' % (r['mc_rms'], r['mc_p99'], r['mc_max'])) if 'mc_rms' in r else ''
            sat = ('  sat %.1f%%' % r['sat_pct']) if 'sat_pct' in r else ''
            print('   %-18s tot %5.2f mot %5.2f art %5.2f | p99 %5.1f max %5.1f | >=4: %5.2f%% | pump %.2f%% | br/mid/fa %.2f/%.2f/%.2f%s%s' % (
                vn, r['total_rms'], r['motion_rms'], r['art_rms'], r['art_p99'], r['art_max'], r['art_px_ge4'], r['energy_mod_pct'],
                r['art_rms_bright'], r['art_rms_mid'], r['art_rms_faint'], extra, sat))
