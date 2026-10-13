R("""    if ($c.Count -ne 0x40) { throw 'Doppelsprung: Hoehle hat die falsche Groesse.' }
""", """    AddRaw $c @(0x00, 0x00, 0x00, 0x00)                            # Zaehler, beginnt bei 0
    if ($c.Count -ne 0x44) { throw 'Doppelsprung: Hoehle hat die falsche Groesse.' }
""")
