# --- texts: Conflict lines out ---
R('''        Conflict      = 'nutzt dieselbe Code-Hoehle wie diese Patches und weicht darum auf eine eigene Sektion am Dateiende aus (die Wow.exe wird dadurch etwas groesser):'
        ConflictBan   = 'Zusammen funktionieren sie, aber viele Server tolerieren eine veraenderte Groesse der Wow.exe nicht - das kann zu einem Bann fuehren!'
''','')
R('''        Conflict      = 'uses the same code cave as these patches and therefore moves to a section of its own at the end of the file (Wow.exe becomes slightly larger):'
        ConflictBan   = 'They work together, but many servers do not tolerate a changed size of Wow.exe - this can lead to a ban!'
''','')
# --- watermark comment reflow ---
R('''#  Nebeneffekt. Er steht im Fuellbereich
#  hinter der .tls-Sektion (Datei 0x72DE19-0x72DFFF, 487 Byte Nullen):
#  ausserhalb der VirtualSize, wird also nie geladen, und kein Patch nutzt
#  diesen Bereich. Die Dateigroesse bleibt gleich. Geschrieben wird ueber
#  Patch(), beim Zuruecknehmen verschwindet das Wasserzeichen also wieder.''',
'''#  Nebeneffekt. Der Text steht im Fuellbereich hinter der .tls-Sektion (Datei
#  0x72DE19-0x72DFFF, 487 Byte Nullen): ausserhalb der VirtualSize, wird also
#  nie geladen, und kein Patch nutzt diesen Bereich. Die Dateigroesse bleibt
#  gleich. Geschrieben wird ueber Patch(), beim Zuruecknehmen verschwindet das
#  Wasserzeichen also wieder.''')
# --- Add-CodeSection comment ---
R('''#  Genutzt vom Doppelsprung (braucht beschreibbaren Speicher) und als
#  Ausweichmodus von WorldFrame-Absturzfix und NPC-Ausblenden, wenn der
#  Slider-Patch die Luecke in .text belegt (siehe Get-CodeCave).
#  Liefert @(VA der Sektion, Dateioffset der Sektion).''',
'''#  Genutzt vom Doppelsprung, der beschreibbaren Speicher braucht.
#  Liefert @(VA der Sektion, Dateioffset der Sektion).''')
# --- code cave block ---
R('''#  Code-Hoehle am Ende von .text
#  Hinter dem Code von .text liegen 77 freie Bytes (Datei 0x5DD7B3-0x5DD7FF,
#  Nullen). Der Slider-Patch legt dort seinen Code ab (0x5DD7B8-0x5DD7E2).
#  WorldFrame-Absturzfix (38 Byte) und NPC-Ausblenden (37 Byte) passen
#  zusammen ebenfalls hinein - aber nicht neben den Slider-Patch. Ist der
#  Slider-Patch gewaehlt, weichen beide automatisch auf eine eigene kleine
#  Sektion am Dateiende aus (Ausweichmodus, siehe Add-CodeSection).
#  Liefert @(VA, Dateioffset) der Hoehle.
# ============================================================
$TEXT_CAVE = @{ worldcrash = 0x5DD7B3; nofade = 0x5DD7D9 }

function Get-CodeCave([string]$Id, [int]$Size, [string]$SectionName) {
    if ($script:chosenIds -contains 'sliders') { return , (Add-CodeSection $SectionName $Size) }
    $off = $TEXT_CAVE[$Id]''',
'''#  Code-Hoehle am Ende von .text
#  Hinter dem Code von .text liegen 77 freie Bytes (Datei 0x5DD7B3-0x5DD7FF,
#  Nullen). WorldFrame-Absturzfix (38 Byte) und NPC-Ausblenden (37 Byte)
#  teilen sie sich. Liefert @(VA, Dateioffset) der Hoehle.
# ============================================================
$TEXT_CAVE = @{ worldcrash = 0x5DD7B3; nofade = 0x5DD7D9 }

function Get-CodeCave([string]$Id, [int]$Size) {
    $off = $TEXT_CAVE[$Id]''')
