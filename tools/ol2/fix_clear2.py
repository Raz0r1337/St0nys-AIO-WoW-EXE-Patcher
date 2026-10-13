# Ergaenzung zu fix_clear.py: nach dem Leeren wieder das ASCII-Banner oben (Startmenue-Seite).
import sys
w = sys.argv[1]
p = w + '/apply_patches.ps1'
raw = open(p, 'rb').read(); assert raw.count(b'\r\n') == raw.count(b'\n')
s = raw.decode('ascii').replace('\r\n', '\n')
a = """# Danach auf leerem Bildschirm weiter: Pruefung, Startmenue bzw. Patch-Menue
# stehen dann nicht unter Banner und Warnungen.
if (-not $Unattended) {
    [void](Read-Host "  $(T 'PressStart')")
    Clear-Host
    Write-Host ''
}
"""
b = """# Danach auf einer neuen Seite weiter, oben wieder das Banner: Pruefung und
# Startmenue stehen dann nicht unter Begruessung und Warnungen. Das
# Patch-Menue und alles danach kommen ohne Banner (eigene Seiten).
if (-not $Unattended) {
    [void](Read-Host "  $(T 'PressStart')")
    Clear-Host
    Write-Host ''
    Show-Banner
    Write-Host ''
}
"""
assert s.count(a) == 1
s = s.replace(a, b)
open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('ok')
