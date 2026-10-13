# Wiederherstellungs-Menue bei fehlender Wow.exe in apply_patches.ps1 (dev).
import sys, re
wt = sys.argv[1]
p = wt + '/apply_patches.ps1'
raw = open(p, 'rb').read().decode('ascii'); assert raw.count('\r\n') == raw.count('\n')
s = raw.replace('\r\n', '\n')
def once(s, a, b, label):
    n = s.count(a); assert n == 1, '%s: %d Treffer' % (label, n); return s.replace(a, b)

# --- A/B: Texte
m = re.search(r"(?m)^        WowMulti      = '\[FEHLER\].*\n", s); assert m
s = s[:m.end()] + (
"        RestFound     = 'Keine Wow.exe gefunden, aber Sicherungen im Ordner:'\n"
"        RestOri       = '  Original: {0}'\n"
"        RestBak       = '  Backup:   {0} (Stand vor dem letzten Patchen)'\n"
"        RestBadOri    = 'Hinweis: {0} ist nicht die originale Wow.exe (SHA256 passt nicht) und wird nicht verwendet.'\n"
"        RestBadBak    = 'Hinweis: {0} ist weder original noch mit diesem Patcher gepatcht und wird nicht verwendet.'\n"
"        RestAsk       = 'Was moechtest du tun?'\n"
"        RestOpt1      = '  1 = Neue Wow.exe aus dem Original bauen (Patches wie zuletzt, im Menue aenderbar)'\n"
"        RestOpt2      = '  2 = Vorherige Wow.exe wiederherstellen (Stand vor dem letzten Patchen)'\n"
"        RestOpt3      = '  3 = Original wiederherstellen'\n"
"        RestOptQ      = '  Q = Abbrechen, nichts aendern'\n"
"        RestDone      = '[OK] {0} wurde aus {1} wiederhergestellt. Original und Backup bleiben erhalten.'\n"
"        RestCopyBack  = 'Danach die Wow.exe wie gewohnt in den WoW-Ordner kopieren.'\n"
"        RestFail      = '[FEHLER] Wiederherstellen fehlgeschlagen:'\n"
"        RestUnatt     = 'Im Ordner liegen Sicherungen ({0}). Ohne -Unattended gestartet bietet der Patcher an, sie wiederherzustellen.'\n"
"        LastLoaded    = 'Ausgewaehlt sind die Patches, die zuletzt eingespielt waren. Mit R, B oder S laedst du ein Preset.'\n"
) + s[m.end():]
m = re.search(r"(?m)^        WowMulti      = '\[ERROR\].*\n", s); assert m
s = s[:m.end()] + (
"        RestFound     = 'No Wow.exe found, but there are backups in the folder:'\n"
"        RestOri       = '  Original: {0}'\n"
"        RestBak       = '  Backup:   {0} (state before the last patching)'\n"
"        RestBadOri    = 'Note: {0} is not the original Wow.exe (SHA256 does not match) and is not used.'\n"
"        RestBadBak    = 'Note: {0} is neither original nor patched with this patcher and is not used.'\n"
"        RestAsk       = 'What do you want to do?'\n"
"        RestOpt1      = '  1 = Build a new Wow.exe from the original (patches as last time, changeable in the menu)'\n"
"        RestOpt2      = '  2 = Restore the previous Wow.exe (state before the last patching)'\n"
"        RestOpt3      = '  3 = Restore the original'\n"
"        RestOptQ      = '  Q = Cancel, change nothing'\n"
"        RestDone      = '[OK] {0} has been restored from {1}. Original and backup are kept.'\n"
"        RestCopyBack  = 'Then copy Wow.exe into your WoW folder as usual.'\n"
"        RestFail      = '[ERROR] Restoring failed:'\n"
"        RestUnatt     = 'There are backups in the folder ({0}). Started without -Unattended, the patcher offers to restore them.'\n"
"        LastLoaded    = 'Selected are the patches applied last time. Load a preset with R, B or S.'\n"
) + s[m.end():]

# --- I: Merker
s = once(s, "$patchedMode = $false\n$appliedIds = @()\n",
            "$patchedMode = $false\n$appliedIds = @()\n"
            "# Keine Wow.exe, im Wiederherstellungs-Menue \"neu aus dem Original\" gewaehlt\n"
            "$fromOri = $false\n", 'Merker')

