R("""# ============================================================
#  Helfer fuer den Sprunghoehen-Patch
""", r"""# ============================================================
#  Eigene Code-Sektion fuer kleine Code-Hoehlen
#  In .text gibt es keine freie Luecke mehr, die gross genug und nicht schon
#  von einem anderen Patch belegt ist. Patches mit Code-Hoehle bekommen darum
#  wie HD-Portraits und CameraReforged eine eigene Sektion am Dateiende:
#  Padding bis FileAlignment, Sektion anhaengen, PE-Header anpassen
#  (NumberOfSections, SizeOfImage, neuer Sektionsheader, ausfuehrbar).
#  Liefert @(VA der Sektion, Dateioffset der Sektion).
# ============================================================
function Add-CodeSection([string]$Name, [int]$Size) {
    $e = RU32 $script:f 0x3C
    $nsec = RU16 $script:f ($e + 6)
    $opt = RU16 $script:f ($e + 20)
    $IB = RU32 $script:f ($e + 24 + 28)
    $SA = RU32 $script:f ($e + 24 + 32)
    $FA = RU32 $script:f ($e + 24 + 36)
    $sectBase = $e + 24 + $opt
    $lastSo = $sectBase + 40 * ($nsec - 1)
    $new_rva = AlignUp ((RU32 $script:f ($lastSo + 12)) + (RU32 $script:f ($lastSo + 8))) $SA
    $hoff = $sectBase + 40 * $nsec
    if (($hoff + 40) -gt (RU32 $script:f ($sectBase + 20))) { throw "${Name}: kein Platz im PE-Header fuer einen weiteren Sektionseintrag." }

    $raw_size = AlignUp $Size $FA
    $oldLen = $script:f.Length
    $new_raw = AlignUp $oldLen $FA
    $nf = New-Object byte[] ($new_raw + $raw_size)
    [Array]::Copy($script:f, 0, $nf, 0, $oldLen)
    for ($i = $new_raw; $i -lt $nf.Length; $i++) { $nf[$i] = 0xCC }
    $script:f = $nf

    Patch ($e + 6) ([BitConverter]::GetBytes([uint16]($nsec + 1)))
    Patch ($e + 24 + 56) ([BitConverter]::GetBytes([uint32](AlignUp ($new_rva + $Size) $SA)))
    $sh = New-Object byte[] 40
    $nm = [System.Text.Encoding]::ASCII.GetBytes($Name)
    [Array]::Copy($nm, 0, $sh, 0, [Math]::Min(8, $nm.Length))
    [Array]::Copy([BitConverter]::GetBytes([uint32]$Size), 0, $sh, 8, 4)
    [Array]::Copy([BitConverter]::GetBytes([uint32]$new_rva), 0, $sh, 12, 4)
    [Array]::Copy([BitConverter]::GetBytes([uint32]$raw_size), 0, $sh, 16, 4)
    [Array]::Copy([BitConverter]::GetBytes([uint32]$new_raw), 0, $sh, 20, 4)
    [Array]::Copy([byte[]](0x20, 0x00, 0x00, 0x60), 0, $sh, 36, 4)     # 0x60000020 = Code | ausfuehrbar | lesbar
    Patch $hoff $sh
    return , @(($IB + $new_rva), $new_raw)
}

# Sprung von $FromVA zur Code-Hoehle: E9 rel32, Rest bis $Len mit NOPs.
function Get-JmpPatch([int64]$FromVA, [int64]$ToVA, [int]$Len) {
    $b = New-Object byte[] $Len
    $b[0] = 0xE9
    [Array]::Copy([BitConverter]::GetBytes([int32]($ToVA - ($FromVA + 5))), 0, $b, 1, 4)
    for ($i = 5; $i -lt $Len; $i++) { $b[$i] = 0x90 }
    return , $b
}

# ============================================================
#  WorldFrame-Absturzfix (0x539wowmod, Alyst3r)
#  Die Funktion bei VA 0x81D510 laeuft ueber Dreiecke aus Index-Tripeln
#  (WORDs) und rechnet Index minus Basis ([ebp+10h]) in eine Vertex-Adresse
#  um. Ist ein Index kleiner als die Basis, landet die Adresse vor dem Puffer
#  und der Client stuerzt ab. Die Hoehle prueft die drei Indizes des ersten
#  Dreiecks und springt in dem Fall direkt zum Funktionsende (VA 0x81D66E,
#  dorthin springt auch die eingebaute Pruefung davor - gleicher Stack).
#  Neu umgesetzt: Im Original sind die Sprungweiten der drei jg falsch
#  berechnet (ohne die Laenge des jg selbst).
# ============================================================
function Add-WorldFrameCrashFix {
    $HOOK_VA = 0x81D521; $BACK_VA = 0x81D531; $EXIT_VA = 0x81D66E
    $orig = [byte[]](0xD9, 0xEE, 0x53, 0x8B, 0x5D, 0x10, 0x56, 0x8B, 0xB1, 0x24, 0x01, 0x00, 0x00, 0x89, 0x75, 0x08)
    for ($i = 0; $i -lt 16; $i++) {
        if ($script:f[$HOOK_VA - 0x400C00 + $i] -ne $orig[$i]) { throw 'WorldFrame-Absturzfix: Code bei VA 0x81D521 unbekannt.' }
    }
    $sec = Add-CodeSection '.wfcfix' 0x40
    $CAVE = $sec[0]
    $c = New-Object System.Collections.Generic.List[byte]
    foreach ($idx in 0, 2, 4) {
        if ($idx -eq 0) { AddRaw $c @(0x0F, 0xB7, 0x07) } else { AddRaw $c @(0x0F, 0xB7, 0x47, $idx) }   # movzx eax, word [edi+idx]
        AddRaw $c @(0x39, 0x45, 0x10)                                                                  # cmp [ebp+10h], eax
        AddRaw $c @(0x0F, 0x8F); AddLE32 $c ($EXIT_VA - ($CAVE + $c.Count + 4))                         # jg Funktionsende
    }
    AddRaw $c $orig                                                                                    # ueberschriebener Originalcode
    AddRaw $c @(0xE9); AddLE32 $c ($BACK_VA - ($CAVE + $c.Count + 4))                                   # jmp zurueck
    Patch $sec[1] $c.ToArray()
    Patch ($HOOK_VA - 0x400C00) (Get-JmpPatch $HOOK_VA $CAVE 16)
}

# ============================================================
#  Kein Ausblenden fuer NPCs mit UNIT_FLAG2_DO_NOT_FADE_IN (0x539wowmod, Alyst3r)
#  Beim Entfernen eines Objekts (Funktion bei VA 0x743D50) blendet der
#  Client das Modell normalerweise aus. Die Hoehle prueft vorher: Ist es
#  ein CGUnit (vtable 0xA34D90, Spieler haben eine eigene) und ist in
#  UNIT_FIELD_FLAGS_2 das Bit 0x20 (DO_NOT_FADE_IN) gesetzt, geht es direkt
#  zum Zweig ohne Ausblenden (VA 0x743DE3), sonst normal weiter. Das Flag
#  muss der Server setzen.
# ============================================================
function Add-NoFadeOutFlag {
    $HOOK_VA = 0x743DA3; $BACK_VA = 0x743DAE; $NOFADE_VA = 0x743DE3
    $orig = [byte[]](0x8B, 0x06, 0x8B, 0x50, 0x40, 0x8B, 0xCE, 0xFF, 0xD2, 0x52, 0x50)
    for ($i = 0; $i -lt 11; $i++) {
        if ($script:f[$HOOK_VA - 0x400C00 + $i] -ne $orig[$i]) { throw 'NPC-Ausblenden: Code bei VA 0x743DA3 unbekannt.' }
    }
    $sec = Add-CodeSection '.nofade' 0x40
    $CAVE = $sec[0]
    $c = New-Object System.Collections.Generic.List[byte]
    AddRaw $c @(0x81, 0x3E); AddLE32 $c 0xA34D90                          # cmp dword [esi], CGUnit-vtable
    AddRaw $c @(0x75, 0x13)                                                # jne normal (+19)
    AddRaw $c @(0x8B, 0x86, 0xD0, 0x00, 0x00, 0x00)                        # mov eax, [esi+0D0h]  (Unit-Felder)
    AddRaw $c @(0xF6, 0x80, 0xD8, 0x00, 0x00, 0x00, 0x20)                  # test byte [eax+0D8h], 20h (FLAGS_2)
    AddRaw $c @(0x0F, 0x85); AddLE32 $c ($NOFADE_VA - ($CAVE + $c.Count + 4))   # jnz ohne Ausblenden
    AddRaw $c $orig                                                        # normal: ueberschriebener Originalcode
    AddRaw $c @(0xE9); AddLE32 $c ($BACK_VA - ($CAVE + $c.Count + 4))       # jmp zurueck
    Patch $sec[1] $c.ToArray()
    Patch ($HOOK_VA - 0x400C00) (Get-JmpPatch $HOOK_VA $CAVE 11)
}

# ============================================================
#  Helfer fuer den Sprunghoehen-Patch
""")

