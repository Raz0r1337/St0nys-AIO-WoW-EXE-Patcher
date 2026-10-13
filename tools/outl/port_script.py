# Outline (st0ny-dev-outline) in st0ny-dev uebernehmen: Add-SectionBlock, Add-CodeSection,
# Add-HdPortraits (Outline-Fassung), Add-Outline, Patch-Eintrag nach iconsnap, Nummern ab 68 (+1).
# Aufruf: port_script.py <outline-Skript> <dev-Skript (wird ueberschrieben)>
import re, sys
O = open(sys.argv[1], encoding='ascii', newline='').read().split('\r\n')
D = open(sys.argv[2], encoding='ascii', newline='').read().split('\r\n')
def funcs(t):
    res = {}
    for i, l in enumerate(t):
        m = re.match(r'^function ([\w-]+)', l)
        if m:
            j = i
            while t[j] != '}': j += 1
            k = i
            while k > 0 and t[k - 1].startswith('#'): k -= 1
            res[m.group(1)] = (k, i, j)
    return res
def entry(t, pid):
    a = [n for n, l in enumerate(t) if l.startswith("    @{ Id = '%s';" % pid)]; assert len(a) == 1, pid
    z = a[0]
    while t[z] != '    }}': z += 1
    return a[0], z
of = funcs(O)
# 1) Funktionen ersetzen (Funktionszeile bis schliessende Klammer; Kommentar ist gleich)
for n in ('Add-CodeSection', 'Add-HdPortraits'):
    df = funcs(D)
    assert D[df[n][0]:df[n][1]] == O[of[n][0]:of[n][1]], n + ': Kommentar weicht ab'
    D[df[n][1]:df[n][2] + 1] = O[of[n][1]:of[n][2] + 1]
# 2) Add-SectionBlock vor Add-CodeSection einsetzen
df = funcs(D); k = df['Add-CodeSection'][0]
assert D[k - 1] == ''
blk = O[of['Add-SectionBlock'][0]:of['Add-SectionBlock'][2] + 1]
D[k:k] = blk + ['']
# 3) Add-Outline vor Add-IconPixelSnap einsetzen (im Outline-Zweig steht es hinter Add-HoldRepeat)
df = funcs(D); k = df['Add-IconPixelSnap'][0]
assert D[k - 1] == '' and D[k - 2] == '}' and df['Add-HoldRepeat'][2] == k - 2
blk = O[of['Add-Outline'][0]:of['Add-Outline'][2] + 1]
D[k:k] = blk + ['']
# 4) Patch-Eintrag hinter iconsnap
oa, oz = entry(O, 'outline'); da, dz = entry(D, 'iconsnap')
D[dz + 1:dz + 1] = [''] + O[oa:oz + 1]
# 5) Nummern-Hinweise ab 68 um 1 schieben (Patch-Liste und Kommentare)
ids = [re.match(r"^    @\{ Id = '([^']+)'", l).group(1) for l in D if re.match(r"^    @\{ Id = '", l)]
C = ids.index('outline') + 1; assert C == 68 and ids[C - 2] == 'iconsnap' and len(ids) == 90, (C, len(ids))
def sh(m):
    n = int(m.group(2)); return '%s %d' % (m.group(1), n + 1 if n >= C else n)
for n, l in enumerate(D):
    nl = re.sub(r'(Nr\.|No\.) (\d+)(?!\d)(?!\.\d)', sh, l)
    if nl != l: print('%5d: %s\n    -> %s' % (n + 1, l.strip(), nl.strip())); D[n] = nl
open(sys.argv[2], 'w', encoding='ascii', newline='').write('\r\n'.join(D))
print('ok, Patches:', len(ids))
