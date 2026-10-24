#!/usr/bin/env python3
# st0ny-main bekommt aus st0ny-dev den Luxvelum-Lader als Nr. 32 (hinter dem Lux-Lader, sicher - DLL riskant, im
# Preset "Reforged"). Verweise ab Nr. 32 ruecken um eins. Patcher: Eintrag (wie dev), Hinweis im Lexara-Lader,
# Set-ClientDate laesst den PE-Zeitstempel mit Luxvelum in Ruhe, Preset und Kommentar dazu. Doku: Abschnitt und
# Tabellenzeile wie dev (Nummern auf main umgestellt), Saetze bei wow_optimize, Lexara, Lux und Build-Datum, Liste
# "DLL riskant", Absatz zum Preset. Die Bytetabelle danach mit -BuildTable neu erzeugen.
# Aufruf: port_luxvelum_main.py <dev-Ordner (Quelle, nach luxvelum_safe.py)> <main-Ordner (Ziel, wird geaendert)>
import sys, os, re
DEV, D = sys.argv[1], sys.argv[2]
NEW = 32
def sh(n): n = int(n); return str(n + 1 if n >= NEW else n)
def shift_refs(s, dash):
    """Nummern hinter "Nr."/"No." verschieben - auch Listen ("Nr. 9, 66 und 67") und Bereiche ("77-79")."""
    item = r'\d+(?:%s\d+)?' % dash
    lst = re.compile(r'(Nr\.|No\.)(\s+)(%s(?:(?:,\s+|\s+(?:und|and|oder|or)\s+)%s)*)' % (item, item))
    def one(m):
        def num(x):
            a, _, b = x.group(0).partition(dash)
            return sh(a) + (dash + sh(b) if b else '')
        return m.group(1) + m.group(2) + re.sub(item, num, m.group(3))
    return lst.sub(one, s)
def rd(p, crlf=False):
    s = open(p, encoding='utf-8', newline='').read()
    if crlf: assert '\r\n' in s; s = s.replace('\r\n', '\n')
    else: assert '\r' not in s
    return s
def wr(p, s, crlf=False):
    if crlf: s.encode('ascii'); s = s.replace('\n', '\r\n')
    open(p, 'w', encoding='utf-8', newline='').write(s)
def once(s, a, b, tag=''):
    assert s.count(a) == 1, (tag, a[:80], s.count(a)); return s.replace(a, b)
