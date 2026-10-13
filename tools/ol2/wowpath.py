# Pfad zur Wow.exe im Startmenue (P), gemerkt als wowpath= in patcher_selection.ini; Sicherungen und
# patcher_state.ini immer im Patcher-Ordner (auch mit -Path). Aufruf: wowpath.py <Worktree>
import sys, re
w = sys.argv[1]
p = w + '/apply_patches.ps1'
raw = open(p, 'rb').read(); assert raw.count(b'\r\n') == raw.count(b'\n')
s = raw.decode('ascii').replace('\r\n', '\n')
def once(a, b):
    global s
    n = s.count(a); assert n == 1, (a[:90], n)
    s = s.replace(a, b)

# 1) Kopf: Pfad bestimmen ueber Set-WowFile
once("""$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path -Parent $scriptPath
$wowHits = @()
if (-not $Path) {
    $Path = Join-Path $scriptDir 'Wow.exe'
    # Linux unterscheidet Gross-/Kleinschreibung: dann auch WoW.exe, wow.exe
    # usw. finden. Unter Windows passt immer schon der Pfad oben. Liegen
    # mehrere Schreibweisen im Ordner, bricht der Patcher weiter unten ab.
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        $wowHits = @(Get-ChildItem -LiteralPath $scriptDir -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -ieq 'Wow.exe' })
        if ($wowHits.Count -eq 1) { $Path = $wowHits[0].FullName }
    }
} elseif (-not [System.IO.Path]::IsPathRooted($Path)) {
    # .NET loest relative Pfade gegen das Prozessverzeichnis auf, nicht gegen
    # das aktuelle PowerShell-Verzeichnis - daher selbst absolut machen.
    $Path = Join-Path (Get-Location).ProviderPath $Path
}
""", """$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path -Parent $scriptPath
$settingsFile = Join-Path $scriptDir 'patcher_selection.ini'
$stateFile = Join-Path $scriptDir 'patcher_state.ini'
if ($Path -and -not [System.IO.Path]::IsPathRooted($Path)) {
    # .NET loest relative Pfade gegen das Prozessverzeichnis auf, nicht gegen
    # das aktuelle PowerShell-Verzeichnis - daher selbst absolut machen.
    $Path = Join-Path (Get-Location).ProviderPath $Path
}

# Gemerkter Pfad zur Wow.exe (Zeile "wowpath=..." in patcher_selection.ini,
# im Startmenue mit P festgelegt).
function Get-SavedWowPath {
    if (-not (Test-Path -LiteralPath $settingsFile -PathType Leaf)) { return $null }
    try { $lines = [System.IO.File]::ReadAllLines($settingsFile) } catch { return $null }
    foreach ($l in $lines) {
        if ($l -match '^\\s*wowpath\\s*=\\s*(.+?)\\s*$') { return $matches[1] }
    }
    return $null
}

# Welche Wow.exe: -Path (nur fuer diesen Lauf), sonst der gemerkte Pfad, sonst
# die im Patcher-Ordner. Linux unterscheidet Gross-/Kleinschreibung: im
# Patcher-Ordner dann auch WoW.exe, wow.exe usw. finden. Unter Windows passt
# immer schon der erste Pfad. Liegen dort mehrere Schreibweisen, bricht der
# Patcher weiter unten ab. Die Sicherungen (.ORI/.BAK) liegen immer im
# Patcher-Ordner, auch wenn die Wow.exe woanders liegt.
function Set-WowFile {
    $script:wowHits = @()
    $script:wowPathSaved = Get-SavedWowPath
    $script:wowExternal = $true
    if ($Path) { $p = $Path }
    elseif ($script:wowPathSaved) { $p = $script:wowPathSaved }
    else {
        $script:wowExternal = $false
        $p = Join-Path $scriptDir 'Wow.exe'
        if (-not (Test-Path -LiteralPath $p -PathType Leaf)) {
            $script:wowHits = @(Get-ChildItem -LiteralPath $scriptDir -File -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -ieq 'Wow.exe' })
            if ($script:wowHits.Count -eq 1) { $p = $script:wowHits[0].FullName }
        }
    }
    $script:file = $p
    $leaf = Split-Path -Leaf $p
    $script:backup = Join-Path $scriptDir ($leaf + '.ORI')       # Original, wird beim ersten Start angelegt
    $script:backupPrev = Join-Path $scriptDir ($leaf + '.BAK')   # vorherige (gepatchte) Wow.exe
}
Set-WowFile
""")
once("""$file = $Path
$backup = $file + '.ORI'       # Original, wird beim ersten Patchen angelegt
$backupPrev = $file + '.BAK'   # vorherige (gepatchte) Wow.exe bei jedem weiteren Lauf
$settingsFile = Join-Path $scriptDir 'patcher_selection.ini'
$stateFile = Join-Path $scriptDir 'patcher_state.ini'
""", "")

