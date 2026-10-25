#!/usr/bin/env python3
# MPQ-Limit-Fix (MacWarrior, patch_mpq_limit.py) als Nr. 22 in st0ny-dev einbauen (hinter "Erweiterte MPQ-Namen",
# ungetestet). Verweise ab Nr. 22 ruecken um eins. Statt MacWarriors eigener Sektion mit Hook ersetzt die Portierung den
# Block, der im Original die 64 Tabellenplaetze anlegt (VA 0x405E33-0x405E78), an Ort und Stelle - gleiche Wirkung,
# Dateigroesse und PE-Header bleiben gleich. Danach die Bytetabelle mit -BuildTable neu erzeugen.
# Aufruf: add_mpqlimit.py <dev-Ordner>
import sys, os, re, struct
D = sys.argv[1]
NEW = 22
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
def hexlist(b, ind):
    rows = [', '.join('0x%02X' % x for x in b[i:i + 16]) for i in range(0, len(b), 16)]
    return (',\n' + ind).join(rows)

OLD = bytes.fromhex('33ff391d3cfab200733c391d38fab20073348b0d44fab20085c9750d53b938fab200e8e6a11c008bc833d28bc3'
                    'f7f18bf385d274062bca03cb8bf156b938fab200e877d9ffff')
NEWB = (bytes.fromhex('33ff' 'c70544fab20040000000' '8b45dc' '8d440040' '3b0538fab200' '760b' '50' 'b938fab200' 'e8')
        + struct.pack('<i', 0x4037F0 - 0x405E59) + b'\x90' * 32)
assert len(OLD) == len(NEWB) == 70
ind = '            '
ENTRY = r"""    @{ Id = 'mpqlimit'; Cat = 'modding'; On = $false; PublicUntested = $true; GameUntested = $true
       Author = 'MacWarrior (ported by St0ny)'
       De = 'MPQ-Limit-Fix (Abstuerze bei vielen Patch-MPQs)'
       En = 'MPQ limit fix (crashes with many patch MPQs)'
       NoteDe = 'erst ab etwa 30 eigenen Patch-MPQs noetig'
       NoteEn = 'only needed from about 30 custom patch MPQs'
       Code = {
        # Nach patch_mpq_limit.py von MacWarrior. Der MPQ-Lader (VA 0x405DD0)
        # legt die Tabelle der Archiv-Handles (Objekt bei VA 0xB2FA38:
        # Kapazitaet, Anzahl, Daten, Schrittweite) mit nur 64 Plaetzen an und
        # schreibt dann ohne Pruefung hinein: je ein Handle fuer jedes gefundene
        # Patch-MPQ, fuer alternate.MPQ und dessen Kind-Archive in den Patches,
        # dann ein Platz fuer jeden der 28 Basis-Eintraege (common.MPQ,
        # expansion.MPQ, locale-xxXX.MPQ ...). Vergroessert wird erst ganz am
        # Ende (VA 0x40624A). Ab etwa 37 geoeffneten Patch-MPQs (mit den sechs
        # mitgelieferten also ab etwa 31 eigenen) ist der Heap da schon
        # ueberschrieben - zufaellige Abstuerze beim Starten oder Beenden.
        # Hier reserviert der Block, der im Original die 64 Plaetze anlegt
        # (VA 0x405E33-0x405E78), gleich 2*N+64 Plaetze ueber die
        # Original-Vergroesserung (VA 0x4037F0), N = Zahl der gefundenen
        # Patch-Pfade ([ebp-24h]). Beschrieben werden hoechstens 2*N+31 Plaetze
        # (N Patches, N Kind-Archive, alternate.MPQ, 28 Basis-Plaetze, zwei
        # Streaming-Archive). Wie im Original wird die Schrittweite 64 gesetzt;
        # ebx (Prioritaet der Patches, 64), edi und die Ladereihenfolge bleiben
        # gleich. MacWarriors Skript haengt dafuer eine Sektion mit Hook an -
        # hier gleiche Wirkung ohne Sektion, der Rest des Blocks ist nop.
        #   xor edi,edi / mov dword [0B2FA44h],40h / mov eax,[ebp-24h]
        #   lea eax,[eax+eax+40h] / cmp eax,[0B2FA38h] / jbe weiter
        #   push eax / mov ecx,0B2FA38h / call 4037F0h / weiter: 32x nop
        Assert-Bytes 0x5233 @(
            %s
        ) 'MPQ-Limit-Fix'
        Patch 0x5233 @(
            %s
        )
    }}

""" % (hexlist(OLD, ind), hexlist(NEWB, ind))

