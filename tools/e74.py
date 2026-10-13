R("""       Author = 'unbekannt (v1) / St0ny (v2)'
       De = 'Custom Item Fix (BETA) v2 by St0ny'""", """       Author = 'Kebabstorm'
       De = 'Custom Item Fix (BETA) v2 by St0ny'""")
R("""        # v1 hatte zwei Fehler, die den Client abstuerzen lassen: Bei 0x35813C
        # fehlte vorne das Byte 01 (der Klassen-Helfer wurde zu Datenmuell), und
        # 0x1AAAFA war eine Kopie der Zeile 0x1AA9D0 (der call landete mitten in
        # 0x758F50). Beides ist hier korrigiert. Nicht uebernommen: die PE-
        # Pruefsumme bei 0x168 (Windows prueft sie bei Programmen nicht) und
        # "Cache" -> "||che" bei 0x61BE58 - das ist genau der Patch "CACHE-
        # Ordner-Erstellung deaktivieren", deshalb hier nur als Needs.
""", """        # Vorlage ist "Custom Item Fix (BETA) v1" aus Kebabstorms "WoW 3.3.5
        # Patcher (Custom Item Fix)" (wowmodding.net, Datei 283). Die Patch-Liste,
        # aus der er uebernommen wurde, hatte zwei Fehler, die den Client
        # abstuerzen lassen: Bei 0x35813C fehlte vorne das Byte 01 (der Klassen-
        # Helfer wurde zu Datenmuell), und 0x1AAAFA war eine Kopie der Zeile
        # 0x1AA9D0 (der call landete mitten in 0x758F50). Beides ist hier
        # korrigiert. Nicht uebernommen: die PE-Pruefsumme bei 0x168 (Windows
        # prueft sie bei Programmen nicht) und "Cache" -> "||che" bei 0x61BE58 -
        # das ist genau der Patch "CACHE-Ordner-Erstellung deaktivieren",
        # deshalb hier nur als Needs.
""")
