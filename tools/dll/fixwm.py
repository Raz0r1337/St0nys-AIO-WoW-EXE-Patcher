# st0ny-dev, Nr. 27: keine Servernamen im Kasten und im Code-Kommentar.
import sys
wt = sys.argv[1]

def rep(s, old, new, label):
    n = s.count(old)
    assert n == 1, '%s: %d Treffer' % (label, n)
    return s.replace(old, new)

PS = wt + '/apply_patches.ps1'
raw = open(PS, encoding='ascii', newline='').read()
assert raw.count('\r\n') == raw.count('\n') and raw.count('\r\r') == 0
s = raw.replace('\r\n', '\n')
s = rep(s,
"        # DLL, startet WoW ganz normal. Laut wow_optimize bannt Warmane dafuer.\n",
"        # DLL, startet WoW ganz normal. Laut wow_optimize bannen manche\n"
"        # oeffentlichen Server dafuer.\n", 'Kommentar')
open(PS, 'w', encoding='ascii', newline='').write(s.replace('\n', '\r\n'))

def edit(fn, old, new, label):
    p = wt + '/docs/' + fn
    t = open(p, encoding='utf-8', newline='').read()
    assert '\r' not in t
    open(p, 'w', encoding='utf-8', newline='').write(rep(t, old, new, label))

edit('PATCHES.de.md',
"> erkannt oder blockiert werden: Laut dem Autor von wow_optimize wertet\n"
"> **Warmane** die DLL als verbotene Software – die Folge ist ein **dauerhafter\n"
"> Bann**. Auf **WoW Circle** führt sie zum Disconnect. Nur auf Servern\n"
"> verwenden, die das erlauben.\n",
"> erkannt oder blockiert werden: Laut dem Autor von wow_optimize führt sie auf\n"
"> manchen öffentlichen Servern zu einem **dauerhaften Bann**, auf anderen zum\n"
"> Disconnect. Nur auf Servern verwenden, die das erlauben.\n", 'de Kasten')

edit('PATCHES.en.md',
"> servers: according to the author of wow_optimize, **Warmane** treats the DLL\n"
"> as prohibited software – the result is a **permanent ban**. On **WoW Circle**\n"
"> it gets you disconnected. Only use it on servers that allow it.\n",
"> servers: according to the author of wow_optimize, it leads to a **permanent\n"
"> ban** on some public servers and to a disconnect on others. Only use it on\n"
"> servers that allow it.\n", 'en Kasten')
print('fixwm OK')
