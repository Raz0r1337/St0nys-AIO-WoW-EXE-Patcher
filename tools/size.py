import sys
def ed(p,pairs,crlf=False):
    s=open(p,encoding='utf-8',newline='').read()
    if crlf: s=s.replace('\r\n','\n')
    for o,n in pairs:
        if s.count(o)!=1: sys.exit(p+': '+o)
        s=s.replace(o,n)
    if crlf: s=s.replace('\n','\r\n')
    open(p,'w',encoding='utf-8',newline='').write(s)
ed('README.md',[
("> der Patcher weist vor der Sicherheitsabfrage darauf hin.\n",
 "> der Patcher weist vor der Sicherheitsabfrage darauf hin. Die `Wow.exe` wird\n> dadurch etwas größer: Jede ausgelagerte Höhle bekommt eine 512-Byte-Sektion,\n> dazu kommt das Auffüllen des Dateiendes – mit Nr. 4 und 48 zusammen rund 1,4 KB.\n> Beim Zurücknehmen fällt das wieder weg.\n"),
("> `.nofade` am Dateiende aus.\n","> `.nofade` am Dateiende aus. Auch hier wird die `Wow.exe` dadurch etwas größer\n> (siehe Nr. 4).\n"),
("> Sektionen am Dateiende aus.\n","> Sektionen am Dateiende aus – die `Wow.exe` wird dadurch etwas größer.\n"),
])
ed('README.en.md',[
("> patcher points this out before the confirmation prompt.\n",
 "> patcher points this out before the confirmation prompt. This makes `Wow.exe`\n> slightly larger: each moved cave gets a 512-byte section, plus padding of the\n> end of the file – about 1.4 KB for No. 4 and 48 together. Removing the patches\n> takes this away again.\n"),
("> `.nofade` of its own at the end of the file.\n","> `.nofade` of its own at the end of the file. Here too `Wow.exe` becomes slightly\n> larger (see No. 4).\n"),
("> of their own at the end of the file.\n","> of their own at the end of the file – this makes `Wow.exe` slightly larger.\n"),
])
ed('apply_patches.ps1',[
("weicht darum auf eine eigene Sektion am Dateiende aus:'","weicht darum auf eine eigene Sektion am Dateiende aus (die Wow.exe wird dadurch etwas groesser):'"),
("therefore moves to a section of its own at the end of the file:'","therefore moves to a section of its own at the end of the file (Wow.exe becomes slightly larger):'"),
],crlf=True)
print('ok')
