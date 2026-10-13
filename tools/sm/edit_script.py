# Startmenue bei jedem Start (abschaltbar mit M) in apply_patches.ps1 einbauen.
# Aufruf: edit_script.py <apply_patches.ps1> <new_step2.txt>
import sys
path, step2 = sys.argv[1], sys.argv[2]
raw = open(path, 'rb').read()
assert raw.count(b'\r\n') == raw.count(b'\n'), 'erwarte CRLF'
s = raw.decode('ascii').replace('\r\n', '\n')

def once(a, b):
    global s
    n = s.count(a)
    assert n == 1, (a[:100], n)
    s = s.replace(a, b)

# --- Kopf: Ablauf ---
once('''#    2. Pruefen: Wow.exe vorhanden und original (SHA256) bzw. mit diesem
#       Patcher gepatcht (Wasserzeichen) - dann Patchstand ermitteln
#    3. Patches auswaehlen (Menue mit Vorauswahl)
#    4. Bestaetigen, Backup anlegen''', '''#    2. Pruefen: Wow.exe vorhanden und original (SHA256) bzw. mit diesem
#       Patcher gepatcht (Wasserzeichen) - dann Patchstand ermitteln
#    3. Startmenue: Patch-Menue oeffnen oder die Wow.exe aus einer Sicherung
#       wiederherstellen (abschaltbar, dann direkt weiter mit 4)
#    4. Patches auswaehlen (Menue mit Vorauswahl)
#    5. Bestaetigen, Backup anlegen''')

once('''# Keine Wow.exe, im Wiederherstellungs-Menue "neu aus dem Original" gewaehlt
$fromOri = $false''', '''# Im Startmenue "neu aus dem Original" gewaehlt (Wow.exe fehlt oder ist nicht verwendbar)
$fromOri = $false''')