R("    $loc = Get-CodeCave 'worldcrash' 38 '.wfcfix'\n", "    $loc = Get-CodeCave 'worldcrash' 38\n")
R("    $loc = Get-CodeCave 'nofade' 37 '.nofade'\n", "    $loc = Get-CodeCave 'nofade' 37\n")
# --- BuildTable config ---
R('''#  Spielt auf Kopien der originalen Wow.exe alle Patches ein - alle
#  zusammen, alle ohne Slider-Patch (Code-Hoehle in .text) und jeden
#  einzeln (Sektionsheader an der ersten freien Stelle) - und merkt sich je''',
'''#  Spielt auf Kopien der originalen Wow.exe alle Patches ein - alle
#  zusammen und jeden einzeln (Sektionsheader an der ersten freien Stelle) -
#  und merkt sich je''')
R('''    $configs.Add($allIds)
    $configs.Add(@($allIds | Where-Object { $_ -ne 'sliders' }))
''','''    $configs.Add($allIds)
''')
# --- field doc ---
R('''#    Conflicts - optional: Ids von Patches, die dieselbe Code-Hoehle nutzen;
#            sind sie gewaehlt, weicht dieser Patch auf eine eigene Sektion aus
#            (erzeugt einen Hinweis)
''','')
# --- worldcrash entry ---
R('''    @{ Id = 'worldcrash'; Cat = 'system'; On = $false; Conflicts = @('sliders')
       Author = 'Alyst3r (0x539wowmod) / St0ny'
       De = 'WorldFrame-Absturzfix (ungueltige Dreiecks-Indizes)'
       En = 'WorldFrame crash fix (invalid triangle indices)'
       NoteDe = 'teilt Code-Hoehle mit Slider-Patch; zusammen wird die Exe groesser - Bann-Gefahr'
       NoteEn = 'shares code cave with the slider patch; together the exe grows - ban risk'
       Code = {
        # Code-Hoehle am Ende von .text, mit Slider-Patch eigene Sektion
        # (.wfcfix), siehe Get-CodeCave / Add-WorldFrameCrashFix.
        Add-WorldFrameCrashFix''',
'''    @{ Id = 'worldcrash'; Cat = 'system'; On = $false
       Author = 'Alyst3r (0x539wowmod) / St0ny'
       De = 'WorldFrame-Absturzfix (ungueltige Dreiecks-Indizes)'
       En = 'WorldFrame crash fix (invalid triangle indices)'
       Code = {
        # Code-Hoehle am Ende von .text, siehe Get-CodeCave / Add-WorldFrameCrashFix.
        Add-WorldFrameCrashFix''')
# --- nofade entry ---
R('''    @{ Id = 'nofade'; Cat = 'graphics'; On = $false; Conflicts = @('sliders')
       Author = 'Alyst3r (0x539wowmod) / St0ny'
       De = 'Kein Ausblenden fuer NPCs mit Flag DO_NOT_FADE_IN'
       En = 'No fade-out for NPCs with flag DO_NOT_FADE_IN'
       NoteDe = 'Server muss das Flag setzen, teilt Code-Hoehle mit Slider-Patch; zusammen wird die Exe groesser - Bann-Gefahr'
       NoteEn = 'server must set the flag, shares code cave with the slider patch; together the exe grows - ban risk'
       Code = {
        # Code-Hoehle am Ende von .text, mit Slider-Patch eigene Sektion
        # (.nofade), siehe Get-CodeCave / Add-NoFadeOutFlag.
        Add-NoFadeOutFlag''',
'''    @{ Id = 'nofade'; Cat = 'graphics'; On = $false
       Author = 'Alyst3r (0x539wowmod) / St0ny'
       De = 'Kein Ausblenden fuer NPCs mit Flag DO_NOT_FADE_IN'
       En = 'No fade-out for NPCs with flag DO_NOT_FADE_IN'
       NoteDe = 'Server muss das Flag setzen'
       NoteEn = 'server must set the flag'
       Code = {
        # Code-Hoehle am Ende von .text, siehe Get-CodeCave / Add-NoFadeOutFlag.
        Add-NoFadeOutFlag''')
