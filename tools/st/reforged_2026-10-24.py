#!/usr/bin/env python3
# Preset "Reforged" vom 24.10.2026 aus der gespeicherten Auswahl reforged_2026-10-24.ini setzen (gleicher Ordner):
# Ids mit 1 sind drin, mit 0 nicht, fehlende behalten ihren Stand. Gegenueber dem Stand vom 19.10. faellt nur
# "HD Unit-Frame Portraits" (hdportraits) heraus. Patcher: $PRESET_REFORGED und Kommentar dazu; README DE/EN:
# Spalte "Reforged" aller Zeilen und der Absatz zum Preset (nur noch zwei Patches, die die Wow.exe vergroessern).
# Aufruf: reforged_2026-10-24.py <Ordner des Zweigs>   (st0ny-dev oder st0ny-main)
import sys, os, re
D = sys.argv[1]
INI = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reforged_2026-10-24.ini')
def rd(p, crlf=False):
    s = open(p, encoding='utf-8', newline='').read()
    if crlf: assert '\r\n' in s; s = s.replace('\r\n', '\n')
    else: assert '\r' not in s
    return s
def wr(p, s, crlf=False):
    if crlf: s.encode('ascii'); s = s.replace('\n', '\r\n')
    open(p, 'w', encoding='utf-8', newline='').write(s)
def once(s, a, b, tag):
    assert s.count(a) == 1, (tag, a[:80], s.count(a)); return s.replace(a, b)
ini = {}
for l in open(INI, encoding='utf-8'):
    m = re.match(r'^\s*([A-Za-z0-9_]+)\s*=\s*([01])\s*$', l)
    if m: ini[m.group(1)] = m.group(2) == '1'
# ---------------- Patcher ----------------
p = os.path.join(D, 'apply_patches.ps1'); s = rd(p, True)
ids = re.findall(r"(?m)^    @\{ Id = '(\w+)'", s[s.index('\n$patches = @(\n'):])
m = re.search(r'(?ms)^\$PRESET_REFORGED = @\(\n.*?\n\)\n', s); blk = m.group(0)
cur = re.findall(r"'(\w+)'", blk)
new = [i for i in ids if ini.get(i, i in cur)]
gone = [i for i in cur if i not in new]; added = [i for i in new if i not in cur]
assert gone == ['hdportraits'] and added == [], (gone, added)
blk = once(blk, " 'hdportraits',", '', 'Preset')
assert re.findall(r"'(\w+)'", blk) == [i for i in cur if i != 'hdportraits']
s = s[:m.start()] + blk + s[m.end():]
n9 = ids.index('glyphfix') + 1; nh = ids.index('hdportraits') + 1; ni = ids.index('iconsnap') + 1
assert (n9, ni) == (9, nh + 1)
s = once(s, '# Warmane getestet (Nr. %d, %d und %d vergroessern die Wow.exe); dazu die\n' % (n9, nh, ni),
            '# Warmane getestet (Nr. %d und %d vergroessern die Wow.exe); dazu die\n' % (n9, ni), 'Kommentar')
wr(p, s, True)
# ---------------- README: Spalte "Reforged" und Absatz ----------------
for f, tag, a, b in (
    ('README.de.md', 'PATCHES.de.md', 'Drei davon (Nr. %d, %d und %d) vergrößern die `Wow.exe`' % (n9, nh, ni),
                                       'Zwei davon (Nr. %d und %d) vergrößern die `Wow.exe`' % (n9, ni)),
    ('README.md', 'PATCHES.en.md', 'Three of them\n(No. %d, %d and %d) make `Wow.exe` larger' % (n9, nh, ni),
                                    'Two of them\n(No. %d and %d) make `Wow.exe` larger' % (n9, ni))):
    p = os.path.join(D, 'docs', f); t = once(rd(p), a, b, f)
    lines = t.split('\n'); hit = 0
    for k, l in enumerate(lines):
        mm = re.match(r'^\| \[(\d+)\]\(%s#patch-(\w+)\) \|' % re.escape(tag), l)
        if not mm: continue
        c = l.split('|'); assert c[-1] == '' and c[-4].strip() in ('✅', '–'), (f, l[:60])
        want = ' ✅ ' if mm.group(2) in new else ' – '
        if c[-4] != want: c[-4] = want; lines[k] = '|'.join(c); hit += 1; print('%s Nr. %s %s -> %s' % (f, mm.group(1), mm.group(2), want.strip()))
    assert hit == 1, (f, hit)
    wr(p, '\n'.join(lines))
print('Reforged neu: %d Patches (ohne hdportraits, Nr. %d)' % (len(new), nh))
