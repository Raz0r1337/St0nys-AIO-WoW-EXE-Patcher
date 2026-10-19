#!/usr/bin/env python3
# Autor eines Patches setzen: Patcher (Author = '...'), PATCHES DE/EN (Ueberschrift "*(Nr. X, Autor: ...)*")
# und README DE/EN (Spalte "Autor"). Ohne bisherigen Autor kommt die Author-Zeile direkt unter die Id-Zeile.
# Aufruf: set_author.py <Ordner> <Id> <Autor>
import sys, os, re
D, PID, AU = sys.argv[1], sys.argv[2], sys.argv[3]
def rd(p, crlf=False):
    s = open(p, encoding='utf-8', newline='').read()
    if crlf: assert '\r\n' in s; s = s.replace('\r\n', '\n')
    else: assert '\r' not in s
    return s
def wr(p, s, crlf=False):
    if crlf: s.encode('ascii'); s = s.replace('\n', '\r\n')
    open(p, 'w', encoding='utf-8', newline='').write(s)
# Patcher
p = os.path.join(D, 'apply_patches.ps1'); s = rd(p, True)
body0 = s.index('\n$patches = @(\n')
ids = re.findall(r"(?m)^    @\{ Id = '(\w+)'", s[body0:]); num = ids.index(PID) + 1
m = re.search(r"(?m)^    @\{ Id = '%s';[^\n]*\n" % PID, s); assert m and m.start() > body0
nxt = s[m.end():s.index('\n', m.end()) + 1]
if nxt.startswith("       Author = '"):
    s = s[:m.end()] + "       Author = '%s'\n" % AU + s[m.end() + len(nxt):]
else:
    s = s[:m.end()] + "       Author = '%s'\n" % AU + s[m.end():]
wr(p, s, True)
# PATCHES
for f, nr, au in (('PATCHES.de.md', 'Nr.', 'Autor'), ('PATCHES.en.md', 'No.', 'Author')):
    p = os.path.join(D, 'docs', f); s = rd(p)
    i = s.index('<a id="patch-%s"></a>\n' % PID); j = s.index('\n', i) + 1; k = s.index('\n', j)
    line = s[j:k]
    mm = re.search(r"\*\(%s %d(, %s: (.*?))?\)\* " % (re.escape(nr), num, au), line); assert mm, (f, line)
    line = line[:mm.start()] + "*(%s %d, %s: %s)* " % (nr, num, au, AU) + line[mm.end():]
    s = s[:j] + line + s[k:]; wr(p, s)
# README
for f, tag in (('README.de.md', 'PATCHES.de.md'), ('README.md', 'PATCHES.en.md')):
    p = os.path.join(D, 'docs', f); lines = rd(p).split('\n')
    hit = [n for n, l in enumerate(lines) if l.startswith('| [%d](%s#patch-%s) |' % (num, tag, PID))]
    assert len(hit) == 1, (f, hit)
    c = lines[hit[0]].split('|'); assert c[-1] == '' and len(c) >= 9, c   # ..., Autor, Reforged, Billy, St0ny, ''
    c[-5] = ' %s ' % AU; lines[hit[0]] = '|'.join(c); wr(p, '\n'.join(lines))
print('Nr. %d %s: Autor %s' % (num, PID, AU))
