# seq_study2.py - extra variants (look-preserving soft curve k=2.5) on the cached sequences -> seq_results2.json
import json, os, seq_study as Q
Q.VARIANTS.update({'c soft k2.5': dict(down='box', curve_mode='soft', gain=5.0),
                   'a+c tent soft k2.5': dict(down='tent', curve_mode='soft', gain=5.0)})
res = Q.run(list(Q.SEQS), ['bin', 'ms4'], ['current', 'a tent', 'c soft k2.5', 'a+c tent soft k2.5'])
json.dump({'variants': {'|'.join(k): v for k, v in res.items()}, 'decomp': {}}, open(os.path.join(Q.HERE, 'seq_results2.json'), 'w'), indent=1)
print('ok')
