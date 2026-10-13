# 28-Jahre-Datumsverschiebung (zurueckgestellt, 2026-10-07)
- Idee: Server schickt Daten -28 Jahre (gepackt 5-Bit-Jahr 2000-2031, Unix-Zeit -883612800 s), Client zeigt +28.
- Nr. 6 (Jahr-2031-Fix) entfernt (e679871 auf st0ny-dev).
- Client: Jahresbasis 0x7D0 -> 0x7EC an Lua-Schnittstellen:
  Ausgabe: 5B81BD 5B827A 5B8323 5B83E7 5B8474 5B9A5E 5B9B91 5BA504 5BDA51 5BDAE4; Gilde 6CC4EE; Chat-Datum 5B7EB2; Erfolge 76CB3B (via 5B115D)
  Eingabe: 5B9B4B 5BB551 5BB701 5C4439
  Intern (nicht aendern): 76C49A/76C4A2 (pack), 76CDCD; keine Jahre: 5B8B5C 5BC39F 7344xx 73AA59 743F6E 74B092 755EDD 782F69 42D76F 4505E2 5AC1A5 5AD351 5AD50B 4ED94A 9D2810 56C1ED
- Kalender-Untergrenze 23.11.2004 (CalendarGetMinDate 5B8206.. konstanten 0xA,0x17,4) -> auf 2000 senken.
- Offen: Core (AC/TC)? Erfolge/Gilde: Erkennungsregel (Jahr+28 > heute -> alt) oder +2000 lassen?

## Stand 2026-10-07 (spaet)
- Agent-Analyse: scratchpad/y38/y38_patches.json (39 Patches), Bericht siehe Session.
- Entscheidungen Nutzer:
  - Fix gilt ab 2028; Modul muss alle gespeicherten Daten korrekt schicken (Modulthema).
  - Verschiebung einstellbar in 28er-Schritten (28/56/84...), damit Zyklus neu gestartet werden kann.
  - PC-Uhr (_time32, Lua date/time) ab 2038: spaeter fixen.
  - WotLKExt-DLL eigener Zeitfix nur wenn dort aktiviert (default aus) -> nur Doku-Hinweis.
- PC-Uhr NICHT verschieben (nur Chat/Lua date/Logs, kein Vergleich mit Serverdaten).