# --- C: Sicherung suchen
s = once(s, "function Show-BakHint {\n",
"# Sicherung (.ORI/.BAK) zu einer fehlenden Wow.exe: der erwartete Name, sonst\n"
"# (Linux) jede Schreibweise davon - aber nur bei genau einem Treffer.\n"
"function Find-Backup([string]$want) {\n"
"    if (Test-Path -LiteralPath $want -PathType Leaf) { return $want }\n"
"    $leaf = Split-Path -Leaf $want\n"
"    $hits = @(Get-ChildItem -LiteralPath (Split-Path -Parent $want) -File -ErrorAction SilentlyContinue |\n"
"        Where-Object { $_.Name -ieq $leaf })\n"
"    if ($hits.Count -eq 1) { return $hits[0].FullName }\n"
"    return $null\n"
"}\n\n"
"function Show-BakHint {\n", 'Find-Backup')

# --- D: Werte wie zuletzt auch beim Neubau aus dem Original
s = once(s, "    return ($script:patchedMode -and ($script:appliedIds -contains $p.Id) -and $script:state.Values.ContainsKey($p.Id))\n",
            "    return (($script:patchedMode -or $script:fromOri) -and ($script:appliedIds -contains $p.Id) -and $script:state.Values.ContainsKey($p.Id))\n", 'Test-ValueActive')

# --- E: Abschnitt 2
s = once(s,
"if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {\n"
"    Say (T 'NotFound' $file) 'Red'\n"
"    Exit-Patcher 1\n"
"}\n\n"
"Say (T 'Checking')\n"
"$f = [System.IO.File]::ReadAllBytes($file)\n",
"if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {\n"
"    # Keine Wow.exe, aber Sicherungen im Ordner (z.B. die gepatchte Exe in den\n"
"    # WoW-Ordner verschoben statt kopiert): 1 = neu aus dem Original bauen,\n"
"    # 2 = vorherige Wow.exe (.BAK), 3 = Original (.ORI). Die Sicherungen werden\n"
"    # nur gelesen bzw. kopiert, nie verschoben oder ueberschrieben.\n"
"    $oriFile = Find-Backup $backup\n"
"    $bakFile = Find-Backup $backupPrev\n"
"    $oriOk = $false; $bakOk = $false; $oriBytes = $null\n"
"    if ($oriFile) {\n"
"        try { $oriBytes = [System.IO.File]::ReadAllBytes($oriFile); $oriOk = ((Get-Sha256 $oriBytes) -eq $EXPECTED_HASH) } catch { }\n"
"    }\n"
"    if ($bakFile) {\n"
"        try { $b = [System.IO.File]::ReadAllBytes($bakFile); $bakOk = ((Get-Sha256 $b) -eq $EXPECTED_HASH) -or (Test-Watermark $b) } catch { }\n"
"    }\n"
"    if ((-not $oriOk -and -not $bakOk) -or $Unattended) {\n"
"        Say (T 'NotFound' $file) 'Red'\n"
"        if ($oriFile -and -not $oriOk) { Say (T 'RestBadOri' (Split-Path -Leaf $oriFile)) 'Yellow' }\n"
"        if ($bakFile -and -not $bakOk) { Say (T 'RestBadBak' (Split-Path -Leaf $bakFile)) 'Yellow' }\n"
"        if ($oriOk -or $bakOk) {\n"
"            $names = @(); if ($oriOk) { $names += Split-Path -Leaf $oriFile }; if ($bakOk) { $names += Split-Path -Leaf $bakFile }\n"
"            Say (T 'RestUnatt' ($names -join ', ')) 'Yellow'\n"
"        }\n"
"        Exit-Patcher 1\n"
"    }\n"
"    Say (T 'RestFound') 'Yellow'\n"
"    if ($oriOk) { Say (T 'RestOri' (Split-Path -Leaf $oriFile)) }\n"
"    if ($bakOk) { Say (T 'RestBak' (Split-Path -Leaf $bakFile)) }\n"
"    if ($oriFile -and -not $oriOk) { Say (T 'RestBadOri' (Split-Path -Leaf $oriFile)) 'Yellow' }\n"
"    if ($bakFile -and -not $bakOk) { Say (T 'RestBadBak' (Split-Path -Leaf $bakFile)) 'Yellow' }\n"
"    Write-Host ''\n"
"    Say (T 'RestAsk')\n"
"    $keys = @()\n"
"    if ($oriOk) { Say (T 'RestOpt1'); $keys += '1' }\n"
"    if ($bakOk) { Say (T 'RestOpt2'); $keys += '2' }\n"
"    if ($oriOk) { Say (T 'RestOpt3'); $keys += '3' }\n"
"    Say (T 'RestOptQ')\n"
"    $keys += 'Q'\n"
"    $pick = $null\n"
"    while (-not $pick) {\n"
"        $in = (Ask \"  [$($keys -join '/')]\").ToUpperInvariant()\n"
"        if ($keys -contains $in) { $pick = $in }\n"
"    }\n"
"    Write-Host ''\n"
"    if ($pick -eq 'Q') {\n"
"        Say (T 'Aborted') 'Yellow'\n"
"        Exit-Patcher 2\n"
"    }\n"
"    # Die Wow.exe bekommt den Namen der Sicherung ohne Endung - unter Linux\n"
"    # also z.B. wow.exe zu wow.exe.ORI. Die Sicherungen heissen dann wieder\n"
"    # passend dazu.\n"
"    if ($pick -eq '2') { $src = $bakFile } else { $src = $oriFile }\n"
"    $file = $src.Substring(0, $src.Length - 4)\n"
"    $backup = $file + '.ORI'\n"
"    $backupPrev = $file + '.BAK'\n"
"    if ($pick -eq '1') {\n"
"        $fromOri = $true\n"
"    } else {\n"
"        try {\n"
"            Copy-Item -LiteralPath $src -Destination $file\n"
"        } catch {\n"
"            Say (T 'RestFail') 'Red'\n"
"            Say $_.Exception.Message 'Red'\n"
"            Exit-Patcher 1\n"
"        }\n"
"        if (Get-Command Unblock-File -ErrorAction SilentlyContinue) {\n"
"            try { Unblock-File -LiteralPath $file -ErrorAction Stop } catch { }\n"
"        }\n"
"        Say (T 'RestDone' (Split-Path -Leaf $file) (Split-Path -Leaf $src)) 'Green'\n"
"        Say (T 'RestCopyBack')\n"
"        Exit-Patcher 0\n"
"    }\n"
"}\n\n"
"Say (T 'Checking')\n"
"if ($fromOri) { $f = $oriBytes } else { $f = [System.IO.File]::ReadAllBytes($file) }\n", 'Abschnitt 2')

