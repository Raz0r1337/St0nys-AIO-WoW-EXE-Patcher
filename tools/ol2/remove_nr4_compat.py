# Alte Nr.-4-Stelle (VA 0x81D51B) wieder aus Skript und Doku nehmen (Tabelle danach mit -BuildTable neu).
# Aufruf: remove_nr4_compat.py <Worktree>
import sys
w = sys.argv[1]
def edit(p, pairs, crlf=False):
    raw = open(w + '/' + p, 'rb').read()
    if crlf: assert raw.count(b'\r\n') == raw.count(b'\n')
    s = raw.decode('ascii' if crlf else 'utf-8').replace('\r\n', '\n')
    for a, b in pairs:
        assert s.count(a) == 1, (p, a[:90], s.count(a))
        s = s.replace(a, b)
    if crlf: open(w + '/' + p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
    else: open(w + '/' + p, 'w', encoding='utf-8', newline='\n').write(s)
edit('apply_patches.ps1', [
("""    Patch ($HOOK_VA - 0x400C00) ([byte[]](Get-Rel32 @(0xE9) $HOOK_VA $CAVE))
    # Die Fassung bis 9.10.2026 sprang schon bei VA 0x81D51B ab (6 Byte, jae).
    # Die Stelle bleibt unveraendert, wird aber mit ihren Original-Bytes
    # geschrieben, damit sie in der Original-Byte-Tabelle steht: So erkennt der
    # Patcher auch Exes mit der alten Fassung und kann sie zuruecknehmen.
    Assert-Bytes 0x41C91B @(0x0F, 0x83, 0x4D, 0x01, 0x00, 0x00) 'WorldFrame-Absturzfix'
    Patch 0x41C91B @(0x0F, 0x83, 0x4D, 0x01, 0x00, 0x00)
}
""", """    Patch ($HOOK_VA - 0x400C00) ([byte[]](Get-Rel32 @(0xE9) $HOOK_VA $CAVE))
}
"""),
], crlf=True)
edit('docs/PATCHES.de.md', [
("""Prüfung im Schleifenkörper, bei gleicher Codegröße. Eine `Wow.exe` mit der
Fassung bis zum 9.10.2026 (Sprung bei VA `0x81D51B`) erkennt der Patcher
ebenfalls und kann sie zurücknehmen.
""", """Prüfung im Schleifenkörper, bei gleicher Codegröße.
"""),
])
edit('docs/PATCHES.en.md', [
("""the loop body, with the same code size. A `Wow.exe` with the version up to
2026-10-09 (jump at VA `0x81D51B`) is recognized as well and can be reverted.
""", """the loop body, with the same code size.
"""),
])
print('ok')
