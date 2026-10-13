# ============================================================
#  mod-voicechat - voice.dll loader patch for Wow.exe 3.3.5a (12340)
#  SPDX-License-Identifier: GPL-2.0-or-later
# ============================================================
#
#  DE: Dateigroesse und PE-Header bleiben UNVERAENDERT. Der Patch nutzt eine
#      27-Byte-int3-Luecke zwischen zwei Funktionen (VA 0x944B45, Datei 0x543F45)
#      und biegt den Sprung am Einstiegspunkt (VA 0x401005: jmp 0x40BA9B,
#      direkt vor __security_init_cookie/__tmainCRTStartup) dorthin um:
#          push "voice.dll" / call [LoadLibraryA] / jmp 0x40BA9B
#      eax/ecx/edx/Flags sind an dieser Stelle tot (naechster Code ist ein
#      normaler Funktionsaufruf), ebx/esi/edi/ebp sichert LoadLibraryA selbst.
#      Fehlt die DLL, startet WoW ganz normal.
#      Geaenderte Bytes: 4 (Sprungziel) + 26 (Luecke). Kollidiert mit keinem
#      Patch aus St0ny's Patcher (aktiv oder auskommentiert). Mehrfach
#      ausfuehren ist harmlos.
#
#  EN: File size and PE header stay UNCHANGED. The patch uses a 27-byte int3
#      gap between two functions (VA 0x944B45, file 0x543F45) and redirects the
#      jump at the entry point (VA 0x401005: jmp 0x40BA9B, right before
#      __security_init_cookie/__tmainCRTStartup) to it:
#          push "voice.dll" / call [LoadLibraryA] / jmp 0x40BA9B
#      eax/ecx/edx/flags are dead at this point (the next code is a plain
#      function call), ebx/esi/edi/ebp are preserved by LoadLibraryA.
#      If the DLL is missing, WoW starts normally.
#      Changed bytes: 4 (jump target) + 26 (gap). Does not collide with any
#      patch of St0ny's patcher (active or commented out). Idempotent.
#
#  DE: Einbindung in apply_patches.ps1:   EN: Integration into apply_patches.ps1:
#      . "$PSScriptRoot\Add-VoiceLoader.ps1"
#      ,@('voice.dll laden (mod-voicechat)', { [void](Add-VoiceLoader -Image $script:f) })
# ============================================================

function Add-VoiceLoader {
    param(
        [Parameter(Mandatory = $true)][byte[]]$Image,   # wird direkt veraendert / patched in place
        [string]$DllName = 'voice.dll'
    )

    $IB        = 0x400000
    $TEXT_DIFF = 0x400C00          # VA - Dateioffset in .text / VA - file offset in .text
    $JMP_VA    = 0x401005          # jmp __tmainCRTStartup-Kette / chain
    $CRT_VA    = 0x40BA9B          # urspruengliches Sprungziel / original jump target
    $CAVE_VA   = 0x944B45          # int3-Luecke / int3 gap
    $CAVE_LEN  = 27
    $IAT_LLA   = 0x9DF248          # KERNEL32!LoadLibraryA (IAT)

    function VlU32([byte[]]$a, [int64]$o) { return [int64][BitConverter]::ToUInt32($a, $o) }
    function VlRel([int64]$from, [int64]$to) { $v = $to - $from; if ($v -lt 0) { $v += 4294967296 }; return [uint32]$v }

    $jmpOff  = $JMP_VA - $TEXT_DIFF
    $caveOff = $CAVE_VA - $TEXT_DIFF

    # --- Build pruefen / verify build ---
    if ($Image.Length -lt ($caveOff + $CAVE_LEN)) { throw 'Add-VoiceLoader: Datei zu klein / file too small' }
    $e = VlU32 $Image 0x3C
    if ((VlU32 $Image ($e + 24 + 16)) -ne ($JMP_VA - 5 - $IB)) { throw 'Add-VoiceLoader: unerwarteter Einstiegspunkt (kein 3.3.5a 12340?) / unexpected entry point' }
    if ($Image[$jmpOff - 5] -ne 0xE8 -or $Image[$jmpOff] -ne 0xE9) { throw 'Add-VoiceLoader: Einstiegscode unbekannt / unknown entry code' }

    # --- Payload: push str / call [LoadLibraryA] / jmp CRT / "voice.dll\0" ---
    $nameBytes = [System.Text.Encoding]::ASCII.GetBytes($DllName)
    if ($nameBytes.Length -lt 1 -or $nameBytes.Length -gt ($CAVE_LEN - 17)) { throw 'Add-VoiceLoader: DLL-Name max. 10 Zeichen / DLL name max 10 chars' }
    $p = New-Object System.Collections.Generic.List[byte]
    $p.Add(0x68); $p.AddRange([BitConverter]::GetBytes([uint32]($CAVE_VA + 16)))
    $p.Add(0xFF); $p.Add(0x15); $p.AddRange([BitConverter]::GetBytes([uint32]$IAT_LLA))
    $p.Add(0xE9); $p.AddRange([BitConverter]::GetBytes((VlRel ($CAVE_VA + 16) $CRT_VA)))
    foreach ($nb in $nameBytes) { $p.Add($nb) }; $p.Add(0)
    $payload = $p.ToArray()

    # --- Zustand pruefen / check state ---
    $target = $JMP_VA + 5 + [BitConverter]::ToInt32($Image, $jmpOff + 1)
    $caveIsOurs = $true; $caveIsFree = $true
    for ($i = 0; $i -lt $CAVE_LEN; $i++) {
        $b = $Image[$caveOff + $i]
        if ($b -ne 0xCC) { $caveIsFree = $false }
        $want = if ($i -lt $payload.Length) { $payload[$i] } else { 0xCC }
        if ($b -ne $want) { $caveIsOurs = $false }
    }
    if ($target -eq $CAVE_VA -and $caveIsOurs) {
        Write-Host '  [=] voice.dll-Loader ist bereits eingebaut / already installed'
        return $false
    }
    if ($target -ne $CRT_VA) { throw ('Add-VoiceLoader: Einstiegssprung bereits umgebogen auf 0x{0:X} / entry jump already redirected' -f $target) }
    if (-not $caveIsFree) { throw 'Add-VoiceLoader: Luecke bei 0x944B45 ist belegt / gap at 0x944B45 is in use' }

    # --- LoadLibraryA-Import pruefen (Hint/Name ueber IAT-Thunk) / verify import ---
    $rdataDiff = 0x401800          # VA - Dateioffset in .rdata / VA - file offset in .rdata
    $thunk = VlU32 $Image ($IAT_LLA - $rdataDiff)
    if (($thunk -band 0x80000000) -ne 0 -or [System.Text.Encoding]::ASCII.GetString($Image, ($thunk + $IB - $rdataDiff + 2), 12) -cne 'LoadLibraryA') {
        throw 'Add-VoiceLoader: IAT-Eintrag LoadLibraryA nicht gefunden / IAT entry not found'
    }

    # --- Patchen / patch ---
    [Array]::Copy($payload, 0, $Image, $caveOff, $payload.Length)
    [Array]::Copy([BitConverter]::GetBytes((VlRel ($JMP_VA + 5) $CAVE_VA)), 0, $Image, $jmpOff + 1, 4)

    Write-Host ('  [+] voice.dll-Loader: jmp 0x{0:X} -> 0x{1:X}, {2} + 4 Byte, Dateigroesse unveraendert / file size unchanged' -f $JMP_VA, $CAVE_VA, $payload.Length)
    return $true
}
