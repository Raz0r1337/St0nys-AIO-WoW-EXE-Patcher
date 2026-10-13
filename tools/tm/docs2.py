import re,os,json
os.chdir('/home/user/St0nys-WoW-EXE-Patcher')
mp={int(k):v for k,v in json.load(open('/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/tm/renum2.json')).items()}
sh=lambda n: str(mp[int(n)])
def refs(s):
    pat=re.compile(r'(Nr\.|No\.) (\d+)((?:, \d+)*)((?: (?:und|and) (?:Nr\. |No\. )?)(\d+))?')
    def f(m):
        out=m.group(1)+' '+sh(m.group(2))
        if m.group(3): out+=re.sub(r'\d+',lambda x: sh(x.group(0)),m.group(3))
        if m.group(4): out+=m.group(4)[:-len(m.group(5))]+sh(m.group(5))
        return out
    return pat.sub(f,s)
def table(s,md): return re.sub(r'(?m)^\| \[(\d+)\]\(%s#'%re.escape(md), lambda m:'| [%s](%s#'%(sh(m.group(1)),md), s)
def once(s,old,new):
    assert s.count(old)==1,(old[:80],s.count(old)); return s.replace(old,new)
def after_row(s,anchor_id,md,rows):
    i=s.index('](%s#patch-%s)'%(md,anchor_id)); j=s.index('\n',i)+1
    return s[:j]+rows+s[j:]
R={'de':{
 7:'| [7](PATCHES.md#patch-nothrottle) | Server-Abfragen nicht drosseln (Item- und Quest-Infos schneller) – ungetestet | Hour of Twilight (ported by St0ny) | – | – | – |\n',
 8:'| [8](PATCHES.md#patch-mirrorfix) | Mirror-Image-Absturzfix (Speicherleck bei Spiegelbildern) – ungetestet | Hour of Twilight (ported by St0ny) | – | – | – |\n',
 9:'| [9](PATCHES.md#patch-wmocube) | Fehlende WMO-Datei: Fehlerwürfel statt ERROR #134 – ungetestet | Alyst3r (ported by St0ny) | – | – | – |\n',
 51:'| [51](PATCHES.md#patch-noammo) | Fernkampf ohne Munition – ungetestet *(Server muss mitspielen, sonst meldet er weiter „Keine Munition“)* | Alyst3r (ported by St0ny) | – | – | – |\n',
 70:'| [70](PATCHES.md#patch-lootopen) | Lootfenster bleibt beim Laufen offen – ungetestet | Hour of Twilight (ported by St0ny) | – | – | – |\n',
 71:'| [71](PATCHES.md#patch-showlevel) | Echtes Level statt „??“ bei Gegnern ab 10 Level über dir – ungetestet *(Bosse zeigen weiter „??“)* | Hour of Twilight (ported by St0ny) | – | – | – |\n'},
 'en':{
 7:'| [7](PATCHES.en.md#patch-nothrottle) | Do not throttle server queries (item and quest info loads faster) – untested | Hour of Twilight (ported by St0ny) | – | – | – |\n',
 8:'| [8](PATCHES.en.md#patch-mirrorfix) | Mirror Image crash fix (memory leak with mirror images) – untested | Hour of Twilight (ported by St0ny) | – | – | – |\n',
 9:'| [9](PATCHES.en.md#patch-wmocube) | Missing WMO file: error cube instead of ERROR #134 – untested | Alyst3r (ported by St0ny) | – | – | – |\n',
 51:'| [51](PATCHES.en.md#patch-noammo) | Ranged attacks without ammo – untested *(the server has to support it, otherwise it still reports "no ammo")* | Alyst3r (ported by St0ny) | – | – | – |\n',
 70:'| [70](PATCHES.en.md#patch-lootopen) | Loot window stays open while moving – untested | Hour of Twilight (ported by St0ny) | – | – | – |\n',
 71:'| [71](PATCHES.en.md#patch-showlevel) | Real level instead of "??" for enemies 10+ levels above you – untested *(bosses still show "??")* | Hour of Twilight (ported by St0ny) | – | – | – |\n'}}
