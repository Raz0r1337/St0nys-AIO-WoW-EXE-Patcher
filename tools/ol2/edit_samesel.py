import sys
p = sys.argv[1]
raw = open(p, 'rb').read()
assert b'\r\n' in raw
s = raw.decode('ascii').replace('\r\n', '\n')
def rep(a, b):
    global s
    n = s.count(a); assert n == 1, (n, a[:90]); s = s.replace(a, b)
rep("""        RedoAsk       = 'Trotzdem neu patchen? (J = neu patchen, N = beenden)'
""", """        SameSel       = 'Gleiche Patches wie in der aktuellen Wow.exe.'
        SameOptJ      = 'J = neu patchen mit den aktuellen Einstellungen'
        SameOptE      = 'E = Einstellungen aendern'
        SameOptN      = 'N = beenden'
        SameKeyE      = 'E'
""")
rep("""        RedoAsk       = 'Patch again anyway? (Y = patch again, N = quit)'
""", """        SameSel       = 'Same patches as in the current Wow.exe.'
        SameOptJ      = 'Y = patch again with the current settings'
        SameOptE      = 'S = change settings'
        SameOptN      = 'N = quit'
        SameKeyE      = 'S'
""")
rep("""# --- 3b. Werte fuer Patches mit eigener Eingabe (Vorschlag: Get-ValueSuggestion) ---
$VALUES = @{}
$atConfirm = @()      # Ids, deren Wert erst beim Bestaetigen mit J feststeht (Build-Datum: jetzt)
$asked = $false
foreach ($p in $chosen) {
""", """# Gleiche Patches wie in der aktuellen Wow.exe: gleich hier, noch vor den Werten,
# fragen - neu patchen mit den aktuellen Einstellungen (z.B. nach einem Update,
# wenn ein Patch neuen Code hat - der Patchstand zaehlt nur Ids und Werte),
# Einstellungen aendern oder beenden. So muss niemand erst alle Werte
# durchgehen, um dann doch zu beenden. Ohne Rueckfragen (-Unattended) wie bisher.
$redo = $false
$sameIds = $patchedMode -and $chosen.Count -gt 0 -and $chosen.Count -eq @($appliedIds).Count
if ($sameIds) { foreach ($id in $chosenIds) { if ($appliedIds -notcontains $id) { $sameIds = $false } } }
if ($sameIds -and -not $Unattended) {
    $hasValues = $false
    foreach ($p in $chosen) { if ($p.Check) { $hasValues = $true } }
    Write-Host ''
    Say (T 'SameSel') 'Green'
    Say (T 'RedoInfo')
    Say "  $(T 'SameOptJ')"
    if ($hasValues) { Say "  $(T 'SameOptE')" }
    Say "  $(T 'SameOptN')"
    $def = 'N'; if ($hasValues) { $def = T 'SameKeyE' }
    $pick = $null
    while (-not $pick) {
        $a = (Ask "  $(T 'SafeAsk') [$def]").ToUpperInvariant()
        if ($a -eq '') { $a = $def }
        if ($a -eq (T 'Yes') -or $a -eq 'Y' -or $a -eq 'J') { $pick = 'J' }
        elseif ($hasValues -and ($a -eq 'E' -or $a -eq 'S')) { $pick = 'E' }
        elseif ($a -eq 'N') { $pick = 'N' }
    }
    if ($pick -eq 'N') {
        if ($state.Scanned -and $null -ne (Restore-Original $origPatched $state)) {
            # Patchstand kam ueber das Wasserzeichen - jetzt merken, dann geht es beim naechsten Mal schneller.
            if ($null -eq (Write-State $stateFile $state.Hash $state.Size $state.Ids $state.Values $state.Undo)) { Say (T 'StateSaved') 'DarkGray' }
        }
        Exit-Patcher 0
    }
    $redo = ($pick -eq 'J')
}

# --- 3b. Werte fuer Patches mit eigener Eingabe (Vorschlag: Get-ValueSuggestion) ---
$VALUES = @{}
$atConfirm = @()      # Ids, deren Wert erst beim Bestaetigen mit J feststeht (Build-Datum: jetzt)
$asked = $false
$askList = $chosen
if ($redo) {
    # Neu patchen mit den aktuellen Einstellungen: die Werte wie in der Wow.exe,
    # ohne Rueckfragen. Ist einer davon ungueltig, wird doch gefragt.
    foreach ($p in $chosen) {
        if (-not $p.Check) { continue }
        $v = Get-ValueSuggestion $p
        if (& $p.Check $v) { $redo = $false; $VALUES = @{}; $atConfirm = @(); break }
        if (Test-SuggestNow $p) { $atConfirm += $p.Id }
        if ($p.Normalize) { $v = & $p.Normalize $v }
        $VALUES[$p.Id] = $v
    }
    if ($redo) { $askList = @() }
}
foreach ($p in $askList) {
""")
rep("""    $redo = $false
    if ($added.Count + $changed.Count + $removed.Count -eq 0 -and $chosen.Count -gt 0) {
        Say (T 'NoChange') 'Green'
        # Ohne -Unattended fragen: trotzdem neu patchen (z.B. nach einem Update, wenn ein Patch neuen Code
        # hat - der Patchstand zaehlt nur Ids und Werte) oder beenden.
        if (-not $Unattended) {
            Write-Host ''
            Say (T 'RedoInfo')
            $answer = (Ask "  $(T 'RedoAsk')").ToUpperInvariant()
            $redo = ($answer -eq (T 'Yes') -or $answer -eq 'Y' -or $answer -eq 'J')
        }
        if (-not $redo) {
            if ($state.Scanned -and $null -ne (Restore-Original $origPatched $state)) {
                # Patchstand kam ueber das Wasserzeichen - jetzt merken, dann geht es beim naechsten Mal schneller.
                if ($null -eq (Write-State $stateFile $state.Hash $state.Size $state.Ids $state.Values $state.Undo)) { Say (T 'StateSaved') 'DarkGray' }
            }
            Exit-Patcher 0
        }
        Write-Host ''
        Say (T 'SumRedo' $chosen.Count) 'Cyan'
""", """    if ($added.Count + $changed.Count + $removed.Count -eq 0 -and $chosen.Count -gt 0) {
        # Neu patchen gab es schon nach der Auswahl (vor den Werten) - sonst gibt es nichts zu tun.
        if (-not $redo) {
            Say (T 'NoChange') 'Green'
            if ($state.Scanned -and $null -ne (Restore-Original $origPatched $state)) {
                # Patchstand kam ueber das Wasserzeichen - jetzt merken, dann geht es beim naechsten Mal schneller.
                if ($null -eq (Write-State $stateFile $state.Hash $state.Size $state.Ids $state.Values $state.Undo)) { Say (T 'StateSaved') 'DarkGray' }
            }
            Exit-Patcher 0
        }
        Say (T 'SumRedo' $chosen.Count) 'Cyan'
""")
assert 'RedoAsk' not in s
s.encode('ascii')
open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
