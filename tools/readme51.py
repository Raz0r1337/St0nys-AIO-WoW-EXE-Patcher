import re, json
S='/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/'
old=json.load(open(S+'old_order.json'))
ps=open('apply_patches.ps1').read()
E=re.findall(r"@\{ Id = '(\w+)'; On = \$(true|false)[^\n]*\n(?:\s+Author = '([^']*)'\s*\n)?",ps)
new=[e[0] for e in E]; on={e[0]:e[1]=='true' for e in E}; auth={e[0]:e[2] for e in E}
assert len(new)==51
N={i:n+1 for n,i in enumerate(new)}
oldnum2id={n+1:i for n,i in enumerate(old)}
AFTER_AUTH=['mpqsig','scandll','farclip','level101','itemcache','areatrigger','forcereaction','horizon']

L={}
L['README.md']=dict(word='Nr.',head='| Nr. | Patch | Autor | Standard |',autor='Autor',off='standardmäßig aus',
 names={'wardenoff':'Warden komplett abschalten (RCE-Fix) *(Kick-Gefahr bei aktivem Warden)*','noserverpatch':'Client-Patches vom Server verbieten',
  'nosurvey':'Hardware-Umfragen vom Server verbieten','nohttp':'HTTP-Anfragen an Battle.net deaktivieren','skipbnet':'Battle.net-Login überspringen',
  'skiprdp':'Remote-Desktop-Prüfung überspringen','localdata':'Daten direkt aus dem Data-Ordner laden (ohne MPQ)',
  'luaunlock':'LUA Unlock (geschützte Funktionen freigeben) *(kann als Botting gewertet werden)*','mail':'Neue Post ohne 60 Sekunden Wartezeit',
  'deadchat':'Chat-Befehle auch im Tod erlauben','raceclass':'Unbegrenzte Rasse/Klasse-Kombinationen *(Server muss es unterstützen)*',
  'notransparency':'Keine Transparenz beim Heranzoomen','windowfix':'Kein schwarzer Bildschirm beim Wechsel in den Fenstermodus'},
 edits=[("""FocusWindow: Holt das WoW-Fenster aktiv in den Vordergrund. Beide Funktionen
können per Addon angesprochen werden.
""","""Die Funktion kann per Addon angesprochen werden.
"""),("**FlashWindow und FocusWindow Patch**","**FlashWindow Patch**"),
 ("""relevantes Ereignis eintritt und das Spiel im Hintergrund läuft.
""","""relevantes Ereignis eintritt und das Spiel im Hintergrund läuft.
"""),
 ("""Barbierstuhl funktioniert für alle Charaktere ab Level 101.
""","""Barbierstuhl funktioniert für alle Charaktere ab Level 101.
**Benötigt** den Patch „Custom Glue-XML erlauben“ (Nr. [[glue]]). In der Quelle
heißt er „Disable XML SIG MD5“, daher der dortige Hinweis „Use XML MD5“.
"""),
 ("""Schließt eine Sicherheitslücke, die Remote-Code-Ausführung über manipulierte
Pakete ermöglichen konnte.
""","""Schließt eine Sicherheitslücke, die Remote-Code-Ausführung über manipulierte
Pakete ermöglichen konnte: Die Sektion `.zdata` verliert ihr Ausführungsrecht,
und Warden-Module werden nicht mehr aus dem lokalen Cache geladen. Warden selbst
läuft weiter, auf Servern mit aktivem Warden gibt es also keine Probleme.
""")],
 inserts=[("**Remote Code Execution Exploit Fix**",[
"""**Warden komplett abschalten (RCE-Fix)** [[P:wardenoff]]
Der Client verwirft alle Warden-Pakete des Servers (`SMSG_WARDEN_DATA`).
Warden-Module sind Code, den der Server im Client ausführen lässt – mit diesem
Patch ist das überhaupt nicht mehr möglich, auch nicht über künftige Tricks.
Macht den RCE-Fix (Nr. [[rce]]) überflüssig; beide zusammen schaden aber nicht,
der Patcher weist dann nur darauf hin.""",
"""> [!WARNING]
> Der Client antwortet danach nicht mehr auf Warden. Server mit aktivem Warden
> (z. B. AzerothCore oder TrinityCore in der Standardeinstellung) können dich
> deshalb kicken.""",
"""**Client-Patches vom Server verbieten** [[P:noserverpatch]]
Der Server kann dem Client keine Patch-Dateien mehr schicken und installieren
lassen.""",
"""**Hardware-Umfragen vom Server verbieten** [[P:nosurvey]]
Der Server kann keine Hardware-Umfrage (Informationen über deinen PC) mehr beim
Client anfordern."""],
 "### Login & Verbindung",[
"""**Battle.net-Login überspringen** [[P:skipbnet]]
Der Client überspringt den Battle.net-Login-Schritt und nutzt direkt den
klassischen Login.""",
"""**Remote-Desktop-Prüfung überspringen** [[P:skiprdp]]
Der Client prüft nicht mehr, ob er über eine Remote-Desktop-Verbindung läuft –
WoW lässt sich damit z. B. per RDP spielen.""",
"""**HTTP-Anfragen an Battle.net deaktivieren** [[P:nohttp]]
Der Client ruft keine News, Hilfe-Artikel und Nutzungsbedingungen mehr von
Blizzards Servern ab – die gibt es für 3.3.5 ohnehin nicht mehr."""]),
 ("**Custom Glue-XML erlauben**",[
"""**LUA Unlock (geschützte Funktionen freigeben)** [[P:luaunlock]]
Addons und Makros dürfen geschützte Funktionen aufrufen, z. B.
`CastSpellByName`, `CastSpellByID`, `TargetUnit`, `FocusUnit`, `InteractUnit`,
Bewegungsfunktionen oder `ReloadUI`. `AttackTarget` meldet weiterhin einen
Fehler.""",
"""> [!WARNING]
> Das ermöglicht Automatisierung. Server mit Anti-Cheat können das als Botting
> werten."""],None,None),
 ("**Force-Reaction bleibt bei /reload erhalten**",[
"""**Neue Post ohne 60 Sekunden Wartezeit** [[P:mail]]
Der Client fragt neue Post sofort ab – kein Warten mehr von 60 Sekunden und kein
Relog, um neue Post zu bekommen.""",
"""**Chat-Befehle auch im Tod erlauben** [[P:deadchat]]
Slash-Befehle funktionieren auch, während der Charakter tot ist.""",
"""**Unbegrenzte Rasse/Klasse-Kombinationen** [[P:raceclass]]
Die Charaktererstellung lässt jede Rasse mit jeder Klasse zu. Der Server muss
das ebenfalls unterstützen."""],None,None),
 ("**Erweiterte MPQ-Namen erlauben**",[
"""**Daten direkt aus dem Data-Ordner laden (ohne MPQ)** [[P:localdata]]
Der Client liest Dateien direkt aus dem Data-Ordner, ohne dass sie in ein MPQ
gepackt werden müssen – z. B. `Data\\DBFilesClient\\ItemDisplayInfo.dbc`.
Praktisch für Modder."""],None,None),
 ("**Blauer Mond am Nachthimmel reaktiviert**",[
"""**Keine Transparenz beim Heranzoomen** [[P:notransparency]]
Der eigene Charakter wird nicht mehr durchsichtig, wenn die Kamera nah
herangezoomt wird."""],None,None),
 ("**Fenstermodus maximiert als Standard setzen**",[
"""**Kein schwarzer Bildschirm beim Wechsel in den Fenstermodus** [[P:windowfix]]
Wer im laufenden Spiel in den Fenstermodus wechselt, bekommt danach keinen
schwarzen Bildschirm mehr."""],None,None)])

