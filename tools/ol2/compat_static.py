# Statische Kompatibilitaetspruefung: Deckt die Original-Byte-Tabelle des neuen Skripts alle Bytes ab,
# die alte Versionen laut patcher_state.ini geaendert haben? Zuordnung zu den alten Patch-Ids ueber die
# Tabelle der alten Version. Aufruf: compat_static.py <neues Skript> <Lauf-Ordner> <Auswahl> <Repo>
import sys, re, os, subprocess
new, R, SEL, repo = sys.argv[1:5]
def table(path):
    s = open(path, encoding='ascii', errors='replace').read().replace('\r\n', '\n')
    a = re.search(r'(?m)^# BEGIN ORIGINAL-BYTES$', s); z = re.search(r'(?m)^# END ORIGINAL-BYTES$', s)
    ent = []
    if a and z:
        for line in s[a.start():z.start()].split('\n'):
            m = re.match(r'^([a-z0-9]+);([0-9A-F]+);([0-9A-F]*)(?:;[01])?$', line)
            if m: ent.append((m.group(1), int(m.group(2), 16), bytes.fromhex(m.group(3))))
    ids = re.findall(r"(?m)^    @\{ Id = '([^']+)'", s)
    return ent, ids
nent, nids = table(new)
cov = set()
for i, off, b in nent:
    cov.update(range(off, off + len(b)))
commits = open(os.path.join(R, 'commits.txt')).read().split()
bad = 0
for c in commits:
    d = os.path.join(R, '%s-%s' % (c, SEL))
    date = subprocess.run(['git', '-C', repo, 'log', '-1', '--format=%ad', '--date=format:%Y-%m-%d %H:%M', c], capture_output=True, text=True).stdout.strip()
    rc = open(os.path.join(d, 'rc.txt')).read().strip() if os.path.exists(os.path.join(d, 'rc.txt')) else '?'
    st = os.path.join(d, 'patcher_state.ini')
    if not os.path.exists(st):
        print('%s %s rc=%s KEIN STATE' % (c, date, rc)); bad += 1; continue
    oent, oids = table(os.path.join(d, 'apply_patches.ps1'))
    owner = {}
    for i, off, b in oent:
        for k in range(len(b)): owner.setdefault(off + k, set()).add(i)
    miss = {}
    for line in open(st, encoding='utf-8'):
        m = re.match(r'^undo=0x([0-9A-F]+):([0-9A-F]*)$', line.strip())
        if not m: continue
        off = int(m.group(1), 16); n = len(m.group(2)) // 2
        for k in range(off, off + n):
            if k not in cov:
                for i in (owner.get(k) or {'?'}):
                    miss.setdefault(i, []).append(k)
    gone = [i for i in oids if i not in nids]
    if miss:
        bad += 1
        parts = ['%s:%dB@0x%X' % (i, len(v), min(v)) for i, v in sorted(miss.items())]
        print('%s %s rc=%s FEHLT %s | nicht mehr im Skript: %s' % (c, date, rc, ' '.join(parts), ','.join(gone)))
    else:
        print('%s %s rc=%s OK | nicht mehr im Skript: %s' % (c, date, rc, ','.join(gone)))
print('fertig: %d von %d Versionen mit Luecken' % (bad, len(commits)))