# --- Texte ---
once('''        RestFound     = 'Keine Wow.exe gefunden, aber Sicherungen im Ordner:'
''', '''        RestFound     = 'Keine Wow.exe gefunden, aber Sicherungen im Ordner:'
        RestBroken    = 'Die Wow.exe ist nicht verwendbar, es gibt aber Sicherungen im Ordner:'
        StartBackups  = 'Sicherungen im Ordner:'
''')
once('''        RestAsk       = 'Was moechtest du tun?'
        RestOpt1      = '  1 = Neue Wow.exe aus dem Original bauen (Patches wie zuletzt, im Menue aenderbar)'
''', '''        RestAsk       = 'Was moechtest du tun?'
        StartOpt1     = '  1 = Patch-Menue oeffnen (Patches auswaehlen, dazu- oder abwaehlen)'
        RestOpt1      = '  1 = Neue Wow.exe aus dem Original bauen (Patches wie zuletzt, im Menue aenderbar)'
        RestOpt1Repl  = '  1 = Neue Wow.exe aus dem Original bauen (ersetzt die aktuelle, Patches wie zuletzt)'
''')
once('''        RestOptQ      = '  Q = Abbrechen, nichts aendern'
''', '''        StartOptM     = '  M = Patch-Menue oeffnen und das Startmenue kuenftig ueberspringen (wird gemerkt)'
        RestOptQ      = '  Q = Abbrechen, nichts aendern'
        RestReplace   = 'Die aktuelle {0} wird durch {1} ersetzt.'
        RestConfirm   = 'Fortfahren? (J/N)'
        RestSame      = '{0} ist bereits identisch mit {1} - es gibt nichts zu tun.'
''')
once('''        RestFound     = 'No Wow.exe found, but there are backups in the folder:'
''', '''        RestFound     = 'No Wow.exe found, but there are backups in the folder:'
        RestBroken    = 'This Wow.exe cannot be used, but there are backups in the folder:'
        StartBackups  = 'Backups in the folder:'
''')
once('''        RestAsk       = 'What do you want to do?'
        RestOpt1      = '  1 = Build a new Wow.exe from the original (patches as last time, changeable in the menu)'
''', '''        RestAsk       = 'What do you want to do?'
        StartOpt1     = '  1 = Open the patch menu (select, add or remove patches)'
        RestOpt1      = '  1 = Build a new Wow.exe from the original (patches as last time, changeable in the menu)'
        RestOpt1Repl  = '  1 = Build a new Wow.exe from the original (replaces the current one, patches as last time)'
''')
once('''        RestOptQ      = '  Q = Cancel, change nothing'
''', '''        StartOptM     = '  M = Open the patch menu and skip the start menu from now on (remembered)'
        RestOptQ      = '  Q = Cancel, change nothing'
        RestReplace   = 'The current {0} will be replaced by {1}.'
        RestConfirm   = 'Continue? (Y/N)'
        RestSame      = '{0} is already identical to {1} - nothing to do.'
''')
# BakHint wird nicht mehr gebraucht (die Hinweise kommen jetzt aus dem Startmenue bzw. RestUnatt)
once('''        BakHint       = 'Tipp: {0} ist die originale Wow.exe. Zurueck nach Wow.exe kopieren und den Patcher neu starten.'
''', '')
once('''        BakHint       = 'Tip: {0} is the original Wow.exe. Copy it back to Wow.exe and start the patcher again.'
''', '')
once('''        MenuHelp2     = 'A = alle an    N = alle aus    L = English    Q = abbrechen'
''', '''        MenuHelp2     = 'A = alle an    N = alle aus    L = English    M = {0}    Q = abbrechen'
        MenuStartOff  = 'Startmenue ausschalten'
        MenuStartOn   = 'Startmenue einschalten'
''')
once('''        MenuHelp2     = 'A = all on    N = all off    L = Deutsch    Q = quit'
''', '''        MenuHelp2     = 'A = all on    N = all off    L = Deutsch    M = {0}    Q = quit'
        MenuStartOff  = 'turn start menu off'
        MenuStartOn   = 'turn start menu on'
''')
once('''        LangInfo      = 'Sprache: Deutsch (gemerkt, im Menue mit L umschaltbar)'
''', '''        LangInfo      = 'Sprache: Deutsch (gemerkt, im Menue mit L umschaltbar)'
        StartMenuOff  = 'Startmenue: aus (gemerkt, im Patch-Menue mit M wieder einschaltbar)'
        StartNowOff   = 'Startmenue ausgeschaltet: Beim naechsten Start geht es direkt ins Patch-Menue (mit M wieder einschalten).'
        StartNowOn    = 'Startmenue eingeschaltet: Es erscheint wieder bei jedem Start.'
''')
once('''        LangInfo      = 'Language: English (remembered, switch with L in the menu)'
''', '''        LangInfo      = 'Language: English (remembered, switch with L in the menu)'
        StartMenuOff  = 'Start menu: off (remembered, switch it back on with M in the patch menu)'
        StartNowOff   = 'Start menu turned off: next time the patch menu opens directly (turn it back on with M).'
        StartNowOn    = 'Start menu turned on: it appears at every start again.'
''')

# --- Einstellung lesen/schreiben ---
once('''# Nur die Werte (value.<Id>=...) in patcher_selection.ini erneuern''', '''# Startmenue abgeschaltet? (Zeile "startmenu=off" in patcher_selection.ini)
function Get-StartMenuOff {
    if (-not (Test-Path -LiteralPath $settingsFile -PathType Leaf)) { return $false }
    try { $lines = [System.IO.File]::ReadAllLines($settingsFile) } catch { return $false }
    foreach ($l in $lines) {
        if ($l -match '^\\s*startmenu\\s*=\\s*off\\s*$') { return $true }
    }
    return $false
}

# Nur die Einstellung fuer das Startmenue in patcher_selection.ini setzen
# (startmenu=on bzw. off), alles andere bleibt stehen. Fehler beim Schreiben
# sind hier unkritisch und werden ignoriert.
function Save-StartMenu {
    try {
        $lines = New-Object System.Collections.Generic.List[string]
        if (Test-Path -LiteralPath $settingsFile -PathType Leaf) {
            foreach ($l in [System.IO.File]::ReadAllLines($settingsFile)) {
                if ($l -notmatch '^\\s*startmenu\\s*=') { $lines.Add($l) }
            }
        }
        if ($script:startMenuOff) { $lines.Add('startmenu=off') } else { $lines.Add('startmenu=on') }
        [System.IO.File]::WriteAllLines($settingsFile, $lines.ToArray())
    } catch { }
}

# Nur die Werte (value.<Id>=...) in patcher_selection.ini erneuern''')
once('''    $lines.Add("language=$script:lang")
    try {''', '''    $lines.Add("language=$script:lang")
    if ($script:startMenuOff) { $lines.Add('startmenu=off') } else { $lines.Add('startmenu=on') }
    try {''')

