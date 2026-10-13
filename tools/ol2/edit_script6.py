# Umrandung Nr. 68: "nur wo verdeckt" repariert (outline6), Vorgabe hidden = J.
# Aufruf: edit_script6.py <apply_patches.ps1> <outline6_ps.txt>
import sys
path, gen = sys.argv[1], sys.argv[2]
raw = open(path, 'rb').read(); assert raw.count(b'\r\n') == raw.count(b'\n')
s = raw.decode('ascii').replace('\r\n', '\n')
new = open(gen, encoding='ascii').read().rstrip('\n') + '\n'
def once(a, b):
    global s
    n = s.count(a); assert n == 1, (a[:90], n)
    s = s.replace(a, b)
# 1) Kommentarkopf + Add-Outline + Einstellungen ersetzen
a = s.index('#  Umrandung fuer Ziel und Mouseover (St0ny), mit Einstellungen\n')
a = s.rindex('# ====', 0, a)
g = s.index('function Get-OutlineOptionsFromExe {', a)
z = s.index('\n}\n', g) + 3
assert s[a:z].count('function Add-Outline {') == 1
s = s[:a] + new + s[z:]
# 2) Vorgabe
once("""       Questions = $OUTLINE_OPTIONS
       Default = 'none'
""", """       Questions = $OUTLINE_OPTIONS
       Default = 'hidden'
""")
once("""        # Eigene Sektion (.outl), siehe Add-Outline. Die Einstellungen (J/N vor
        # dem Patchen, Standard alles N = nur Ziel und Mouseover, nicht durch
        # Waende) setzt Set-OutlineOptions.
""", """        # Eigene Sektion (.outl), siehe Add-Outline. Die Einstellungen (J/N vor
        # dem Patchen, Standard: nur "eigener Charakter nur wo verdeckt" = J)
        # setzt Set-OutlineOptions.
""")
# 3) Anzeige von "none" ist nicht mehr der Standard
once("""        OptNone       = 'Standard (alles N)'
""", """        OptNone       = 'alles N'
""")
once("""        OptNone       = 'default (all N)'
""", """        OptNone       = 'all N'
""")
open(path, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('ok')
