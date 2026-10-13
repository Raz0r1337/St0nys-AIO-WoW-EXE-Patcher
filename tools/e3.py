R("""# Datei-Inhalt, wird einmal gelesen, im Speicher gepatcht und einmal geschrieben
$f = $null
""", """# Datei-Inhalt, wird einmal gelesen, im Speicher gepatcht und einmal geschrieben
$f = $null

# Gepatchte Wow.exe aus einem frueheren Lauf? Dann die dort aktiven Patch-Ids.
$patchedMode = $false
$appliedIds = @()
""")
R("""Say (T 'Welcome4')
Write-Host ''
""", """Say (T 'Welcome4')
Say (T 'Welcome5')
Write-Host ''
""")
R("""# --- 2. Wow.exe vorhanden und original? ---""", """# --- 2. Wow.exe vorhanden und original oder zuletzt von hier gepatcht? ---
# Beim ersten Start muss die Wow.exe original sein. Danach muss sie exakt die
# Datei sein, die der letzte Lauf erzeugt hat (Hash in patcher_state.ini);
# aus ihr wird dann das Original im Speicher rekonstruiert.""")
R("""Say (T 'Checking')
$f = [System.IO.File]::ReadAllBytes($file)
$sha = [System.Security.Cryptography.SHA256]::Create()
$hash = ([BitConverter]::ToString($sha.ComputeHash($f))).Replace('-', '')
if ($hash -ne $EXPECTED_HASH) {
    Write-Host ''
    Say (T 'HashBad1') 'Red'
    Say (T 'HashBad2') 'Red'
    Write-Host ''
    Say (T 'Expected' $EXPECTED_HASH)
    Say (T 'Found' $hash)
    Write-Host ''
    Say (T 'HashBad3')
    Exit-Patcher 1
}
Say (T 'HashOk') 'Green'
Write-Host ''
""", """Say (T 'Checking')
$f = [System.IO.File]::ReadAllBytes($file)
$hash = Get-Sha256 $f
$state = $null
if ($hash -eq $EXPECTED_HASH) {
    Say (T 'HashOk') 'Green'
} else {
    $state = Read-State
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
}
Write-Host ''
""")
R("""} else {
    $selection = Select-Patches
    if ($null -eq $selection) {""", """} else {
    $message = ''
    if ($patchedMode) {
        $initial = New-Object bool[] $patches.Count
        for ($i = 0; $i -lt $patches.Count; $i++) { $initial[$i] = $appliedIds -contains $patches[$i].Id }
        $message = T 'AppliedLoaded'
    } else {
        $initial = Get-SavedSelection
        if ($null -eq $initial) { $initial = Get-DefaultSelection } else { $message = T 'SavedLoaded' }
    }
    $selection = Select-Patches $initial $message
    if ($null -eq $selection) {""")
