$oriFile = Find-Backup $backup
$bakFile = Find-Backup $backupPrev
$oriOk = $false; $bakOk = $false; $oriBytes = $null; $bakHash = $null
if ($oriFile) {
    try { $oriBytes = [System.IO.File]::ReadAllBytes($oriFile); $oriOk = ((Get-Sha256 $oriBytes) -eq $EXPECTED_HASH) } catch { }
}
if ($bakFile) {
    try { $b = [System.IO.File]::ReadAllBytes($bakFile); $bakHash = Get-Sha256 $b; $bakOk = ($bakHash -eq $EXPECTED_HASH) -or (Test-Watermark $b) } catch { }
}

$haveExe = Test-Path -LiteralPath $file -PathType Leaf
$broken = $false      # Wow.exe vorhanden, aber weder original noch sicher zuruecknehmbar
$state = $null
if ($haveExe) {
    Say (T 'Checking')
    $f = [System.IO.File]::ReadAllBytes($file)
    $hash = Get-Sha256 $f
    if ($hash -eq $EXPECTED_HASH) {
        Say (T 'HashOk') 'Green'
    } else {
        $state = Read-State
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
                $broken = $true
            } else {
                # Zustand wie nach dem Patchen: Original-Bytes aller erkannten Patches
                # aus der Tabelle. Gibt es nichts zu tun, wird er unten gespeichert,
                # damit der naechste Start wieder den schnellen Weg nehmen kann.
                $undo = New-Object System.Collections.Generic.List[object]
                foreach ($e in (Get-OriginalTable).Entries) {
                    if ($ids -contains $e.Id -or $e.Id -eq 'watermark' -or $e.Id -eq 'pe') { $undo.Add(@($e.Off, $e.Bytes)) }
                }
                $state = @{ Hash = $hash; Size = (Get-OriginalTable).Size; Ids = $ids; Values = $vals; Undo = $undo; Scanned = $true }
                Say (T 'WmFound') 'Green'
                Say (T 'WmScanned' $ids.Count) 'Green'
            }
        } else {
            Write-Host ''
            Say (T 'HashBad1') 'Red'
            Say (T 'HashBad2') 'Red'
            Write-Host ''
            Say (T 'Expected' $EXPECTED_HASH)
            Say (T 'Found' $hash)
            Write-Host ''
            Say (T 'HashBad3')
            $broken = $true
        }
        if (-not $broken) {
            $origPatched = $f      # die gepatchte Datei, wie sie auf der Platte liegt
            $f = $orig
            $patchedMode = $true
            $appliedIds = @($state.Ids)
        }
    }
    Write-Host ''
}

# Ohne verwendbare Wow.exe geht es nur ueber eine Sicherung weiter - ohne
# Rueckfragen (-Unattended) oder ohne Sicherung ist hier Schluss.
$usable = $haveExe -and -not $broken
$canRestore = $oriOk -or $bakOk
if (-not $usable -and ($Unattended -or -not $canRestore)) {
    if (-not $haveExe) { Say (T 'NotFound' $file) 'Red' }
    if ($oriFile -and -not $oriOk) { Say (T 'RestBadOri' (Split-Path -Leaf $oriFile)) 'Yellow' }
    if ($bakFile -and -not $bakOk) { Say (T 'RestBadBak' (Split-Path -Leaf $bakFile)) 'Yellow' }
    if ($canRestore) {
        $names = @(); if ($oriOk) { $names += Split-Path -Leaf $oriFile }; if ($bakOk) { $names += Split-Path -Leaf $bakFile }
        Say (T 'RestUnatt' ($names -join ', ')) 'Yellow'
    }
    Exit-Patcher 1
}

