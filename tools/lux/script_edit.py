# Lux-Lader (Nr. 31) ins dev-Skript einbauen, Verweise ab Nr. 31 um eins verschieben,
# CameraReforged-Zuordnung korrigieren. Skript bleibt ASCII + CRLF.
import sys
p = sys.argv[1] + '/apply_patches.ps1'
s = open(p, 'rb').read().decode('ascii').replace('\r\n', '\n')
def once(a, b, label):
    global s
    n = s.count(a)
    assert n == 1, '%s: %d Treffer' % (label, n)
    s = s.replace(a, b)

ENTRY = r"""    @{ Id = 'lux'; Cat = 'dll'; On = $false; PublicUntested = $true; GameUntested = $true
       Author = 'St0ny'
       De = 'LuxShoulderCam.dll beim Start laden (Schulterkamera von Stormhand) [BETA]'
       En = 'Load LuxShoulderCam.dll at startup (shoulder camera by Stormhand) [BETA]'
       NoteDe = 'benoetigt LuxShoulderCam - mit Lexara (Nr. 30) nicht noetig'
       NoteEn = 'requires LuxShoulderCam - not needed with Lexara (No. 30)'
       Url = 'https://github.com/Stormhand-dev/Lux-Shoulder-Cam'
       Code = {
        # BETA - noch ungetestet. Laedt beim Start LuxShoulderCam.dll
        # (Schulterkamera von Stormhand) aus dem WoW-Ordner - genau wie Lexara,
        # das die DLL in seinem DllMain direkt nach dem eigenen Start per
        # LoadLibraryA("LuxShoulderCam.dll") nachlaedt. Wer Lexara nutzt, braucht
        # diesen Patch nicht; beide zusammen schaden nicht, weil Windows eine DLL
        # mit demselben Namen nur einmal laedt (zweiter Aufruf = nur Referenz).
        # Fehlt die DLL, startet WoW ganz normal.
        # Eingehaengt ist das in den Sprung bei VA 0x76E495 (jmp 0x5EEB70, dort
        # steht nur ein ret). Ihn erreicht nur der Einstiegspunkt, einmalig nach
        # dem Lexara- und dem wow_optimize-Lader, vor dem voice.dll-Lader. Der
        # Code steht in drei freien 16-Byte-Luecken hinter Aufrufen, die nie
        # zurueckkehren (wie beim Lexara-Lader), den DLL-Namen legt er auf den
        # Stack. Dateigroesse und PE-Header bleiben unveraendert.
        #   A (VA 0x6B68A0): push "ll" / push "am.d" / jmp B
        #   B (VA 0x6B69C0): push "derC" / push "houl" / jmp C
        #   C (VA 0x6B6AE0): push "LuxS" / push esp / call [LoadLibraryA] /
        #                    add esp, 14h / ret
        # Lux selbst setzt zur Laufzeit einen Sprung in die erste freie Luecke
        # ab 24 Byte im Code; die drei Luecken hier sind kleiner, Lux waehlt also
        # dieselbe Stelle wie beim Laden ueber Lexara.
        Assert-Bytes 0x36D895 @(0xE9, 0xD6, 0x06, 0xE8, 0xFF) 'Lux-Lader'
        foreach ($o in @(0x2B5CA0, 0x2B5DC0, 0x2B5EE0)) { Assert-Bytes $o (@(0xCC) * 16) 'Lux-Lader' }
        Patch 0x36D896 @(0x06, 0x84, 0xF4, 0xFF)                       # jmp 0x5EEB70 -> jmp A
        Patch 0x2B5CA0 @(0x68, 0x6C, 0x6C, 0x00, 0x00, 0x68, 0x61, 0x6D, 0x2E, 0x64, 0xE9, 0x11, 0x01, 0x00, 0x00)   # A
        Patch 0x2B5DC0 @(0x68, 0x64, 0x65, 0x72, 0x43, 0x68, 0x68, 0x6F, 0x75, 0x6C, 0xE9, 0x11, 0x01, 0x00, 0x00)   # B
        Patch 0x2B5EE0 @(0x68, 0x4C, 0x75, 0x78, 0x53, 0x54, 0xFF, 0x15, 0x48, 0xF2, 0x9D, 0x00, 0x83, 0xC4, 0x14, 0xC3)   # C
    }}

"""
once("    @{ Id = 'voicedll'; Cat = 'dll';", ENTRY + "    @{ Id = 'voicedll'; Cat = 'dll';", 'Eintrag Lux')

