i=s.index("    @{ Id = 'airforward';"); j=s.index("    # --- Grafik & Sichtweite ---")
s=s[:i]+"""    @{ Id = 'airforward'; Cat = 'gameplay'; On = $false
       Author = 'Alyst3r (0x539wowmod) / St0ny'
       De = 'Im Sprung vorwaerts/rueckwaerts steuern [TEST]'
       En = 'Steer forward/backward while jumping [TEST]'
       NoteDe = 'kann vom Server als Cheat erkannt werden'
       NoteEn = 'may be detected as cheating by the server'
       Code = {
        # TEST - nach 0x539wowmod. Dort ersetzt die DLL die Vorwaerts-Eingabe
        # (VA 0x988A20) durch eine eigene Funktion; die unterscheidet sich vom
        # Original nur in zwei Spruengen, die hier direkt geaendert werden:
        #  - VA 0x988A3D je -> jmp: in der Luft (Fall-Flag 0x1000) nicht mehr
        #    abbrechen, sondern die Richtung wie am Boden setzen
        #  - VA 0x988AD2 je -> jmp: Geschwindigkeit auch in der Luft neu berechnen
        # Dazu aus der DLL: VA 0x987EFD je -> jmp, die Bewegung wird auch in der
        # Luft aktualisiert.
        Patch 0x587E3D @(0xEB)
        Patch 0x587ED2 @(0xEB)
        Patch 0x5872FD @(0xEB)
    }}

    @{ Id = 'airlateral'; Cat = 'gameplay'; On = $false
       Author = 'Alyst3r (0x539wowmod) / St0ny'
       De = 'Im Sprung seitwaerts steuern [TEST]'
       En = 'Steer sideways while jumping [TEST]'
       NoteDe = 'kann vom Server als Cheat erkannt werden'
       NoteEn = 'may be detected as cheating by the server'
       Code = {
        # TEST - nach 0x539wowmod, wie oben fuer die Seitwaerts-Eingabe
        # (VA 0x988B00):
        #  - VA 0x988B25 je -> jmp: in der Luft nicht mehr abbrechen
        #  - VA 0x988B81 je -> jmp: Geschwindigkeit auch in der Luft neu berechnen
        # Dazu aus der DLL: VA 0x988BEF jne -> 6x NOP (Funktion bei VA 0x988BA0
        # bricht bei gesetztem Fall-Flag nicht mehr vor der Neuberechnung ab).
        Patch 0x587F25 @(0xEB)
        Patch 0x587F81 @(0xEB)
        Patch 0x587FEF @(0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
    }}

    @{ Id = 'airturn'; Cat = 'gameplay'; On = $false
       Author = 'Alyst3r (0x539wowmod) / St0ny'
       De = 'Im Sprung drehen aendert die Flugrichtung [TEST]'
       En = 'Turning while jumping changes the flight direction [TEST]'
       NoteDe = 'kann vom Server als Cheat erkannt werden'
       NoteEn = 'may be detected as cheating by the server'
       Code = {
        # TEST - nach 0x539wowmod. Beim Drehen (VA 0x989B70) setzt der Client
        # die Bewegungsrichtung nur am Boden neu; in der Luft springt er bei
        # VA 0x989B97 (jne) daran vorbei. 2x NOP: auch in der Luft.
        Patch 0x588F97 @(0x90, 0x90)
    }}

"""+s[j:]