# 2) Texte
once("""        StartOptM     = '  M = Patch-Menue oeffnen und das Startmenue kuenftig ueberspringen (wird gemerkt)'
""", """        StartOptM     = '  M = Patch-Menue oeffnen und das Startmenue kuenftig ueberspringen (wird gemerkt)'
        StartOptP     = '  P = Pfad zur Wow.exe festlegen (wird gemerkt)'
        PathAsk       = 'Pfad zur Wow.exe oder zum WoW-Ordner (ENTER = Wow.exe im Patcher-Ordner)'
        PathBad       = 'Dort ist keine Wow.exe: {0}'
        PathSet       = 'Gemerkt - der Patcher nimmt jetzt diese Wow.exe: {0}'
        PathReset     = 'Gemerkt - der Patcher nimmt wieder die Wow.exe im Patcher-Ordner.'
        WowAt         = 'Wow.exe: {0} (Sicherungen im Patcher-Ordner)'
        NoExeHint     = 'Lege eine originale Wow.exe in den Patcher-Ordner oder gib mit P ihren Pfad an.'
""")
once("""        StartOptM     = '  M = Open the patch menu and skip the start menu from now on (remembered)'
""", """        StartOptM     = '  M = Open the patch menu and skip the start menu from now on (remembered)'
        StartOptP     = '  P = Set the path to Wow.exe (remembered)'
        PathAsk       = 'Path to Wow.exe or to the WoW folder (ENTER = Wow.exe in the patcher folder)'
        PathBad       = 'There is no Wow.exe there: {0}'
        PathSet       = 'Remembered - the patcher now uses this Wow.exe: {0}'
        PathReset     = 'Remembered - the patcher uses the Wow.exe in the patcher folder again.'
        WowAt         = 'Wow.exe: {0} (backups in the patcher folder)'
        NoExeHint     = 'Put an original Wow.exe into the patcher folder or set its path with P.'
""")

