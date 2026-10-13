# Vereinigung aller nicht abgedeckten Bytes ueber alle Versionen/Auswahlen -> zusammenhaengende Bereiche je alter Id.
# Aufruf: compat_union.py <neues Skript> <Lauf-Ordner> [<Lauf-Ordner> ...]
import sys, re, os, glob
def table(path):
    s = open(path, encoding='ascii', errors='replace').read().replace('\r\n', '\n')
    a = re.search(r'(?m)^# BEGIN ORIGINAL-BYTES$', s); z = re.search(r'(?m)^# END ORIGINAL-BYTES$', s)
    ent = []
    for line in s[a.start():z.start()].split('\n'):
        m = re.match(r'^([a-z0-9]+);([0-9A-F]+);([0-9A-F]*)(?:;[01])?$', line)
        if m: ent.append((m.group(1), int(m.group(2), 16), bytes.fromhex(m.group(3))))
    return ent
cov = set()
for i, off, b in table(sys.argv[1]): cov.update(range(off, off + len(b)))
miss = {}
for R in sys.argv[2:]:
    for d in glob.glob(os.path.join(R, '*-*')):
        st = os.path.join(d, 'patcher_state.ini')
        if not os.path.exists(st): continue
        owner = {}
        for i, off, b in table(os.path.join(d, 'apply_patches.ps1')):
            for k in range(len(b)): owner.setdefault(off + k, set()).add(i)
        for line in open(st, encoding='utf-8'):
            m = re.match(r'^undo=0x([0-9A-F]+):([0-9A-F]*)$', line.strip())
            if not m: continue
            off = int(m.group(1), 16)
            for k in range(off, off + len(m.group(2)) // 2):
                if k not in cov:
                    for i in (owner.get(k) or {'?'}): miss.setdefault(k, set()).add(i)
offs = sorted(miss)
runs = []
for k in offs:
    if runs and k == runs[-1][1] and miss[k] == runs[-1][2]: runs[-1][1] = k + 1
    else: runs.append([k, k + 1, miss[k]])
tot = 0
for a, z, ids in runs:
    tot += z - a
    print('0x%06X %3d Byte  %s' % (a, z - a, ','.join(sorted(ids))))
print('gesamt %d Byte in %d Bereichen' % (tot, len(runs)))
