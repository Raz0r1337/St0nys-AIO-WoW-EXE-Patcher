# Lichter-Zweig = neuer dev-Stand + Nr. 69 "Mehr Lichter" + Nr. 70 "Lichter bleiben an" (hinter der Umrandung Nr. 68).
# Aufruf: port_lights.py <dev-Ordner (apply_patches.ps1 + docs/)> <lights-Ordner> <Ziel-Ordner>
import re, sys, os, shutil
DEV, LG, OUT = sys.argv[1:4]
FIRST, LAST, SHIFT = 69, 90, 2
def sh(n): n = int(n); return str(n + SHIFT if FIRST <= n <= LAST else n)
def once(s, a, b):
    assert s.count(a) == 1, (a[:100], s.count(a)); return s.replace(a, b)
def refs(s):
    # "Nr. N", "Nr. N–M" (Bereich) und "Nr. N und M"; nur die Zahlen direkt nach Nr./No. (Listen in der README von Hand)
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
s = refs(s)                                   # Verweise auf Nr. 69-90 -> 71-92 (vor dem Einfuegen)
a = l.index('# ============================================================' + NL + '#  Mehr Lichter: 8 statt 4')
b = l.index(NL + '}' + NL, l.index('function Add-MoreLights')) + len(NL + '}' + NL)
block = l[a:b]
i = s.index('function Add-IconPixelSnap'); j = s.index(NL + '}' + NL, i) + len(NL + '}' + NL)
s = s[:j] + NL + block + s[j:]
a = l.index("    @{ Id = 'lights';"); b = l.index(NL + '    }}' + NL, l.index("    @{ Id = 'lightstay';")) + len(NL + '    }}' + NL)
entries = l[a:b]
i = s.index("    @{ Id = 'outline';"); j = s.index(NL + '    }}' + NL, i) + len(NL + '    }}' + NL)
s = s[:j] + NL + entries + s[j:]
s = once(s, "    'occluder', 'bluemoon', 'notransparency', 'hdportraits', 'iconsnap'," + NL,
            "    'occluder', 'bluemoon', 'notransparency', 'hdportraits', 'iconsnap'," + NL + "    'lights', 'lightstay'," + NL)
s = once(s, "# Lexara-Lader (Nr. 30, Patch sicher, DLL riskant). Im Menue mit R, ueber",
            "# Lexara-Lader (Nr. 30, Patch sicher, DLL riskant) und die noch ungetesteten" + NL +
            "# Licht-Patches Nr. 69 und 70. Im Menue mit R, ueber")
assert all(ord(c) < 128 for c in s), 'Skript nicht ASCII'
wr(os.path.join(OUT, 'apply_patches.ps1'), s)
# ---------- PATCHES ----------
for lang, head, nr in (('de', '## Interface & Komfort', 'Nr.'), ('en', '## Interface & comfort', 'No.')):
    p = 'docs/PATCHES.%s.md' % lang
    d = refs(rd(os.path.join(DEV, p))); g = rd(os.path.join(LG, p))
    a = g.index('<a id="patch-lights"></a>'); b = g.index(head)
    sec = g[a:b]
    sec = once(sec, '(%s 66, ' % nr, '(%s 69, ' % nr); sec = once(sec, '(%s 67, ' % nr, '(%s 70, ' % nr)
    sec = once(sec, '%s 68' % nr, '%s 70' % nr)    # TIP verwies faelschlich auf Nr. 68 (gemeint: Lichter bleiben an)
    assert not re.search(r'(Nr\.|No\.) (6[6-8])\b', sec), sec
    d = once(d, head, sec + head)
    wr(os.path.join(OUT, p), d)
