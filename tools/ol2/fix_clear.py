# Startmenue auf leerem Bildschirm: nach "ENTER zum Starten" den Bildschirm leeren. Aufruf: fix_clear.py <Worktree>
import sys
w = sys.argv[1]
p = w + '/apply_patches.ps1'
raw = open(p, 'rb').read(); assert raw.count(b'\r\n') == raw.count(b'\n')
s = raw.decode('ascii').replace('\r\n', '\n')
a = """if (-not $Unattended) {
    [void](Read-Host "  $(T 'PressStart')")
    Write-Host ''
}
"""
b = """# Danach auf leerem Bildschirm weiter: Pruefung, Startmenue bzw. Patch-Menue
# stehen dann nicht unter Banner und Warnungen.
if (-not $Unattended) {
    [void](Read-Host "  $(T 'PressStart')")
    Clear-Host
    Write-Host ''
}
"""
assert s.count(a) == 1
s = s.replace(a, b)
open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('ok')
