# Ergaenzung zu fix_ori_bak.py: englische README-Zeile zu den Sicherungen, Hinweis bei Nr. 4 in PATCHES.
# Aufruf: fix_ori_bak2.py <Worktree>
import sys
w = sys.argv[1]
def edit(p, pairs):
    s = open(w + '/' + p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:90], s.count(a))
        s = s.replace(a, b)
    open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)

edit('docs/README.md', [
("""- `Wow.exe.ORI` is not touched on later runs and is always the original. If
  it is missing, the patcher recreates it from the reconstructed original. In
  addition, every later run saves the previous `Wow.exe` as `Wow.exe.BAK`, so
  one step back is always possible.
""", """- `Wow.exe.ORI` is not touched on later runs and is always the original. In
  addition, every later run saves the previous `Wow.exe` as `Wow.exe.BAK`, so
  one step back is always possible.
- **Missing backups** are created right at the start, even if nothing is
  patched afterwards – for example when you copy a patched `Wow.exe` into a new
  patcher folder: `Wow.exe.ORI` from the original (reconstructed from a patched
  `Wow.exe` and checked by SHA256) and, for a patched `Wow.exe`, its current
  state as `Wow.exe.BAK`. Existing backups are left untouched.
"""),
])
edit('docs/PATCHES.de.md', [
("""Prüfung im Schleifenkörper, bei gleicher Codegröße.
""", """Prüfung im Schleifenkörper, bei gleicher Codegröße. Eine `Wow.exe` mit der
Fassung vor dem 9.10.2026 (Sprung bei VA `0x81D51B`) erkennt der Patcher
ebenfalls und kann sie zurücknehmen.
"""),
])
edit('docs/PATCHES.en.md', [
("""the loop body, with the same code size.
""", """the loop body, with the same code size. A `Wow.exe` with the version from
before 2026-10-09 (jump at VA `0x81D51B`) is recognized as well and can be
reverted.
"""),
])
print('ok')