# --- follow comment ---
R('''        # ignoriert und immer zum Erfolgsweg 0x72B546 springt. Diese Hoehle liegt
        # im .text-Padding bei 0x9DE3B8 - genau dort, wo der Slider-Patch seine
        # Such-Routine ablegt; beide zusammen waeren nicht moeglich.''',
'''        # ignoriert und immer zum Erfolgsweg 0x72B546 springt. Diese Hoehle laege
        # im .text-Padding bei 0x9DE3B8 - genau dort, wo WorldFrame-Absturzfix
        # und NPC-Ausblenden ihre Code-Hoehlen haben.''')
# --- areatrigger ---
R('''       De = 'Area-Trigger-Timer genauer (50 ms statt 250 ms)'
       En = 'More precise area trigger timer (50 ms instead of 250 ms)'
       Code = {
        Patch 0x2DB241 @(0x32)''',
'''       De = 'Area-Trigger-Timer genauer (50 ms statt 100 ms)'
       En = 'More precise area trigger timer (50 ms instead of 100 ms)'
       Code = {
        # push 64h -> push 32h: Intervall des Area-Trigger-Timers (VA 0x6DBE40)
        Patch 0x2DB241 @(0x32)''')
# --- sliders: text in the explanation about search routine + patch bytes ---
R('''        # WAS DER PATCH TUT
        # In beiden Funktionen wird der farclip-Vergleich durch einen Aufruf einer
        # gemeinsamen Such-Routine ersetzt, die eine Tabelle {Name, Maximum}
        # durchlaeuft. Treffer -> Wert auf den FPU-Stack und weiter im vorhandenen
        # lua_pushnumber-Pfad. Kein Treffer -> in den vorhandenen nil-Pfad, alle
        # uebrigen CVars verhalten sich also unveraendert.''',
'''        # WAS DER PATCH TUT
        # In beiden Funktionen wird der farclip-Vergleich durch einen Aufruf einer
        # gemeinsamen Such-Routine ersetzt, die eine Namensliste durchlaeuft.
        # Treffer -> zugehoeriges Maximum auf den FPU-Stack und weiter im
        # vorhandenen lua_pushnumber-Pfad. Kein Treffer -> in den vorhandenen
        # nil-Pfad, alle uebrigen CVars verhalten sich also unveraendert.
        # Die Dateigroesse bleibt gleich, und die Code-Hoehle am Ende von .text
        # bleibt frei fuer WorldFrame-Absturzfix und NPC-Ausblenden.''')