p = os.path.join(D, 'apply_patches.ps1'); s = rd(p, True)
keep = '# Name mit Patch-Nummer davor ("Nr. 64 ..."), fuer Hinweise auf andere Patches'
assert s.count(keep) == 1
s = shift_refs(s.replace(keep, '\0KEEP\0'), '-').replace('\0KEEP\0', keep)
s = once(s, "    @{ Id = 'localdata'; Cat = 'modding';", ENTRY + "    @{ Id = 'localdata'; Cat = 'modding';", 'Eintrag')
ids = re.findall(r"(?m)^    @\{ Id = '(\w+)'", s[s.index('\n$patches = @(\n'):])
assert ids.index('mpqlimit') + 1 == NEW and ids.index('mpqnames') + 1 == NEW - 1
wr(p, s, True)

SEC = {'de': """<a id="patch-mpqlimit"></a>
**MPQ-Limit-Fix (Abstürze bei vielen Patch-MPQs)** *(Nr. 22, Autor: MacWarrior (ported by St0ny))* 🟠 **[ungetestet]**

Behebt zufällige Abstürze („WoW Error“) beim Starten oder Beenden, wenn sehr
viele Patch-MPQs im `Data`-Ordner und im Sprachordner liegen – laut MacWarrior
ab etwa 30 eigenen zusätzlich zu den mitgelieferten. Auf Inhalt und Größe der
Archive kommt es nicht an, nur auf ihre Anzahl. Mit „Erweiterte MPQ-Namen
erlauben“ (Nr. 21), das beliebige Namen wie `patch-meinmod.MPQ` zulässt, kommt
man leicht in diesen Bereich.

> [!WARNING]
> Noch ungetestet, online wie im Spiel. Deshalb ist der Patch standardmäßig
> abgewählt und vorerst nur im Zweig `st0ny-dev`.

Ursache: Der MPQ-Lader (VA `0x405DD0`) legt die Tabelle der Archiv-Handles mit
nur 64 Plätzen an und schreibt dann ohne Prüfung hinein – erst je einen Handle
für jedes gefundene Patch-MPQ (dazu gegebenenfalls `alternate.MPQ` und dessen
Kind-Archive), danach je einen Platz für die 28 Basis-Archive (`common.MPQ`,
`expansion.MPQ`, `locale-xxXX.MPQ` …). Vergrößert wird die Tabelle erst ganz
am Ende. Ab etwa 37 geöffneten Patch-MPQs – mit den sechs mitgelieferten also
ab etwa 31 eigenen – schreibt der Lader vorher schon über ihr Ende hinaus und
beschädigt den Speicher. Der Absturz kommt dann irgendwann später, oft erst
beim Beenden.

Der Patch reserviert die Tabelle gleich am Anfang groß genug: 2 × N + 64 Plätze
(N = Zahl der gefundenen Patch-MPQs), mehr als die höchstens 2 × N + 31, die
der Lader beschreiben kann. Gerechnet wird bei jedem Start neu. MacWarriors
Skript lagert den Code dafür in eine neue Sektion aus; diese Fassung ersetzt
stattdessen den Block, der im Original die 64 Plätze anlegt (VA
`0x405E33`–`0x405E78`), an Ort und Stelle. Die Wirkung ist dieselbe,
Dateigröße und PE-Header bleiben unverändert. Ladereihenfolge und Prioritäten
der Archive ändern sich nicht.

""", 'en': """<a id="patch-mpqlimit"></a>
**MPQ limit fix (crashes with many patch MPQs)** *(No. 22, Author: MacWarrior (ported by St0ny))* 🟠 **[untested]**

Fixes random crashes ("WoW Error") when starting or closing the game with very
many patch MPQs in the `Data` folder and the locale folder – according to
MacWarrior from about 30 custom ones on top of the stock files. Content and
size of the archives do not matter, only their number. With "Allow extended
MPQ names" (No. 21), which allows any name such as `patch-mymod.MPQ`, you
easily get there.

> [!WARNING]
> Still untested, online and in game. That is why the patch is deselected by
> default and only in the `st0ny-dev` branch for now.

Cause: the MPQ loader (VA `0x405DD0`) creates the table of archive handles with
only 64 slots and then writes to it without any check – first one handle for
every patch MPQ found (plus `alternate.MPQ` and its child archives, if any),
then one slot for each of the 28 base archives (`common.MPQ`, `expansion.MPQ`,
`locale-xxXX.MPQ` …). The table is only enlarged at the very end. From about 37
opened patch MPQs – with the six stock ones that is about 31 custom ones – the
loader writes past its end before that and corrupts memory. The crash then
comes at some later point, often only when closing the game.

The patch makes the table big enough right at the start: 2 × N + 64 slots
(N = number of patch MPQs found), more than the at most 2 × N + 31 the loader
can write. It is recalculated on every start. MacWarrior's script moves the
code for this into a new section; this version instead replaces the block that
creates the 64 slots in the original (VA `0x405E33`–`0x405E78`) in place. The
effect is the same, file size and PE header stay unchanged. Load order and
archive priorities do not change.

"""}
ROW = {'de': '| [22](PATCHES.de.md#patch-mpqlimit) | MPQ-Limit-Fix (Abstürze bei vielen Patch-MPQs) *(erst ab etwa 30 eigenen Patch-MPQs nötig)* | 🟠 **[ungetestet]** | MacWarrior (ported by St0ny) | – | – | – |\n',
       'en': '| [22](PATCHES.en.md#patch-mpqlimit) | MPQ limit fix (crashes with many patch MPQs) *(only needed from about 30 custom patch MPQs)* | 🟠 **[untested]** | MacWarrior (ported by St0ny) | – | – | – |\n'}