# --- Show-BakHint faellt weg ---
once('''# Hinweis auf Wow.exe.ORI bzw. Wow.exe.BAK, wenn eine davon das Original enthaelt
# (.BAK war in aelteren Versionen das Original).
# Sicherung (.ORI/.BAK)''', '''# Sicherung (.ORI/.BAK)''')
once('''function Show-BakHint {
    foreach ($b in @($backup, $backupPrev)) {
        try {
            if (-not (Test-Path -LiteralPath $b -PathType Leaf)) { continue }
            if ((Get-Sha256 ([System.IO.File]::ReadAllBytes($b))) -ne $EXPECTED_HASH) { continue }
            Write-Host ''
            Say (T 'BakHint' $b) 'Yellow'
            return
        } catch { }
    }
}

''', '')
once('''# Sicherung (.ORI/.BAK) zu einer fehlenden Wow.exe: der erwartete Name, sonst''',
     '''# Sicherung (.ORI/.BAK) zur Wow.exe: der erwartete Name, sonst''')

# --- Patch-Menue: Taste M ---
once('''    Say (T 'MenuHelp2')
''', '''    if ($script:startMenuOff) { $mk = T 'MenuStartOn' } else { $mk = T 'MenuStartOff' }
    Say (T 'MenuHelp2' $mk)
''')
once('''                Save-Language $script:lang
                break
            }
''', '''                Save-Language $script:lang
                break
            }
            '^[mM]$'   {
                $script:startMenuOff = -not $script:startMenuOff
                Save-StartMenu
                if ($script:startMenuOff) { $message = T 'StartNowOff' } else { $message = T 'StartNowOn' }
                break
            }
''')

# --- Begruessung: gemerkte Einstellungen ---
once('''if ($langFromSettings) {
    Say (T 'LangInfo') 'DarkGray'
    Write-Host ''
}
''', '''# Gemerkte Einstellungen kurz anzeigen: Sprache und abgeschaltetes Startmenue
$startMenuOff = Get-StartMenuOff
$infos = @()
if ($langFromSettings) { $infos += T 'LangInfo' }
if ($startMenuOff -and -not $Unattended -and -not $Select) { $infos += T 'StartMenuOff' }
if ($infos.Count -gt 0) {
    foreach ($i in $infos) { Say $i 'DarkGray' }
    Write-Host ''
}
''')

# --- Schritt 2 komplett ---
a = s.index('# --- 2. Wow.exe vorhanden und original oder mit diesem Patcher gepatcht? ---\n')
z = s.index('# --- 3. Patches auswaehlen ---\n')
new2 = open(step2, encoding='ascii').read().replace('\r\n', '\n').rstrip('\n') + '\n\n'
s = s[:a] + new2 + s[z:]

# --- Schritt 3: Hinweis nach M im Startmenue ---
once('''    $selection = Select-Patches $initial $message
''', '''    if ($startNote) { if ($message) { $message = "$message`n  $startNote" } else { $message = $startNote } }
    $selection = Select-Patches $initial $message
''')

# --- Schritt 5: Kommentar ---
once('''        # Neu aus dem Original: Wow.exe.ORI bleibt, wie es ist, und eine
        # bisherige Wow.exe fuer ein .BAK gibt es nicht.''', '''        # Neu aus dem Original: Wow.exe.ORI bleibt, wie es ist. Ein .BAK gibt
        # es nicht - eine fehlende Wow.exe hat keins, eine nicht verwendbare
        # wird ersetzt.''')

assert 'Show-BakHint' not in s and "'BakHint'" not in s
open(path, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('ok', path)
