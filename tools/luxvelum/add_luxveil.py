#!/usr/bin/env python3
# Luxveil-Lader als Nr. 32 in st0ny-dev einbauen (hinter dem Lux-Lader). Verweise ab Nr. 32 ruecken um eins.
# Teil "code": Patch-Eintrag, Hinweise im Lexara-Lader und in "Build-Datum aendern" (PE-Zeitstempel bleibt mit
# Luxveil unveraendert), Nummern in Texten und Kommentaren. Teil "docs": README/PATCHES DE/EN.
# Aufruf: add_luxveil.py <dev-Ordner> code  |  add_luxveil.py <dev-Ordner> docs
import sys, os, re
D, MODE = sys.argv[1], sys.argv[2]
NEW = 32                       # Nummer des neuen Patches, alles ab hier rueckt um eins
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

if MODE == 'code':
    p = os.path.join(D, 'apply_patches.ps1'); s = rd(p, True)
    # Nummern in Texten und Kommentaren (ausser dem Beispiel in der Erklaerung von PatchName)
    keep = '# Name mit Patch-Nummer davor ("Nr. 64 ..."), fuer Hinweise auf andere Patches'
    assert s.count(keep) == 1
    s = shift_refs(s.replace(keep, '\0KEEP\0'), '-').replace('\0KEEP\0', keep)
    entry = r"""    @{ Id = 'luxveil'; Cat = 'dll'; On = $false; PublicUntested = $true; GameUntested = $true; DllRisky = $true
       Author = 'St0ny'
       De = 'Luxveil.dll beim Start laden (Nebel, Licht und Wasser - Atmospheric Immersion for Project Reforged)'
       En = 'Load Luxveil.dll at startup (fog, light and water - Atmospheric Immersion for Project Reforged)'
       NoteDe = 'benoetigt Luxveil - ohne version.dll; alte CoAVolFog.dll und version.dll loeschen'
       NoteEn = 'requires Luxveil - no version.dll needed; delete the old CoAVolFog.dll and version.dll'
       Url = 'https://github.com/Raz0r1337/coa-vfog'
       Code = {
        # Laedt beim Start Luxveil.dll (volumetrischer Nebel, Licht und Wasser,
        # frueher CoAVolFog) aus dem WoW-Ordner. Bisher kam Luxveil ueber eine
        # Proxy-version.dll, die Luxveil.dll fest importiert. Luxveil erledigt
        # alles in DllMain (kein Export-Aufruf noetig) und muss vor Direct3D
        # geladen sein: Es biegt den GetProcAddress-Zeiger des Clients bei VA
        # 0xB2ED98 um und faengt so Direct3DCreate9 ab.
        # Deshalb ganz vorne in der Einstiegskette, noch vor dem Lexara-Lader
        # (so wie die Proxy-DLL vor allen Ladern lief): Der erste Aufruf am
        # Einstiegspunkt (VA 0x401000) zeigt auf einen Lader in einer freien
        # 16-Byte-Luecke (VA 0x6D3080, hinter einem Aufruf, der nie
        # zurueckkehrt): push "Luxveil.dll" / call [LoadLibraryA] / jmp zum
        # bisherigen Ziel des Aufrufs - dem Lexara-Lader, wenn er gewaehlt ist
        # (er steht davor in der Liste und ist dann schon eingespielt), sonst
        # __security_init_cookie (VA 0x76E490). Der Name steht in einer zweiten
        # Luecke (VA 0x6D3214, genau 12 Byte). Beide Luecken sind kleiner als
        # 24 Byte (Lux sucht sich zur Laufzeit die erste Luecke ab 24 Byte) und
        # liegen ausserhalb der Stellen, die Luxveil prueft oder umschreibt.
        # Fehlt die DLL, startet WoW ganz normal; zusammen mit der Proxy-
        # version.dll laedt Windows die DLL nur einmal. Luxveil erkennt den
        # Client am Zeitstempel im PE-Kopf - "Build-Datum aendern" laesst ihn
        # deshalb in Ruhe, wenn dieser Lader eingespielt ist (Set-ClientDate).
        # Dateigroesse und PE-Header bleiben unveraendert.
        Assert-Bytes 0x400 @(0xE8) 'Luxveil-Lader'
        Assert-Bytes 0x2D2480 (@(0xCC) * 16) 'Luxveil-Lader'
        Assert-Bytes 0x2D2614 (@(0xCC) * 12) 'Luxveil-Lader'
        $next = 0x401005 + [BitConverter]::ToInt32($script:f, 0x401)   # bisheriges Ziel des Aufrufs
        if ($next -eq 0x6DC8C0) {
            Assert-Bytes 0x2DBCC0 @(0x68, 0xE0, 0xC0, 0x6D, 0x00, 0xFF, 0x15, 0x48, 0xF2, 0x9D, 0x00, 0xE9, 0xC0, 0x1B, 0x09, 0x00) 'Luxveil-Lader'   # Lexara-Lader
        } elseif ($next -ne 0x76E490) { throw 'Luxveil-Lader: Code bei Datei 0x400 unbekannt.' }
        Patch 0x2D2480 ([byte[]](@(0x68, 0x14, 0x32, 0x6D, 0x00, 0xFF, 0x15, 0x48, 0xF2, 0x9D, 0x00) + (Get-Rel32 @(0xE9) 0x6D308B $next)))
        Patch 0x2D2614 @(0x4C, 0x75, 0x78, 0x76, 0x65, 0x69, 0x6C, 0x2E, 0x64, 0x6C, 0x6C, 0x00)   # "Luxveil.dll"
        Patch 0x401 ([BitConverter]::GetBytes([int32](0x6D3080 - 0x401005)))   # call -> Luxveil-Lader
    }}

"""
    s = once(s, "    @{ Id = 'voicedll'; Cat = 'dll';", entry + "    @{ Id = 'voicedll'; Cat = 'dll';", 'Eintrag')
    s = once(s, """        # Vertraegt sich mit dem voice.dll-Lader (der aendert nur den Sprung
        # danach). Fehlt die DLL, startet WoW ganz normal. Lexara laedt selbst
""", """        # Vertraegt sich mit dem voice.dll-Lader (der aendert nur den Sprung
        # danach). Mit dem Luxveil-Lader zeigt der Aufruf auf dessen Lader, der
        # danach hierher springt (Luxveil wird zuerst geladen). Fehlt die DLL,
        # startet WoW ganz normal. Lexara laedt selbst
""", 'Lexara')
    s = once(s, """    # Zeitstempel im PE-Kopf (TimeDateStamp, Sekunden seit 1970 in UTC), den
    # Analyse-Werkzeuge als Erstellungszeit zeigen. Datum und Uhrzeit gelten
    # als Ortszeit dieses Rechners, so zeigt Windows sie hier wieder genauso an.
    $e = RU32 $script:f 0x3C
""", """    # Zeitstempel im PE-Kopf (TimeDateStamp, Sekunden seit 1970 in UTC), den
    # Analyse-Werkzeuge als Erstellungszeit zeigen. Datum und Uhrzeit gelten
    # als Ortszeit dieses Rechners, so zeigt Windows sie hier wieder genauso an.
    # Nicht mit dem Luxveil-Lader (steht in der Liste davor, sein DLL-Name ist
    # dann schon eingespielt): Luxveil erkennt den Client 12340 an diesem
    # Zeitstempel und schaltet sich sonst ab - dann bleibt er im Original.
    if ([System.Text.Encoding]::ASCII.GetString($script:f, 0x2D2614, 12) -ceq "Luxveil.dll`0") { return }
    $e = RU32 $script:f 0x3C
""", 'Set-ClientDate')
    s = once(s, """        # Portierung von edit_date.py (MacWarrior): die drei Datumsfelder
        # ("Jun 24 2010") und das Jahr im LegalCopyright, dazu die Uhrzeit im
        # Build-Text und der Zeitstempel im PE-Kopf.
""", """        # Portierung von edit_date.py (MacWarrior): die drei Datumsfelder
        # ("Jun 24 2010") und das Jahr im LegalCopyright, dazu die Uhrzeit im
        # Build-Text und der Zeitstempel im PE-Kopf (nicht mit dem
        # Luxveil-Lader, siehe Set-ClientDate).
""", 'clientdate')
    wr(p, s, True)
    print('code ok')