# ---------- README ----------
for lang, md in (('de', 'PATCHES.de.md'), ('en', 'PATCHES.en.md')):
    p = 'docs/README.de.md' if lang == 'de' else 'docs/README.md'
    d = rd(os.path.join(DEV, p)); g = rd(os.path.join(LG, p))
    d = table(refs(d), md)
    rows = [ln for ln in g.split('\n') if ln.startswith('| [66](%s#patch-lights)' % md) or ln.startswith('| [67](%s#patch-lightstay)' % md)]
    assert len(rows) == 2, rows
    rows = [rows[0].replace('| [66](', '| [69]('), rows[1].replace('| [67](', '| [70](')]
    k = d.index('| [68](%s#patch-outline)' % md); k2 = d.index('\n', k) + 1
    d = d[:k2] + '\n'.join(rows) + '\n' + d[k2:]
    if lang == 'de':
        d = once(d, 'Dazu kommt der Lexara-Lader (Nr. 30) für Stormhands HD-Schriften. Der Patch\nselbst ist sicher, die `Lexara.dll` kann auf öffentlichen Servern aber erkannt\noder blockiert werden; ohne `Lexara.dll` im WoW-Ordner bewirkt er nichts.\n',
                 'Dazu kommen der Lexara-Lader (Nr. 30) für Stormhands HD-Schriften und die\nLicht-Patches Nr. 69 und 70. Beim Lexara-Lader ist der Patch selbst sicher,\ndie `Lexara.dll` kann auf öffentlichen Servern aber erkannt oder blockiert\nwerden; ohne `Lexara.dll` im WoW-Ordner bewirkt er nichts. Die Licht-Patches\nsind noch ungetestet, Nr. 69 vergrößert die `Wow.exe` ebenfalls.\n')
        d = once(d, 'Nr. 4, 10,\n    11, 23–25, 44, 45, 48–53, 78 und 86–90 (rote Warnung).', 'Nr. 4, 10,\n    11, 23–25, 44, 45, 48–53, 80 und 88–92 (rote Warnung).')
        d = once(d, 'Nr. 26, 31, 32, 42, 47, 54, 65, 68, 72, 75–77 und 84', 'Nr. 26, 31, 32, 42, 47, 54, 65, 68–70, 74, 77–79 und 86')
        d = once(d, 'Nr. 25, 26, 31, 32, 47, 54, 65, 68 und 84 (orange Warnung).', 'Nr. 25, 26, 31, 32, 47, 54, 65, 68–70 und 86 (orange Warnung).')
        d = once(d, 'Nr. 9, 53, 66–68, 78 und 84.', 'Nr. 9, 53, 66–69, 80 und 86.')
    else:
        d = once(d, 'On top of that comes the Lexara loader\n(No. 30) for Stormhand\'s HD fonts. The patch itself is safe, but `Lexara.dll`\nmay be detected or blocked on public servers; without `Lexara.dll` in the WoW\nfolder it does nothing.',
                 'On top of that come the Lexara loader\n(No. 30) for Stormhand\'s HD fonts and the light patches No. 69 and 70. For the\nLexara loader the patch itself is safe, but `Lexara.dll` may be detected or\nblocked on public servers; without `Lexara.dll` in the WoW folder it does\nnothing. The light patches are still untested; No. 69 makes `Wow.exe` larger\nas well.')
        d = once(d, 'No. 4, 10, 11, 23–25,\n    44, 45, 48–53, 78 and 86–90 (red warning).', 'No. 4, 10, 11, 23–25,\n    44, 45, 48–53, 80 and 88–92 (red warning).')
        d = once(d, 'No. 26, 31, 32, 42, 47, 54, 65, 68, 72, 75–77 and 84', 'No. 26, 31, 32, 42, 47, 54, 65, 68–70, 74, 77–79 and 86')
        d = once(d, 'No. 25, 26, 31, 32, 47, 54, 65, 68 and 84 (orange warning).', 'No. 25, 26, 31, 32, 47, 54, 65, 68–70 and 86 (orange warning).')
        d = once(d, 'No. 9, 53,\n    66–68, 78 and 84.', 'No. 9, 53,\n    66–69, 80 and 86.')
    wr(os.path.join(OUT, p), d)
# ---------- alles andere unveraendert aus dev ----------
print('ok')
