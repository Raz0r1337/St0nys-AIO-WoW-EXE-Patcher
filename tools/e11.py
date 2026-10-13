import re
# Texte
R("""        Obsolete      = 'macht diese Patches ueberfluessig (beide zusammen schaden nicht):'
""", """        Obsolete      = 'macht diese Patches ueberfluessig (beide zusammen schaden nicht):'
        Conflict      = 'nutzt dieselbe Code-Hoehle wie diese Patches und weicht darum auf eine eigene Sektion am Dateiende aus:'
""")
R("""        Obsolete      = 'makes these patches unnecessary (both together do no harm):'
""", """        Obsolete      = 'makes these patches unnecessary (both together do no harm):'
        Conflict      = 'uses the same code cave as these patches and therefore moves to a section of its own at the end of the file:'
""")
R("""#    Needs - optional: Ids von Patches, ohne die dieser nicht voll wirkt
""", """#    Conflicts - optional: Ids von Patches, die dieselbe Code-Hoehle nutzen;
#            sind sie gewaehlt, weicht dieser Patch auf eine eigene Sektion aus
#            (erzeugt einen Hinweis)
#    Needs - optional: Ids von Patches, ohne die dieser nicht voll wirkt
""")
R("""    if ($both.Count -gt 0) {
        Write-Host ''
        Say (T 'HintHead' (PatchName $p)) 'Yellow'
        Say (T 'Obsolete') 'Yellow'
        foreach ($m in $both) { Say "  - $m" 'Yellow' }
    }
}
""", """    if ($both.Count -gt 0) {
        Write-Host ''
        Say (T 'HintHead' (PatchName $p)) 'Yellow'
        Say (T 'Obsolete') 'Yellow'
        foreach ($m in $both) { Say "  - $m" 'Yellow' }
    }
}
foreach ($p in $chosen) {
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
    }
}
""")
# Funktionen ersetzen
i=s.index("# ============================================================\n#  WorldFrame-Absturzfix (0x539wowmod, Alyst3r)")
j=s.index("# ============================================================\n#  Helfer fuer den Sprunghoehen-Patch")
s=s[:i]+r"""# ============================================================
#  Code-Hoehle am Ende von .text
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
    $off = $TEXT_CAVE[$Id]
    for ($i = 0; $i -lt $Size; $i++) {
        if ($script:f[$off + $i] -ne 0) { throw ('Code-Hoehle bei 0x{0:X} ist belegt.' -f ($off + $i)) }
    }
    # VirtualSize von .text bis hinter die Hoehle anheben, damit der Lader sie
    # sicher mit einblendet (bleibt innerhalb von SizeOfRawData).
    $e = RU32 $script:f 0x3C
    $text = $e + 24 + (RU16 $script:f ($e + 20))
    $need = $off + $Size - (RU32 $script:f ($text + 20))
    if ((RU32 $script:f ($text + 8)) -lt $need) { Patch ($text + 8) ([BitConverter]::GetBytes([uint32]$need)) }
    return , @(($off + 0x400C00), $off)
}

# Relativer Sprung/Aufruf: Opcode + rel32 von $FromVA nach $ToVA.
function Get-Rel32([byte[]]$Op, [int64]$FromVA, [int64]$ToVA) {
    $b = New-Object byte[] ($Op.Length + 4)
    [Array]::Copy($Op, 0, $b, 0, $Op.Length)
    [Array]::Copy([BitConverter]::GetBytes([int32]($ToVA - ($FromVA + $b.Length))), 0, $b, $Op.Length, 4)
    return , $b
}

function Assert-Bytes([int64]$Off, [byte[]]$Expected, [string]$What) {
    for ($i = 0; $i -lt $Expected.Length; $i++) {
        if ($script:f[$Off + $i] -ne $Expected[$i]) { throw "${What}: Code bei Datei 0x$('{0:X}' -f $Off) unbekannt." }
    }
}

# ============================================================
#  WorldFrame-Absturzfix (0x539wowmod, Alyst3r)
#  Die Funktion bei VA 0x81D510 laeuft ueber Dreiecke aus Index-Tripeln
#  (WORDs) und rechnet Index minus Basis ([ebp+10h]) in eine Vertex-Adresse
#  um. Ist ein Index kleiner als die Basis, landet die Adresse vor dem Puffer
#  und der Client stuerzt ab. Die Hoehle prueft die drei Indizes des ersten
#  Dreiecks und springt in dem Fall zum Funktionsende (VA 0x81D66E).
#  Einstieg ist das jae bei VA 0x81D51B, das genau dorthin springt (leere
#  Liste) - es wird in der Hoehle nachgebildet, der Stack ist derselbe.
#  edx ist hier frei (wird erst bei VA 0x81D547 gesetzt).
#  Neu umgesetzt: Im Original sind die Sprungweiten der drei jg falsch
#  berechnet, ausserdem ist diese Form kuerzer (38 statt 59 Byte).
# ============================================================
function Add-WorldFrameCrashFix {
    $HOOK_VA = 0x81D51B; $BACK_VA = 0x81D521; $EXIT_VA = 0x81D66E
    Assert-Bytes ($HOOK_VA - 0x400C00) @(0x0F, 0x83, 0x4D, 0x01, 0x00, 0x00) 'WorldFrame-Absturzfix'
    $cave = Get-CodeCave 'worldcrash' 38 '.wfcfix'
    $CAVE = $cave[0]
    $c = New-Object System.Collections.Generic.List[byte]
    AddRaw $c @(0x73, 0x1F)                      # jae Ausgang (leere Liste, wie im Original)
    AddRaw $c @(0x8B, 0x55, 0x10)                # mov edx, [ebp+10h]   (Basis)
    AddRaw $c @(0x0F, 0xB7, 0x07)                # movzx eax, word [edi]
    AddRaw $c @(0x3B, 0xD0, 0x7F, 0x15)          # cmp edx, eax / jg Ausgang
    AddRaw $c @(0x0F, 0xB7, 0x47, 0x02)          # movzx eax, word [edi+2]
    AddRaw $c @(0x3B, 0xD0, 0x7F, 0x0D)          # cmp edx, eax / jg Ausgang
    AddRaw $c @(0x0F, 0xB7, 0x47, 0x04)          # movzx eax, word [edi+4]
    AddRaw $c @(0x3B, 0xD0, 0x7F, 0x05)          # cmp edx, eax / jg Ausgang
    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $BACK_VA)     # jmp zurueck
    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $EXIT_VA)     # Ausgang: jmp Funktionsende
    if ($c.Count -ne 38) { throw 'WorldFrame-Absturzfix: Hoehle hat die falsche Groesse.' }
    Patch $cave[1] $c.ToArray()
    $hook = (Get-Rel32 @(0xE9) $HOOK_VA $CAVE) + [byte[]](0x90)
    Patch ($HOOK_VA - 0x400C00) ([byte[]]$hook)
}

# ============================================================
#  Kein Ausblenden fuer NPCs mit UNIT_FLAG2_DO_NOT_FADE_IN (0x539wowmod, Alyst3r)
#  Beim Entfernen eines Objekts (Funktion bei VA 0x743D50) blendet der
#  Client das Modell normalerweise aus. Die Hoehle prueft vorher: Ist es
#  ein CGUnit (vtable 0xA34D90, Spieler haben eine eigene) und ist in
#  UNIT_FIELD_FLAGS_2 das Bit 0x20 (DO_NOT_FADE_IN) gesetzt, geht es direkt
#  zum Zweig ohne Ausblenden (VA 0x743DE3), sonst normal weiter. Das Flag
#  muss der Server setzen. Ersetzt werden die 5 Byte "mov eax, [esi] /
#  mov edx, [eax+40h]" bei VA 0x743DA3; edx ist bis dahin frei.
# ============================================================
function Add-NoFadeOutFlag {
    $HOOK_VA = 0x743DA3; $BACK_VA = 0x743DA8; $NOFADE_VA = 0x743DE3
    Assert-Bytes ($HOOK_VA - 0x400C00) @(0x8B, 0x06, 0x8B, 0x50, 0x40) 'NPC-Ausblenden'
    $cave = Get-CodeCave 'nofade' 37 '.nofade'
    $CAVE = $cave[0]
    $c = New-Object System.Collections.Generic.List[byte]
    AddRaw $c @(0x8B, 0x06)                                  # mov eax, [esi]          (Original)
    AddRaw $c @(0x3D); AddLE32 $c 0xA34D90                   # cmp eax, CGUnit-vtable
    AddRaw $c @(0x75, 0x0F)                                  # jne normal
    AddRaw $c @(0x8B, 0x96, 0xD0, 0x00, 0x00, 0x00)          # mov edx, [esi+0D0h]     (Unit-Felder)
    AddRaw $c @(0xF6, 0x82, 0xD8, 0x00, 0x00, 0x00, 0x20)    # test byte [edx+0D8h], 20h (FLAGS_2)
    AddRaw $c @(0x75, 0x08)                                  # jnz ohne Ausblenden
    AddRaw $c @(0x8B, 0x50, 0x40)                            # normal: mov edx, [eax+40h] (Original)
    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $BACK_VA)     # jmp zurueck
    AddRaw $c (Get-Rel32 @(0xE9) ($CAVE + $c.Count) $NOFADE_VA)   # jmp ohne Ausblenden
    if ($c.Count -ne 37) { throw 'NPC-Ausblenden: Hoehle hat die falsche Groesse.' }
    Patch $cave[1] $c.ToArray()
    Patch ($HOOK_VA - 0x400C00) (Get-Rel32 @(0xE9) $HOOK_VA $CAVE)
}

"""+s[j:]
# Get-JmpPatch entfernen (nicht mehr gebraucht)
a=s.index("# Sprung von $FromVA zur Code-Hoehle: E9 rel32, Rest bis $Len mit NOPs.")
b=s.index("# ============================================================\n#  Code-Hoehle am Ende von .text")
s=s[:a]+s[b:]
# Patch-Definitionen
R("""    @{ Id = 'worldcrash'; Cat = 'system'; On = $false
       Author = 'Alyst3r (0x539wowmod) / St0ny'
       De = 'WorldFrame-Absturzfix (ungueltige Dreiecks-Indizes)'
       En = 'WorldFrame crash fix (invalid triangle indices)'
       Code = {
        # Haengt eine kleine Code-Sektion an (.wfcfix), siehe Add-WorldFrameCrashFix.
""", """    @{ Id = 'worldcrash'; Cat = 'system'; On = $false; Conflicts = @('sliders')
       Author = 'Alyst3r (0x539wowmod) / St0ny'
       De = 'WorldFrame-Absturzfix (ungueltige Dreiecks-Indizes)'
       En = 'WorldFrame crash fix (invalid triangle indices)'
       NoteDe = 'teilt Code-Hoehle mit Slider-Patch'
       NoteEn = 'shares code cave with the slider patch'
       Code = {
        # Code-Hoehle am Ende von .text, mit Slider-Patch eigene Sektion
        # (.wfcfix), siehe Get-CodeCave / Add-WorldFrameCrashFix.
""")
R("""    @{ Id = 'nofade'; Cat = 'graphics'; On = $false
       Author = 'Alyst3r (0x539wowmod) / St0ny'
       De = 'Kein Ausblenden fuer NPCs mit Flag DO_NOT_FADE_IN'
       En = 'No fade-out for NPCs with flag DO_NOT_FADE_IN'
       NoteDe = 'Server muss das Flag setzen'
       NoteEn = 'server must set the flag'
       Code = {
        # Haengt eine kleine Code-Sektion an (.nofade), siehe Add-NoFadeOutFlag.
""", """    @{ Id = 'nofade'; Cat = 'graphics'; On = $false; Conflicts = @('sliders')
       Author = 'Alyst3r (0x539wowmod) / St0ny'
       De = 'Kein Ausblenden fuer NPCs mit Flag DO_NOT_FADE_IN'
       En = 'No fade-out for NPCs with flag DO_NOT_FADE_IN'
       NoteDe = 'Server muss das Flag setzen, teilt Code-Hoehle mit Slider-Patch'
       NoteEn = 'server must set the flag, shares code cave with the slider patch'
       Code = {
        # Code-Hoehle am Ende von .text, mit Slider-Patch eigene Sektion
        # (.nofade), siehe Get-CodeCave / Add-NoFadeOutFlag.
""")
R("""        # VA 0x4E147B: je -> jmp, die automatischen Zufallsaufrufe beim Oeffnen
        # bzw. Volk-/Klassenwechsel werden uebersprungen. Der Zufall-Knopf
""", """        # VA 0x4E147B: je -> jmp, die automatischen Zufallsaufrufe beim Oeffnen
        # (ResetCharCustomize) bzw. Volk-/Geschlechtswechsel werden
        # uebersprungen. Der Zufall-Knopf
""")
