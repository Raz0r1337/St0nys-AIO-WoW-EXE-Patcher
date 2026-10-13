# Visus - St0nyCam in das dev-Skript einbauen: Helfer Add-Visus + Patch-Eintrag hinter 'mouse'.
import sys, os
wt = sys.argv[1]; here = os.path.dirname(os.path.abspath(__file__))
P = wt + '/apply_patches.ps1'
s = open(P, 'rb').read().decode('ascii').replace('\r\n', '\n')
code = open(here + '/ps_code.txt', encoding='ascii').read().rstrip('\n').split('\n')
reg = [l for l in code[1:code.index([x for x in code if 'Kamera-Haken' in x][0])]]
cam = code[code.index([x for x in code if 'Kamera-Haken' in x][0]) + 1:]
def once(a, b, label):
    global s
    n = s.count(a); assert n == 1, '%s: %d Treffer' % (label, n); s = s.replace(a, b)
HELPER = '''# ============================================================
#  Helfer fuer Visus - St0nyCam (Schulterkamera und Zoom, BETA)
#  Eigene Umsetzung aus eigener Analyse dieser Exe. Vorlage fuer die
#  Schulterkamera ist LuxShoulderCam von Stormhand (mit seiner Erlaubnis):
#  Blickpunkt der Kamera anheben und quer zur Blickrichtung verschieben.
#
#  1. CVars: Am Ende der Funktion, die alle Kamera-CVars anlegt (VA
#     0x5FD910), zeigt der letzte Befehl vor dem Epilog (mov [0xC24970], eax
#     bei VA 0x5FE2AF) auf einen Sprung in die Sektion. Dort werden mit
#     CVar_Register (VA 0x767FC0, cdecl, 9 Argumente) visusHeight und
#     visusShoulder angelegt - Flags 0x10, Kategorie 5, Vorgabe "0", wie die
#     Kamera-CVars. Die Zeiger auf die CVar-Objekte merkt sich die Sektion,
#     den Zahlenwert liest der Kamera-Haken bei jedem Bild frisch (+2Ch).
#  2. Kamera-Haken: Die Kamera-Funktion (VA 0x606F90) hat bei VA 0x6070CB
#     gerade den Blickpunkt berechnet (X/Y/Z in [ebp-34h]/[ebp-30h]/[ebp-2Ch],
#     esi = Kamera, Position X/Y bei +8/+0Ch). Statt fld [0x9F1670] springt
#     sie in die Sektion:
#       - Z += visusHeight, begrenzt auf -1 .. 1.
#       - X/Y werden um visusShoulder (-2 .. 2) quer zur Blickrichtung
#         verschoben, positiv = nach rechts (die Figur steht dann links im
#         Bild). Die Blickrichtung kommt aus der Kameraposition minus dem im
#         letzten Bild verschobenen Blickpunkt (gleiche Kamera), sonst minus
#         dem aktuellen Blickpunkt - so dreht der Versatz exakt mit der Kamera.
#         Ist die Kamera naeher als 0.01 am Blickpunkt (Ich-Perspektive), gibt
#         es keinen Seitenversatz.
#       - Danach der ueberschriebene Befehl und zurueck nach VA 0x6070D1.
#  3. Zoom: Die feste Grenze der Kamera von 50 Yards (float bei 0xA1E2FC)
#     lesen acht Stellen: Pruefung von cameraDistanceMax, maximale Entfernung,
#     gespeicherte Fahrzeug-Entfernung, Zoom-Funktion. Sie zeigen jetzt auf
#     100.0 in der Sektion. Die Pruefung von cameraDistanceMoveSpeed (VA
#     0x5FD87B) liest dieselbe Konstante als Tempo-Grenze - die bleibt bei 50.
#     Vorgabe von cameraDistanceMoveSpeed: 8.33 -> 20.
#  Sektion ".visus" (0x200 Byte, ausfuehrbar + beschreibbar):
#     +0x000 Registrierung, +0x060 Kamera-Haken, +0x180 Daten,
#     +0x1A0 Konstanten 1.0/-1.0/2.0/-2.0/0.01/100.0, +0x1C0 Texte.
# ============================================================
function Add-Visus {
    $TEXT_DIFF  = 0x400C00
    $REG_HOOK   = 0x5FE2AF          # mov [0xC24970], eax (Ende der Kamera-CVars)
    $CAM_HOOK   = 0x6070CB          # fld dword [0x9F1670] (Blickpunkt fertig)
    $SPEED_PUSH = 0x5FDA37          # push "8.33" (Vorgabe cameraDistanceMoveSpeed)
    $CAP_SITES  = @(0x5FD699, 0x5FE572, 0x5FF3F7, 0x600137, 0x60015F, 0x6005E0, 0x6005FE, 0x600922)
    Assert-Bytes ($REG_HOOK - $TEXT_DIFF) @(0xA3, 0x70, 0x49, 0xC2, 0x00) 'Visus'
    Assert-Bytes ($CAM_HOOK - $TEXT_DIFF) @(0xD9, 0x05, 0x70, 0x16, 0x9F, 0x00) 'Visus'
    Assert-Bytes ($SPEED_PUSH - $TEXT_DIFF) @(0xE0, 0xE7, 0xA1, 0x00) 'Visus'
    foreach ($a in $CAP_SITES) { Assert-Bytes ($a - $TEXT_DIFF) @(0xFC, 0xE2, 0xA1, 0x00) 'Visus' }

    $sec = Add-CodeSection '.visus' 0x200 -Writable
    $V = $sec[0]
    $blk = New-Object byte[] 0x200
    for ($i = 0; $i -lt $blk.Length; $i++) { $blk[$i] = 0xCC }

    $c = New-Object System.Collections.Generic.List[byte]
''' + '\n'.join(reg) + '''
    [Array]::Copy($c.ToArray(), 0, $blk, 0x000, $c.Count)

    $c = New-Object System.Collections.Generic.List[byte]
''' + '\n'.join(cam) + '''
    if ($c.Count -gt 0x120) { throw 'Visus: Kamera-Haken zu gross.' }
    [Array]::Copy($c.ToArray(), 0, $blk, 0x060, $c.Count)

    # Daten +0x180: CVar visusHeight, CVar visusShoulder, letztes X, letztes Y,
    # letzte Kamera, gemerkt (alles 0)
    for ($i = 0x180; $i -lt 0x198; $i++) { $blk[$i] = 0 }
    $k = 0x1A0
    foreach ($v in @(1.0, -1.0, 2.0, -2.0, 0.01, 100.0)) {
        [Array]::Copy([BitConverter]::GetBytes([single]$v), 0, $blk, $k, 4); $k += 4
    }
    foreach ($t in @(@(0x1C0, '0'), @(0x1C4, '20'), @(0x1C8, 'visusHeight'), @(0x1D8, 'visusShoulder'))) {
        $b = [System.Text.Encoding]::ASCII.GetBytes($t[1] + [char]0)
        [Array]::Copy($b, 0, $blk, $t[0], $b.Length)
    }
    Patch $sec[1] $blk

    # Spruenge in die Sektion, Zoom-Grenze, Zoom-Tempo
    Patch ($REG_HOOK - $TEXT_DIFF) ([byte[]](@(0xE9) + [BitConverter]::GetBytes([int32](($V + 0x000) - ($REG_HOOK + 5)))))
    Patch ($CAM_HOOK - $TEXT_DIFF) ([byte[]](@(0xE9) + [BitConverter]::GetBytes([int32](($V + 0x060) - ($CAM_HOOK + 5))) + @(0x90)))
    foreach ($a in $CAP_SITES) { Patch ($a - $TEXT_DIFF) ([BitConverter]::GetBytes([uint32]($V + 0x1B4))) }
    Patch ($SPEED_PUSH - $TEXT_DIFF) ([BitConverter]::GetBytes([uint32]($V + 0x1C4)))
}

'''
anchor = '# ============================================================\n#  Helfer fuer die Client-Info-Patches von MacWarrior\n'
once(anchor, HELPER + anchor, 'Helfer')
ENTRY = '''    @{ Id = 'visus'; Cat = 'window'; On = $false; GrowsExe = $true; PublicUntested = $true; GameUntested = $true
       Author = 'St0ny'
       De = 'Visus - St0nyCam [BETA]: Schulterkamera und Zoom'
       En = 'Visus - St0nyCam [BETA]: shoulder camera and zoom'
       NoteDe = 'Schulterkamera per /console visusHeight und visusShoulder, Zoom bis 100 Yards'
       NoteEn = 'shoulder camera via /console visusHeight and visusShoulder, zoom up to 100 yards'
       Code = {
        # BETA - noch ungetestet. Eigene Schulterkamera und Zoom ohne DLL:
        # neue CVars visusHeight (-1..1) und visusShoulder (-2..2), Zoom-Grenze
        # 100 statt 50 Yards, Zoom-Tempo-Vorgabe 20 statt 8.33. Haengt eine
        # eigene Sektion an (Exe wird groesser). Nicht zusammen mit
        # LuxShoulderCam: beide setzen an derselben Stelle der Kamera an.
        # Details bei Add-Visus.
        Add-Visus
    }}

'''
anchor2 = '    # --- Sound ---\n'
once(anchor2, ENTRY + anchor2, 'Eintrag')
# Lux-Eintrag: Hinweis auf Visus im Kommentar
once("""        # Lux selbst setzt zur Laufzeit einen Sprung in die erste freie Luecke
        # ab 24 Byte im Code; die drei Luecken hier sind kleiner, Lux waehlt also
        # dieselbe Stelle wie beim Laden ueber Lexara.
""", """        # Lux selbst setzt zur Laufzeit einen Sprung in die erste freie Luecke
        # ab 24 Byte im Code; die drei Luecken hier sind kleiner, Lux waehlt also
        # dieselbe Stelle wie beim Laden ueber Lexara. Nicht zusammen mit Visus
        # (St0nyCam): beide setzen an derselben Stelle der Kamera an.
""", 'Lux-Kommentar')
assert all(ord(ch) < 128 for ch in s)
open(P, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('Skript angepasst')
