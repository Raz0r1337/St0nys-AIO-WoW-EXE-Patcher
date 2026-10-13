import os
os.chdir('/home/user/St0nys-WoW-EXE-Patcher')
def edit(p,pairs):
    s=open(p,encoding='utf-8').read()
    for a,b in pairs:
        assert s.count(a)==1,(p,a,s.count(a)); s=s.replace(a,b)
    open(p,'w',encoding='utf-8',newline='\n').write(s)
# after git mv: README.md = English (was README.en.md), README.de.md = German (was README.md)
edit('README.md',[('[🇩🇪 Deutsch](README.md) | 🇬🇧 English','[🇩🇪 Deutsch](README.de.md) | 🇬🇧 English'),
                  ('| `README.md`         | German documentation |\n| `README.en.md`      | This file |','| `README.md`         | This file |\n| `README.de.md`      | German documentation |')])
edit('README.de.md',[('🇩🇪 Deutsch | [🇬🇧 English](README.en.md)','🇩🇪 Deutsch | [🇬🇧 English](README.md)'),
                     ('| `README.md`         | Diese Datei |\n| `README.en.md`      | Englische Anleitung |','| `README.md`         | Englische Anleitung |\n| `README.de.md`      | Diese Datei |')])
edit('PATCHES.en.md',[('[St0nys-AIO-WoW-EXE-Patcher](README.en.md)','[St0nys-AIO-WoW-EXE-Patcher](README.md)'),('[README](README.en.md#patch-overview)','[README](README.md#patch-overview)')])
edit('PATCHES.md',[('[St0nys-AIO-WoW-EXE-Patcher](README.md)','[St0nys-AIO-WoW-EXE-Patcher](README.de.md)'),('[README](README.md#patch-übersicht)','[README](README.de.md#patch-übersicht)')])
print('ok')
