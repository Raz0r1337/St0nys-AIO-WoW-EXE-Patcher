# Umrandung Nr. 68: Teile umrandeter Einheiten ans Ende der Sortierung (outline8).
# Aufruf: edit_script8.py <apply_patches.ps1> <outline8_ps.txt>
import sys
path, gen = sys.argv[1], sys.argv[2]
raw = open(path, 'rb').read(); assert raw.count(b'\r\n') == raw.count(b'\n')
s = raw.decode('ascii').replace('\r\n', '\n')
new = open(gen, encoding='ascii').read().rstrip('\n') + '\n'
a = s.index('#  Umrandung fuer Ziel und Mouseover (St0ny), mit Einstellungen\n')
a = s.rindex('# ====', 0, a)
g = s.index('function Get-OutlineOptionsFromExe {', a)
z = s.index('\n}\n', g) + 3
assert s[a:z].count('function Add-Outline {') == 1
s = s[:a] + new + s[z:]
open(path, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('ok')
