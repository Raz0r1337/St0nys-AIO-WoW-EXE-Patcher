#!/usr/bin/env python3
# dev + Nr. 69 "Mehr Lichter" (aus st0ny-dev-lights) direkt vor "Lichter bleiben an" (wird Nr. 70).
# Aufruf: port_lights.py <dev-Ordner> <lights-Ordner> <Ziel-Ordner>
import re, sys, os
DEV, LG, OUT = sys.argv[1:4]
FIRST, LAST, SHIFT = 69, 91, 1
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
NL = '\r\n'
# ---------- Skript ----------
s = rd(os.path.join(DEV, 'apply_patches.ps1')); l = rd(os.path.join(LG, 'apply_patches.ps1'))
s = refs(s)
# Hilfsfunktion Add-MoreLights samt Kopfkommentar vor den Wasserzeichen-Block
k = l.index('function Add-MoreLights {')
a = l.rindex('# ============================================================' + NL, 0, l.rindex('# ============================================================' + NL, 0, k))
b = l.index(NL + '}' + NL, k) + len(NL + '}' + NL)
func = l[a:b]
assert func.count('function ') == 1 and 'Mehr Lichter' in func
w = s.index('# ============================================================' + NL + '#  Wasserzeichen')
s = s[:w] + func + NL + s[w:]
# Eintrag direkt vor "Lichter bleiben an"
a = l.index("    @{ Id = 'lights';"); b = l.index(NL + '    }}' + NL, a) + len(NL + '    }}' + NL)
entry = l[a:b]
i = s.index("    @{ Id = 'lightstay';")
s = s[:i] + entry + NL + s[i:]
assert all(ord(c) < 128 for c in s), 'Skript nicht ASCII'
wr(os.path.join(OUT, 'apply_patches.ps1'), s)
# ---------- PATCHES ----------
for lang, nr in (('de', 'Nr.'), ('en', 'No.')):
    p = 'docs/PATCHES.%s.md' % lang
    d = refs(rd(os.path.join(DEV, p))); g = rd(os.path.join(LG, p))
    a = g.index('<a id="patch-lights"></a>'); b = g.index('<a id="patch-lightstay"></a>')
    sec = g[a:b]
    rest = re.sub(r'\((Nr\.|No\.) 69, ', '', sec)
    assert set(re.findall(r'(?:Nr\.|No\.) (\d+)', rest)) <= {'70'}, re.findall(r'(?:Nr\.|No\.) (\d+)', rest)
    d = once(d, '<a id="patch-lightstay"></a>', sec + '<a id="patch-lightstay"></a>')
    # Abschnitt "Lichter bleiben an" wie im Lichter-Zweig (dort schon mit Bezug auf Nr. 69)
    a2 = g.index('<a id="patch-lightstay"></a>'); b2 = g.index('\n<a id="', a2 + 10)
    a3 = d.index('<a id="patch-lightstay"></a>'); b3 = d.index('\n<a id="', a3 + 10)
    d = d[:a3] + g[a2:b2] + d[b3:]
    wr(os.path.join(OUT, p), d)
# ---------- README ----------
for lang, md in (('de', 'PATCHES.de.md'), ('en', 'PATCHES.en.md')):
    p = 'docs/README.de.md' if lang == 'de' else 'docs/README.md'
    d = rd(os.path.join(DEV, p)); g = rd(os.path.join(LG, p))
    d = table(refs(d), md)
    rows = [ln for ln in g.split('\n') if ln.startswith('| [69](%s#patch-lights)' % md)]
    assert len(rows) == 1, rows
    row = rows[0]
    row = once(row, '| St0ny | ✅ | – | – |', '| St0ny | – | – | – |')   # in dev nicht im Reforged-Preset
    k = d.index('| [70](%s#patch-lightstay)' % md)
    d = d[:k] + row + '\n' + d[k:]
    if lang == 'de':
        d = once(d, 'Nr. 4,\n    11, 23–25, 44, 45, 48–53, 79 und 87–91 (rote Warnung).', 'Nr. 4,\n    11, 23–25, 44, 45, 48–53, 80 und 88–92 (rote Warnung).')
        d = once(d, 'Nr. 26, 31, 32, 42, 47, 54, 65, 68, 69, 73, 76–78 und 85', 'Nr. 26, 31, 32, 42, 47, 54, 65, 68–70, 74, 77–79 und 86')
        d = once(d, 'Nr. 10, 25, 26, 31, 32, 47, 54, 65, 68, 69 und 85 (orange Warnung).', 'Nr. 10, 25, 26, 31, 32, 47, 54, 65, 68–70 und 86 (orange Warnung).')
        d = once(d, 'Nr. 9, 53, 66–68, 79 und 85. Das ist', 'Nr. 9, 53, 66–69, 80 und 86. Das ist')
        d = once(d, '(Nr. 9, 53, 66–68, 79 und 85), entfernen', '(Nr. 9, 53, 66–69, 80 und 86), entfernen')
    else:
        d = once(d, 'No. 4, 11, 23–25,\n    44, 45, 48–53, 79 and 87–91 (red warning).', 'No. 4, 11, 23–25,\n    44, 45, 48–53, 80 and 88–92 (red warning).')
        d = once(d, 'No. 26, 31, 32, 42, 47, 54, 65, 68, 69, 73, 76–78 and 85', 'No. 26, 31, 32, 42, 47, 54, 65, 68–70, 74, 77–79 and 86')
        d = once(d, 'No. 10, 25, 26, 31, 32, 47, 54, 65, 68, 69 and 85 (orange warning).', 'No. 10, 25, 26, 31, 32, 47, 54, 65, 68–70 and 86 (orange warning).')
        d = once(d, 'No. 9, 53,\n    66–68, 79 and 85.', 'No. 9, 53,\n    66–69, 80 and 86.')
        d = once(d, '(No. 9, 53, 66–68, 79 and 85) also remove', '(No. 9, 53, 66–69, 80 and 86) also remove')
    wr(os.path.join(OUT, p), d)
print('ok')
