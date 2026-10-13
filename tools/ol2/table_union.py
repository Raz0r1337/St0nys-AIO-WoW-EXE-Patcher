# Statisch: Welche Stellen aus den Original-Byte-Tabellen alter Versionen deckt die Tabelle des neuen
# Skripts nicht ab? Aufruf: table_union.py <neues Skript> <Repo> <Commit-Liste-Datei>
import sys, re, subprocess
def table_from_text(s):
    s = s.replace('\r\n', '\n')
    a = re.search(r'(?m)^# BEGIN ORIGINAL-BYTES$', s); z = re.search(r'(?m)^# END ORIGINAL-BYTES$', s)
    ent = []
    if not (a and z): return ent
    for line in s[a.start():z.start()].split('\n'):
        m = re.match(r'^([a-z0-9]+);([0-9A-F]+);([0-9A-F]*)(?:;[01])?$', line)
        if m: ent.append((m.group(1), int(m.group(2), 16), bytes.fromhex(m.group(3))))
    return ent
new = table_from_text(open(sys.argv[1], encoding='ascii').read())
cov = set()
for i, off, b in new: cov.update(range(off, off + len(b)))
repo = sys.argv[2]
miss = {}      # Offset -> {(Id)}
first = {}     # (Id) -> erste/letzte Version mit Luecke
for c in open(sys.argv[3]).read().split():
    src = subprocess.run(['git', '-C', repo, 'show', c + ':apply_patches.ps1'], capture_output=True, text=True).stdout
    date = subprocess.run(['git', '-C', repo, 'log', '-1', '--format=%ad', '--date=format:%m-%d %H:%M', c], capture_output=True, text=True).stdout.strip()
    for i, off, b in table_from_text(src):
        hit = False
        for k in range(off, off + len(b)):
            if k not in cov:
                miss.setdefault(k, set()).add(i); hit = True
        if hit:
            f = first.setdefault(i, [date, date])
            f[0] = min(f[0], date); f[1] = max(f[1], date)
offs = sorted(miss); runs = []
for k in offs:
    if runs and k == runs[-1][1] and miss[k] == runs[-1][2]: runs[-1][1] = k + 1
    else: runs.append([k, k + 1, miss[k]])
tot = 0
for a, z, ids in runs:
    tot += z - a
    print('0x%06X %4d Byte  %s' % (a, z - a, ','.join(sorted(ids))))
print('gesamt %d Byte in %d Bereichen' % (tot, len(runs)))
for i, (a, z) in sorted(first.items()):
    print('  %-14s Versionen %s bis %s' % (i, a, z))
