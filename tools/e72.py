R("""        Patch 0x8EFD9 @(0x00)
    }}

    # --- Gameplay-Fixes ---
""", """        Patch 0x8EFD9 @(0x00)
    }}

    @{ Id = 'globalsv'; Cat = 'modding'; On = $false
       Author = 'boredatom / St0ny'
       De = 'Addon-Daten aller Accounts zusammenlegen (SavedVariables)'
       En = 'Merge addon data of all accounts (SavedVariables)'
       NoteDe = 'gemeinsamer Ordner WTF\\Account\\global'
       NoteEn = 'shared folder WTF\\Account\\global'
       Code = {
        # Nach dem Login merkt sich die Funktion bei VA 0x5F9080 den Account-
        # Namen fuer die Addon-Pfade: WTF\\Account\\<Account>\\SavedVariables,
        # ...\\<Realm>\\<Charakter>\\SavedVariables und die AddOns.txt beider
        # Ebenen. Statt des Namens kopiert sie jetzt den Text "global", der
        # schon in der Exe steht (VA 0xA384A0). Makros, Tastenbelegungen und
        # Einstellungen (*-cache.*, layout-local.txt) nutzen einen eigenen
        # Puffer und bleiben je Account getrennt. Gleiche Wirkung wie der Patch
        # von boredatom, aber an Ort und Stelle statt die Funktion zu
        # verschieben: aus mov eax,[ebp+8] / push 0x500 / push eax wird
        # push 0x7F / push "global" / nop / nop. 0x7F ist nur die Hoechstlaenge
        # fuer SStrCopy und reicht fuer "global".
        Patch 0x1F8488 @(0x6A, 0x7F, 0x68, 0xA0, 0x84, 0xA3, 0x00, 0x90, 0x90)
    }}

    # --- Gameplay-Fixes ---
""")
