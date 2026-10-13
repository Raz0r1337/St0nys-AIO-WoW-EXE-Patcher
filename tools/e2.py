R("""function Get-SelectedCount($sel) {""", r"""# ============================================================
#  Zustand der gepatchten Wow.exe (patcher_state.ini)
#  Nach jedem Patchen merkt sich der Patcher den SHA256 der erzeugten Datei,
#  die eingespielten Patches samt Werten, die Groesse des Originals und die
#  Original-Bytes an allen Stellen, die die Patches beschrieben haben. Passt
#  die Wow.exe beim naechsten Start zu diesem Hash, wird daraus das Original
#  rekonstruiert (und per SHA256 geprueft) und die neue Auswahl darauf
#  eingespielt. So lassen sich Patches beliebig dazu- und abwaehlen.
# ============================================================
function Get-Sha256([byte[]]$data) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try { return ([BitConverter]::ToString($sha.ComputeHash($data))).Replace('-', '') } finally { $sha.Dispose() }
}

function ConvertFrom-Hex([string]$hex) {
    $b = New-Object byte[] ($hex.Length / 2)
    for ($i = 0; $i -lt $b.Length; $i++) { $b[$i] = [Convert]::ToByte($hex.Substring(2 * $i, 2), 16) }
    return , $b
}

# Liefert $null, wenn es keine lesbare Zustandsdatei gibt. Undo-Eintraege
# sind Paare @(Offset, Original-Bytes).
function Read-State {
    if (-not (Test-Path -LiteralPath $stateFile -PathType Leaf)) { return $null }
    try { $lines = [System.IO.File]::ReadAllLines($stateFile) } catch { return $null }
    $st = @{ Hash = $null; Size = [int64]-1; Ids = @(); Values = @{}; Undo = New-Object System.Collections.Generic.List[object] }
    foreach ($l in $lines) {
        if ($l -match '^hash=([0-9A-Fa-f]{64})$') { $st.Hash = $matches[1].ToUpperInvariant() }
        elseif ($l -match '^size=(\d+)$') { $st.Size = [int64]$matches[1] }
        elseif ($l -match '^patches=(.*)$') { $st.Ids = @($matches[1] -split ',' | Where-Object { $_ -ne '' }) }
        elseif ($l -match '^value\.([A-Za-z0-9_]+)=(.*)$') { $st.Values[$matches[1]] = $matches[2] }
        elseif ($l -match '^undo=0x([0-9A-Fa-f]+):((?:[0-9A-Fa-f]{2})+)$') {
            $st.Undo.Add(@([Convert]::ToInt64($matches[1], 16), (ConvertFrom-Hex $matches[2])))
        }
    }
    if (-not $st.Hash -or $st.Size -le 0) { return $null }
    return $st
}

# Rekonstruiert aus einer gepatchten Datei das Original: auf die alte Groesse
# kuerzen (angehaengte Sektionen fallen weg), Original-Bytes zurueckschreiben.
# Liefert $null, wenn das Ergebnis nicht exakt die originale Wow.exe ist.
function Restore-Original([byte[]]$data, $st) {
    if ($st.Size -gt $data.Length) { return $null }
    $o = New-Object byte[] $st.Size
    [Array]::Copy($data, 0, $o, 0, $st.Size)
    foreach ($u in $st.Undo) {
        if ($u[0] + $u[1].Length -gt $o.Length) { return $null }
        [Array]::Copy($u[1], 0, $o, $u[0], $u[1].Length)
    }
    if ((Get-Sha256 $o) -ne $EXPECTED_HASH) { return $null }
    return , $o
}

# Original-Bytes zu allen Schreibzugriffen von Patch(), die im Original liegen.
function Get-UndoEntries([byte[]]$orig) {
    $undo = New-Object System.Collections.Generic.List[object]
    $seen = @{}
    for ($i = 0; $i -lt $script:writes.Count; $i += 2) {
        $off = $script:writes[$i]
        $end = $off + $script:writes[$i + 1]
        if ($off -ge $orig.Length) { continue }
        if ($end -gt $orig.Length) { $end = $orig.Length }
        if ($seen.ContainsKey("$off/$end")) { continue }
        $seen["$off/$end"] = $true
        $b = New-Object byte[] ($end - $off)
        [Array]::Copy($orig, $off, $b, 0, $b.Length)
        $undo.Add(@($off, $b))
    }
    return , $undo
}

# Zustandsdatei schreiben. Liefert $null oder die Fehlermeldung.
function Write-State([string]$path, [string]$hash, [int64]$size, $ids, $values, $undo) {
    $lines = New-Object System.Collections.Generic.List[string]
    $lines.Add('# St0nys-AIO-WoW-EXE-Patcher - Zustand der gepatchten Wow.exe / state of the patched Wow.exe')
    $lines.Add('# Nicht von Hand aendern! Ohne diese Datei lassen sich die Patches nicht mehr zuruecknehmen.')
    $lines.Add('# Do not edit! Without this file the patches can no longer be removed.')
    $lines.Add("hash=$hash")
    $lines.Add("size=$size")
    $lines.Add("patches=$($ids -join ',')")
    foreach ($k in ($values.Keys | Sort-Object)) { $lines.Add("value.$k=$($values[$k])") }
    foreach ($u in $undo) {
        $lines.Add(('undo=0x{0:X}:{1}' -f $u[0], ([BitConverter]::ToString($u[1])).Replace('-', '')))
    }
    try {
        [System.IO.File]::WriteAllLines($path, $lines.ToArray())
        return $null
    } catch {
        return $_.Exception.Message
    }
}

# Hinweis auf Wow.exe.BAK, wenn sie das Original enthaelt.
function Show-BakHint {
    try {
        if (-not (Test-Path -LiteralPath $backup -PathType Leaf)) { return }
        if ((Get-Sha256 ([System.IO.File]::ReadAllBytes($backup))) -ne $EXPECTED_HASH) { return }
        Write-Host ''
        Say (T 'BakHint' $backup) 'Yellow'
    } catch { }
}

function Get-PatchById([string]$id) {
    foreach ($q in $patches) { if ($q.Id -eq $id) { return $q } }
    return $null
}

# Anzeigename auch fuer Ids, die es in dieser Version nicht mehr gibt.
function Get-NameById([string]$id) {
    $q = Get-PatchById $id
    if ($q) { return PatchName $q }
    return $id
}

function Get-SelectedCount($sel) {""")