# 3) Speichern/Abfragen des Pfads (bei den anderen Einstellungs-Funktionen)
once("""# Nur die Werte (value.<Id>=...) in patcher_selection.ini erneuern, die Auswahl
""", """# Nur den Pfad zur Wow.exe in patcher_selection.ini setzen (leer = Zeile
# entfernen, dann gilt wieder der Patcher-Ordner), alles andere bleibt stehen.
function Save-WowPath([string]$p) {
    try {
        $lines = New-Object System.Collections.Generic.List[string]
        if (Test-Path -LiteralPath $settingsFile -PathType Leaf) {
            foreach ($l in [System.IO.File]::ReadAllLines($settingsFile)) {
                if ($l -notmatch '^\\s*wowpath\\s*=') { $lines.Add($l) }
            }
        }
        if ($p) { $lines.Add("wowpath=$p") }
        [System.IO.File]::WriteAllLines($settingsFile, $lines.ToArray())
    } catch { }
}

# Startmenue, P: Pfad zur Wow.exe abfragen und merken - die Exe selbst oder
# ein Ordner mit einer Wow.exe. Beim Hineinziehen ins Fenster kommen
# Anfuehrungszeichen (im PowerShell-Fenster auch "& '...'") mit, die fallen
# weg. ENTER = wieder die Wow.exe im Patcher-Ordner. Liefert die Meldung fuer
# die neue Seite.
function Read-WowPath {
    while ($true) {
        $in = Ask "  $(T 'PathAsk')"
        if ($in.StartsWith('& ')) { $in = $in.Substring(2).Trim() }
        $in = $in.Trim('"', "'").Trim()
        if ($in -eq '') {
            Save-WowPath ''
            return (T 'PathReset')
        }
        $p = [Environment]::ExpandEnvironmentVariables($in)
        if (-not [System.IO.Path]::IsPathRooted($p)) { $p = Join-Path (Get-Location).ProviderPath $p }
        if (Test-Path -LiteralPath $p -PathType Container) {
            $hits = @(Get-ChildItem -LiteralPath $p -File -ErrorAction SilentlyContinue | Where-Object { $_.Name -ieq 'Wow.exe' })
            if ($hits.Count -eq 1) { $p = $hits[0].FullName } else { $p = $null }
        } elseif (-not (Test-Path -LiteralPath $p -PathType Leaf)) {
            $p = $null
        }
        if ($p) {
            $p = [System.IO.Path]::GetFullPath($p)
            Save-WowPath $p
            return (T 'PathSet' $p)
        }
        Say (T 'PathBad' $in) 'Yellow'
    }
}

# Nur die Werte (value.<Id>=...) in patcher_selection.ini erneuern, die Auswahl
""")
once("""    if ($script:startMenuOff) { $lines.Add('startmenu=off') } else { $lines.Add('startmenu=on') }
    try {
        [System.IO.File]::WriteAllLines($settingsFile, $lines.ToArray())
        return $null""", """    if ($script:startMenuOff) { $lines.Add('startmenu=off') } else { $lines.Add('startmenu=on') }
    if ($script:wowPathSaved) { $lines.Add("wowpath=$script:wowPathSaved") }
    try {
        [System.IO.File]::WriteAllLines($settingsFile, $lines.ToArray())
        return $null""")

# 4) Abschnitt 2 in eine Schleife (P: neuer Pfad -> Pruefung und Startmenue neu)
once("""# Patch-Menue - ausser die Wow.exe fehlt oder ist nicht verwendbar. Vorhandene
# Sicherungen werden nur gelesen bzw. kopiert, nie verschoben oder
# ueberschrieben.
if ($wowHits.Count -gt 1) {""", """# Patch-Menue - ausser die Wow.exe fehlt oder ist nicht verwendbar. Mit P
# laesst sich ein anderer Pfad zur Wow.exe festlegen (gemerkt als wowpath= in
# patcher_selection.ini), danach laufen Pruefung und Startmenue auf einer
# neuen Seite noch einmal. Vorhandene Sicherungen werden nur gelesen bzw.
# kopiert, nie verschoben oder ueberschrieben.
if ($wowHits.Count -gt 1) {""")
a = s.index("if ($wowHits.Count -gt 1) {")
z = s.index("# --- 3. Patches auswaehlen ---")
body = s[a:z].rstrip('\n') + '\n'
assert "@'" not in body and '@"' not in body
ind = ''.join(('    ' + l if l.strip() else l) for l in body.splitlines(True))
s = s[:a] + """$pathNote = ''
:check while ($true) {
    $patchedMode = $false; $appliedIds = @(); $fromOri = $false; $f = $null; $state = $null
    if ($pathNote) { Say $pathNote 'Green'; Write-Host ''; $pathNote = '' }
    if ($wowExternal) { Say (T 'WowAt' $file) 'DarkGray' }
""" + ind + """    break
}

""" + s[z:]