# Lexara-Lader: Hinweis auf Lux
once("""        # Vertraegt sich mit dem voice.dll-Lader (der aendert nur den Sprung
        # danach). Fehlt die DLL, startet WoW ganz normal.
""", """        # Vertraegt sich mit dem voice.dll-Lader (der aendert nur den Sprung
        # danach). Fehlt die DLL, startet WoW ganz normal. Lexara laedt selbst
        # die LuxShoulderCam.dll mit, wenn sie im WoW-Ordner liegt (siehe
        # Lux-Lader).
""", 'Lexara-Kommentar')
# wow_optimize-Lader: Reihenfolge im Startcode
once("""        # 0x76E490, den nur der Einstiegspunkt erreicht (nach dem Lexara-Lader,
        # vor dem Sprung, den der voice.dll-Lader umbiegt). Der Code steht in
        # acht freien Luecken zwischen Funktionen, den DLL-Namen baut der Thread
        # auf dem Stack. Dateigroesse und PE-Header bleiben unveraendert.
""", """        # 0x76E490, den nur der Einstiegspunkt erreicht (nach dem Lexara-Lader,
        # vor dem Lux-Lader und dem Sprung, den der voice.dll-Lader umbiegt).
        # Der Code steht in acht freien Luecken zwischen Funktionen, den
        # DLL-Namen baut der Thread auf dem Stack. Dateigroesse und PE-Header
        # bleiben unveraendert.
""", 'wow_optimize-Kommentar')

# Verweise ab Nr. 31 (+1)
for a, b in (("dafuer Nr. 75'", "dafuer Nr. 76'"), ("see No. 75'", "see No. 76'"),
             ("(die nimmt Nr. 75 raus)", "(die nimmt Nr. 76 raus)"),
             ("(Erweiterung zu Nr. 74)'", "(Erweiterung zu Nr. 75)'"), ("(extension to No. 74)'", "(extension to No. 75)'"),
             ("zusammen mit Nr. 74.", "zusammen mit Nr. 75."),
             ("maximiert nur zusammen mit Nr. 79'", "maximiert nur zusammen mit Nr. 80'"),
             ("maximized only together with No. 79'", "maximized only together with No. 80'"),
             ("wirkt nur zusammen mit Nr. 78'", "wirkt nur zusammen mit Nr. 79'"),
             ("only works together with No. 78'", "only works together with No. 79'"),
             ("(Nr. 9, 65 und 66 vergroessern die Wow.exe)", "(Nr. 9, 66 und 67 vergroessern die Wow.exe)")):
    once(a, b, a)

# CameraReforged: Quelle ist Zendevve, nicht Stormhand
once("""#  Portierung von CameraReforged (Stormhand) in die Patch-Engine dieses Tools,
#  eingebaut mit seiner ausdruecklichen Erlaubnis.
#  Quelle: https://github.com/Zendevve/CameraReforged
""", """#  Portierung von CameraReforged (Zendevve) in die Patch-Engine dieses Tools.
#  Quelle: https://github.com/Zendevve/CameraReforged
""", 'Kamera-Helfer')
once("""       Author = 'Stormhand (fixed by St0ny)'
       De = 'CameraReforged [BETA]""", """       Author = 'Zendevve (fixed by St0ny)'
       De = 'CameraReforged [BETA]""", 'Kamera-Autor')
once("""        # Portierung von CameraReforged (Stormhand), mit seiner Erlaubnis eingebaut.
""", """        # Portierung von CameraReforged (Zendevve).
        # Nicht zusammen mit LuxShoulderCam (Lux-Lader oder ueber Lexara): Beide
        # setzen an derselben Stelle im Kamera-Fokuspfad an (VA 0x6070CB); ist
        # dieser Patch drin, haengt sich Lux dort nicht ein.
""", 'Kamera-Kommentar')

assert all(ord(c) < 128 for c in s)
open(p, 'wb').write(s.replace('\n', '\r\n').encode('ascii'))
print('Skript angepasst')
