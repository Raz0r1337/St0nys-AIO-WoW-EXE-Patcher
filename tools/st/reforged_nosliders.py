#!/usr/bin/env python3
# Slider-Erweiterung ('sliders') aus dem Preset "Reforged" nehmen - nur dort, das Preset "St0ny" behaelt sie.
# Patcher: Eintrag nur im Block $PRESET_REFORGED entfernen; README DE/EN: Spalte "Reforged" der Zeile #patch-sliders -> "–".
# Aufruf: reforged_nosliders.py <Ordner>   (st0ny-main, st0ny-dev, st0ny-dev-y38fix)
import sys, os, re
D = sys.argv[1]
def rd(p, crlf=False):
    s = open(p, encoding='utf-8', newline='').read()
    if crlf: assert '\r\n' in s; s = s.replace('\r\n', '\n')
    else: assert '\r' not in s
    return s
def wr(p, s, crlf=False):
    if crlf: s.encode('ascii'); s = s.replace('\n', '\r\n')
    open(p, 'w', encoding='utf-8', newline='').write(s)
p = os.path.join(D, 'apply_patches.ps1'); s = rd(p, True)
m = re.search(r'(?ms)^\$PRESET_REFORGED = @\(\n.*?\n\)\n', s); assert m
blk = m.group(0); assert blk.count("'sliders'") == 1
new = blk.replace(" 'sliders',", '', 1); assert new.count("'sliders'") == 0 and new != blk
s = s[:m.start()] + new + s[m.end():]
assert len(re.findall(r"'sliders'", s)) == 2   # Patch-Eintrag + Preset St0ny
wr(p, s, True)
for f, tag in (('README.de.md', 'PATCHES.de.md'), ('README.md', 'PATCHES.en.md')):
    p = os.path.join(D, 'docs', f); lines = rd(p).split('\n')
    hit = [i for i, l in enumerate(lines) if re.match(r'^\| \[\d+\]\(%s#patch-sliders\) \|' % re.escape(tag), l)]
    assert len(hit) == 1, (f, hit)
    c = lines[hit[0]].split('|')                     # ['', Nr, Patch, Status, Autor, Reforged, Billy, St0ny, '']
    assert c[-1] == '' and c[-4].strip() == '✅', (f, c[-4:])
    c[-4] = ' – '; lines[hit[0]] = '|'.join(c)
    wr(p, '\n'.join(lines))
print('reforged ohne sliders ok')
