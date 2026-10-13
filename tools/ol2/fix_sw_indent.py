# Umschalter: Einrueckung buendig (Say setzt selbst zwei Leerzeichen davor). Aufruf: fix_sw_indent.py <Worktree>
import sys
p = sys.argv[1] + '/apply_patches.ps1'
raw = open(p, 'rb').read(); assert raw.count(b'\r\n') == raw.count(b'\n')
s = raw.decode('ascii').replace('\r\n', '\n')
for a, b in (("""        Say "  $(L $q.De $q.En):"
        if ($q.NoteDe) { Say "    $(L $q.NoteDe $q.NoteEn)" 'DarkGray' }
        for ($i = 0; $i -lt $lines.Count - 1; $i++) { Say "    $($lines[$i])" }""",
"""        Say "$(L $q.De $q.En):"
        if ($q.NoteDe) { Say "  $(L $q.NoteDe $q.NoteEn)" 'DarkGray' }
        for ($i = 0; $i -lt $lines.Count - 1; $i++) { Say "  $($lines[$i])" }"""),):
    assert s.count(a) == 1
    s = s.replace(a, b)
open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('ok')