if MODE == 'docs':
    URL = 'https://github.com/Raz0r1337/coa-vfog'
    SEC = {'de': """<a id="patch-luxveil"></a>
**Luxveil.dll beim Start laden (Nebel, Licht und Wasser - Atmospheric Immersion for Project Reforged)** *(Nr. 32, Autor: St0ny)* 🟠 **[ungetestet - DLL riskant]**

Lädt beim Start die `Luxveil.dll` aus dem WoW-Ordner –
[Luxveil](%s) (früher CoAVolFog) bringt volumetrischen
Nebel, Licht und Wasser in den 3.3.5a-Client. Bisher kam Luxveil über eine
Proxy-`version.dll`; mit diesem Patch braucht es sie nicht mehr, und unter
Wine/Proton fällt `WINEDLLOVERRIDES` weg. Luxveil liest `Luxveil.ini`,
`fogdata.bin` und `waterdata.bin` aus dem WoW-Ordner und schreibt
`Luxveil.log`. Fehlt die DLL, startet WoW ganz normal.

> [!WARNING]
> Noch ungetestet, online wie im Spiel. Deshalb ist der Patch standardmäßig
> abgewählt und vorerst nur im Zweig `st0ny-dev`. Der Patch selbst lädt nur
> eine DLL, die hier nicht enthalten ist – die `Luxveil.dll` kann aber auf
> öffentlichen Servern erkannt oder blockiert werden.

> [!IMPORTANT]
> **Alte Dateien löschen:** Liegen noch die alte `CoAVolFog.dll` und ihre
> `version.dll` im WoW-Ordner, lädt die alte DLL zuerst und belegt die
> Einhängestellen. Luxveil hängt sich dann nicht ein (das steht in
> `Luxveil.log`), und der Nebel kommt von der alten DLL. Die `version.dll` von
> Luxveil selbst schadet nicht, sie wird mit diesem Patch nur nicht mehr
> gebraucht: Windows lädt `Luxveil.dll` nur einmal.

Luxveil erkennt den Client am Zeitstempel im Programmkopf. „Build-Datum ändern“
(Nr. 92) lässt diesen Zeitstempel deshalb unverändert, wenn dieser Lader
gewählt ist – das angezeigte Build-Datum ändert sich trotzdem.

Dateigröße und PE-Header bleiben unverändert. Luxveil muss vor Direct3D geladen
sein: Es fängt über den GetProcAddress-Zeiger des Clients (VA `0xB2ED98`)
`Direct3DCreate9` ab. Der Lader sitzt deshalb ganz vorne in der Startkette,
noch vor dem Lexara-Lader – so wie früher die Proxy-DLL: Der erste Aufruf am
Einstiegspunkt (VA `0x401000`) zeigt jetzt auf eine freie 16-Byte-Lücke
(VA `0x6D3080`) mit `push "Luxveil.dll"` → `call [LoadLibraryA]` → Sprung zum
Lexara-Lader (falls gewählt) bzw. zu `__security_init_cookie`. Der Name steht
in einer zweiten Lücke (VA `0x6D3214`). Beide Lücken sind kleiner als 24 Byte –
Lux sucht sich zur Laufzeit die erste Lücke ab 24 Byte – und liegen außerhalb
der Stellen, die Luxveil prüft oder umschreibt. Einen Export muss der Lader
nicht aufrufen, Luxveil erledigt alles in `DllMain`. Der Patch verträgt sich
mit den anderen DLL-Ladern (Nr. 27–31 und 33). Von allen anderen Patches
berührt nur „Lichter bleiben an“ (Nr. 71) eine Stelle, die Luxveil prüft – das
ist gewollt: Luxveil setzt dort denselben Sprung und erkennt ihn.

""" % URL, 'en': """<a id="patch-luxveil"></a>
**Load Luxveil.dll at startup (fog, light and water - Atmospheric Immersion for Project Reforged)** *(No. 32, Author: St0ny)* 🟠 **[untested - DLL risky]**

Loads `Luxveil.dll` from the WoW folder at startup –
[Luxveil](%s) (formerly CoAVolFog) brings volumetric
fog, light and water to the 3.3.5a client. So far Luxveil came with a proxy
`version.dll`; with this patch it is no longer needed, and on Wine/Proton
`WINEDLLOVERRIDES` is not needed any more. Luxveil reads `Luxveil.ini`,
`fogdata.bin` and `waterdata.bin` from the WoW folder and writes
`Luxveil.log`. If the DLL is missing, WoW starts normally.

> [!WARNING]
> Still untested, online and in game. That is why the patch is deselected by
> default and only in the `st0ny-dev` branch for now. The patch itself only
> loads a DLL that is not included here – but `Luxveil.dll` may be detected or
> blocked on public servers.

> [!IMPORTANT]
> **Delete the old files:** if the old `CoAVolFog.dll` and its `version.dll`
> are still in the WoW folder, the old DLL loads first and takes the hook
> spots. Luxveil then does not hook in (it says so in `Luxveil.log`), and the
> fog comes from the old DLL. Luxveil's own `version.dll` does no harm, it is
> just not needed with this patch any more: Windows loads `Luxveil.dll` only
> once.

Luxveil recognizes the client by the timestamp in the program header. "Change
build date" (No. 92) therefore leaves this timestamp unchanged when this loader
is selected – the build date shown still changes.

File size and PE header stay unchanged. Luxveil has to be loaded before
Direct3D: it catches `Direct3DCreate9` through the client's GetProcAddress
pointer (VA `0xB2ED98`). That is why the loader sits at the very front of the
startup chain, even before the Lexara loader – just like the proxy DLL before:
the first call at the entry point (VA `0x401000`) now points to a free 16-byte
gap (VA `0x6D3080`) with `push "Luxveil.dll"` → `call [LoadLibraryA]` → jump
to the Lexara loader (if selected) or to `__security_init_cookie`. The name sits
in a second gap (VA `0x6D3214`). Both gaps are smaller than 24 bytes – Lux picks
the first gap of 24 bytes or more at runtime – and lie outside the spots
Luxveil checks or rewrites. The loader does not need to call an export,
Luxveil does everything in `DllMain`. The patch works together with the other
DLL loaders (No. 27–31 and 33). Of all other patches only "Lights stay on"
(No. 71) touches a spot that Luxveil checks – on purpose: Luxveil sets the same
jump there and recognizes it.

""" % URL}
    PAT = {'de': [
        ("Der Patch verträgt sich mit dem\nLexara-Lader (Nr. 30), dem Lux-Lader (Nr. 31) und dem voice.dll-Lader (Nr. 33).\n",
         "Der Patch verträgt sich mit dem\nLexara-Lader (Nr. 30), dem Lux-Lader (Nr. 31), dem Luxveil-Lader (Nr. 32) und\ndem voice.dll-Lader (Nr. 33).\n"),
        ("Der Patch verträgt sich mit\ndem Lux-Lader (Nr. 31) und dem voice.dll-Lader (Nr. 33), die nur spätere\nSprünge im Startcode ändern.\n",
         "Der Patch verträgt sich mit\ndem Lux-Lader (Nr. 31) und dem voice.dll-Lader (Nr. 33), die nur spätere\nSprünge im Startcode ändern. Mit dem Luxveil-Lader (Nr. 32) zeigt der Aufruf\nam Einstiegspunkt zuerst auf dessen Lader, der danach in den Lexara-Lader\nspringt – Luxveil wird also vor Lexara geladen.\n"),
        ("Der Patch verträgt sich mit\ndem wow_optimize-Lader (Nr. 27), dem Lexara-Lader (Nr. 30) und dem\nvoice.dll-Lader (Nr. 33).\n",
         "Der Patch verträgt sich mit\ndem wow_optimize-Lader (Nr. 27), dem Lexara-Lader (Nr. 30), dem Luxveil-Lader\n(Nr. 32) und dem voice.dll-Lader (Nr. 33).\n"),
        ("`Wow.exe` anzeigen (Original 25.06.2010 06:55:58 UTC). Datum und Uhrzeit gelten\nals Ortszeit des Rechners, auf dem du patchst.\n",
         "`Wow.exe` anzeigen (Original 25.06.2010 06:55:58 UTC). Datum und Uhrzeit gelten\nals Ortszeit des Rechners, auf dem du patchst. Mit dem Luxveil-Lader (Nr. 32)\nbleibt dieser Zeitstempel unverändert: Luxveil erkennt den Client daran und\nschaltet sich sonst ab. Das angezeigte Build-Datum ändert sich trotzdem.\n"),
    ], 'en': [
        ("The patch works together with the Lexara loader (No. 30), the\nLux loader (No. 31) and the voice.dll loader (No. 33).\n",
         "The patch works together with the Lexara loader (No. 30), the\nLux loader (No. 31), the Luxveil loader (No. 32) and the voice.dll loader\n(No. 33).\n"),
        ("The\npatch works together with the Lux loader (No. 31) and the voice.dll loader\n(No. 33), which only change later jumps in the startup code.\n",
         "The\npatch works together with the Lux loader (No. 31) and the voice.dll loader\n(No. 33), which only change later jumps in the startup code. With the Luxveil\nloader (No. 32) the call at the entry point first points to its loader, which\nthen jumps to the Lexara loader – so Luxveil is loaded before Lexara.\n"),
        ("The\npatch works together with the wow_optimize loader (No. 27), the Lexara loader\n(No. 30) and the voice.dll loader (No. 33).\n",
         "The\npatch works together with the wow_optimize loader (No. 27), the Lexara loader\n(No. 30), the Luxveil loader (No. 32) and the voice.dll loader (No. 33).\n"),
        ("time of `Wow.exe` (original 2010-06-25 06:55:58 UTC). Date and time are taken\nas local time of the computer you patch on.\n",
         "time of `Wow.exe` (original 2010-06-25 06:55:58 UTC). Date and time are taken\nas local time of the computer you patch on. With the Luxveil loader (No. 32)\nthis timestamp stays unchanged: Luxveil recognizes the client by it and turns\nitself off otherwise. The build date shown still changes.\n"),
    ]}
    ROW = {'de': '| [32](PATCHES.de.md#patch-luxveil) | Luxveil.dll beim Start laden (Nebel, Licht und Wasser - Atmospheric Immersion for Project Reforged) *(benötigt [Luxveil](%s) – ohne `version.dll`; alte `CoAVolFog.dll` und `version.dll` löschen)* | 🟠 **[ungetestet - DLL riskant]** | St0ny | – | – | – |\n' % URL,
           'en': '| [32](PATCHES.en.md#patch-luxveil) | Load Luxveil.dll at startup (fog, light and water - Atmospheric Immersion for Project Reforged) *(requires [Luxveil](%s) – no `version.dll` needed; delete the old `CoAVolFog.dll` and `version.dll`)* | 🟠 **[untested - DLL risky]** | St0ny | – | – | – |\n' % URL}
    # Listen unter "Hinweise" (nach dem Verschieben): Nr. 32 dazu; Signatur-Absatz um Nr. 94 (Debug-Log) ergaenzt
    LEG = {'de': [
        ("kann zu Kick/Bann führen: Nr. 10, 26, 33,", "kann zu Kick/Bann führen: Nr. 10, 26, 32, 33,"),
        ("möglicherweise verbuggt: Nr. 25, 26, 33,", "möglicherweise verbuggt: Nr. 25, 26, 32, 33,"),
        ("auf öffentlichen Servern erkannt oder blockiert werden kann: Nr. 27–31\n",
         "auf öffentlichen Servern erkannt oder blockiert werden kann: Nr. 27–32\n"),
        ("Die Patches, die eine Sektion anhängen (Nr. 9, 54, 67–70, 81 und 87), entfernen",
         "Die Patches, die eine Sektion anhängen (Nr. 9, 54, 67–70, 81, 87 und 94), entfernen"),
    ], 'en': [
        ("you kicked or banned: No. 10, 26, 33,", "you kicked or banned: No. 10, 26, 32, 33,"),
        ("possibly buggy: No. 25, 26, 33,", "possibly buggy: No. 25, 26, 32, 33,"),
        ("detected or blocked on public servers: No. 27–31 (yellow note).",
         "detected or blocked on public servers: No. 27–32 (yellow note)."),
        ("(No. 9, 54, 67–70, 81 and 87) also remove the reference to the",
         "(No. 9, 54, 67–70, 81, 87 and 94) also remove the reference to the"),
    ]}
    for lang, rdm, pdm in (('de', 'README.de.md', 'PATCHES.de.md'), ('en', 'README.md', 'PATCHES.en.md')):
        p = os.path.join(D, 'docs', pdm); s = rd(p)
        s = shift_refs(s, '–')
        for a, b in PAT[lang]: s = once(s, a, b, pdm)
        s = once(s, '<a id="patch-voicedll"></a>', SEC[lang] + '<a id="patch-voicedll"></a>', pdm)
        wr(p, s)
        p = os.path.join(D, 'docs', rdm); s = rd(p)
        s = shift_refs(s, '–')
        s = re.sub(r'(?m)^\| \[(\d+)\]\(%s#' % re.escape(pdm), lambda m: '| [%s](%s#' % (sh(m.group(1)), pdm), s)
        s = re.sub(r'\[#(\d+)\]\(%s#' % re.escape(pdm), lambda m: '[#%s](%s#' % (sh(m.group(1)), pdm), s)   # Danksagung
        for a, b in LEG[lang]: s = once(s, a, b, rdm)
        m = re.search(r'(?m)^\| \[31\]\(%s#patch-lux\).*\n' % re.escape(pdm), s)
        assert m
        s = s[:m.end()] + ROW[lang] + s[m.end():]
        wr(p, s)
    print('docs ok')