# Menue: Markierungen und O-Taste
R("""        $nr = ([string]($i + 1)).PadLeft($width)
        if ($sel[$i]) {
            Write-Host "   $nr  [X]  $(PatchName $patches[$i])" -ForegroundColor Green
        } else {
            Write-Host "   $nr  [ ]  $(PatchName $patches[$i])" -ForegroundColor DarkGray
        }
""", """        $nr = ([string]($i + 1)).PadLeft($width)
        $was = $script:patchedMode -and ($script:appliedIds -contains $patches[$i].Id)
        if ($sel[$i]) {
            $mark = ''; if ($script:patchedMode -and -not $was) { $mark = ' ' + (T 'MarkNew') }
            Write-Host "   $nr  [X]  $(PatchName $patches[$i])$mark" -ForegroundColor Green
        } elseif ($was) {
            Write-Host "   $nr  [ ]  $(PatchName $patches[$i]) $(T 'MarkRemove')" -ForegroundColor Yellow
        } else {
            Write-Host "   $nr  [ ]  $(PatchName $patches[$i])" -ForegroundColor DarkGray
        }
""")
R("""    Say (T 'MenuHelp3')
    if ($message) {""", """    Say (T 'MenuHelp3')
    if ($script:patchedMode) { Say (T 'MenuHelp4') }
    if ($message) {""")
R("""# Interaktive Auswahl. Liefert das bool-Array oder $null bei Abbruch.
function Select-Patches {
    $sel = Get-SavedSelection
    $message = ''
    if ($null -eq $sel) { $sel = Get-DefaultSelection } else { $message = T 'SavedLoaded' }
    while ($true) {
        Show-Menu $sel $message
        $message = ''
        $in = Ask "  $(T 'Prompt')"
        switch -regex ($in) {
            '^$' {
                if ((Get-SelectedCount $sel) -eq 0) { $message = T 'NoneSelected'; break }
                return , $sel
            }
""", """# Interaktive Auswahl, beginnend mit $sel. Liefert das bool-Array oder $null
# bei Abbruch. Eine leere Auswahl gibt es nur fuer eine gepatchte Wow.exe -
# sie bedeutet: alle Patches zuruecknehmen.
function Select-Patches([bool[]]$sel, [string]$message) {
    while ($true) {
        Show-Menu $sel $message
        $message = ''
        $in = Ask "  $(T 'Prompt')"
        switch -regex ($in) {
            '^$' {
                if ((Get-SelectedCount $sel) -eq 0 -and -not $script:patchedMode) { $message = T 'NoneSelected'; break }
                return , $sel
            }
            '^[oO]$' {
                if (-not $script:patchedMode) { $message = T 'BadInput' $in; break }
                for ($i = 0; $i -lt $sel.Length; $i++) { $sel[$i] = $false }
                return , $sel
            }
""")
R("""    $sel = New-Object bool[] $patches.Count
    if ($v -eq 'all' -or $v -eq 'alle') {""", """    $sel = New-Object bool[] $patches.Count
    if ($v -eq 'none' -or $v -eq 'keine' -or $v -eq 'original') { return , $sel }
    if ($v -eq 'all' -or $v -eq 'alle') {""")
