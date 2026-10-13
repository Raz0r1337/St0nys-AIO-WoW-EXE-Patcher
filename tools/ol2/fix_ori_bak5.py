# Ergaenzung zu fix_ori_bak4.py: Kopfkommentar von Abschnitt 2. Aufruf: fix_ori_bak5.py <Worktree>
import sys
w = sys.argv[1]
p = w + '/apply_patches.ps1'
raw = open(p, 'rb').read()
assert raw.count(b'\r\n') == raw.count(b'\n')
s = raw.decode('ascii').replace('\r\n', '\n')
pairs = [
("""# rekonstruiert, sonst ueber die Original-Byte-Tabelle (mit Erkennung der
# eingespielten Patches und ihrer Werte).
# Danach kommt das Startmenue:""", """# rekonstruiert, sonst ueber die Original-Byte-Tabelle (mit Erkennung der
# eingespielten Patches und ihrer Werte). Fehlende Sicherungen (.ORI, bei einer
# gepatchten Exe auch .BAK) werden dann gleich angelegt.
# Danach kommt das Startmenue:"""),
("""# Patch-Menue - ausser die Wow.exe fehlt oder ist nicht verwendbar. Die
# Sicherungen werden nur gelesen bzw. kopiert, nie verschoben oder
# ueberschrieben.""", """# Patch-Menue - ausser die Wow.exe fehlt oder ist nicht verwendbar. Vorhandene
# Sicherungen werden nur gelesen bzw. kopiert, nie verschoben oder
# ueberschrieben."""),
]
for a, b in pairs:
    assert s.count(a) == 1, (a[:80], s.count(a))
    s = s.replace(a, b)
open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('ok')