# 5) Ohne Wow.exe und ohne Sicherung: interaktiv Startmenue mit P statt Abbruch
once("""    # Ohne verwendbare Wow.exe geht es nur ueber eine Sicherung weiter - ohne
    # Rueckfragen (-Unattended) oder ohne Sicherung ist hier Schluss.
    $usable = $haveExe -and -not $broken
    $canRestore = $oriOk -or $bakOk
    if (-not $usable -and ($Unattended -or -not $canRestore)) {""", """    # Ohne verwendbare Wow.exe geht es nur ueber eine Sicherung oder einen
    # anderen Pfad (P) weiter - ohne Rueckfragen (-Unattended) ist hier
    # Schluss, mit -Path auch ohne Sicherung.
    $usable = $haveExe -and -not $broken
    $canRestore = $oriOk -or $bakOk
    if (-not $usable -and ($Unattended -or ($Path -and -not $canRestore))) {""")
once("""        if (-not $haveExe) { Say (T 'RestFound') 'Yellow' }
        elseif ($broken) { Say (T 'RestBroken') 'Yellow' }
        elseif ($canRestore) { Say (T 'StartBackups') }""", """        if (-not $haveExe -and $canRestore) { Say (T 'RestFound') 'Yellow' }
        elseif (-not $haveExe) { Say (T 'NotFound' $file) 'Red'; Say (T 'NoExeHint'); Write-Host '' }
        elseif ($broken -and $canRestore) { Say (T 'RestBroken') 'Yellow' }
        elseif ($broken) { Say (T 'NoExeHint'); Write-Host '' }
        elseif ($canRestore) { Say (T 'StartBackups') }""")
once("""        if ($usable) { Say (T 'StartOptM'); $keys += 'M' }
        Say (T 'RestOptQ')""", """        if ($usable) { Say (T 'StartOptM'); $keys += 'M' }
        if (-not $Path) { Say (T 'StartOptP'); $keys += 'P' }
        Say (T 'RestOptQ')""")
once("""        if ($pick -eq 'M') {""", """        if ($pick -eq 'P') {
            # Neuer Pfad: gemerkt, dann Pruefung und Startmenue auf einer neuen Seite.
            $pathNote = Read-WowPath
            Set-WowFile
            Clear-Host
            Write-Host ''
            Show-Banner
            Write-Host ''
            continue check
        }
        if ($pick -eq 'M') {""")
once("""                # Die Wow.exe bekommt den Namen der Sicherung ohne Endung - unter
                # Linux also z.B. wow.exe zu wow.exe.ORI.
                $file = $src.Substring(0, $src.Length - 4)""", """                # Die Wow.exe bekommt den Namen der Sicherung ohne Endung - unter
                # Linux also z.B. wow.exe zu wow.exe.ORI. Mit einem Pfad (P,
                # -Path) kommt sie dorthin.
                if (-not $wowExternal) { $file = $src.Substring(0, $src.Length - 4) }""")
once("""            Say (T 'RestCopyBack')
            Exit-Patcher 0""", """            if (-not $wowExternal) { Say (T 'RestCopyBack') }
            Exit-Patcher 0""")
once("""            # Neu aus dem Original. Fehlt die Wow.exe, bekommt sie den Namen des
            # Originals ohne Endung (unter Linux z.B. wow.exe zu wow.exe.ORI), die
            # Sicherungen heissen passend dazu. Eine nicht verwendbare Wow.exe wird
            # beim Schreiben ersetzt.
            if (-not $haveExe) {""", """            # Neu aus dem Original. Fehlt die Wow.exe im Patcher-Ordner, bekommt
            # sie den Namen des Originals ohne Endung (unter Linux z.B. wow.exe
            # zu wow.exe.ORI), die Sicherungen heissen passend dazu. Mit einem
            # Pfad (P, -Path) kommt sie dorthin. Eine nicht verwendbare Wow.exe
            # wird beim Schreiben ersetzt.
            if (-not $haveExe -and -not $wowExternal) {""")
open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('ok')