L['README.en.md']=dict(word='No.',head='| No. | Patch | Author | Default |',autor='Author',off='off by default',
 names={'wardenoff':'Disable Warden completely (RCE fix) *(may get you kicked if Warden is active)*','noserverpatch':'Disallow client patches from the server',
  'nosurvey':'Disallow hardware surveys from the server','nohttp':'Disable HTTP requests to Battle.net','skipbnet':'Skip Battle.net login',
  'skiprdp':'Skip Remote Desktop check','localdata':'Load data directly from the Data folder (no MPQ)',
  'luaunlock':'LUA unlock (allow protected functions) *(may be treated as botting)*','mail':'New mail without the 60-second wait',
  'deadchat':'Allow chat commands while dead','raceclass':'Unlimited race/class combinations *(server must support it)*',
  'notransparency':'No character transparency when zooming in','windowfix':'No black screen when switching to windowed mode'},
 edits=[("""occurs while the game is in the background. FocusWindow: actively brings the
WoW window to the foreground. Both functions can be called from addons.
""","""occurs while the game is in the background. The function can be called from
addons.
"""),("**FlashWindow and FocusWindow patch**","**FlashWindow patch**"),
 ("""barber chair works for all characters at level 101 and above.
""","""barber chair works for all characters at level 101 and above.
**Requires** the patch "Allow custom GlueXML" (No. [[glue]]). In the source it is
called "Disable XML SIG MD5", hence the note "Use XML MD5" there.
"""),
 ("""Closes a vulnerability that could allow remote code execution through crafted
packets.
""","""Closes a vulnerability that could allow remote code execution through crafted
packets: the `.zdata` section loses its execute permission and Warden modules
are no longer loaded from the local cache. Warden itself keeps working, so
servers with active Warden are not a problem.
""")],
 inserts=[("**Remote code execution exploit fix**",[
"""**Disable Warden completely (RCE fix)** [[P:wardenoff]]
The client drops all Warden packets from the server (`SMSG_WARDEN_DATA`).
Warden modules are code the server has the client execute – with this patch
that is no longer possible at all, including future tricks. Makes the RCE fix
(No. [[rce]]) unnecessary; both together do no harm, the patcher just points it
out.""",
"""> [!WARNING]
> The client no longer answers Warden. Servers with active Warden (e.g.
> AzerothCore or TrinityCore with default settings) may therefore kick you.""",
"""**Disallow client patches from the server** [[P:noserverpatch]]
The server can no longer send patch files to the client and have them
installed.""",
"""**Disallow hardware surveys from the server** [[P:nosurvey]]
The server can no longer request a hardware survey (information about your PC)
from the client."""],
 "### Login & connection",[
"""**Skip Battle.net login** [[P:skipbnet]]
The client skips the Battle.net login step and goes straight to the classic
login.""",
"""**Skip Remote Desktop check** [[P:skiprdp]]
The client no longer checks whether it runs over a Remote Desktop connection –
so WoW can be played via RDP, for example.""",
"""**Disable HTTP requests to Battle.net** [[P:nohttp]]
The client no longer fetches news, help articles and terms of use from
Blizzard's servers – they no longer exist for 3.3.5 anyway."""]),
 ("**Allow custom GlueXML**",[
"""**LUA unlock (allow protected functions)** [[P:luaunlock]]
Addons and macros may call protected functions, e.g. `CastSpellByName`,
`CastSpellByID`, `TargetUnit`, `FocusUnit`, `InteractUnit`, movement functions
or `ReloadUI`. `AttackTarget` still prints an error.""",
"""> [!WARNING]
> This enables automation. Servers with anti-cheat may treat it as botting."""],None,None),
 ("**Keep force reaction on /reload**",[
"""**New mail without the 60-second wait** [[P:mail]]
The client checks for new mail immediately – no more 60-second wait and no
relog needed to receive new mail.""",
"""**Allow chat commands while dead** [[P:deadchat]]
Slash commands also work while the character is dead.""",
"""**Unlimited race/class combinations** [[P:raceclass]]
Character creation allows every race with every class. The server has to
support this as well."""],None,None),
 ("**Allow extended MPQ names**",[
"""**Load data directly from the Data folder (no MPQ)** [[P:localdata]]
The client reads files directly from the Data folder without packing them into
an MPQ – e.g. `Data\\DBFilesClient\\ItemDisplayInfo.dbc`. Handy for modders."""],None,None),
 ("**Re-enable the blue moon in the night sky**",[
"""**No character transparency when zooming in** [[P:notransparency]]
Your own character no longer becomes transparent when the camera is zoomed in
close."""],None,None),
 ("**Maximized window by default**",[
"""**No black screen when switching to windowed mode** [[P:windowfix]]
Switching to windowed mode while in-game no longer results in a black
screen."""],None,None)])