LEG = {'de': [("kann zu Kick/Bann führen: Nr. 10, 27,", "kann zu Kick/Bann führen: Nr. 10, 22, 27,"),
              ("möglicherweise verbuggt: Nr. 26, 27,", "möglicherweise verbuggt: Nr. 22, 26, 27,")],
       'en': [("you kicked or banned: No. 10, 27,", "you kicked or banned: No. 10, 22, 27,"),
              ("possibly buggy: No. 26, 27,", "possibly buggy: No. 22, 26, 27,")]}
for lang, rdm, pdm in (('de', 'README.de.md', 'PATCHES.de.md'), ('en', 'README.md', 'PATCHES.en.md')):
    q = os.path.join(D, 'docs', pdm); t = shift_refs(rd(q), '–')
    t = once(t, '<a id="patch-localdata"></a>', SEC[lang] + '<a id="patch-localdata"></a>', pdm)
    wr(q, t)
    q = os.path.join(D, 'docs', rdm); t = shift_refs(rd(q), '–')
    t = re.sub(r'(?m)^\| \[(\d+)\]\(%s#' % re.escape(pdm), lambda m: '| [%s](%s#' % (sh(m.group(1)), pdm), t)
    t = re.sub(r'\[#(\d+)\]\(%s#' % re.escape(pdm), lambda m: '[#%s](%s#' % (sh(m.group(1)), pdm), t)   # Danksagung
    for a, b in LEG[lang]: t = once(t, a, b, rdm)
    m = re.search(r'(?m)^\| \[21\]\(%s#patch-mpqnames\) \|.*\n' % re.escape(pdm), t); assert m
    t = t[:m.end()] + ROW[lang] + t[m.end():]
    wr(q, t)
print('mpqlimit als Nr. %d eingebaut, %d Patches' % (NEW, len(ids)))
