#!/usr/bin/env python3
# Nr. 69 "Mehr Lichter" und Nr. 70 "Lichter bleiben an": im Spiel getestet -> "ingame ungetestet" faellt weg, [BETA] bleibt.
# Aufruf: classify_lights.py <Ordner mit apply_patches.ps1 und docs/> [--lightsbranch]
import sys, os, re
root = sys.argv[1]; LB = '--lightsbranch' in sys.argv
def rd(p, crlf=False):
    s = open(p, encoding='utf-8', newline='').read()
    if crlf: assert '\r\n' in s; s = s.replace('\r\n', '\n')
    else: assert '\r' not in s
    return s
def wr(p, s, crlf=False):
    if crlf: s.encode('ascii'); s = s.replace('\n', '\r\n')
    open(p, 'w', encoding='utf-8', newline='').write(s)
def once(s, a, b, tag=''):
    assert s.count(a) == 1, (tag, a[:90], s.count(a)); return s.replace(a, b)
def in_section(s, start, a, b, tag):
    i = s.index(start); j = s.index('<a id="', i + len(start)); sec = s[i:j]
    return s[:i] + once(sec, a, b, tag) + s[j:]
# --- Skript ---
p = os.path.join(root, 'apply_patches.ps1'); s = rd(p, True)
s = once(s, "    @{ Id = 'lights'; Cat = 'graphics'; On = $false; GrowsExe = $true; PublicUntested = $true; GameUntested = $true\n",
            "    @{ Id = 'lights'; Cat = 'graphics'; On = $false; GrowsExe = $true; PublicUntested = $true\n", 'lights flags')
s = once(s, "    @{ Id = 'lightstay'; Cat = 'graphics'; On = $false; PublicUntested = $true; GameUntested = $true\n",
            "    @{ Id = 'lightstay'; Cat = 'graphics'; On = $false; PublicUntested = $true\n", 'lightstay flags')
for id_ in ('lights', 'lightstay'):
    e = re.search(r"^    @\{ Id = '%s';.*?\n    \}\}\n" % id_, s, re.M | re.S).group(0)
    assert not any(re.search(r'ungetestet|untested', l, re.I) for l in e.split('\n') if l.strip().startswith('#')), (id_, 'Kommentar erwaehnt ungetestet')
wr(p, s, True)
# --- PATCHES ---
for f, l_old, l_new, s_old, s_new in (
    ('PATCHES.de.md', '🟠 **[ungetestet - Exe wird größer]**', '🟠 **[online ungetestet - Exe wird größer]**', '🟠 **[ungetestet]**', '🟠 **[online ungetestet]**'),
    ('PATCHES.en.md', '🟠 **[untested - exe grows]**', '🟠 **[untested online - exe grows]**', '🟠 **[untested]**', '🟠 **[untested online]**')):
    p = os.path.join(root, 'docs', f); s = rd(p)
    s = in_section(s, '<a id="patch-lights"></a>', l_old, l_new, f + ' lights')
    s = in_section(s, '<a id="patch-lightstay"></a>', s_old, s_new, f + ' lightstay')
    wr(p, s)
# --- README ---
for f, md, l_old, l_new, s_old, s_new, a, b in (
    ('README.de.md', 'PATCHES.de.md', '🟠 **[ungetestet - Exe wird größer]**', '🟠 **[online ungetestet - Exe wird größer]**', '🟠 **[ungetestet]**', '🟠 **[online ungetestet]**',
     'möglicherweise verbuggt: Nr. 10, 25, 26, 31, 32, 47, 54, 65, 68–70 und 86 (orange Warnung).', 'möglicherweise verbuggt: Nr. 10, 25, 26, 31, 32, 47, 54, 65, 68 und 86 (orange Warnung).'),
    ('README.md', 'PATCHES.en.md', '🟠 **[untested - exe grows]**', '🟠 **[untested online - exe grows]**', '🟠 **[untested]**', '🟠 **[untested online]**',
     'possibly buggy: No. 10, 25, 26, 31, 32, 47, 54, 65, 68–70 and 86 (orange warning).', 'possibly buggy: No. 10, 25, 26, 31, 32, 47, 54, 65, 68 and 86 (orange warning).')):
    p = os.path.join(root, 'docs', f); s = rd(p)
    for anchor, o, n in (('| [69](%s#patch-lights)' % md, l_old, l_new), ('| [70](%s#patch-lightstay)' % md, s_old, s_new)):
        rows = [ln for ln in s.split('\n') if ln.startswith(anchor)]; assert len(rows) == 1, (f, anchor)
        s = once(s, rows[0], once(rows[0], o, n, f + anchor), f + anchor)
    s = once(s, a, b, f + ' ingame-Liste')
    if LB:
        if f == 'README.de.md':
            s = once(s, 'Die Licht-Patches\nsind noch ungetestet, Nr. 69 vergrößert die `Wow.exe` ebenfalls.\n',
                        'Die Licht-Patches\nsind im Spiel getestet, auf öffentlichen Servern aber noch nicht; Nr. 69\nvergrößert die `Wow.exe` ebenfalls.\n', 'reforged de')
        else:
            s = once(s, 'The light patches are still untested; No. 69 makes `Wow.exe` larger\nas well.',
                        'The light patches are tested in game, but not yet on public servers;\nNo. 69 makes `Wow.exe` larger as well.', 'reforged en')
    wr(p, s)
print('ok')
