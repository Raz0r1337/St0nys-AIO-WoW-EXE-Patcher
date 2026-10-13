# Ergaenzung zu fix_ori_bak3.py: Leerzeile auch nach einem Hinweis; .BAK gleich der Wow.exe
# im Startmenue als solche zeigen und ohne Option 2. Aufruf: fix_ori_bak4.py <Worktree>
import sys
w = sys.argv[1]
p = w + '/apply_patches.ps1'
raw = open(p, 'rb').read()
assert raw.count(b'\r\n') == raw.count(b'\n')
s = raw.decode('ascii').replace('\r\n', '\n')
pairs = [
# --- Leerzeile nach den Meldungen, auch wenn nur ein Hinweis kam ---
("""$madeBackup = $false
if ($haveExe -and -not $broken) {
    if (-not $oriFile) {
        try {""", """$madeBackup = $false
if ($haveExe -and -not $broken) {
    $said = $false
    if (-not $oriFile) {
        $said = $true
        try {"""),
("""    if ($patchedMode -and -not $bakFile) {
        try {
            [System.IO.File]::Copy($file, $backupPrev, $false)""", """    if ($patchedMode -and -not $bakFile) {
        $said = $true
        try {
            [System.IO.File]::Copy($file, $backupPrev, $false)"""),
("""    if ($madeBackup) { Write-Host '' }
}""", """    if ($said) { Write-Host '' }
}"""),
# --- Texte ---
("""        RestBak       = '  Backup:   {0} (Stand vor dem letzten Patchen)'
""", """        RestBak       = '  Backup:   {0} (Stand vor dem letzten Patchen)'
        RestBakSame   = '  Backup:   {0} (gleicher Stand wie die aktuelle Wow.exe)'
"""),
("""        RestBak       = '  Backup:   {0} (state before the last patching)'
""", """        RestBak       = '  Backup:   {0} (state before the last patching)'
        RestBakSame   = '  Backup:   {0} (same state as the current Wow.exe)'
"""),
# --- Startmenue ---
("""    if ($oriOk) { Say (T 'RestOri' (Split-Path -Leaf $oriFile)) }
    if ($bakOk) { Say (T 'RestBak' (Split-Path -Leaf $bakFile)) }
    if ($oriFile -and -not $oriOk) { Say (T 'RestBadOri' (Split-Path -Leaf $oriFile)) 'Yellow' }
    if ($bakFile -and -not $bakOk) { Say (T 'RestBadBak' (Split-Path -Leaf $bakFile)) 'Yellow' }
    if ($canRestore -or $oriFile -or $bakFile) { Write-Host '' }""", """    # Eine .BAK mit demselben Stand wie die Wow.exe (z.B. eben beim Start
    # angelegt) wird nur gelistet - zurueckzuholen gibt es daraus nichts.
    $bakSame = $usable -and $bakOk -and $bakHash -eq $hash
    if ($oriOk) { Say (T 'RestOri' (Split-Path -Leaf $oriFile)) }
    if ($bakSame) { Say (T 'RestBakSame' (Split-Path -Leaf $bakFile)) }
    elseif ($bakOk) { Say (T 'RestBak' (Split-Path -Leaf $bakFile)) }
    if ($oriFile -and -not $oriOk) { Say (T 'RestBadOri' (Split-Path -Leaf $oriFile)) 'Yellow' }
    if ($bakFile -and -not $bakOk) { Say (T 'RestBadBak' (Split-Path -Leaf $bakFile)) 'Yellow' }
    if ($canRestore -or $oriFile -or $bakFile) { Write-Host '' }"""),
("""    if ($bakOk) { Say (T 'RestOpt2'); $keys += '2' }""", """    if ($bakOk -and -not $bakSame) { Say (T 'RestOpt2'); $keys += '2' }"""),
]
for a, b in pairs:
    assert s.count(a) == 1, (a[:80], s.count(a))
    s = s.replace(a, b)
open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('ok')
