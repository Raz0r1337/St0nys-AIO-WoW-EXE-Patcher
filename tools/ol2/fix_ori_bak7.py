# Ergaenzung zu fix_ori_bak6.py: Datum in der Nr.-4-Notiz (alte Fassung bis einschliesslich 9.10.2026).
# Aufruf: fix_ori_bak7.py <Worktree>
import sys
w = sys.argv[1]
def edit(p, pairs):
    s = open(w + '/' + p, encoding='utf-8').read()
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:90], s.count(a))
        s = s.replace(a, b)
    open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)
edit('docs/PATCHES.de.md', [
("""Prüfung im Schleifenkörper, bei gleicher Codegröße. Eine `Wow.exe` mit der
Fassung vor dem 9.10.2026 (Sprung bei VA `0x81D51B`) erkennt der Patcher
ebenfalls und kann sie zurücknehmen.
""", """Prüfung im Schleifenkörper, bei gleicher Codegröße. Eine `Wow.exe` mit der
Fassung bis zum 9.10.2026 (Sprung bei VA `0x81D51B`) erkennt der Patcher
ebenfalls und kann sie zurücknehmen.
"""),
])
edit('docs/PATCHES.en.md', [
("""the loop body, with the same code size. A `Wow.exe` with the version from
before 2026-10-09 (jump at VA `0x81D51B`) is recognized as well and can be
reverted.
""", """the loop body, with the same code size. A `Wow.exe` with the version up to
2026-10-09 (jump at VA `0x81D51B`) is recognized as well and can be reverted.
"""),
])
print('ok')
