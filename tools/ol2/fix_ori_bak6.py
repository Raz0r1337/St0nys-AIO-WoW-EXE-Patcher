# Ergaenzung zu fix_ori_bak5.py: README DE/EN - Schritt 9, Startmenue (.BAK gleich Wow.exe), Dateitabelle.
# Aufruf: fix_ori_bak6.py <Worktree>
import sys
w = sys.argv[1]
def edit(p, pairs):
    s = open(w + '/' + p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:90], s.count(a))
        s = s.replace(a, b)
    open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)

edit('docs/README.de.md', [
("""9. Backup: Beim ersten Patchen wird das Original als `Wow.exe.ORI` gesichert,
   bei jedem weiteren Lauf die bisherige `Wow.exe` als `Wow.exe.BAK`. Fehlende
   Sicherungen legt der Patcher schon nach der Prüfung in Schritt 4 an, auch
   wenn danach nichts gepatcht wird (siehe
   [Patches ändern oder zurücknehmen](#patches-ändern-oder-zurücknehmen)).
""", """9. Backup: Das Original sichert der Patcher als `Wow.exe.ORI` – schon gleich
   nach der Prüfung in Schritt 4, auch wenn danach nichts gepatcht wird –, bei
   jedem weiteren Lauf die bisherige `Wow.exe` als `Wow.exe.BAK` (siehe
   [Patches ändern oder zurücknehmen](#patches-ändern-oder-zurücknehmen)).
"""),
("""sich verwenden lässt: Das Original muss laut SHA256 wirklich das Original sein,
das Backup original oder mit diesem Patcher gepatcht.
""", """sich verwenden lässt: Das Original muss laut SHA256 wirklich das Original sein,
das Backup original oder mit diesem Patcher gepatcht. Hat `Wow.exe.BAK`
denselben Stand wie die `Wow.exe` – etwa weil der Patcher sie gerade erst
angelegt hat –, entfällt `2`.
"""),
("""| `Wow.exe.ORI`       | Sicherung der originalen `Wow.exe`, angelegt beim ersten Patchen |
""", """| `Wow.exe.ORI`       | Sicherung der originalen `Wow.exe`, angelegt beim ersten Start |
"""),
])
edit('docs/README.md', [
("""9. Backup: on the first patch run the original is saved as `Wow.exe.ORI`, on
   every later run the previous `Wow.exe` is saved as `Wow.exe.BAK`. Missing
   backups are created right after the check in step 4, even if nothing is
   patched afterwards (see
   [Changing or removing patches](#changing-or-removing-patches)).
""", """9. Backup: the patcher saves the original as `Wow.exe.ORI` – right after the
   check in step 4, even if nothing is patched afterwards – and on every later
   run the previous `Wow.exe` as `Wow.exe.BAK` (see
   [Changing or removing patches](#changing-or-removing-patches)).
"""),
("""original must really be the original according to SHA256, the backup original
or patched with this patcher.
""", """original must really be the original according to SHA256, the backup original
or patched with this patcher. If `Wow.exe.BAK` has the same state as
`Wow.exe` – e.g. because the patcher has just created it – `2` is left out.
"""),
("""| `Wow.exe.ORI`       | Backup of the original `Wow.exe`, created on the first patch run |
""", """| `Wow.exe.ORI`       | Backup of the original `Wow.exe`, created on the first start |
"""),
])
print('ok')