R("""for ($i = 0; $i -lt $patches.Count; $i++) {
    if ($selection[$i]) { $chosen += , $patches[$i]; $chosenIds += $patches[$i].Id }
}
""", """for ($i = 0; $i -lt $patches.Count; $i++) {
    if ($selection[$i]) { $chosen += , $patches[$i]; $chosenIds += $patches[$i].Id }
}
if ($chosen.Count -eq 0 -and -not $patchedMode) {
    Say (T 'AlreadyOrig') 'Green'
    Exit-Patcher 0
}
""")
R("""# Vorschlag ist der gemerkte Wert, sonst der Default; Patches mit Suggest
# berechnen ihren Vorschlag selbst (Build-Datum: heute). Ohne Rueckfragen
# (-Unattended) gilt der gemerkte Wert, sonst der Vorschlag.
$VALUES = @{}
$savedValues = Get-SavedValues
$asked = $false
foreach ($p in $chosen) {
    if (-not $p.Check) { continue }
    $saved = $savedValues[$p.Id]
    $def = $saved
    if (-not $def) { $def = $p.Default }
    if ($p.Suggest -and -not ($Unattended -and $saved)) { $def = & $p.Suggest $saved }
""", """# Vorschlag ist der gemerkte Wert, sonst der Default; Patches mit Suggest
# berechnen ihren Vorschlag selbst (Build-Datum: heute). Ohne Rueckfragen
# (-Unattended) gilt der gemerkte Wert, sonst der Vorschlag. Ist der Patch
# schon in der Wow.exe, ist sein aktueller Wert der Vorschlag.
$VALUES = @{}
$savedValues = Get-SavedValues
$asked = $false
foreach ($p in $chosen) {
    if (-not $p.Check) { continue }
    $active = $patchedMode -and ($appliedIds -contains $p.Id) -and $state.Values.ContainsKey($p.Id)
    $saved = $savedValues[$p.Id]
    if ($active) { $saved = $state.Values[$p.Id] }
    $def = $saved
    if (-not $def) { $def = $p.Default }
    if ($p.Suggest -and -not $active -and -not ($Unattended -and $saved)) { $def = & $p.Suggest $saved }
""")
R("""# --- 4. Zusammenfassung, Hinweise, Bestaetigung ---
Write-Host ''
Say (T 'Summary' $chosen.Count) 'Cyan'
foreach ($p in $chosen) {
    if ($VALUES.ContainsKey($p.Id)) { Say "  - $(PatchName $p): $($VALUES[$p.Id])" } else { Say "  - $(PatchName $p)" }
    if ($p.Url) { Say "    $($p.Url)" 'DarkCyan' }
}
""", """# --- 4. Zusammenfassung, Hinweise, Bestaetigung ---
Write-Host ''
$added = @(); $changed = @(); $removed = @(); $kept = 0
if (-not $patchedMode) {
    Say (T 'Summary' $chosen.Count) 'Cyan'
    foreach ($p in $chosen) {
        if ($VALUES.ContainsKey($p.Id)) { Say "  - $(PatchName $p): $($VALUES[$p.Id])" } else { Say "  - $(PatchName $p)" }
        if ($p.Url) { Say "    $($p.Url)" 'DarkCyan' }
    }
} else {
    foreach ($p in $chosen) {
        if ($appliedIds -notcontains $p.Id) { $added += , $p }
        elseif ($VALUES.ContainsKey($p.Id) -and $VALUES[$p.Id] -cne $state.Values[$p.Id]) { $changed += , $p }
        else { $kept++ }
    }
    foreach ($id in $appliedIds) { if ($chosenIds -notcontains $id) { $removed += $id } }
    if ($added.Count + $changed.Count + $removed.Count -eq 0) {
        Say (T 'NoChange') 'Green'
        Exit-Patcher 0
    }
    if ($added.Count -gt 0) {
        Say (T 'SumAdd' $added.Count) 'Cyan'
        foreach ($p in $added) {
            if ($VALUES.ContainsKey($p.Id)) { Say "  + $(PatchName $p): $($VALUES[$p.Id])" 'Green' } else { Say "  + $(PatchName $p)" 'Green' }
            if ($p.Url) { Say "    $($p.Url)" 'DarkCyan' }
        }
    }
    if ($changed.Count -gt 0) {
        Say (T 'SumChange' $changed.Count) 'Cyan'
        foreach ($p in $changed) { Say "  ~ $(PatchName $p): $($state.Values[$p.Id]) -> $($VALUES[$p.Id])" 'Green' }
    }
    if ($removed.Count -gt 0) {
        Say (T 'SumRemove' $removed.Count) 'Cyan'
        foreach ($id in $removed) { Say "  - $(Get-NameById $id)" 'Yellow' }
    }
    Say (T 'SumKeep' $kept)
    if ($chosen.Count -eq 0) {
        Write-Host ''
        Say (T 'SumOriginal') 'Yellow'
    }
}
""")
R("""# --- 5. Backup ---
try {
    Copy-Item -LiteralPath $file -Destination $backup -Force
} catch {
    Say (T 'BackupFail') 'Red'
    Say $_.Exception.Message 'Red'
    Exit-Patcher 1
}
Say (T 'BackupOk' $backup)
Write-Host ''
""", """# --- 5. Backup (nur vom Original, eine vorhandene Sicherung bleibt sonst stehen) ---
if ($patchedMode) {
    Say (T 'BackupSkip')
} else {
    try {
        Copy-Item -LiteralPath $file -Destination $backup -Force
    } catch {
        Say (T 'BackupFail') 'Red'
        Say $_.Exception.Message 'Red'
        Exit-Patcher 1
    }
    Say (T 'BackupOk' $backup)
}
Write-Host ''
""")
R("""# --- 6. Patchen (im Speicher) ---
$total = $chosen.Count
$width = ([string]$total).Length
$cur = 0
try {
""", """# --- 6. Patchen (im Speicher) ---
# $f ist hier immer das Original (gelesen oder rekonstruiert); abgewaehlte
# Patches sind damit schon zurueckgenommen, die Auswahl wird neu eingespielt.
$origBytes = [byte[]]$f.Clone()
$writes.Clear()
foreach ($id in $removed) { Say "[-] $(Get-NameById $id)" 'Yellow' }
$total = $chosen.Count
$width = ([string]$total).Length
$cur = 0
try {
""")
R("""# --- 7. Datei einmal zurueckschreiben ---
try {
    [System.IO.File]::WriteAllBytes($file, $f)
} catch {
    Write-Host ''
    Say (T 'WriteFail') 'Red'
    Say $_.Exception.Message 'Red'
    Exit-Patcher 1
}

Write-Host ''
Say '============================================' 'Green'
Say (T 'Done1') 'Green'
Say (T 'Done2' $total) 'Green'
Say '============================================' 'Green'
Exit-Patcher 0""", """# --- 7. Zustand vorbereiten ---
# Erst die Original-Bytes sammeln und pruefen, dass sich das Ergebnis damit
# exakt zum Original zuruecknehmen laesst. Der neue Zustand geht zuerst in
# eine .tmp-Datei und ersetzt den alten erst, wenn die Wow.exe geschrieben ist.
$stateTmp = $stateFile + '.tmp'
if ($total -gt 0) {
    $undo = Get-UndoEntries $origBytes
    if ($null -eq (Restore-Original $f @{ Size = [int64]$origBytes.Length; Undo = $undo })) {
        Write-Host ''
        Say (T 'UndoFail') 'Red'
        Say (T 'NotWritten') 'Red'
        Exit-Patcher 1
    }
    $stateError = Write-State $stateTmp (Get-Sha256 $f) $origBytes.Length $chosenIds $VALUES $undo
    if ($stateError) {
        Write-Host ''
        Say (T 'StateFail') 'Red'
        Say $stateError 'Red'
        Say (T 'NotWritten') 'Red'
        Exit-Patcher 1
    }
}

# --- 8. Datei einmal zurueckschreiben ---
try {
    [System.IO.File]::WriteAllBytes($file, $f)
} catch {
    Write-Host ''
    Say (T 'WriteFail') 'Red'
    Say $_.Exception.Message 'Red'
    try { Remove-Item -LiteralPath $stateTmp -Force -ErrorAction SilentlyContinue } catch { }
    Exit-Patcher 1
}

# --- 9. Zustand uebernehmen (ohne Patches ist die Wow.exe original, dann weg damit) ---
$stateWarn = $null
try {
    if ($total -gt 0) {
        [System.IO.File]::Copy($stateTmp, $stateFile, $true)
        [System.IO.File]::Delete($stateTmp)
    } elseif (Test-Path -LiteralPath $stateFile -PathType Leaf) {
        [System.IO.File]::Delete($stateFile)
    }
} catch {
    $stateWarn = $_.Exception.Message
}

Write-Host ''
Say '============================================' 'Green'
if ($total -eq 0) {
    Say (T 'DoneOrig') 'Green'
} else {
    Say (T 'Done1') 'Green'
    if ($patchedMode) {
        Say (T 'Done3' $added.Count $changed.Count $removed.Count $total) 'Green'
    } else {
        Say (T 'Done2' $total) 'Green'
    }
}
Say '============================================' 'Green'
if ($stateWarn -and $total -gt 0) {
    Write-Host ''
    Say (T 'StateWarn1') 'Yellow'
    Say $stateWarn 'Yellow'
    Say (T 'StateWarn2') 'Yellow'
} elseif ($total -gt 0) {
    Write-Host ''
    Say (T 'StateSaved') 'DarkGray'
}
Exit-Patcher 0""")
