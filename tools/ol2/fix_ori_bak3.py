# Ergaenzung zu fix_ori_bak.py: Q im Startmenue nach angelegter Sicherung -> "Die Wow.exe wurde nicht veraendert."
# Aufruf: fix_ori_bak3.py <Worktree>
import sys
w = sys.argv[1]
p = w + '/apply_patches.ps1'
raw = open(p, 'rb').read()
assert raw.count(b'\r\n') == raw.count(b'\n')
s = raw.decode('ascii').replace('\r\n', '\n')
pairs = [
("""if ($haveExe -and -not $broken) {
    $made = $false
    if (-not $oriFile) {""", """$madeBackup = $false
if ($haveExe -and -not $broken) {
    if (-not $oriFile) {"""),
("""            $oriFile = $backup; $oriOk = $true; $made = $true""",
 """            $oriFile = $backup; $oriOk = $true; $madeBackup = $true"""),
("""            $bakFile = $backupPrev; $bakOk = $true; $bakHash = $hash; $made = $true""",
 """            $bakFile = $backupPrev; $bakOk = $true; $bakHash = $hash; $madeBackup = $true"""),
("""    if ($made) { Write-Host '' }""", """    if ($madeBackup) { Write-Host '' }"""),
("""    if ($pick -eq 'Q') {
        Say (T 'RestAbort') 'Yellow'
        Exit-Patcher 2
    }""", """    if ($pick -eq 'Q') {
        # Eben angelegte Sicherungen bleiben; geaendert wurde nur die Wow.exe nicht.
        if ($madeBackup) { Say (T 'Aborted') 'Yellow' } else { Say (T 'RestAbort') 'Yellow' }
        Exit-Patcher 2
    }"""),
]
for a, b in pairs:
    assert s.count(a) == 1, (a[:80], s.count(a))
    s = s.replace(a, b)
open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('ok')