def ids_of(s): return re.findall(r"(?m)^    @\{ Id = '(\w+)'", s[s.index('\n$patches = @(\n'):])
dsrc = rd(os.path.join(DEV, 'apply_patches.ps1'), True)
dids = ids_of(dsrc); assert dids.index('luxvelum') + 1 == NEW
# ---------------- Patcher ----------------
p = os.path.join(D, 'apply_patches.ps1'); s = rd(p, True)
assert 'luxvelum' not in ids_of(s) and ids_of(s).index('lux') + 1 == NEW - 1
keep = '# Name mit Patch-Nummer davor ("Nr. 65 ..."), fuer Hinweise auf andere Patches'
assert s.count(keep) == 1
s = shift_refs(s.replace(keep, '\0KEEP\0'), '-').replace('\0KEEP\0', keep)
ent = re.search(r"(?ms)^    @\{ Id = 'luxvelum';.*?\n    \}\}\n\n", dsrc).group(0)
assert 'PublicUntested' not in ent and not re.search(r'(Nr|No)\. \d', ent)
s = once(s, "    @{ Id = 'areatrigger'; Cat = 'gameplay';", ent + "    @{ Id = 'areatrigger'; Cat = 'gameplay';", 'Eintrag')
s = once(s, """        # wird ebenfalls vor dem Einstiegspunkt geladen, der Zeitpunkt passt.
        # Fehlt die DLL, startet WoW ganz normal. Lexara laedt selbst die
        # LuxShoulderCam.dll mit, wenn sie im WoW-Ordner liegt (siehe Lux-Lader).
""", """        # wird ebenfalls vor dem Einstiegspunkt geladen, der Zeitpunkt passt.
        # Mit dem Luxvelum-Lader zeigt der Aufruf auf dessen Lader, der danach
        # hierher springt (Luxvelum wird zuerst geladen). Fehlt die DLL,
        # startet WoW ganz normal. Lexara laedt selbst die LuxShoulderCam.dll
        # mit, wenn sie im WoW-Ordner liegt (siehe Lux-Lader).
""", 'Lexara')
guard = re.search(r'(?m)^    # Nicht mit dem Luxvelum-Lader .*?\{ return \}\n', dsrc, re.S).group(0)
s = once(s, """    # als Ortszeit dieses Rechners, so zeigt Windows sie hier wieder genauso an.
    $e = RU32 $script:f 0x3C
""", """    # als Ortszeit dieses Rechners, so zeigt Windows sie hier wieder genauso an.
""" + guard + """    $e = RU32 $script:f 0x3C
""", 'Set-ClientDate')
s = once(s, """        # Build-Text und der Zeitstempel im PE-Kopf.
        Set-ClientDate $script:VALUES['clientdate']
""", """        # Build-Text und der Zeitstempel im PE-Kopf (nicht mit dem
        # Luxvelum-Lader, siehe Set-ClientDate).
        Set-ClientDate $script:VALUES['clientdate']
""", 'clientdate')
s = once(s, "    'glue', 'awesome', 'lexara', 'lux',\n", "    'glue', 'awesome', 'lexara', 'lux', 'luxvelum',\n", 'Preset')
s = once(s, """# Lader fuer awesome_wotlk, Lexara und Lux (Nr. 28, 30 und 31, Patch sicher,
# DLL riskant; Lexara laedt Lux ohnehin mit, der Lux-Lader auch ohne Lexara)
""", """# Lader fuer awesome_wotlk, Lexara, Lux und Luxvelum (Nr. 28, 30, 31 und 32,
# Patch sicher, DLL riskant; Lexara laedt Lux ohnehin mit, der Lux-Lader auch
# ohne Lexara)
""", 'Kommentar')
ids = ids_of(s); N = {i: k + 1 for k, i in enumerate(ids)}
assert N['luxvelum'] == NEW
wr(p, s, True)
# ---------------- Doku ----------------
DN = {i: k + 1 for k, i in enumerate(dids)}
for lang, rdm, pdm, nr, und in (('de', 'README.de.md', 'PATCHES.de.md', 'Nr.', 'und'), ('en', 'README.md', 'PATCHES.en.md', 'No.', 'and')):
    dp = rd(os.path.join(DEV, 'docs', pdm)); dr = rd(os.path.join(DEV, 'docs', rdm))
    # Abschnitt aus dev, Nummern auf main
    sec = dp[dp.index('<a id="patch-luxvelum"></a>'):dp.index('<a id="patch-voicedll"></a>')]
    sec = once(sec, '%s 27–31 %s 33' % (nr, und), '%s 27–31' % nr, 'Lader-Liste')
    def renum(m):
        n = int(m.group(2)); i = dids[n - 1]; assert i in N, (pdm, n, i)
        return m.group(1) + str(N[i])
    sec = re.sub(r'(%s\s+)(\d+)' % re.escape(nr), renum, sec)
    found = set(re.findall(r'%s\s+(\d+)' % re.escape(nr), sec))
    assert found == {'27'} | {str(N[x]) for x in ('luxvelum', 'clientdate', 'lightstay')}, (pdm, found)
    q = os.path.join(D, 'docs', pdm); t = shift_refs(rd(q), '–')
    if lang == 'de':
        t = once(t, """Der Patch verträgt sich mit dem
Lexara-Lader (Nr. 30) und dem Lux-Lader (Nr. 31).
""", """Der Patch verträgt sich mit dem
Lexara-Lader (Nr. 30), dem Lux-Lader (Nr. 31) und dem Luxvelum-Lader (Nr. 32).
""", 'wow_optimize')
        t = once(t, """Der Patch verträgt sich mit
dem Lux-Lader (Nr. 31), der nur einen späteren Sprung im Startcode ändert.
""", """Der Patch verträgt sich mit
dem Lux-Lader (Nr. 31), der nur einen späteren Sprung im Startcode ändert. Mit
dem Luxvelum-Lader (Nr. 32) zeigt der Aufruf am Einstiegspunkt zuerst auf
dessen Lader, der danach in den Lexara-Lader springt – Luxvelum wird also vor
Lexara geladen.
""", 'Lexara')
        t = once(t, """Der Patch verträgt sich mit
dem wow_optimize-Lader (Nr. 27) und dem Lexara-Lader (Nr. 30).

## Gameplay-Fixes
""", """Der Patch verträgt sich mit
dem wow_optimize-Lader (Nr. 27), dem Lexara-Lader (Nr. 30) und dem
Luxvelum-Lader (Nr. 32).

""" + sec + """## Gameplay-Fixes
""", 'Lux')
        t = once(t, """als Ortszeit des Rechners, auf dem du patchst.
""", """als Ortszeit des Rechners, auf dem du patchst. Mit dem Luxvelum-Lader (Nr. 32)
bleibt dieser Zeitstempel unverändert: Luxvelum erkennt den Client daran und
schaltet sich sonst ab. Das angezeigte Build-Datum ändert sich trotzdem.
""", 'Build-Datum')
    else:
        t = once(t, """The patch works together with the Lexara loader (No. 30) and the
Lux loader (No. 31).
""", """The patch works together with the Lexara loader (No. 30), the
Lux loader (No. 31) and the Luxvelum loader (No. 32).
""", 'wow_optimize')
        t = once(t, """patch works together with the Lux loader (No. 31), which only changes a later
jump in the startup code.
""", """patch works together with the Lux loader (No. 31), which only changes a later
jump in the startup code. With the Luxvelum loader (No. 32) the call at the
entry point first points to its loader, which then jumps to the Lexara loader –
so Luxvelum is loaded before Lexara.
""", 'Lexara')
        t = once(t, """patch works together with the wow_optimize loader (No. 27) and the Lexara
loader (No. 30).

## Gameplay fixes
""", """patch works together with the wow_optimize loader (No. 27), the Lexara
loader (No. 30) and the Luxvelum loader (No. 32).

""" + sec + """## Gameplay fixes
""", 'Lux')
        t = once(t, """as local time of the computer you patch on.
""", """as local time of the computer you patch on. With the Luxvelum loader (No. 32)
this timestamp stays unchanged: Luxvelum recognizes the client by it and turns
itself off otherwise. The build date shown still changes.
""", 'Build-Datum')
    wr(q, t)
    # README: Nummern, Tabelle, Zeile, Liste, Absatz
    q = os.path.join(D, 'docs', rdm); t = shift_refs(rd(q), '–')
    t = re.sub(r'(?m)^\| \[(\d+)\]\(%s#' % re.escape(pdm), lambda m: '| [%s](%s#' % (sh(m.group(1)), pdm), t)
    t = re.sub(r'\[#(\d+)\]\(%s#' % re.escape(pdm), lambda m: '[#%s](%s#' % (sh(m.group(1)), pdm), t)   # Danksagung
    row = re.search(r'(?m)^\| \[%d\]\(%s#patch-luxvelum\) \|.*\n' % (DN['luxvelum'], re.escape(pdm)), dr).group(0)
    m = re.search(r'(?m)^\| \[31\]\(%s#patch-lux\) \|.*\n' % re.escape(pdm), t); assert m
    t = t[:m.end()] + row.replace('[%d]' % DN['luxvelum'], '[%d]' % NEW, 1) + t[m.end():]
    if lang == 'de':
        t = once(t, 'auf öffentlichen Servern erkannt oder blockiert werden kann: Nr. 27–31\n',
                    'auf öffentlichen Servern erkannt oder blockiert werden kann: Nr. 27–32\n', rdm)
        t = once(t, """Lux-Lader (Nr. 31) für die Schulterkamera LuxShoulderCam und der
Licht-Patch Nr. %d. Bei den drei Ladern ist der Patch selbst sicher, die
""" % N['lights'], """Lux-Lader (Nr. 31) für die Schulterkamera LuxShoulderCam, der Luxvelum-Lader
(Nr. 32) für volumetrischen Nebel, Licht und Wasser und der Licht-Patch
Nr. %d. Bei den vier Ladern ist der Patch selbst sicher, die
""" % N['lights'], rdm)
    else:
        t = once(t, 'detected or blocked on public servers: No. 27–31 (yellow note).',
                    'detected or blocked on public servers: No. 27–32 (yellow note).', rdm)
        t = once(t, """(No. 30) for Stormhand's HD fonts, the Lux loader (No. 31) for the
LuxShoulderCam shoulder camera and the light patch No. %d. For the three
loaders the patch itself is safe,""" % N['lights'], """(No. 30) for Stormhand's HD fonts, the Lux loader (No. 31) for the
LuxShoulderCam shoulder camera, the Luxvelum loader (No. 32) for volumetric
fog, light and water and the light patch No. %d. For the four
loaders the patch itself is safe,""" % N['lights'], rdm)
    wr(q, t)
print('main: Luxvelum als Nr. %d, %d Patches' % (NEW, len(ids)))
