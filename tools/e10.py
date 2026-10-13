i=s.index("    @{ Id = 'jump';"); j=s.index("    }}\n", i)+len("    }}\n")
s=s[:j]+"""
    @{ Id = 'airforward'; Cat = 'gameplay'; On = $false
       Author = 'Alyst3r (0x539wowmod)'
       De = 'Im Sprung vorwaerts/rueckwaerts steuern [TEST]'
       En = 'Steer forward/backward while jumping [TEST]'
       NoteDe = 'kann vom Server als Cheat erkannt werden'
       NoteEn = 'may be detected as cheating by the server'
       Code = {
        # TEST - aus 0x539wowmod ("update forward air movement"). Die Funktion
        # bei VA 0x987EF0 ueberspringt Vorwaerts-/Rueckwaerts-Eingaben, solange
        # das Fall-Flag (0x1000) gesetzt ist. je -> jmp bei VA 0x987EFD: die
        # Eingabe wird auch in der Luft verarbeitet.
        Patch 0x5872FD @(0xEB)
    }}

    @{ Id = 'airlateral'; Cat = 'gameplay'; On = $false
       Author = 'Alyst3r (0x539wowmod)'
       De = 'Im Sprung seitwaerts steuern [TEST]'
       En = 'Steer sideways while jumping [TEST]'
       NoteDe = 'kann vom Server als Cheat erkannt werden'
       NoteEn = 'may be detected as cheating by the server'
       Code = {
        # TEST - aus 0x539wowmod ("update lateral air movement"). Die Funktion
        # bei VA 0x988BA0 bricht bei gesetztem Fall-Flag vor der Neuberechnung
        # der Bewegung ab (jne bei VA 0x988BEF). 6x NOP: auch in der Luft.
        Patch 0x587FEF @(0x90, 0x90, 0x90, 0x90, 0x90, 0x90)
    }}
"""+s[j:]