# Startmenue: bei jedem Start, ausser abgeschaltet, mit -Select oder mit
# -Unattended. Fehlt die Wow.exe oder ist sie nicht verwendbar, kommt es immer.
$startNote = ''
if (-not $Unattended -and (-not $usable -or (-not $Select -and -not $startMenuOff))) {
    if (-not $haveExe) { Say (T 'RestFound') 'Yellow' }
    elseif ($broken) { Say (T 'RestBroken') 'Yellow' }
    elseif ($canRestore) { Say (T 'StartBackups') }
    if ($oriOk) { Say (T 'RestOri' (Split-Path -Leaf $oriFile)) }
    if ($bakOk) { Say (T 'RestBak' (Split-Path -Leaf $bakFile)) }
    if ($oriFile -and -not $oriOk) { Say (T 'RestBadOri' (Split-Path -Leaf $oriFile)) 'Yellow' }
    if ($bakFile -and -not $bakOk) { Say (T 'RestBadBak' (Split-Path -Leaf $bakFile)) 'Yellow' }
    if ($canRestore -or $oriFile -or $bakFile) { Write-Host '' }
    Say (T 'RestAsk')
    $keys = @()
    if ($usable) { Say (T 'StartOpt1'); $keys += '1' }
    elseif ($oriOk -and $haveExe) { Say (T 'RestOpt1Repl'); $keys += '1' }
    elseif ($oriOk) { Say (T 'RestOpt1'); $keys += '1' }
    if ($bakOk) { Say (T 'RestOpt2'); $keys += '2' }
    if ($oriOk) { Say (T 'RestOpt3'); $keys += '3' }
    if ($usable) { Say (T 'StartOptM'); $keys += 'M' }
    Say (T 'RestOptQ')
    $keys += 'Q'
    $pick = $null
    while (-not $pick) {
        $in = (Ask "  [$($keys -join '/')]").ToUpperInvariant()
        if ($keys -contains $in) { $pick = $in }
    }
    Write-Host ''
    if ($pick -eq 'Q') {
        Say (T 'RestAbort') 'Yellow'
        Exit-Patcher 2
    }
    if ($pick -eq 'M') {
        # Ab jetzt direkt ins Patch-Menue; der Hinweis steht dort unter der Liste.
        $startMenuOff = $true
        Save-StartMenu
        $startNote = T 'StartNowOff'
    }
    if ($pick -eq '2' -or $pick -eq '3') {
        if ($pick -eq '2') { $src = $bakFile; $srcHash = $bakHash } else { $src = $oriFile; $srcHash = $EXPECTED_HASH }
        if ($haveExe) {
            # Die vorhandene Wow.exe wird ersetzt: nur nach Rueckfrage und nicht,
            # wenn sie schon genau der Sicherung entspricht.
            if ($hash -eq $srcHash) {
                Say (T 'RestSame' (Split-Path -Leaf $file) (Split-Path -Leaf $src)) 'Green'
                Exit-Patcher 0
            }
            Say (T 'RestReplace' (Split-Path -Leaf $file) (Split-Path -Leaf $src)) 'Yellow'
            $answer = (Ask "  $(T 'RestConfirm')").ToUpperInvariant()
            Write-Host ''
            if ($answer -ne (T 'Yes') -and $answer -ne 'Y' -and $answer -ne 'J') {
                Say (T 'RestAbort') 'Yellow'
                Exit-Patcher 2
            }
        } else {
            # Die Wow.exe bekommt den Namen der Sicherung ohne Endung - unter
            # Linux also z.B. wow.exe zu wow.exe.ORI.
            $file = $src.Substring(0, $src.Length - 4)
        }
        try {
            [System.IO.File]::Copy($src, $file, $haveExe)
        } catch {
            Say (T 'RestFail') 'Red'
            Say $_.Exception.Message 'Red'
            Exit-Patcher 1
        }
        if (Get-Command Unblock-File -ErrorAction SilentlyContinue) {
            try { Unblock-File -LiteralPath $file -ErrorAction Stop } catch { }
        }
        Say (T 'RestDone' (Split-Path -Leaf $file) (Split-Path -Leaf $src)) 'Green'
        Say (T 'RestCopyBack')
        Exit-Patcher 0
    }
    if ($pick -eq '1' -and -not $usable) {
        # Neu aus dem Original. Fehlt die Wow.exe, bekommt sie den Namen des
        # Originals ohne Endung (unter Linux z.B. wow.exe zu wow.exe.ORI), die
        # Sicherungen heissen passend dazu. Eine nicht verwendbare Wow.exe wird
        # beim Schreiben ersetzt.
        if (-not $haveExe) {
            $file = $oriFile.Substring(0, $oriFile.Length - 4)
            $backup = $file + '.ORI'
            $backupPrev = $file + '.BAK'
        }
        $fromOri = $true
        $f = $oriBytes
        # Auswahl und Werte wie bei der zuletzt gepatchten Wow.exe, soweit
        # patcher_state.ini sie kennt.
        $state = $null
        $last = Read-State
        if ($null -ne $last -and @($last.Ids).Count -gt 0) { $state = $last; $appliedIds = @($last.Ids) }
    }
}