for p,md,lang in (('README.md','PATCHES.md','de'),('README.en.md','PATCHES.en.md','en')):
    s=open(p,encoding='utf-8').read()
    s=table(s,md); s=refs(s)
    if lang=='de':
        s=once(s,'Steigwinkel (42), Sprunghöhe\n  (43), die Sprungsteuerung (44–46) und der Doppelsprung (47).','Steigwinkel (45), Sprunghöhe\n  (46), die Sprungsteuerung (47–49) und der Doppelsprung (50).')
        s=once(s,'[#23](PATCHES.md#patch-globalsv)','[#26](PATCHES.md#patch-globalsv)')
        s=once(s,'Jahr-2031-Fix (Datum und Kalender bis Ende 2031) |','Jahr-2031-Fix (Datum und Kalender bis Ende 2031) – ungetestet |')
        s=once(s,'WotLKExtensions.dll Unterstützung aktivieren *(','WotLKExtensions.dll Unterstützung aktivieren – ungetestet *(')
    else:
        s=once(s,'climb angle (42), jump height (43), the air steering\n  (44–46) and the double jump (47).','climb angle (45), jump height (46), the air steering\n  (47–49) and the double jump (50).')
        s=once(s,'[#23](PATCHES.en.md#patch-globalsv)','[#26](PATCHES.en.md#patch-globalsv)')
        s=once(s,'Year 2031 fix (date and calendar until the end of 2031) |','Year 2031 fix (date and calendar until the end of 2031) – untested |')
        s=once(s,'Enable WotLKExtensions.dll support *(','Enable WotLKExtensions.dll support – untested *(')
    r=R[lang]
    s=after_row(s,'year2031',md,r[7]+r[8]+r[9])
    s=after_row(s,'doublejump',md,r[51])
    s=after_row(s,'charrandom',md,r[70]+r[71])
    open(p,'w',encoding='utf-8',newline='\n').write(s)

