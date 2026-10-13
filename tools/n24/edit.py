# Nr. 24 (luaunlockfull): Autor "St0ny (original by Alastor StrixEfuartus)". Aufruf: edit.py <worktree>
import sys, re
wt = sys.argv[1]
NEW = 'St0ny (original by Alastor StrixEfuartus)'
p = wt + '/apply_patches.ps1'
raw = open(p, 'rb').read(); assert raw.count(b'\r\n') == raw.count(b'\n')
s = raw.decode('ascii').replace('\r\n', '\n')
a = "    @{ Id = 'luaunlockfull';"
i = s.index(a); assert s.count(a) == 1
old = "\n       Author = 'St0ny'\n"; j = s.index(old, i); assert j - i < 200
s = s[:j] + "\n       Author = '%s'\n" % NEW + s[j + len(old):]
open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
def md(fn, a, b):
    p = wt + '/docs/' + fn
    t = open(p, encoding='utf-8').read(); assert t.count(a) == 1, (fn, a, t.count(a))
    open(p, 'w', encoding='utf-8', newline='\n').write(t.replace(a, b))
md('README.de.md', '| LUA Unlock (vollständig): alle geschützten Funktionen freigeben | 🔴 **[unsicher]** | St0ny |',
   '| LUA Unlock (vollständig): alle geschützten Funktionen freigeben | 🔴 **[unsicher]** | %s |' % NEW)
md('README.md', '| LUA unlock (complete): allow all protected functions | 🔴 **[unsafe]** | St0ny |',
   '| LUA unlock (complete): allow all protected functions | 🔴 **[unsafe]** | %s |' % NEW)
md('PATCHES.de.md', '*(Nr. 24, Autor: St0ny)*', '*(Nr. 24, Autor: %s)*' % NEW)
md('PATCHES.en.md', '*(No. 24, Author: St0ny)*', '*(No. 24, Author: %s)*' % NEW)
print('ok', wt.split('/')[-1])
