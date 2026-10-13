import sys
d=sys.argv[1]
REL='https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher/releases/latest'
ISS='https://github.com/Raz0r1337/St0nys-AIO-WoW-EXE-Patcher/issues'
def edit(fn,pairs,crlf=False):
    p=d+'/'+fn; raw=open(p,'rb').read()
    assert (b'\r\n' in raw)==crlf,fn
    t=raw.decode('utf-8')
    if crlf: t=t.replace('\r\n','\n')
    for a,b in pairs:
        assert t.count(a)==1,(fn,a[:70],t.count(a)); t=t.replace(a,b)
    if crlf: t=t.replace('\n','\r\n')
    open(p,'wb').write(t.encode('utf-8')); print(fn,'ok')
edit('docs/README.md',[("""If you still run into problems, please let me know via an
[issue](%s).
""" % ISS,"""If you still run into problems, please let me know via an
[issue](%s/new/choose).
If you have a patch that should be part of this patcher, you can send it to me
via an issue as well.
""" % ISS)])
edit('docs/README.de.md',[("""Solltest du trotzdem auf Probleme stoßen, melde dich bitte über ein
[Issue](%s).
""" % ISS,"""Solltest du trotzdem auf Probleme stoßen, melde dich bitte über ein
[Issue](%s/new/choose).
Hast du einen Patch, der hier mit rein sollte, kannst du ihn mir ebenfalls über
ein Issue schicken.
""" % ISS)])
