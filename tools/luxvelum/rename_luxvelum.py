#!/usr/bin/env python3
# Nr. 32: Luxveil heisst jetzt Luxvelum. Patch-Id, Namen, Texte, Doku und Hilfsskripte umbenennen; der neue
# DLL-Name "Luxvelum.dll" (13 Byte mit NUL) passt nicht mehr in die 12-Byte-Luecke bei VA 0x6D3214 und steht
# jetzt in der 13-Byte-Luecke bei VA 0x6D2063 (hinter einem ret, vor der naechsten Funktion).
# Aufruf: rename_luxvelum.py <dev-Ordner>
import sys, os
D = sys.argv[1]
def rd(p):
    b = open(p, 'rb').read().decode('utf-8'); crlf = '\r\n' in b
    return b.replace('\r\n', '\n'), crlf
def wr(p, s, crlf):
    if crlf: s = s.replace('\n', '\r\n')
    open(p, 'wb').write(s.encode('utf-8'))
def once(s, a, b, tag):
    assert s.count(a) == 1, (tag, a[:70], s.count(a)); return s.replace(a, b)
def names(s): return s.replace('Luxveil', 'Luxvelum').replace('luxveil', 'luxvelum')
# ---- Patcher: Luecke fuer den Namen, dann alle Namen ----
p = os.path.join(D, 'apply_patches.ps1'); s, crlf = rd(p)
s = once(s, '''if ([System.Text.Encoding]::ASCII.GetString($script:f, 0x2D2614, 12) -ceq "Luxveil.dll`0") { return }''',
            '''if ([System.Text.Encoding]::ASCII.GetString($script:f, 0x2D1463, 13) -ceq "Luxvelum.dll`0") { return }''', 'Set-ClientDate')
s = once(s, "        Assert-Bytes 0x2D2614 (@(0xCC) * 12) 'Luxveil-Lader'\n", "        Assert-Bytes 0x2D1463 (@(0xCC) * 13) 'Luxveil-Lader'\n", 'Assert Name')
s = once(s, "Patch 0x2D2480 ([byte[]](@(0x68, 0x14, 0x32, 0x6D, 0x00,", "Patch 0x2D2480 ([byte[]](@(0x68, 0x63, 0x20, 0x6D, 0x00,", 'push Name')
s = once(s, '''        Patch 0x2D2614 @(0x4C, 0x75, 0x78, 0x76, 0x65, 0x69, 0x6C, 0x2E, 0x64, 0x6C, 0x6C, 0x00)   # "Luxveil.dll"\n''',
            '''        Patch 0x2D1463 @(0x4C, 0x75, 0x78, 0x76, 0x65, 0x6C, 0x75, 0x6D, 0x2E, 0x64, 0x6C, 0x6C, 0x00)   # "Luxvelum.dll"\n''', 'Name')
s = once(s, '''        # __security_init_cookie (VA 0x76E490). Der Name steht in einer zweiten
        # Luecke (VA 0x6D3214, genau 12 Byte). Beide Luecken sind kleiner als''',
            '''        # __security_init_cookie (VA 0x76E490). Der Name steht in einer zweiten
        # Luecke (VA 0x6D2063, genau 13 Byte). Beide Luecken sind kleiner als''', 'Kommentar')
s = once(s, '''        # Laedt beim Start Luxveil.dll (volumetrischer Nebel, Licht und Wasser,
        # frueher CoAVolFog) aus dem WoW-Ordner. Bisher kam Luxveil ueber eine
        # Proxy-version.dll, die Luxveil.dll fest importiert. Luxveil erledigt
        # alles in DllMain (kein Export-Aufruf noetig) und muss vor Direct3D
        # geladen sein: Es biegt den GetProcAddress-Zeiger des Clients bei VA
        # 0xB2ED98 um und faengt so Direct3DCreate9 ab.
''', '''        # Laedt beim Start Luxvelum.dll (volumetrischer Nebel, Licht und Wasser,
        # frueher CoAVolFog, kurz auch Luxveil) aus dem WoW-Ordner. Bisher kam
        # Luxvelum ueber eine Proxy-version.dll, die Luxvelum.dll fest
        # importiert. Luxvelum erledigt alles in DllMain (kein Export-Aufruf
        # noetig) und muss vor Direct3D geladen sein: Es biegt den
        # GetProcAddress-Zeiger des Clients bei VA 0xB2ED98 um und faengt so
        # Direct3DCreate9 ab.
''', 'Kopf')
s = s.replace('kurz auch Luxveil', '\0ALT\0')
s = names(s).replace('\0ALT\0', 'kurz auch Luxveil')
s.encode('ascii'); wr(p, s, crlf)
# ---- Doku ----
for f in ('README.de.md', 'README.md', 'PATCHES.de.md', 'PATCHES.en.md'):
    p = os.path.join(D, 'docs', f); s, crlf = rd(p)
    s = once(s, 'in einer zweiten Lücke (VA `0x6D3214`).' if f.endswith('de.md') else 'in a second gap (VA `0x6D3214`).',
                'in einer zweiten Lücke (VA `0x6D2063`).' if f.endswith('de.md') else 'in a second gap (VA `0x6D2063`).', f) if f.startswith('PATCHES') else s
    wr(p, names(s), crlf)
# ---- Hilfsskripte (add_luxveil.py bleibt als Geschichte, wie Nr. 32 als Luxveil-Lader dazukam) ----
T = os.path.join(D, 'tools', 'luxvelum')
for f in ('emu_entry.py', 'check_sites.py', 'itest_luxvelum.sh', 'luxvelum_sites.txt'):
    p = os.path.join(T, f); s, crlf = rd(p)
    if f == 'itest_luxvelum.sh':
        s = once(s, '0x2D2614<=i<0x2D2620', '0x2D1463<=i<0x2D1470', f)
    wr(p, names(s), crlf)
print('umbenannt')
