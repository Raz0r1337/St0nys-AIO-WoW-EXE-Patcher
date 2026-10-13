# dev + Nr. 69 "Lichter bleiben an" (aus st0ny-dev-lights, dort Nr. 70) direkt hinter der Umrandung Nr. 68.
# Aufruf: port_lightstay.py <dev-Ordner> <lights-Ordner> <Ziel-Ordner>
import re, sys, os
DEV, LG, OUT = sys.argv[1:4]
FIRST, LAST, SHIFT = 69, 90, 1
def sh(n): n = int(n); return str(n + SHIFT if FIRST <= n <= LAST else n)
def once(s, a, b):
    assert s.count(a) == 1, (a[:100], s.count(a)); return s.replace(a, b)
def refs(s):
    def f(m):
        out = '%s %s' % (m.group(1), sh(m.group(2)))
        if m.group(3): out += m.group(3) + sh(m.group(4))
        if m.group(5): out += m.group(5) + sh(m.group(6))
        return out
    return re.sub(r'(Nr\.|No\.) (\d+)(?:(–)(\d+))?(?!\d)(?!\.\d)(?:( (?:und|and) )(\d+)(?!\d))?', f, s)
def table(s, md):
    return re.sub(r'(?m)^\| \[(\d+)\]\(%s#' % re.escape(md), lambda m: '| [%s](%s#' % (sh(m.group(1)), md), s)
rd = lambda p: open(p, encoding='utf-8', newline='').read()
def wr(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, 'w', encoding='utf-8', newline='').write(s)
# ---------- Skript ----------
s = rd(os.path.join(DEV, 'apply_patches.ps1')); l = rd(os.path.join(LG, 'apply_patches.ps1'))
NL = '\r\n'
s = refs(s)
a = l.index("    @{ Id = 'lightstay';"); b = l.index(NL + '    }}' + NL, a) + len(NL + '    }}' + NL)
entry = l[a:b]
i = s.index("    @{ Id = 'outline';"); j = s.index(NL + '    }}' + NL, i) + len(NL + '    }}' + NL)
s = s[:j] + NL + entry + s[j:]
assert all(ord(c) < 128 for c in s), 'Skript nicht ASCII'
wr(os.path.join(OUT, 'apply_patches.ps1'), s)
# ---------- PATCHES ----------
for lang, head, nr in (('de', '## Interface & Komfort', 'Nr.'), ('en', '## Interface & comfort', 'No.')):
    p = 'docs/PATCHES.%s.md' % lang
    d = refs(rd(os.path.join(DEV, p))); g = rd(os.path.join(LG, p))
    a = g.index('<a id="patch-lightstay"></a>'); b = g.index(head)
    sec = once(g[a:b], '(%s 70, ' % nr, '(%s 69, ' % nr)
    assert not re.search(r'(Nr\.|No\.) (6[6-9]|7\d)\b', sec.replace('(%s 69, ' % nr, '')), sec
    d = once(d, head, sec + head)
    wr(os.path.join(OUT, p), d)
# ---------- README ----------
for lang, md in (('de', 'PATCHES.de.md'), ('en', 'PATCHES.en.md')):
    p = 'docs/README.de.md' if lang == 'de' else 'docs/README.md'
    d = rd(os.path.join(DEV, p)); g = rd(os.path.join(LG, p))
    d = table(refs(d), md)
    rows = [ln for ln in g.split('\n') if ln.startswith('| [70](%s#patch-lightstay)' % md)]
    assert len(rows) == 1, rows
    row = rows[0].replace('| [70](', '| [69](')
    row = once(row, '| St0ny | ✅ | – | – |', '| St0ny | – | – | – |')   # in dev nicht im Reforged-Preset
    k = d.index('| [68](%s#patch-outline)' % md); k2 = d.index('\n', k) + 1
    d = d[:k2] + row + '\n' + d[k2:]
    if lang == 'de':
        d = once(d, 'Nr. 4, 10,\n    11, 23–25, 44, 45, 48–53, 78 und 86–90 (rote Warnung).', 'Nr. 4, 10,\n    11, 23–25, 44, 45, 48–53, 79 und 87–91 (rote Warnung).')
        d = once(d, 'Nr. 26, 31, 32, 42, 47, 54, 65, 68, 72, 75–77 und 84', 'Nr. 26, 31, 32, 42, 47, 54, 65, 68, 69, 73, 76–78 und 85')
        d = once(d, 'Nr. 25, 26, 31, 32, 47, 54, 65, 68 und 84 (orange Warnung).', 'Nr. 25, 26, 31, 32, 47, 54, 65, 68, 69 und 85 (orange Warnung).')
        d = once(d, 'Nr. 9, 53, 66–68, 78 und 84. Das ist', 'Nr. 9, 53, 66–68, 79 und 85. Das ist')
        d = once(d, '(Nr. 9, 53, 66–68, 78 und 84), entfernen', '(Nr. 9, 53, 66–68, 79 und 85), entfernen')
    else:
        d = once(d, 'No. 4, 10, 11, 23–25,\n    44, 45, 48–53, 78 and 86–90 (red warning).', 'No. 4, 10, 11, 23–25,\n    44, 45, 48–53, 79 and 87–91 (red warning).')
        d = once(d, 'No. 26, 31, 32, 42, 47, 54, 65, 68, 72, 75–77 and 84', 'No. 26, 31, 32, 42, 47, 54, 65, 68, 69, 73, 76–78 and 85')
        d = once(d, 'No. 25, 26, 31, 32, 47, 54, 65, 68 and 84 (orange warning).', 'No. 25, 26, 31, 32, 47, 54, 65, 68, 69 and 85 (orange warning).')
        d = once(d, 'No. 9, 53,\n    66–68, 78 and 84.', 'No. 9, 53,\n    66–68, 79 and 85.')
        d = once(d, '(No. 9, 53, 66–68, 78 and 84) also remove', '(No. 9, 53, 66–68, 79 and 85) also remove')
    wr(os.path.join(OUT, p), d)
print('ok')
