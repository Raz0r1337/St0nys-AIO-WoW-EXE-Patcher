import re, json
SP='/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/'
old=json.load(open(SP+'old_order2.json'))
ps=open('apply_patches.ps1').read()
E=re.findall(r"@\{ Id = '(\w+)'; Cat = '(\w+)'; On = \$(true|false)[^\n]*\n(?:\s+Author = '([^']*)'\s*\n)?",ps)
ids=[e[0] for e in E]; cat={e[0]:e[1] for e in E}; on={e[0]:e[2]=='true' for e in E}; auth={e[0]:e[3] for e in E}
N={i:n+1 for n,i in enumerate(ids)}; O={n+1:i for n,i in enumerate(old)}
assert len(ids)==57
C={'README.md':dict(w='Nr.',off='standardmäßig aus',au='Autor',head='| Nr. | Patch | Autor | Standard |',
  cats={'system':'System & Leistung','security':'Sicherheit & Datenschutz','login':'Login & Verbindung','modding':'Modding: Interface, MPQs & Addons',
        'gameplay':'Gameplay-Fixes','graphics':'Grafik & Sichtweite','ui':'Interface & Komfort','window':'Fenster, Maus & Kamera','sound':'Sound',
        'client':'Client-Infos: Version, Build, Titel, Datum'},
  names={'follow':'/follow auch bei NPCs erlauben','clientversion':'Client-Version ändern (Original 3.3.5) *(fragt den Wert ab)*',
         'clientbuild':'Build-Nummer ändern (Original 12340) *(fragt den Wert ab)*','clienttitle':'Programmtitel in den Dateieigenschaften ändern *(fragt den Wert ab)*',
         'clientdate':'Build-Datum ändern (Original Jun 24 2010) *(fragt den Wert ab)*'},
  follow_after='**Chat-Befehle auch im Tod erlauben**',
  follow="""**/follow auch bei NPCs erlauben** [[P:follow]]
Mit `/follow` lässt sich auch NPCs folgen, nicht nur Spielern. Portierung von
MacWarriors `patch-007-allow_follow.bat`: Das Original leitet die Prüfung in
eine Code-Höhle um, die ihr Ergebnis ignoriert. Diese Höhle läge aber genau
dort, wo der Slider-Patch (Nr. [[sliders]]) seinen Code ablegt. Hier wird
stattdessen der bedingte Sprung hinter der Prüfung unbedingt gemacht – ein
einziges Byte, gleiche Wirkung, und beide Patches vertragen sich.""",
  section="""### Client-Infos: Version, Build, Titel, Datum

Diese vier Patches von MacWarrior (portiert aus seinen Python-Scripten
`edit_version.py`, `edit_revision.py`, `edit_title.py` und `edit_date.py`)
ändern, wie sich der Client ausweist. Sind sie ausgewählt, **fragt der Patcher
nach der Auswahl die gewünschten Werte ab**. In eckigen Klammern steht ein
Vorschlag, ENTER übernimmt ihn. Ungültige Eingaben werden mit einer Meldung neu
abgefragt, und alle Werte werden geprüft, bevor irgendetwas geschrieben wird.
Die Werte merkt sich der Patcher in `patcher_selection.ini` (`value.<Id>=…`);
mit `-Unattended` werden die gemerkten Werte bzw. die Originalwerte genommen.

> [!NOTE]
> Server können die Client-Version bzw. Build-Nummer prüfen. Ein geänderter Wert
> muss also zum Server passen.

**Client-Version ändern** [[P:clientversion]]
Setzt eine neue Version im Format `x.y.z` (z. B. `3.3.6` oder `3.3.123`, höchstens
7 Zeichen). Geändert werden die Version, die der Client im Spiel anzeigt, die
FileVersion und die ProductVersion (`Version x.y`) der Versionsressource sowie
`VS_FIXEDFILEINFO`. Die Build-Nummer bleibt erhalten. Haupt- und Nebenversion
müssen zusammen in das ProductVersion-Feld passen (z. B. `3.3`).

**Build-Nummer ändern** [[P:clientbuild]]
Setzt eine neue Build-Nummer (0 bis 65535, Original `12340`): die interne
Build-Nummer, die sichtbare Build-Nummer und den vierten Teil der FileVersion.

**Programmtitel in den Dateieigenschaften ändern** [[P:clienttitle]]
Setzt FileDescription, InternalName und ProductName der Versionsressource, also
das, was Windows z. B. in den Dateieigenschaften und im Task-Manager anzeigt.
Höchstens 17 Zeichen, nur ASCII.

**Build-Datum ändern** [[P:clientdate]]
Setzt das Build-Datum (Original `Jun 24 2010`) an allen drei Stellen in der EXE
und das Jahr im Copyright-Vermerk. Eingabe als `JJJJ-MM-TT`, optional mit `FR`
dahinter für französische Monatsnamen (z. B. `2026-09-28 FR` → `Sep 28 2026`)."""),
 'README.en.md':dict(w='No.',off='off by default',au='Author',head='| No. | Patch | Author | Default |',
  cats={'system':'System & performance','security':'Security & privacy','login':'Login & connection','modding':'Modding: interface, MPQs & addons',
        'gameplay':'Gameplay fixes','graphics':'Graphics & view distance','ui':'Interface & comfort','window':'Window, mouse & camera','sound':'Sound',
        'client':'Client info: version, build, title, date'},
  names={'follow':'Allow /follow on NPCs','clientversion':'Change client version (original 3.3.5) *(asks for the value)*',
         'clientbuild':'Change build number (original 12340) *(asks for the value)*','clienttitle':'Change program title in the file properties *(asks for the value)*',
         'clientdate':'Change build date (original Jun 24 2010) *(asks for the value)*'},
  follow_after='**Allow chat commands while dead**',
  follow="""**Allow /follow on NPCs** [[P:follow]]
`/follow` also works on NPCs, not just players. Port of MacWarrior's
`patch-007-allow_follow.bat`: the original redirects the check into a code cave
that ignores its result. That cave, however, sits exactly where the slider
patch (No. [[sliders]]) puts its code. Here the conditional jump after the check
is made unconditional instead – a single byte, same effect, and both patches
work together.""",
  section="""### Client info: version, build, title, date

These four patches by MacWarrior (ported from his Python scripts
`edit_version.py`, `edit_revision.py`, `edit_title.py` and `edit_date.py`)
change how the client identifies itself. When selected, **the patcher asks for
the desired values after the selection**. A suggestion is shown in square
brackets, ENTER accepts it. Invalid input is asked again with a message, and all
values are checked before anything is written. The patcher remembers the values
in `patcher_selection.ini` (`value.<Id>=…`); with `-Unattended` the remembered
values or the original values are used.

> [!NOTE]
> Servers may check the client version or build number, so a changed value has
> to match the server.

**Change client version** [[P:clientversion]]
Sets a new version in the format `x.y.z` (e.g. `3.3.6` or `3.3.123`, at most 7
characters). Changes the version the client shows in-game, the FileVersion and
ProductVersion (`Version x.y`) of the version resource and `VS_FIXEDFILEINFO`.
The build number is kept. Major and minor version together must fit into the
ProductVersion field (e.g. `3.3`).

**Change build number** [[P:clientbuild]]
Sets a new build number (0 to 65535, original `12340`): the internal build
number, the visible build number and the fourth part of the FileVersion.

**Change program title in the file properties** [[P:clienttitle]]
Sets FileDescription, InternalName and ProductName of the version resource,
i.e. what Windows shows in the file properties and the Task Manager. At most 17
characters, ASCII only.

**Change build date** [[P:clientdate]]
Sets the build date (original `Jun 24 2010`) at all three places in the EXE and
the year in the copyright notice. Input as `YYYY-MM-DD`, optionally followed by
`FR` for French month names (e.g. `2026-09-28 FR` → `Sep 28 2026`).""")}
for p,c in C.items():
    s=open(p).read(); w=re.escape(c['w'])
    s=re.sub(r'(%s )(\d+)'%w, lambda m: m.group(1)+str(N[O[int(m.group(2))]]), s)
    lines=s.split('\n'); i=lines.index(c['head']); j=i+2; rows={}
    while lines[j].startswith('|'):
        m=re.match(r'^\| (\d+)\s*\| (.*) \| (.*?) \| (✅|–) \|$',lines[j])
        if m: rows[O[int(m.group(1))]]=m.group(2)
        j+=1
    assert len(rows)==52,len(rows)
    rows.update(c['names'])
    out=[]; last=None
    for x in ids:
        if cat[x]!=last:
            last=cat[x]; out.append('|    | **%s** |  |  |'%c['cats'][last])
        out.append('| %-2d | %s | %s | %s |'%(N[x],rows[x],auth[x],'✅' if on[x] else '–'))
    lines[i+2:j]=out; s='\n'.join(lines)
    k=s.index(c['follow_after']); k=s.index('\n\n',k)+2
    s=s[:k]+c['follow']+'\n\n'+s[k:]
    a=s.index('\n---\n', s.index('\n### Sound\n'))
    s=s[:a]+'\n\n'+c['section']+'\n'+s[a:]
    def P(m):
        x=m.group(1); parts=['%s %d'%(c['w'],N[x])]
        if not on[x]: parts.append(c['off'])
        if auth[x]: parts.append('%s: %s'%(c['au'],auth[x]))
        return '*(%s)*'%', '.join(parts)
    s=re.sub(r'\[\[P:(\w+)\]\]',P,s); s=re.sub(r'\[\[(\w+)\]\]',lambda m:str(N[m.group(1)]),s)
    open(p,'w').write(s)
print('ok')