DE={}; EN={}
DE['sys']='''<a id="patch-nothrottle"></a>
**Server-Abfragen nicht drosseln (Item- und Quest-Infos schneller) – ungetestet** *(Nr. 7, Autor: Hour of Twilight (ported by St0ny))*

Kennt der Client einen Gegenstand, eine Kreatur, eine Quest oder einen Namen
noch nicht, fragt er beim Server nach. Jeder der 15 Datenbank-Caches erlaubt
dabei nur eine begrenzte Zahl Anfragen pro 30 Sekunden – deshalb stehen in
Tooltips, Taschen oder im Questlog oft eine Weile „Lade Gegenstandsinformationen“
oder leere Einträge. Der Patch hebt das Limit auf (0 = unbegrenzt, je ein Byte
in den 15 Cache-Konstruktoren), die Infos kommen sofort.

> [!NOTE]
> Der Client schickt dadurch mehr Anfragen auf einmal. Server mit
> Flood-Schutz könnten das bemängeln – auf öffentlichen Servern also erst
> testen.

<a id="patch-mirrorfix"></a>
**Mirror-Image-Absturzfix (Speicherleck bei Spiegelbildern) – ungetestet** *(Nr. 8, Autor: Hour of Twilight (ported by St0ny))*

Behebt einen Blizzard-Fehler: Bekommt eine Einheit, die das Aussehen eines
Spielers kopiert (Spiegelbilder, auf manchen Servern auch Spieler-Kopien als
Kreaturen), neue Aussehensdaten, legt der Client eine neue
Charakter-Komponente an, ohne die alte freizugeben. Die alte bleibt mit ihrer
Textur am Grafikgerät hängen – beim Beenden greift der Client dann auf schon
freigegebenen Speicher zu und stürzt ab.

Der Patch gibt eine noch vorhandene alte Komponente vorher mit der
Original-Funktion frei. Der kleine Zusatzcode (29 Byte) liegt in einer
ungenutzten Funktion der Exe – die Dateigröße ändert sich nicht.

<a id="patch-wmocube"></a>
**Fehlende WMO-Datei: Fehlerwürfel statt ERROR #134 – ungetestet** *(Nr. 9, Autor: Alyst3r (ported by St0ny))*

Fehlt eine WMO-Datei (große Weltobjekte wie Gebäude oder Dungeons, z. B. in
eigenen MPQs), bricht der Client mit „ERROR #134 Fatal Condition:
CMap::SafeOpen() failed“ ab. Mit dem Patch lädt er stattdessen den
Fehlerwürfel `Spells\\ErrorCube.mdx` – wie in WotLK-Extensions, wo das fest in
der DLL steckt. Die Änderung passt in die Original-Funktion, die Dateigröße
ändert sich nicht.

> [!NOTE]
> Ob der Client den Würfel an jeder Stelle verkraftet, an der eine WMO-Datei
> fehlt, ist noch nicht getestet.
'''
EN['sys']='''<a id="patch-nothrottle"></a>
**Do not throttle server queries (item and quest info loads faster) – untested** *(No. 7, Author: Hour of Twilight (ported by St0ny))*

When the client does not know an item, creature, quest or name yet, it asks the
server. Each of the 15 database caches only allows a limited number of queries
per 30 seconds – which is why tooltips, bags or the quest log often show
"Retrieving item information" or empty entries for a while. The patch lifts the
limit (0 = unlimited, one byte in each of the 15 cache constructors), so the
information arrives right away.

> [!NOTE]
> The client sends more queries at once this way. Servers with flood
> protection could object – test it first on public servers.

<a id="patch-mirrorfix"></a>
**Mirror Image crash fix (memory leak with mirror images) – untested** *(No. 8, Author: Hour of Twilight (ported by St0ny))*

Fixes a Blizzard bug: when a unit that copies a player's appearance (mirror
images, on some servers also player copies as creatures) receives new
appearance data, the client creates a new character component without freeing
the old one. The old one stays attached to the graphics device with its
texture – when exiting, the client then accesses memory that has already been
freed and crashes.

The patch frees a remaining old component first, using the original function.
The small extra code (29 bytes) sits in an unused function of the exe – the
file size does not change.

<a id="patch-wmocube"></a>
**Missing WMO file: error cube instead of ERROR #134 – untested** *(No. 9, Author: Alyst3r (ported by St0ny))*

If a WMO file is missing (large world objects such as buildings or dungeons,
e.g. in custom MPQs), the client aborts with "ERROR #134 Fatal Condition:
CMap::SafeOpen() failed". With the patch it loads the error cube
`Spells\\ErrorCube.mdx` instead – as in WotLK-Extensions, where this is built
into the DLL. The change fits into the original function, the file size does
not change.

> [!NOTE]
> Whether the client copes with the cube everywhere a WMO file is missing has
> not been tested yet.
'''
DE['ammo']='''<a id="patch-noammo"></a>
**Fernkampf ohne Munition – ungetestet** *(Nr. 51, Autor: Alyst3r (ported by St0ny))*

Der Client prüft bei Schießen, Automatischem Schuss und anderen Fähigkeiten,
die Munition brauchen, ob Pfeile oder Kugeln vorhanden sind. Der Patch lässt
diese Prüfung im Client weg (Sprung zum Erfolgsausgang bei VA `0x809540`).

> [!IMPORTANT]
> Der Server prüft selbst. Nur wenn er so angepasst ist, dass er keine
> Munition verlangt, funktioniert Fernkampf ohne Munition – sonst meldet er
> weiter „Keine Munition“. Ohne angepasste Anzeige fliegen die Geschosse
> unsichtbar.
'''
EN['ammo']='''<a id="patch-noammo"></a>
**Ranged attacks without ammo – untested** *(No. 51, Author: Alyst3r (ported by St0ny))*

For Shoot, Auto Shot and other abilities that need ammo, the client checks
whether arrows or bullets are present. The patch skips this check in the
client (jump to the success exit at VA `0x809540`).

> [!IMPORTANT]
> The server checks on its own. Ranged attacks without ammo only work if the
> server is changed so that it does not require ammo – otherwise it still
> reports "no ammo". Without adjusted visuals the projectiles are invisible.
'''
DE['ui']='''<a id="patch-lootopen"></a>
**Lootfenster bleibt beim Laufen offen – ungetestet** *(Nr. 70, Autor: Hour of Twilight (ported by St0ny))*

Im Original schließt sich das Lootfenster, sobald du läufst, seitwärts gehst
oder dich drehst. Mit dem Patch bleibt es offen. Die zehn Stellen in den
Bewegungs-Handlern, die das Fenster schließen, werden übersprungen (je ein
Byte).

<a id="patch-showlevel"></a>
**Echtes Level statt „??“ bei Gegnern ab 10 Level über dir – ungetestet** *(Nr. 71, Autor: Hour of Twilight (ported by St0ny))*

Ist ein feindliches Ziel 10 oder mehr Level über dir, zeigt der Client statt
des Levels „??“ (bzw. einen Totenkopf auf der Namensplakette, `UnitLevel`
liefert -1). Mit dem Patch zeigen Tooltip, Namensplakette und `UnitLevel` das
echte Level. Bosse zeigen weiterhin „??“ – diese Prüfung bleibt erhalten.
'''
EN['ui']='''<a id="patch-lootopen"></a>
**Loot window stays open while moving – untested** *(No. 70, Author: Hour of Twilight (ported by St0ny))*

In the original the loot window closes as soon as you walk, strafe or turn.
With the patch it stays open. The ten places in the movement handlers that
close the window are skipped (one byte each).

<a id="patch-showlevel"></a>
**Real level instead of "??" for enemies 10+ levels above you – untested** *(No. 71, Author: Hour of Twilight (ported by St0ny))*

If a hostile target is 10 or more levels above you, the client shows "??"
instead of the level (or a skull on the nameplate, `UnitLevel` returns -1).
With the patch, tooltip, nameplate and `UnitLevel` show the real level. Bosses
still show "??" – that check is kept.
'''
def insert_after_section(s,anchor_id,text):
    i=s.index('<a id="patch-%s"></a>'%anchor_id)
    j=s.find('\n<a id="patch-',i+10); k=s.find('\n## ',i+10)
    cut=min(x for x in (j,k) if x!=-1)
    return s[:cut]+'\n'+text+s[cut:]
for p,T,lang in (('PATCHES.md',DE,'de'),('PATCHES.en.md',EN,'en')):
    s=open(p,encoding='utf-8').read()
    s=refs(s)
    if lang=='de':
        s=once(s,'**Jahr-2031-Fix (Datum und Kalender bis Ende 2031)** *(','**Jahr-2031-Fix (Datum und Kalender bis Ende 2031) – ungetestet** *(')
        s=once(s,'**WotLKExtensions.dll Unterstützung aktivieren** *(','**WotLKExtensions.dll Unterstützung aktivieren – ungetestet** *(')
    else:
        s=once(s,'**Year 2031 fix (date and calendar until the end of 2031)** *(','**Year 2031 fix (date and calendar until the end of 2031) – untested** *(')
        s=once(s,'**Enable WotLKExtensions.dll support** *(','**Enable WotLKExtensions.dll support – untested** *(')
    s=insert_after_section(s,'year2031',T['sys'])
    s=insert_after_section(s,'doublejump',T['ammo'])
    s=insert_after_section(s,'charrandom',T['ui'])
    open(p,'w',encoding='utf-8',newline='\n').write(s)
print('ok')