# --- F: zuletzt eingespielte Patches und Werte beim Neubau
s = once(s, "# --- 3. Patches auswaehlen ---\n",
"# Neu aus dem Original (Wiederherstellungs-Menue, Option 1): Auswahl und Werte\n"
"# wie bei der zuletzt gepatchten Wow.exe, soweit patcher_state.ini sie kennt.\n"
"if ($fromOri) {\n"
"    $last = Read-State\n"
"    if ($null -ne $last -and @($last.Ids).Count -gt 0) { $state = $last; $appliedIds = @($last.Ids) }\n"
"}\n\n"
"# --- 3. Patches auswaehlen ---\n", 'Abschnitt 3 vorher')

# --- G: Vorauswahl
s = once(s,
"    } else {\n"
"        $initial = Get-SavedSelection\n"
"        if ($null -eq $initial) { $initial = Get-DefaultSelection } else { $message = T 'SavedLoaded' }\n"
"    }\n",
"    } elseif ($fromOri -and $appliedIds.Count -gt 0) {\n"
"        $initial = New-Object bool[] $patches.Count\n"
"        for ($i = 0; $i -lt $patches.Count; $i++) { $initial[$i] = $appliedIds -contains $patches[$i].Id }\n"
"        $message = T 'LastLoaded'\n"
"    } else {\n"
"        $initial = Get-SavedSelection\n"
"        if ($null -eq $initial) { $initial = Get-DefaultSelection } else { $message = T 'SavedLoaded' }\n"
"    }\n", 'Vorauswahl')

# --- H: Backup
s = once(s,
"try {\n"
"    if (-not $patchedMode) {\n"
"        Copy-Item -LiteralPath $file -Destination $backup -Force\n",
"try {\n"
"    if ($fromOri) {\n"
"        # Neu aus dem Original: Wow.exe.ORI bleibt, wie es ist, und eine\n"
"        # bisherige Wow.exe fuer ein .BAK gibt es nicht.\n"
"        Say (T 'BackupSkip')\n"
"    } elseif (-not $patchedMode) {\n"
"        Copy-Item -LiteralPath $file -Destination $backup -Force\n", 'Backup')

s.encode('ascii')
open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('Skript OK')
