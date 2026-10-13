R='/home/user/St0nys-WoW-EXE-Patcher/'
def edit(fn,pairs):
    s=open(R+fn,encoding='utf-8').read()
    for a,b in pairs:
        assert s.count(a)==1,(fn,a[:70],s.count(a)); s=s.replace(a,b)
    open(R+fn,'w',encoding='utf-8').write(s)
edit('README.de.md',[
("""> **Benutzung auf eigene Gefahr.** Die meisten Patches sind im Spiel getestet.
> Solange du keinen Patch wählst, der als **Bann-Gefahr** markiert ist oder die
> `Wow.exe` vergrößert, sollte auch auf öffentlichen Servern nichts passieren –
> eine 100-%-Garantie gibt es aber nicht: Was ein Server erkennt und duldet,
> entscheidet er selbst und ändert es auch mal. Im Zweifel prüfe die
> Richtlinien deines Servers, bevor du eine gepatchte `Wow.exe` dort benutzt.
> Der Patcher zeigt diesen Hinweis auch bei jedem Start an.""",
"""> **Benutzung auf eigene Gefahr.** Patches ohne Warnung sind im Spiel getestet
> und sollten auch auf öffentlichen Servern unbedenklich sein – eine
> 100-%-Garantie gibt es aber nicht: Was ein Server erkennt und duldet,
> entscheidet er selbst und ändert es auch mal. Alle anderen Patches tragen in
> der Übersicht und im Patcher eine einheitliche Warnung (siehe
> [Hinweise](#hinweise)). Im Zweifel prüfe die Richtlinien deines Servers,
> bevor du eine gepatchte `Wow.exe` dort benutzt. Der Patcher zeigt diesen
> Hinweis auch bei jedem Start an."""),
("überflüssige Ergänzungs-Patches, Bann-Gefahr) und Sicherheitsabfrage (J/N).",
 "überflüssige Ergänzungs-Patches, Warnungen) und Sicherheitsabfrage (J/N)."),
("""(Warden komplett abschalten ersetzt den RCE-Fix) und – als rote Zeile – wenn
gewählte Patches zu einem Bann führen können (Anti-Cheat, Eingriff in Warden
oder veränderte Dateigröße, siehe [Hinweise](#hinweise)).""",
"""(Warden komplett abschalten ersetzt den RCE-Fix) und wenn gewählte Patches eine
Warnung tragen – rot bei Bann-Gefahr und vergrößerter `Wow.exe`, gelb bei
Patches, die auf öffentlichen Servern oder im Spiel noch ungetestet sind (siehe
[Hinweise](#hinweise))."""),
("""zusammengestellt von Stormhand, und die Standard-Auswahl. Es enthält nur
Patches ohne Bann-Gefahr, die die `Wow.exe` nicht vergrößern – **das Preset ist
sicher**""","""zusammengestellt von Stormhand, und die Standard-Auswahl. Es enthält nur
Patches ohne Warnung, die die `Wow.exe` nicht vergrößern – **das Preset ist
sicher**"""),
("""- **Bann-Gefahr:** Drei Gruppen von Patches können auf vielen Servern zu einem
  Bann führen. Erstens Patches, die Server mit Anti-Cheat als Cheat oder
  Botting werten können: LUA Unlock (Nr. 23 und 24), Steigwinkel (45),
  Sprunghöhe (46), die Sprungsteuerung (47–49) und der Doppelsprung (50) sowie
  „Aktionstasten gedrückt halten“ (74). Zweitens Patches, die eine Sektion an
  die `Wow.exe` anhängen und die Datei damit größer machen: Nr. 9, 50, 63, 64,
  74 und 79 – viele Server tolerieren eine veränderte Dateigröße nicht.
  Drittens Patches, die in den Anti-Cheat Warden eingreifen: der RCE-Fix
  (Nr. 10) und „Warden komplett abschalten“ (Nr. 11) – öffentliche Server
  können das erkennen. Alle drei Gruppen sind in der Übersicht mit
  „Bann-Gefahr“ markiert, und der Patcher zeigt vor der Sicherheitsabfrage
  eine rote Warnung. Alle anderen Patches ändern die Dateigröße nicht.""",
"""- **Warnungen:** Jeder Patch hat eine einheitliche Einstufung. In der
  [Patch-Übersicht](#patch-übersicht) steht sie hinter dem Namen, im Patcher in
  eckigen Klammern, und vor der Sicherheitsabfrage listet der Patcher die
  gewählten Patches mit Warnung noch einmal auf:
  - **ohne Warnung** – sicher, im Spiel getestet.
  - 🔴 **Bann-Gefahr** – kann auf vielen Servern zu einem Bann führen: Nr. 10,
    11, 23–25, 41, 42, 45–50, 74 und 81–85 (rote Warnung).
  - 🟡 **auf öffentlichen Servern ungetestet** – mögliche Bann-Gefahr, Vorsicht,
    kann zu Kick/Bann führen: Nr. 4, 7–9, 26, 29, 44, 51, 62–64, 68 und 70–73
    sowie 79 (gelber Hinweis).
  - 🟡 **im Spiel ungetestet** – die Funktion ist im Spiel noch nicht geprüft,
    möglicherweise verbuggt: Nr. 4, 7–9, 25, 26, 29, 44, 51, 62–64, 68 und 70
    (gelber Hinweis).
  - **Exe wird größer** – diese Patches hängen eine Sektion an die `Wow.exe` an:
    Nr. 9, 50, 63, 64, 74 und 79. Viele Server tolerieren eine veränderte
    Dateigröße nicht – das kann zu einem Bann führen (rote Warnung). Alle
    anderen Patches ändern die Dateigröße nicht."""),
])
edit('README.md',[
("""> **Use at your own risk.** Most patches have been tested in game. As long as
> you don't select a patch that is marked as a **ban risk** or makes `Wow.exe`
> larger, nothing should happen on public servers either – but there is no
> 100 % guarantee: what a server detects and tolerates is up to the server and
> changes from time to time. If in doubt, check the rules of your server before
> using a patched `Wow.exe` there. The patcher also shows this note on every
> start.""",
"""> **Use at your own risk.** Patches without a warning have been tested in game
> and should be harmless on public servers as well – but there is no 100 %
> guarantee: what a server detects and tolerates is up to the server and
> changes from time to time. All other patches carry a uniform warning in the
> overview and in the patcher (see [Notes](#notes)). If in doubt, check the
> rules of your server before using a patched `Wow.exe` there. The patcher
> also shows this note on every start."""),
("what is removed), notes (missing or redundant companion patches, ban risk)",
 "what is removed), notes (missing or redundant companion patches, warnings)"),
("""completely replaces the RCE fix) and – as a red line – when selected patches
can lead to a ban (anti-cheat, interfering with Warden or changed file size,
see [Notes](#notes)).""",
"""completely replaces the RCE fix) and when selected patches carry a warning –
red for ban risk and a larger `Wow.exe`, yellow for patches that are still
untested on public servers or in game (see [Notes](#notes))."""),
("""together by Stormhand, and the default selection. It contains only patches
without ban risk that do not make `Wow.exe` larger – **the preset is safe**""",
"""together by Stormhand, and the default selection. It contains only patches
without a warning that do not make `Wow.exe` larger – **the preset is safe**"""),
("""- **Ban risk:** three groups of patches can lead to a ban on many servers.
  First, patches that servers with anti-cheat may treat as cheating or
  botting: LUA unlock (No. 23 and 24), climb angle (45), jump height (46), the
  air steering (47–49) and the double jump (50) as well as "Hold action
  buttons to repeat" (74). Second, patches that append a section to `Wow.exe`
  and thus make the file larger: No. 9, 50, 63, 64, 74 and 79 – many servers
  do not tolerate a changed file size. Third, patches that interfere with the
  Warden anti-cheat: the RCE fix (No. 10) and "Disable Warden completely"
  (No. 11) – public servers can detect this. All three groups are marked "ban
  risk" in the overview, and the patcher shows a red warning before the
  confirmation prompt. All other patches do not change the file size.""",
"""- **Warnings:** every patch has a uniform rating. In the
  [patch overview](#patch-overview) it is shown after the name, in the patcher
  in square brackets, and before the confirmation prompt the patcher lists the
  selected patches with a warning once more:
  - **no warning** – safe, tested in game.
  - 🔴 **ban risk** – can lead to a ban on many servers: No. 10, 11, 23–25,
    41, 42, 45–50, 74 and 81–85 (red warning).
  - 🟡 **untested on public servers** – possible ban risk, careful, may get
    you kicked or banned: No. 4, 7–9, 26, 29, 44, 51, 62–64, 68 and 70–73 as
    well as 79 (yellow note).
  - 🟡 **untested in game** – the function has not been checked in game yet,
    possibly buggy: No. 4, 7–9, 25, 26, 29, 44, 51, 62–64, 68 and 70 (yellow
    note).
  - **exe grows** – these patches append a section to `Wow.exe`: No. 9, 50,
    63, 64, 74 and 79. Many servers do not tolerate a changed file size – this
    can lead to a ban (red warning). All other patches do not change the file
    size."""),
])