R('''        # 1) Such-Routine im .text-Padding (VA 0x9DE3B8, 77 freie Bytes ab
        #    0x5DD7B3). Eingang esi = CVar-Name aus dem CVar-Objekt ([obj+0x14]),
        #    Ausgang eax = Zeiger auf den Tabelleneintrag oder 0.
        #    [ebp-4] ist der freie Slot aus dem Prolog beider Funktionen und
        #    dient als Laufzeiger; ebx/edi bleiben unberuehrt, damit beide
        #    Aufrufer ihren Lua-State behalten.
        #      mov  dword [ebp-4], 0xAB5680     Tabellenanfang
        #    L:mov  eax, [ebp-4]
        #      mov  ecx, [eax]                  Namenszeiger
        #      test ecx, ecx / je notfound      0x00000000 = Endmarke
        #      push 0x7FFFFFFF / push ecx / push esi
        #      call SStrCmpI (0x76E780)         stdcall, raeumt selbst auf
        #      test eax, eax / je hit
        #      add  dword [ebp-4], 12 / jmp L
        #    hit:      mov eax, [ebp-4] / ret
        #    notfound: xor eax, eax / ret
        Patch 0x5DD7B8 @(0xC7, 0x45, 0xFC, 0x80, 0x56, 0xAB, 0x00, 0x8B, 0x45, 0xFC, 0x8B, 0x08, 0x85, 0xC9, 0x74, 0x1A, 0x68, 0xFF, 0xFF, 0xFF, 0x7F, 0x51, 0x56, 0xE8, 0xAC, 0x03, 0xD9, 0xFF, 0x85, 0xC0, 0x74, 0x06, 0x83, 0x45, 0xFC, 0x0C, 0xEB, 0xE1, 0x8B, 0x45, 0xFC, 0xC3, 0x33, 0xC0, 0xC3)

        # 2) Aufrufstelle im Glue-Screen: ersetzt den farclip-Vergleich bei
        #    0x4DE046. 21 Byte Stub, Rest bis 0x4DE060 mit int3 gefuellt.
        #      call 0x9DE3B8 / test eax,eax / je 0x4DE07A (nil-Pfad)
        #      fld qword [eax+4] / jmp 0x4DE060 (lua_pushnumber-Pfad)
        Patch 0xDD446 @(0xE8, 0x6D, 0x03, 0x50, 0x00, 0x85, 0xC0, 0x0F, 0x84, 0x27, 0x00, 0x00, 0x00, 0xDD, 0x40, 0x04, 0xE9, 0x05, 0x00, 0x00, 0x00, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC)

        # 3) Dieselbe Aufrufstelle im Spiel, bei 0x514EEA. Gleicher Stub, nur
        #    andere Ziele: nil-Pfad 0x514F1E, Fortsetzung 0x514F04.
        Patch 0x1142EA @(0xE8, 0xC9, 0x94, 0x4C, 0x00, 0x85, 0xC0, 0x0F, 0x84, 0x27, 0x00, 0x00, 0x00, 0xDD, 0x40, 0x04, 0xE9, 0x05, 0x00, 0x00, 0x00, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC)

        # 4) Tabelle im .rdata-Padding (VA 0xAB5680, 384 freie Bytes ab 0x6B3E80).
        #    Je 12 Byte: char* Name, double Maximum. Endmarke 0x00000000.
        #    Als Namen dienen die CVar-Namen, die ohnehin in der EXE stehen:
        #      0x9F57A0 "farclip"              2477.0
        #      0xA3F3BC "environmentDetail"       2.5
        #      0xA3F438 "groundEffectDist"      250.0
        #      0xA3F460 "groundEffectDensity"   256.0
        Patch 0x6B3E80 @(0xA0, 0x57, 0x9F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x5A, 0xA3, 0x40, 0xBC, 0xF3, 0xA3, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x40, 0x38, 0xF4, 0xA3, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x40, 0x6F, 0x40, 0x60, 0xF4, 0xA3, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x70, 0x40, 0x00, 0x00, 0x00, 0x00)''',
'''        # 1) Such-Routine in einer 19-Byte-int3-Luecke zwischen zwei Funktionen
        #    (VA 0x9296ED, Datei 0x528AED; nichts springt dorthin). 18 Byte.
        #    Eingang: ebx = CVar-Name (aus dem CVar-Objekt, [obj+0x14]),
        #    esi = Anfang der Namensliste. Ausgang: esi steht hinter dem
        #    gefundenen Namen bzw. hinter der Endmarke; die Stubs lesen
        #    [esi-4] (0 = Endmarke) und das Maximum bei [esi+16].
        #    Als Laengenlimit fuer SStrCmpI dient esi selbst - eine feste
        #    Adresse in .rdata, also immer unter 0x7FFFFFFF (die CRT lehnt
        #    groessere Werte ab) und weit laenger als jeder CVar-Name.
        #    SStrCmpI (stdcall, raeumt selbst auf) erhaelt ebx/esi/edi.
        #    L:lodsd                           eax = Namenszeiger, esi += 4
        #      test eax, eax / jz R            0x00000000 = Endmarke
        #      push esi / push eax / push ebx
        #      call SStrCmpI (0x76E780)
        #      test eax, eax / jnz L           0 = Treffer
        #    R:ret
        Patch 0x528AED @(0xAD, 0x85, 0xC0, 0x74, 0x0C, 0x56, 0x50, 0x53, 0xE8, 0x86, 0x50, 0xE4, 0xFF, 0x85, 0xC0, 0x75, 0xEF, 0xC3)

        # 2) Aufrufstelle im Glue-Screen: ersetzt den farclip-Vergleich bei
        #    0x4DE046 (26 Byte). esi (der Name) ist danach tot, ebx wird
        #    gesichert - im Spiel haelt es den Lua-State. eax/ecx/edx waren
        #    schon im Original durch den SStrCmpI-Aufruf verbraucht.
        #      push ebx / mov ebx, esi / mov esi, 0xAB5680 (Namensliste)
        #      call 0x9296ED / pop ebx
        #      cmp dword [esi-4], 0 / je 0x4DE07A (nil-Pfad)
        #      fld dword [esi+16] / 3x nop -> 0x4DE060 (lua_pushnumber-Pfad)
        Patch 0xDD446 @(0x53, 0x8B, 0xDE, 0xBE, 0x80, 0x56, 0xAB, 0x00, 0xE8, 0x9A, 0xB6, 0x44, 0x00, 0x5B, 0x83, 0x7E, 0xFC, 0x00, 0x74, 0x20, 0xD9, 0x46, 0x10, 0x90, 0x90, 0x90)

        # 3) Dieselbe Aufrufstelle im Spiel, bei 0x514EEA. Gleicher Stub, nur
        #    andere Ziele: nil-Pfad 0x514F1E, Fortsetzung 0x514F04.
        Patch 0x1142EA @(0x53, 0x8B, 0xDE, 0xBE, 0x80, 0x56, 0xAB, 0x00, 0xE8, 0xF6, 0x47, 0x41, 0x00, 0x5B, 0x83, 0x7E, 0xFC, 0x00, 0x74, 0x20, 0xD9, 0x46, 0x10, 0x90, 0x90, 0x90)

        # 4) Tabelle im .rdata-Padding (VA 0xAB5680, 384 freie Bytes ab 0x6B3E80,
        #    hinter der VirtualSize, aber innerhalb der Rohdaten - der Lader
        #    blendet die ganze Seite ein). Erst fuenf Namenszeiger (der letzte
        #    0x00000000 = Endmarke), dahinter die vier Maxima als float, in
        #    derselben Reihenfolge: Maximum i liegt 16 Byte hinter Name i+1.
        #    Als Namen dienen die CVar-Namen, die ohnehin in der EXE stehen:
        #      0x9F57A0 "farclip"              2477.0
        #      0xA3F3BC "environmentDetail"       2.5
        #      0xA3F438 "groundEffectDist"      250.0
        #      0xA3F460 "groundEffectDensity"   256.0
        Patch 0x6B3E80 @(0xA0, 0x57, 0x9F, 0x00, 0xBC, 0xF3, 0xA3, 0x00, 0x38, 0xF4, 0xA3, 0x00, 0x60, 0xF4, 0xA3, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xD0, 0x1A, 0x45, 0x00, 0x00, 0x20, 0x40, 0x00, 0x00, 0x7A, 0x43, 0x00, 0x00, 0x80, 0x43)''')
# --- Conflicts hint block in main flow ---
R('''foreach ($p in $chosen) {
    if (-not $p.Conflicts) { continue }
    $both = @()
    foreach ($id in $p.Conflicts) {
        if ($chosenIds -contains $id) { $both += Get-NameById $id }
    }
    if ($both.Count -gt 0) {
        Write-Host ''
        Say (T 'HintHead' (PatchName $p)) 'Yellow'
        Say (T 'Conflict') 'Yellow'
        foreach ($m in $both) { Say "  - $m" 'Yellow' }
        Say (T 'ConflictBan') 'Red'
    }
}
''','')
