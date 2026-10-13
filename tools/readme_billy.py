import re
ps=open('apply_patches.ps1').read()
E=re.findall(r"@\{ Id = '(\w+)'; Cat = '\w+'; On = \$(true|false)[^\n]*\n(?:\s+Author = '([^']*)'\s*\n)?",ps)
ids=[e[0] for e in E]; on={e[0]:e[1]=='true' for e in E}; auth={e[0]:e[2] for e in E}; N={i:n+1 for n,i in enumerate(ids)}
OAL='https://github.com/kcat/openal-soft'
C={'README.md':dict(w='Nr.',off='standardmäßig aus',au='Autor',edits=[
("""Vorausgewählt ist die empfohlene
Standard-Auswahl (Spalte „Standard“ in der Übersicht).""","""Vorausgewählt ist die Standard-Auswahl,
das **Preset „Billy's_Wow.exe“** (Spalte „Standard“ in der Übersicht)."""),
("| `S` (oder `D`)     | zurück zur Standard-Auswahl                 |","| `B`                | Preset „Billy's_Wow.exe“ laden (= Standard) |"),
("""- **Zurücksetzen:** im Menü `S` drücken oder `patcher_selection.ini` löschen –
  dann gilt wieder die Standard-Auswahl.""","""- **Zurücksetzen:** im Menü `B` drücken oder `patcher_selection.ini` löschen –
  dann gilt wieder das Preset „Billy's_Wow.exe“."""),
("""Die Standard-Auswahl ist in `apply_patches.ps1` festgelegt: Jeder Patch hat dort
einen Eintrag `On = $true` (vorausgewählt) bzw. `On = $false` (abgewählt).""","""Das Preset „Billy's_Wow.exe“ ist das Patch-Set von Billy Hoyle und zugleich die
Standard-Auswahl. Es ist in `apply_patches.ps1` festgelegt: Jeder Patch hat dort
einen Eintrag `On = $true` (im Preset) bzw. `On = $false` (nicht im Preset)."""),
("`saved` (gespeicherte Auswahl), `default`, `all`","`saved` (gespeicherte Auswahl), `billy` (Preset „Billy's_Wow.exe“, auch `default`), `all`"),
("ohne `-Select` die gespeicherte bzw. die Standard-Auswahl.","ohne `-Select` die gespeicherte Auswahl bzw. das Preset „Billy's_Wow.exe“."),
("""- `Sound_EnableHardware` aktiviert (Hardware-Audiobeschleunigung)
""",f"""- `Sound_EnableHardware` aktiviert (Hardware-Audiobeschleunigung)

> [!IMPORTANT]
> Damit diese Einstellungen überhaupt greifen, wird **OpenAL** benötigt, z. B.
> [OpenAL Soft]({OAL}).
"""),
("| Sound-Einstellungen optimieren |",f"| Sound-Einstellungen optimieren *(benötigt [OpenAL]({OAL}))* |"),
("""> [!IMPORTANT]
> Dieses Repository enthält **keine** `Wow.exe`""","""> [!TIP]
> **Danke an Billy Hoyle und MacWarrior!** – siehe [Danksagung](#danksagung).

> [!IMPORTANT]
> Dieses Repository enthält **keine** `Wow.exe`"""),
("- [Hinweise](#hinweise)\n","- [Hinweise](#hinweise)\n- [Danksagung](#danksagung)\n"),
("## Lizenz\n","""## Danksagung

Ein ganz besonderer Dank geht an **Billy Hoyle** – für seine viele Hilfe und
seine Tipps in den letzten Monaten und für die Hilfe beim Zusammentragen der
Patches. Sein Patch-Set steckt als Preset „Billy's_Wow.exe“ in diesem Patcher
und ist die Standard-Auswahl.

Beim Zusammentragen der Patches hat auch **MacWarrior** geholfen – vielen Dank
auch dafür!

Und natürlich danke an alle Autoren der Patches, die in der
[Patch-Übersicht](#patch-übersicht) genannt sind.

## Lizenz
""")]),
'README.en.md':dict(w='No.',off='off by default',au='Author',edits=[
("""The recommended default selection is
preselected (see the "Default" column in the overview).""","""The default selection is preselected:
the **preset "Billy's_Wow.exe"** (see the "Default" column in the overview)."""),
("| `D` (or `S`)       | back to the default selection              |","| `B`                | load preset \"Billy's_Wow.exe\" (= default)  |"),
("""- **Reset:** press `D` in the menu or delete `patcher_selection.ini` – then
  the default selection applies again.""","""- **Reset:** press `B` in the menu or delete `patcher_selection.ini` – then
  the preset "Billy's_Wow.exe" applies again."""),
("""The default selection is defined in `apply_patches.ps1`: every patch has an
entry `On = $true` (preselected) or `On = $false` (deselected).""","""The preset "Billy's_Wow.exe" is Billy Hoyle's patch set and also the default
selection. It is defined in `apply_patches.ps1`: every patch has an entry
`On = $true` (in the preset) or `On = $false` (not in the preset)."""),
("`saved` (saved selection), `default`, `all`","`saved` (saved selection), `billy` (preset \"Billy's_Wow.exe\", also `default`), `all`"),
("without `-Select` the saved or default selection.","without `-Select` the saved selection or the preset \"Billy's_Wow.exe\"."),
("""- `Sound_EnableHardware` enabled (hardware audio acceleration)
""",f"""- `Sound_EnableHardware` enabled (hardware audio acceleration)

> [!IMPORTANT]
> **OpenAL** is required for these settings to take effect at all, e.g.
> [OpenAL Soft]({OAL}).
"""),
("| Optimize sound settings |",f"| Optimize sound settings *(requires [OpenAL]({OAL}))* |"),
("""> [!IMPORTANT]
> This repository does **not** contain""","""> [!TIP]
> **Thanks to Billy Hoyle and MacWarrior!** – see [Acknowledgements](#acknowledgements).

> [!IMPORTANT]
> This repository does **not** contain"""),
("- [Notes](#notes)\n","- [Notes](#notes)\n- [Acknowledgements](#acknowledgements)\n"),
("## License\n","""## Acknowledgements

A very special thank you goes to **Billy Hoyle** – for all his help and tips
over the past months and for helping to collect the patches. His patch set is
included as the preset "Billy's_Wow.exe" and is the default selection.

**MacWarrior** also helped collecting the patches – thank you as well!

And of course thanks to all patch authors named in the
[patch overview](#patch-overview).

## License
""")])}
for p,c in C.items():
    s=open(p).read(); w=re.escape(c['w'])
    for o,n in c['edits']:
        assert s.count(o)==1,(p,o[:60]); s=s.replace(o,n)
    # Tabelle: Standard + Autor aus dem Script
    def row(m):
        n=int(m.group(1)); i=ids[n-1]
        return '| %-2d | %s | %s | %s |'%(n,m.group(2),auth[i],'✅' if on[i] else '–')
    s,k=re.subn(r'^\| (\d+)\s*\| (.*) \| (.*?) \| (?:✅|–) \|$',lambda m: row(m) if '|' not in m.group(2) else m.group(0),s,flags=re.M)
    # Beschreibungs-Klammern neu
    def head(m):
        n=int(m.group(1)); i=ids[n-1]; parts=['%s %d'%(c['w'],n)]
        if not on[i]: parts.append(c['off'])
        if auth[i]: parts.append('%s: %s'%(c['au'],auth[i]))
        return '*(%s)*'%', '.join(parts)
    s,h=re.subn(r'(?<=\*\* )\*\(%s (\d+)(?:, [^)]*)?\)\*'%w,head,s)
    assert h==51,(p,h)
    open(p,'w').write(s)
print('ok')