def after(id_, block):
    global s
    i=s.index(f"    @{{ Id = '{id_}';")
    j=s.index("    }}\n", i)+len("    }}\n")
    s=s[:j]+"\n"+block+s[j:]

after('itemcache', """    @{ Id = 'worldcrash'; Cat = 'system'; On = $false
       Author = 'Alyst3r (0x539wowmod) / St0ny'
       De = 'WorldFrame-Absturzfix (ungueltige Dreiecks-Indizes)'
       En = 'WorldFrame crash fix (invalid triangle indices)'
       Code = {
        # Haengt eine kleine Code-Sektion an (.wfcfix), siehe Add-WorldFrameCrashFix.
        Add-WorldFrameCrashFix
    }}
""")
after('voicedll', """    @{ Id = 'keyprop'; Cat = 'modding'; On = $false
       Author = 'Alyst3r (0x539wowmod)'
       De = 'Alle Tastatur-Ereignisse an Addons weiterreichen (OnKeyDown)'
       En = 'Pass all keyboard events on to addons (OnKeyDown)'
       Code = {
        # CSimpleFrame::OnKeyDown (VA 0x48FB80) meldet nach dem OnKeyDown-Skript
        # eines Frames "erledigt" (mov eax, 1 bei VA 0x48FBD8). Mit 0 laeuft die
        # Taste danach weiter zu den Tastenbelegungen.
        Patch 0x8EFD9 @(0x00)
    }}
""")
after('raceclass', """    @{ Id = 'namecheck'; Cat = 'gameplay'; On = $false
       Author = 'Alyst3r (0x539wowmod) / St0ny'
       De = 'Namenspruefung bei der Charaktererstellung abschalten (z.B. Zahlen im Namen)'
       En = 'Disable the name check in character creation (e.g. digits in names)'
       NoteDe = 'Server muss die Namen ebenfalls erlauben'
       NoteEn = 'server must allow the names as well'
       Code = {
        # Die Pruefung bei VA 0x6B0F90 (cdecl) liefert sofort 0x57 = Name gueltig:
        # mov eax, 57h / ret. Im Original (0x539wowmod) per Detour mit falscher
        # Aufrufkonvention (stdcall), hier direkt in der Funktion.
        Patch 0x2B0390 @(0xB8, 0x57, 0x00, 0x00, 0x00, 0xC3)
    }}
""")
after('notransparency', """    @{ Id = 'nofade'; Cat = 'graphics'; On = $false
       Author = 'Alyst3r (0x539wowmod) / St0ny'
       De = 'Kein Ausblenden fuer NPCs mit Flag DO_NOT_FADE_IN'
       En = 'No fade-out for NPCs with flag DO_NOT_FADE_IN'
       NoteDe = 'Server muss das Flag setzen'
       NoteEn = 'server must set the flag'
       Code = {
        # Haengt eine kleine Code-Sektion an (.nofade), siehe Add-NoFadeOutFlag.
        Add-NoFadeOutFlag
    }}
""")
after('flash', """    @{ Id = 'charrandom'; Cat = 'ui'; On = $false
       Author = 'Alyst3r (0x539wowmod)'
       De = 'Charaktererstellung: Aussehen nicht automatisch auswuerfeln'
       En = 'Character creation: do not randomize the appearance automatically'
       Code = {
        # VA 0x4E147B: je -> jmp, die automatischen Zufallsaufrufe beim Oeffnen
        # bzw. Volk-/Klassenwechsel werden uebersprungen. Der Zufall-Knopf
        # (RandomizeCharCustomization, VA 0x4E1B60) nutzt einen eigenen Weg.
        Patch 0xE087B @(0xEB)
    }}
""")
