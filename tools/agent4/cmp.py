import sys
from lib import *

n = sys.argv[1]
window_before = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x30
window_after = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x30
p = load(n)
print('== patch %s: ori len %d, patched len %d' % (n, len(d), len(p)))
# 1. verify that diffs == undo ranges
undo = ini_undo(n)
ranges = sorted((o, len(b)) for o, b in undo)
diffs = diff_ranges(d, p)
print('undo ranges:', ['%X+%d' % r for r in ranges])
print('actual diffs:', ['%X+%d' % r for r in diffs])
# each diff must be covered by some undo range
for do, dl in diffs:
    cov = [r for r in ranges if r[0] <= do and do + dl <= r[0] + r[1]]
    if not cov and do < len(d):
        print('  !! diff %X+%d not covered by undo' % (do, dl))
# undo original bytes must match original exe
for o, b in undo:
    if d[o:o + len(b)] != b:
        print('  !! undo bytes at %X do not match original exe' % o)
# also compare with the table rows for this id
pid = [ln.split('=')[1].strip() for ln in open(os.path.join(OUT, '%s.ini' % n)) if ln.startswith('patches=')][0]
rows = table_rows([pid])
tr = sorted((o, len(b)) for _, o, b, _ in rows)
print('table ranges:', ['%X+%d' % r for r in tr])
for _, o, b, excl in rows:
    if d[o:o + len(b)] != b:
        print('  !! table original bytes mismatch at %X' % o)
print()
# 2. per range: disasm/hex of original vs patched
for o, b in undo:
    if o == 0x72DE20:
        continue
    L = len(b)
    va = f2v(o)
    sec = [s[0] for s in SECS if s[3] <= o < s[3] + s[4]]
    sec = sec[0] if sec else '(hdr/appended)'
    print('---- range file %X (+%d) VA %s sec %s' % (o, L, ('%08X' % va) if va else '-', sec))
    print('  old:', d[o:o + L].hex())
    print('  new:', p[o:o + L].hex())
    if sec == '.text' and L >= 1:
        fs = find_func_start(d, va)
        start = max(fs, va - window_before)
        if fs >= va - 0x200:
            start = fs
        n_bytes = (va - start) + L + window_after
        print('  [original] from %08X (func start %08X)' % (start, fs))
        dis(d, start, n_bytes, mark=(va, va + L))
        print('  [patched]')
        dis(p, start, n_bytes, mark=(va, va + L))
    print()