for p,c in L.items():
    s=open(p).read()
    w=re.escape(c['word'])
    # 1) renumber old -> new
    s=re.sub(r'(%s )(\d+)'%w, lambda m: m.group(1)+str(N[oldnum2id[int(m.group(2))]]), s)
    # 2) table
    lines=s.split('\n'); i=lines.index(c['head']); j=i+2; rows={}
    while lines[j].startswith('|'):
        m=re.match(r'^\| (\d+)\s*\| (.*) \| (.*?) \| (✅|–) \|$',lines[j]); assert m, lines[j]
        rows[old[int(m.group(1))-1]]=m.group(2); j+=1
    assert len(rows)==38
    rows.update(c['names'])
    lines[i+2:j]=['| %-2d | %s | %s | %s |'%(n+1,rows[x],auth[x],'✅' if on[x] else '–') for n,x in enumerate(new)]
    s='\n'.join(lines)
    # 3) authors for existing descriptions
    for x in AFTER_AUTH:
        pat=re.compile(r'\*\(%s %d(, [^)]*?)?\)\*'%(w,N[x]))
        ms=pat.findall(s); assert len(ms)==1,(p,x,ms)
        s=pat.sub(lambda m:'*(%s %d%s, %s: %s)*'%(c['word'],N[x],m.group(1) or '',c['autor'],auth[x]),s)
    # 4) edits
    for o,n_ in c['edits']:
        assert s.count(o)==1,(p,o[:50]); s=s.replace(o,n_)
    # 5) inserts
    for ins in c['inserts']:
        anchor,paras,sec,secparas=ins
        k=s.index(anchor); k=s.index('\n\n',k)+2
        # skip following warning blocks belonging to anchor? insert right after anchor paragraph
        s=s[:k]+'\n\n'.join(paras)+'\n\n'+s[k:]
        if sec:
            # new section right before the next '### ' after the inserted block
            k2=s.index('\n### ',k)+1
            s=s[:k2]+sec+'\n\n'+'\n\n'.join(secparas)+'\n\n'+s[k2:]
    # 6) tokens
    def P(m):
        x=m.group(1); parts=['%s %d'%(c['word'],N[x])]
        if not on[x]: parts.append(c['off'])
        if auth[x]: parts.append('%s: %s'%(c['autor'],auth[x]))
        return '*(%s)*'%', '.join(parts)
    s=re.sub(r'\[\[P:(\w+)\]\]',P,s)
    s=re.sub(r'\[\[(\w+)\]\]',lambda m:str(N[m.group(1)]),s)
    open(p,'w').write(s)
print('ok')
