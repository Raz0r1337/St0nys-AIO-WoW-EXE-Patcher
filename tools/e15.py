# --- Parameter ---
R("""    [string]$Path
)
""", """    [string]$Path,
    [switch]$BuildTable
)
""")
R("""#    -Path     <Datei>        Andere Wow.exe als die im Skriptordner
# ============================================================
""", """#    -Path     <Datei>        Andere Wow.exe als die im Skriptordner
#
#  Fuer Entwickler:
#    -BuildTable              Erzeugt die eingebaute Original-Byte-Tabelle
#                             neu (braucht die originale Wow.exe, siehe
#                             Invoke-BuildTable). Nach jeder Aenderung an
#                             einem Patch ausfuehren.
# ============================================================
""")
R("""$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
""", """$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path -Parent $scriptPath
""")
# --- Texte ---
R("""        HashBad1      = '[FEHLER] Die Wow.exe ist nicht die originale Datei.'
        HashBad2      = '         Sie wurde bereits gepatcht (anderes Tool, alte Patcher-Version) oder ist eine andere Version.'
        HashBad3      = 'Beim ersten Start wird eine unmodifizierte Wow.exe benoetigt.'
        HashBadState1 = '[FEHLER] Die Wow.exe ist weder das Original noch die zuletzt von diesem Patcher erzeugte Datei.'
        HashBadState2 = '         Sie wurde seitdem veraendert (anderes Tool, Client-Update o.ae.).'
        HashBadState3 = 'Bitte die zuletzt gepatchte oder eine unmodifizierte Wow.exe verwenden.'
        Expected      = 'Original:  {0}'
        ExpectedLast  = 'Zuletzt:   {0}'
""", """        HashBad1      = '[FEHLER] Die Wow.exe ist weder original noch mit diesem Patcher gepatcht (kein Wasserzeichen).'
        HashBad2      = '         Sie wurde mit einem anderen Tool oder einer alten Patcher-Version gepatcht oder ist eine andere Version.'
        HashBad3      = 'Beim ersten Start wird eine unmodifizierte Wow.exe benoetigt.'
        Expected      = 'Original:  {0}'
""")
R("""        RevertOk      = '[OK] Original aus patcher_state.ini rekonstruiert und per SHA256 geprueft.'
        StateBroken1  = '[FEHLER] patcher_state.ini passt zur Wow.exe, das Original laesst sich daraus aber nicht'
        StateBroken2  = '         wiederherstellen (Datei beschaedigt oder von Hand geaendert?).'
""", """        RevertOk      = '[OK] Original aus patcher_state.ini rekonstruiert und per SHA256 geprueft.'
        Scanning      = 'Wasserzeichen gefunden, ermittle den Patchstand aus der Wow.exe...'
        WmFound       = '[OK] Wasserzeichen gefunden: Die Wow.exe wurde mit diesem Patcher gepatcht.'
        WmScanned     = '[OK] Patchstand aus der Exe ermittelt ({0} Patches erkannt), Original per SHA256 geprueft.'
        WmBroken1     = '[FEHLER] Die Wow.exe traegt das Wasserzeichen dieses Patchers, das Original laesst sich aber'
        WmBroken2     = '         nicht sicher wiederherstellen (danach veraendert oder mit einer anderen Patcher-Version erstellt).'
        TableWarn     = 'HINWEIS: Die eingebaute Original-Byte-Tabelle passt nicht zu dieser Auswahl - ohne patcher_state.ini liesse sich diese Wow.exe nicht zuruecknehmen.'
""")
R("""        HashBad1      = '[ERROR] This Wow.exe is not the original file.'
        HashBad2      = '        It has already been patched (another tool, old patcher version) or is a different version.'
        HashBad3      = 'The first run requires an unmodified Wow.exe.'
        HashBadState1 = '[ERROR] This Wow.exe is neither the original nor the file last produced by this patcher.'
        HashBadState2 = '        It has been changed since (another tool, client update or similar).'
        HashBadState3 = 'Please use the last patched or an unmodified Wow.exe.'
        Expected      = 'Original:  {0}'
        ExpectedLast  = 'Last run:  {0}'
""", """        HashBad1      = '[ERROR] This Wow.exe is neither original nor patched with this patcher (no watermark).'
        HashBad2      = '        It has been patched with another tool or an old patcher version, or is a different version.'
        HashBad3      = 'The first run requires an unmodified Wow.exe.'
        Expected      = 'Original:  {0}'
""")
R("""        RevertOk      = '[OK] Original reconstructed from patcher_state.ini and verified by SHA256.'
        StateBroken1  = '[ERROR] patcher_state.ini matches Wow.exe, but the original cannot be restored from it'
        StateBroken2  = '        (file damaged or edited by hand?).'
""", """        RevertOk      = '[OK] Original reconstructed from patcher_state.ini and verified by SHA256.'
        Scanning      = 'Watermark found, determining the patch state from Wow.exe...'
        WmFound       = '[OK] Watermark found: this Wow.exe was patched with this patcher.'
        WmScanned     = '[OK] Patch state read from the exe ({0} patches detected), original verified by SHA256.'
        WmBroken1     = '[ERROR] This Wow.exe carries the watermark of this patcher, but the original cannot be'
        WmBroken2     = '        restored safely (changed afterwards or made with another patcher version).'
        TableWarn     = 'NOTE: The built-in original bytes table does not match this selection - without patcher_state.ini this Wow.exe could not be reverted.'
""")
# --- Funktionen ---
R("""# ============================================================
#  Helfer fuer den Sprunghoehen-Patch
""", r"""# ============================================================
#  Patchstand aus der Exe ermitteln (Wasserzeichen + Original-Byte-Tabelle)
#  Ob eine Wow.exe mit diesem Patcher gepatcht wurde, zeigt das Wasserzeichen.
#  Passt der Hash aus patcher_state.ini, geht es ueber die Zustandsdatei
#  (schneller Weg). Sonst ermittelt der Patcher den Patchstand aus der Exe
#  selbst: Die Tabelle $ORIGINAL_TABLE (am Ende der Patch-Definitionen)
#  enthaelt fuer jeden Patch die Original-Bytes an allen Stellen, die er
#  beschreibt. Ein Patch gilt als eingespielt, wenn eine seiner eigenen
#  Stellen (die kein anderer Patch beschreibt) vom Original abweicht. Werte
#  (Sprunghoehe, Build-Datum ...) liest Decode des Patches aus der Exe. Fuer
#  das Original werden alle Stellen zurueckgeschrieben und angehaengte
#  Sektionen abgeschnitten; das Ergebnis muss exakt den Original-Hash haben.
# ============================================================
function Test-Watermark([byte[]]$data) {
    $b = [System.Text.Encoding]::ASCII.GetBytes($WATERMARK)
    if ($data.Length -lt $WATERMARK_OFF + $b.Length) { return $false }
    for ($i = 0; $i -lt $b.Length; $i++) { if ($data[$WATERMARK_OFF + $i] -ne $b[$i]) { return $false } }
    return $true
}

# Tabelle einmal einlesen: Zeilen "size;<Laenge>" und "<Id>;<Offset hex>;<Bytes hex>;<1 = nur dieser Patch>"
function Get-OriginalTable {
    if ($script:origTable) { return $script:origTable }
    $t = @{ Size = [int64]0; Entries = (New-Object System.Collections.Generic.List[object]) }
    foreach ($l in ($ORIGINAL_TABLE -split "`r?`n")) {
        if ($l -match '^size;(\d+)$') { $t.Size = [int64]$matches[1] }
        elseif ($l -match '^([a-z0-9]+);([0-9A-F]+);([0-9A-F]+);([01])$') {
            $t.Entries.Add(@{ Id = $matches[1]; Off = [Convert]::ToInt64($matches[2], 16); Bytes = (ConvertFrom-Hex $matches[3]); Own = ($matches[4] -eq '1') })
        }
    }
    $script:origTable = $t
    return $t
}

# Original aus einer gepatchten Exe zurueckgewinnen. $null, wenn das nicht exakt klappt.
function Restore-FromTable([byte[]]$data) {
    $t = Get-OriginalTable
    if ($t.Size -le 0 -or $data.Length -lt $t.Size) { return $null }
    $o = New-Object byte[] $t.Size
    [Array]::Copy($data, 0, $o, 0, $t.Size)
    foreach ($e in $t.Entries) { [Array]::Copy($e.Bytes, 0, $o, $e.Off, $e.Bytes.Length) }
    if ((Get-Sha256 $o) -ne $EXPECTED_HASH) { return $null }
    return , $o
}

# Ids der Patches, deren eigene Stellen vom Original abweichen (in Menue-Reihenfolge).
function Find-AppliedPatches([byte[]]$data) {
    $hit = @{}
    foreach ($e in (Get-OriginalTable).Entries) {
        if (-not $e.Own -or $hit.ContainsKey($e.Id)) { continue }
        for ($i = 0; $i -lt $e.Bytes.Length; $i++) {
            if ($data[$e.Off + $i] -ne $e.Bytes[$i]) { $hit[$e.Id] = $true; break }
        }
    }
    $ids = @()
    foreach ($p in $patches) { if ($hit.ContainsKey($p.Id)) { $ids += $p.Id } }
    return , $ids
}

# Hilfen fuer Decode: Text aus der Exe lesen, VA in Dateioffset umrechnen.
function Read-AsciiZ([int64]$off, [int]$max) {
    $s = ''
    for ($i = 0; $i -lt $max; $i++) { $b = $script:f[$off + $i]; if ($b -eq 0) { break }; $s += [char]$b }
    return $s
}
function Read-Utf16Z([int64]$off, [int]$max) {
    $s = ''
    for ($i = 0; $i + 1 -lt $max; $i += 2) { $c = RU16 $script:f ($off + $i); if ($c -eq 0) { break }; $s += [char]$c }
    return $s
}
function ConvertTo-FileOffset([int64]$va) {
    $e = RU32 $script:f 0x3C
    $nsec = RU16 $script:f ($e + 6)
    $IB = RU32 $script:f ($e + 24 + 28)
    $sectBase = $e + 24 + (RU16 $script:f ($e + 20))
    for ($i = 0; $i -lt $nsec; $i++) {
        $so = $sectBase + 40 * $i
        $rva = RU32 $script:f ($so + 12); $raw = RU32 $script:f ($so + 20); $rs = RU32 $script:f ($so + 16)
        if ($va -ge $IB + $rva -and $va -lt $IB + $rva + $rs) { return $raw + ($va - $IB - $rva) }
    }
    return -1
}
function Get-ClientDateFromExe {
    $t = [System.Text.Encoding]::ASCII.GetString($script:f, 0x5F39F4, 11)
    if ($t -notmatch '^([A-Za-z]{3}) (\d{2}) (\d{4})$') { return $null }
    $en = @('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    $fr = @('Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec')
    $m = [array]::IndexOf($en, $matches[1]); $suffix = ''
    if ($m -lt 0) { $m = [array]::IndexOf($fr, $matches[1]); $suffix = ' FR' }
    if ($m -lt 0) { return $null }
    return ('{0}-{1:00}-{2}{3}' -f $matches[3], ($m + 1), $matches[2], $suffix)
}
function Get-DoubleJumpFromExe {
    $hook = 0x98842A - 0x400C00
    if ($script:f[$hook] -ne 0xE9) { return $null }
    $cave = ConvertTo-FileOffset (0x98842A + 5 + [BitConverter]::ToInt32($script:f, $hook + 1))
    if ($cave -lt 0 -or $script:f[$cave + 11] -ne 0xC6) { return $null }
    return [string]$script:f[$cave + 17]
}

# ============================================================
#  Original-Byte-Tabelle erzeugen (Entwickler, Parameter -BuildTable)
#  Spielt auf Kopien der originalen Wow.exe alle Patches ein - alle
#  zusammen, alle ohne Slider-Patch (Code-Hoehle in .text) und jeden
#  einzeln (Sektionsheader an der ersten freien Stelle) - und merkt sich je
#  Patch alle Stellen im Original, die er beschreibt. Stellen, die nur ein
#  Patch beschreibt, bekommen die Markierung 1 (fuer die Erkennung).
#  Das Ergebnis ersetzt den Block $ORIGINAL_TABLE in diesem Skript.
# ============================================================
function Invoke-BuildTable {
    $orig = [System.IO.File]::ReadAllBytes($file)
    if ((Get-Sha256 $orig) -ne $EXPECTED_HASH) { Write-Host 'BuildTable: braucht die originale Wow.exe (-Path).'; exit 1 }
    $ranges = @{}
    $allIds = @($patches | ForEach-Object { $_.Id })
    $configs = New-Object System.Collections.Generic.List[object]
    $configs.Add($allIds)
    $configs.Add(@($allIds | Where-Object { $_ -ne 'sliders' }))
    foreach ($id in $allIds) { $configs.Add(@($id)) }
    $n = 0
    foreach ($cfg in $configs) {
        $n++
        Write-Host ("  Konfiguration {0}/{1}" -f $n, $configs.Count)
        $script:f = [byte[]]$orig.Clone()
        $script:chosenIds = $cfg
        $script:VALUES = @{}
        foreach ($p in $patches) { if ($p.Check) { $script:VALUES[$p.Id] = $p.Default } }
        $script:writes.Clear()
        foreach ($p in $patches) {
            if ($cfg -notcontains $p.Id) { continue }
            $start = $script:writes.Count
            & $p.Code
            Add-BuildRanges $ranges $p.Id $start $orig.Length
        }
        $start = $script:writes.Count
        Add-Watermark
        Add-BuildRanges $ranges 'watermark' $start $orig.Length
    }
    # je Patch sortieren und zusammenfassen
    $merged = @{}
    foreach ($id in $ranges.Keys) {
        $list = @($ranges[$id] | Sort-Object { $_[0] })
        $out = New-Object System.Collections.Generic.List[object]
        foreach ($r in $list) {
            if ($out.Count -gt 0 -and $r[0] -le $out[$out.Count - 1][1]) {
                if ($r[1] -gt $out[$out.Count - 1][1]) { $out[$out.Count - 1][1] = $r[1] }
            } else { $out.Add(@($r[0], $r[1])) }
        }
        $merged[$id] = $out
    }
    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add("size;$($orig.Length)")
    foreach ($id in (@($allIds) + 'watermark')) {
        if (-not $merged.ContainsKey($id)) { continue }
        $own = 0
        foreach ($r in $merged[$id]) {
            $shared = $false
            foreach ($other in $merged.Keys) {
                if ($other -eq $id) { continue }
                foreach ($q in $merged[$other]) { if ($q[0] -lt $r[1] -and $r[0] -lt $q[1]) { $shared = $true; break } }
                if ($shared) { break }
            }
            $b = New-Object byte[] ($r[1] - $r[0])
            [Array]::Copy($orig, $r[0], $b, 0, $b.Length)
            $flag = 1; if ($shared) { $flag = 0 } else { $own++ }
            $lines.Add(('{0};{1:X};{2};{3}' -f $id, $r[0], ([BitConverter]::ToString($b)).Replace('-', ''), $flag))
        }
        if ($own -eq 0) { Write-Host "  WARNUNG: $id hat keine eigene Stelle und ist nicht erkennbar." }
    }
    $block = "# BEGIN ORIGINAL-BYTES`r`n`$ORIGINAL_TABLE = @'`r`n" + ($lines -join "`r`n") + "`r`n'@`r`n# END ORIGINAL-BYTES"
    $src = [System.IO.File]::ReadAllText($scriptPath)
    $src = [regex]::Replace($src, '(?s)# BEGIN ORIGINAL-BYTES.*?# END ORIGINAL-BYTES', { param($m) $block })
    [System.IO.File]::WriteAllText($scriptPath, $src, (New-Object System.Text.ASCIIEncoding))
    Write-Host ("  {0} Eintraege geschrieben." -f ($lines.Count - 1))
}

function Add-BuildRanges($ranges, [string]$id, [int]$start, [int64]$origLen) {
    if (-not $ranges.ContainsKey($id)) { $ranges[$id] = New-Object System.Collections.Generic.List[object] }
    for ($i = $start; $i -lt $script:writes.Count; $i += 2) {
        $off = $script:writes[$i]; $end = $off + $script:writes[$i + 1]
        if ($off -ge $origLen) { continue }
        if ($end -gt $origLen) { $end = $origLen }
        $ranges[$id].Add(@($off, $end))
    }
}

# ============================================================
#  Helfer fuer den Sprunghoehen-Patch
""")
# Decode-Felder
R("""       Check = { param($v) Test-JumpValue $v }
""", """       Check = { param($v) Test-JumpValue $v }
       Decode = { ([BitConverter]::ToSingle($script:f, 0x6A1BDC)).ToString('R', [System.Globalization.CultureInfo]::InvariantCulture) }
""")
R("""       Check = { param($v) Test-DoubleJump $v }
""", """       Check = { param($v) Test-DoubleJump $v }
       Decode = { Get-DoubleJumpFromExe }
""")
R("""       Check = { param($v) Test-ClientVersion $v }
""", """       Check = { param($v) Test-ClientVersion $v }
       Decode = { Read-AsciiZ 0x5F3A08 8 }
""")
R("""       Check = { param($v) Test-ClientBuild $v }
""", """       Check = { param($v) Test-ClientBuild $v }
       Decode = { [string](RU16 $script:f 0x4C99F0) }
""")
R("""       Check = { param($v) Test-ClientTitle $v }
""", """       Check = { param($v) Test-ClientTitle $v }
       Decode = { Read-Utf16Z 0x7577C0 50 }
""")
R("""       Check = { param($v) Test-ClientDate $v }
""", """       Check = { param($v) Test-ClientDate $v }
       Decode = { Get-ClientDateFromExe }
""")
R("""#    Suggest - optional: Scriptblock, der den Vorschlag im Dialog aus dem
""", """#    Decode - optional: Scriptblock, der den eingespielten Wert aus der Exe
#            ($script:f) liest - fuer die Erkennung ueber das Wasserzeichen
#    Suggest - optional: Scriptblock, der den Vorschlag im Dialog aus dem
""")
# Tabelle nach den Patch-Definitionen
R("""# ============================================================
#  Auswahl-Logik
""", """# ============================================================
#  Original-Bytes je Patch - erzeugt mit -BuildTable, nicht von Hand aendern
# ============================================================
# BEGIN ORIGINAL-BYTES
$ORIGINAL_TABLE = @'
'@
# END ORIGINAL-BYTES

# ============================================================
#  Auswahl-Logik
""")
# Build-Modus vor dem Banner
R("""Write-Host ''
Show-Banner
""", """if ($BuildTable) {
    Invoke-BuildTable
    exit 0
}

Write-Host ''
Show-Banner
""")
# Ablauf
R("""# --- 2. Wow.exe vorhanden und original oder zuletzt von hier gepatcht? ---
# Beim ersten Start muss die Wow.exe original sein. Danach muss sie exakt die
# Datei sein, die der letzte Lauf erzeugt hat (Hash in patcher_state.ini);
# aus ihr wird dann das Original im Speicher rekonstruiert.""", """# --- 2. Wow.exe vorhanden und original oder mit diesem Patcher gepatcht? ---
# Beim ersten Start muss die Wow.exe original sein. Danach erkennt der
# Patcher eine von ihm gepatchte Exe am Wasserzeichen. Passt der Hash aus
# patcher_state.ini, wird das Original schnell aus der Zustandsdatei
# rekonstruiert, sonst ueber die Original-Byte-Tabelle (mit Erkennung der
# eingespielten Patches und ihrer Werte).""")
R("""    $state = Read-State
    if ($null -eq $state -or $state.Hash -ne $hash) {
        Write-Host ''
        if ($null -eq $state) {
            Say (T 'HashBad1') 'Red'
            Say (T 'HashBad2') 'Red'
        } else {
            Say (T 'HashBadState1') 'Red'
            Say (T 'HashBadState2') 'Red'
        }
        Write-Host ''
        Say (T 'Expected' $EXPECTED_HASH)
        if ($null -ne $state) { Say (T 'ExpectedLast' $state.Hash) }
        Say (T 'Found' $hash)
        Write-Host ''
        if ($null -eq $state) { Say (T 'HashBad3') } else { Say (T 'HashBadState3') }
        Show-BakHint
        Exit-Patcher 1
    }
    $orig = Restore-Original $f $state
    if ($null -eq $orig) {
        Write-Host ''
        Say (T 'StateBroken1') 'Red'
        Say (T 'StateBroken2') 'Red'
        Show-BakHint
        Exit-Patcher 1
    }
    $f = $orig
    $patchedMode = $true
    $appliedIds = @($state.Ids)
    Say (T 'HashKnown' $appliedIds.Count) 'Green'
    Say (T 'RevertOk') 'Green'
}""", """    $state = Read-State
    $orig = $null
    if ($null -ne $state -and $state.Hash -eq $hash) { $orig = Restore-Original $f $state }
    if ($null -ne $orig) {
        # schneller Weg ueber patcher_state.ini
        Say (T 'HashKnown' @($state.Ids).Count) 'Green'
        Say (T 'RevertOk') 'Green'
    } elseif (Test-Watermark $f) {
        # Patchstand aus der Exe selbst ermitteln
        Say (T 'Scanning')
        $ids = Find-AppliedPatches $f
        $vals = @{}
        foreach ($id in $ids) {
            $p = Get-PatchById $id
            if (-not $p.Decode) { continue }
            $v = $null
            try { $v = & $p.Decode } catch { }
            if ($v -and -not (& $p.Check $v)) { $vals[$id] = [string]$v }
        }
        $orig = Restore-FromTable $f
        if ($null -eq $orig) {
            Write-Host ''
            Say (T 'WmBroken1') 'Red'
            Say (T 'WmBroken2') 'Red'
            Show-BakHint
            Exit-Patcher 1
        }
        $state = @{ Hash = $hash; Ids = $ids; Values = $vals }
        Say (T 'WmFound') 'Green'
        Say (T 'WmScanned' $ids.Count) 'Green'
    } else {
        Write-Host ''
        Say (T 'HashBad1') 'Red'
        Say (T 'HashBad2') 'Red'
        Write-Host ''
        Say (T 'Expected' $EXPECTED_HASH)
        Say (T 'Found' $hash)
        Write-Host ''
        Say (T 'HashBad3')
        Show-BakHint
        Exit-Patcher 1
    }
    $f = $orig
    $patchedMode = $true
    $appliedIds = @($state.Ids)
}""")
# Selbsttest Tabelle nach dem Patchen
R("""    $stateError = Write-State $stateTmp (Get-Sha256 $f) $origBytes.Length $chosenIds $VALUES $undo
""", """    if ($null -eq (Restore-FromTable $f)) { Write-Host ''; Say (T 'TableWarn') 'Yellow' }
    $stateError = Write-State $stateTmp (Get-Sha256 $f) $origBytes.Length $chosenIds $VALUES $undo
""")
