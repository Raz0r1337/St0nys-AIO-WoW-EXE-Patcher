import sys
def ed(p,pairs,crlf=False):
    s=open(p,encoding='utf-8',newline='').read()
    if crlf: s=s.replace('\r\n','\n')
    for o,n in pairs:
        if s.count(o)!=1: sys.exit(p+': '+o)
        s=s.replace(o,n)
    if crlf: s=s.replace('\n','\r\n')
    open(p,'w',encoding='utf-8',newline='').write(s)
WDE="""> [!WARNING]
> Alle drei Patches (Nr. 4, die NPC-Ausblendung und der Slider-Patch) lassen sich
> zusammen einspielen, die `Wow.exe` wird dann aber größer. **Viele Server
> tolerieren eine veränderte Dateigröße der `Wow.exe` nicht – das kann zu einem
> Bann führen.**
"""
WEN="""> [!WARNING]
> All three patches (No. 4, the NPC fade-out and the slider patch) can be applied
> together, but then `Wow.exe` becomes larger. **Many servers do not tolerate a
> changed file size of `Wow.exe` – this can lead to a ban.**
"""
ed('README.md',[
("*(teilt Code-Höhle mit Slider-Patch)*","*(teilt Code-Höhle mit Slider-Patch; zusammen wird die Exe größer – Bann-Gefahr)*"),
("*(Server muss das Flag setzen, teilt Code-Höhle mit Slider-Patch)*","*(Server muss das Flag setzen, teilt Code-Höhle mit Slider-Patch; zusammen wird die Exe größer – Bann-Gefahr)*"),
("> Beim Zurücknehmen fällt das wieder weg.\n","> Beim Zurücknehmen fällt das wieder weg.\n\n"+WDE),
("> Sektionen am Dateiende aus – die `Wow.exe` wird dadurch etwas größer.\n","> Sektionen am Dateiende aus – die `Wow.exe` wird dadurch etwas größer.\n\n"+WDE),
("> (siehe Nr. 4).\n","> (siehe Nr. 4).\n\n"+WDE),
])
ed('README.en.md',[
("*(shares code cave with the slider patch)*","*(shares code cave with the slider patch; together the exe grows – ban risk)*"),
("*(server must set the flag, shares code cave with the slider patch)*","*(server must set the flag, shares code cave with the slider patch; together the exe grows – ban risk)*"),
("> takes this away again.\n","> takes this away again.\n\n"+WEN),
("> of their own at the end of the file – this makes `Wow.exe` slightly larger.\n","> of their own at the end of the file – this makes `Wow.exe` slightly larger.\n\n"+WEN),
("> larger (see No. 4).\n","> larger (see No. 4).\n\n"+WEN),
])
ed('apply_patches.ps1',[
("       NoteDe = 'teilt Code-Hoehle mit Slider-Patch'\n       NoteEn = 'shares code cave with the slider patch'\n",
 "       NoteDe = 'teilt Code-Hoehle mit Slider-Patch; zusammen wird die Exe groesser - Bann-Gefahr'\n       NoteEn = 'shares code cave with the slider patch; together the exe grows - ban risk'\n"),
("       NoteDe = 'Server muss das Flag setzen, teilt Code-Hoehle mit Slider-Patch'\n       NoteEn = 'server must set the flag, shares code cave with the slider patch'\n",
 "       NoteDe = 'Server muss das Flag setzen, teilt Code-Hoehle mit Slider-Patch; zusammen wird die Exe groesser - Bann-Gefahr'\n       NoteEn = 'server must set the flag, shares code cave with the slider patch; together the exe grows - ban risk'\n"),
("        Conflict      = 'nutzt dieselbe Code-Hoehle wie diese Patches und weicht darum auf eine eigene Sektion am Dateiende aus (die Wow.exe wird dadurch etwas groesser):'\n",
 "        Conflict      = 'nutzt dieselbe Code-Hoehle wie diese Patches und weicht darum auf eine eigene Sektion am Dateiende aus (die Wow.exe wird dadurch etwas groesser):'\n        ConflictBan   = 'Zusammen funktionieren sie, aber viele Server tolerieren eine veraenderte Groesse der Wow.exe nicht - das kann zu einem Bann fuehren!'\n"),
("        Conflict      = 'uses the same code cave as these patches and therefore moves to a section of its own at the end of the file (Wow.exe becomes slightly larger):'\n",
 "        Conflict      = 'uses the same code cave as these patches and therefore moves to a section of its own at the end of the file (Wow.exe becomes slightly larger):'\n        ConflictBan   = 'They work together, but many servers do not tolerate a changed size of Wow.exe - this can lead to a ban!'\n"),
("        Say (T 'Conflict') 'Yellow'\n        foreach ($m in $both) { Say \"  - $m\" 'Yellow' }\n",
 "        Say (T 'Conflict') 'Yellow'\n        foreach ($m in $both) { Say \"  - $m\" 'Yellow' }\n        Say (T 'ConflictBan') 'Red'\n"),
],crlf=True)
print('ok')
