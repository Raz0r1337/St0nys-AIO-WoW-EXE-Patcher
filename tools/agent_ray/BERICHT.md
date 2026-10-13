# Bericht: TraceLine und Sichtstrahlen für Patch 68 (Umrandung)

WoW 3.3.5a, Build 12340, `Wow.exe` (MD5 `45892bdedd0ad70aed4ccd22d9fb5984`, identisch mit `ol2/exe14/Wow.exe.ORI`).
Dateiversatz = VA − 0x400C00 (gilt für `.text`).

Kennzeichnung im ganzen Bericht:
- **[V]**: verifiziert, durch Disassembly und/oder Unicorn-Emulation belegt.
- **[T]**: teilweise verifiziert. Der Mechanismus ist belegt, die Deutung (Name, Zweck) ist plausibel.
- **[?]**: vermutet bzw. nicht geprüft.

Werkzeuge und Tests liegen in diesem Ordner:
- `wx.py`, `ix.py`, `build_idx.py`, `strs.py`, `vt.py`: Disassembly, Querverweise, Strings, Vtables
- `emu_trace.py`: TraceLine mit leerer Welt, Aufrufkette, Stack und Register
- `emu_cost.py`: Kosten pro geladener WMO-Instanz
- `emu_terrain.py`: TraceLine gegen synthetisches, ebenes Gelände (prüft frac, hitOut, Rückgabe und Kosten je Strahllänge)
- `emu_hook.py`: vorgeschlagener Hook bei 0x4FB036 mit Stub-Skizze, emuliert bis zum Rücksprung

---

## 0. Kurzfazit

1. `TraceLine` = **0x7A3B70**, cdecl, 6 Argumente, Rückgabe in AL **[V]**:
   `bool TraceLine(const C3Vector* start, const C3Vector* end, C3Vector* hitOut /*NULL erlaubt*/, float* frac /*ein/aus, Pflicht*/, uint32 flags, void* hitInfo /*NULL*/)`.
   Die Funktion 0x77F310 ist nur ein `jmp 0x7A3B70`. Fast alle Spielaufrufer nehmen diesen Weg (21 Aufrufstellen).
2. TraceLine ist **nicht reentrant und nicht threadsicher**. Sie benutzt mehrere globale Puffer und Zähler, und sie setzt Markierungen in gemeinsam genutzten Modell- und WMO-Daten. Das Spiel ruft sie aber selbst viele Male pro Bild im Hauptthread auf, **auch mitten in `RenderWorld`** (Flugbahn-Vorschau, Zaubereffekte). Sicher ist der Aufruf daher im Hauptthread, solange keine andere Kollisionsabfrage läuft.
3. **Empfohlener Hook: VA 0x4FB036** (Datei 0xFA436), `E8 45 B4 2E 00` = `call 0x7E6480`. Die Stelle liegt im Render-Rückruf des WorldFrames (0x4FAF90), **direkt nach** `CGWorldFrame::OnWorldUpdate` (0x4FA5F0, enthält das Kamera-Update) und **direkt vor** `RenderWorld` (0x4F8EA0). Der Call wird auf einen Stub umgebogen. Der Stub ruft 0x7E6480 selbst auf, erledigt die Strahlen und kehrt mit `ret` zurück. Die Emulation bestätigt das **[V]**.
4. Kamera in Weltkoordinaten: `cam = [[0xB7436C] + 0x7E20]`, Position `cam+0x08/+0x0C/+0x10` **[V]**. Das Spiel liest sie selbst genau so (0x4F6650).
5. Einheit: `obj = 0x4D4DB0(guidLo, guidHi, 8, 0, 0)` (NULL bei veraltetem oder unbekanntem GUID) **[V]**. Die Weltposition liefert die virtuelle Funktion `[vtbl+0x2C](&vec)`; sie berücksichtigt Transporter **[V]**. Als Höhe eignet sich `float [obj+0x854]` (= Bewegung+0xCC, Kollisionshöhe × Skalierung) **[T]**.
6. Kosten: etwa 1 000 Befehle Grundlast, dazu **~88 Befehle je geladener WMO-Instanz** (lineare Liste) und **~600–800 Befehle je durchlaufener 4,17-yd-Zelle** **[V, emuliert]**. Hinzu kommen M2- und WMO-Treffertests. Ein 20–40-yd-Strahl in einer Stadt dürfte etwa 10–30 µs kosten **[?]**. Empfohlen: **12–24 Strahlen pro Bild**, reihum.

---

## 1. TraceLine (0x7A3B70)

### 1.1 Signatur, Aufrufkonvention, Rückgabe [V]

```
bool __cdecl TraceLine(const C3Vector* start,   // [ebp+08]
                       const C3Vector* end,     // [ebp+0C]
                       C3Vector*       hitOut,  // [ebp+10]  darf NULL sein
                       float*          frac,    // [ebp+14]  ein/aus, darf NICHT NULL sein
                       uint32          flags,   // [ebp+18]
                       void*           hitInfo) // [ebp+1C]  darf NULL sein (großer Struct, >= 0x770 Byte)
// Rückgabe: AL = 1 bei Treffer, sonst 0. Der Aufrufer räumt 0x18 Byte ab.
// Erhalten bleiben EBX/ESI/EDI/EBP. EAX/ECX/EDX sind danach undefiniert. FPU-Stapel ist danach leer.
```

Semantik, per Emulation gegen synthetisches Gelände geprüft (`emu_terrain.py`):

| Fall | Ergebnis |
|---|---|
| senkrecht z 10 → −10 über Boden z=0 | AL=1, frac=0.5000, hit=(x,y,0.0) |
| schräg z 10 → −30 | AL=1, frac=0.25, hit = start + (end−start)·0.25 |
| endet über dem Boden | AL=0, frac bleibt 1.0, hitOut unverändert |
| frac_in = 0.4 (Treffer läge bei 0.5) | AL=0, frac bleibt 0.4. **frac_in ist das Maximum.** |
| hitOut = NULL | AL=1, frac=0.5, kein Absturz |
| Ziel 0,5 yd unter dem Boden („Fuß im Boden“), 47 yd Strahl | AL=1, frac=0.9836 (Treffer ~0,77 yd vor dem Ende) |

- **frac**: Eingabe ist der maximale Anteil, normalerweise **1.0f**. Ausgabe ist der Anteil bis zum nächsten Treffer, geschrieben **nur bei Treffer**. Vor jedem Aufruf neu auf 1.0 setzen.
- **hitOut**: Wird nur bei Treffer geschrieben: `start + (end−start)·frac` (0x7A3C90 ff.).
- **hitInfo**: Bei Treffer füllt 0x7A2C60 einen großen Struct (Felder bis mindestens +0x768). Für uns NULL übergeben.
- Nebenwirkungen: GUID des getroffenen Objekts (Transporter-WMO, GameObject) landet in `0xCD7768/0xCD776C`. Bei M2-Treffern steht das getroffene M2 in `[0xCD754C]+0x12C`.

Ablauf:
```
007A3B79  add dword ptr [0xce04c4], 1        ; globaler Abfragezähler (Mailbox-Markierung)
007A3B8A  test eax, 0x40f300ff                ; Pfad 1 nötig?
007A3BCF  call 0x7a30d0                       ; Pfad 1: alle WMO-Instanzen (Liste 0xD25440) + M2 in WMO-Gruppen
007A3C2E  test eax, 0x40f3010f                ; Pfad 2 nötig?
007A3C4C  call 0x7a39f0                       ; Pfad 2: Zellraster entlang des Strahls (Gelände, M2-Doodads, Wasser, GO)
007A3C90  ...                                 ; hitOut = start + (end-start)*frac, falls Treffer und hitOut != NULL
007A3CDD  mov al, bl                          ; Rückgabe
```
Pfad 2 läuft nach Pfad 1 mit dem schon verkürzten `frac` und findet deshalb nur noch nähere Treffer.

Pfad 1, 0x7A30D0 **[V]**:
- Erst `_alloca(0x1770)`. Allein dadurch braucht TraceLine **~6,5 KB Stack** (emuliert: 6 484 Byte).
- Dann wird die **verkettete Liste aller geladenen WMO-Instanzen** abgelaufen (CMapObjDef; Kopf `[0xD25440]`, Link-Offset `[0xD25438]`, sowohl ADT-MODF-Instanzen aus 0x7BF460 als auch dynamische Instanzen aus 0x783500). Pro Instanz: Flag-Test `[def+0xC] & 0x100` und Strecken-AABB-Test (0x7F9480, AABB bei `def+0x48`).
- Kandidaten-Gruppen werden nach Abstand sortiert (qsort 0x40BE50) und dann per BSP getestet: 0x7AF200 → 0x7CB2F0 → 0x7CA180.

Pfad 2, 0x7A39F0/0x7A3570 **[V]**:
- Die Weltkoordinaten werden ins 8192er-Zellraster umgerechnet: Zelle = (17066,67 − Koordinate) · 0,24, eine Zelle ist 4,1667 yd groß. Die Zellen entlang des Strahls landen im globalen Puffer `[0xCF4930]`, die Anzahl steht in `0xCE04C8`.
- Pro neuem Chunk: ADT `[0xCE48D0 + ((x>>7)*64+(y>>7))*4]`, Chunk `[area+0xBC + idx*4]`. M2-Doodads werden gesammelt (0x7A2760, Liste `chunk+0xC4`), GameObjects über einen Rückruf (0x7A2960, Liste `chunk+0xDC`, Rückruf `[0xCE04B0]` = 0x4F6560, nur Typ GameObject).
- Pro Zelle: Geländetest (0x7D8730, 4 Dreiecke) bei Flag 0x100, Wasser bei 0x30000.
- Am Ende kommt der M2-Test der gesammelten Modelle: 0x81E110, der schnelle Weg nur für Kollisionsnetze, oder 0x81DF10, der allgemeine Weg.
- **Abbruch:** Ist für eine Zelle das ADT oder der Chunk nicht geladen, endet die Zellschleife sofort. Das Ergebnis ist dann „kein Treffer“.

### 1.2 Flag-Bits

Grundlage: Masken 0x40F300FF (Pfad 1), 0x40F3010F (Pfad 2), 0x40F0000F (M2 an), 0x40F00000 (Objekte), 0x16000AE (allgemeiner M2-Weg) sowie die Funktionen 0x7AE140 (Flags → Ablehnungsmaske für WMO-Dreiecke, MOPY), 0x7A2760/0x7A2960 (M2-Modus) und 0x7A37CF ff. (Wasser).

| Bit | Bedeutung | Status |
|---|---|---|
| 0x00000001 | M2-Doodads: **Kollisionsnetz** (M2 `nBoundingTriangles` +0xD8/+0xDC, Modus 3) | [V] |
| 0x00000002 / 0x00000004 | M2: **Render-Geometrie** (Modus 0; mit 0x1000000 Modus 1, nur bestimmte Materialien) | [T] |
| 0x00000008 | M2: Render-Geometrie, Modus 2 (Variante mit Material-/Batch-Prüfung) | [T] |
| 0x00000010 | WMO: **Kollisionsgeometrie** (Ablehnungsmaske 0xC6: akzeptiert MOPY F_RENDER und F_COLLISION, verwirft F_DETAIL) | [V] Maske / [T] MOPY-Bedeutung nach wowdev |
| 0x00000020 | WMO: **sichtbare Geometrie** (Maske ohne 0x24: akzeptiert F_RENDER und F_DETAIL, verwirft reine Kollisionsdreiecke 0x08) | [V]/[T] |
| 0x00000040 | „Kamera“: verwirft WMO-Dreiecke mit F_NOCAMCOLLIDE (0x02) | [V]/[T] |
| 0x00000080 | WMO: Maske 0x2CA: verwirft MOPY 0x02/0x08/0x40 sowie Dreiecke ohne Material oder mit opakem Material (Masken-Bit 0x200), übrig bleiben praktisch nur Alpha-Dreiecke | [V] Maske / [T] Deutung |
| 0x00000100 | **Gelände** (ADT-Zellen, 0x7D8730) | [V] (Emulation) |
| 0x00004000 | WMO: verwirft auch MOPY-0x40-Dreiecke | [V] Maske |
| 0x00010000 | Wasser: nur LiquidType mit Flag 0x4 (wohl „begehbar“, Wasserwandeln setzt dieses Bit) | [T] |
| 0x00020000 | Wasser: **alle** Flüssigkeiten (ADT und WMO); die Kamera nutzt es mit CVar `cameraWaterCollision` | [V] |
| 0x00100000 | **Objekte mit GUID** (GameObject-M2, z. B. Türen) mit Kollisionsnetz; WMO-Transporter liegen ohnehin in Pfad 1 | [V] |
| 0x00200000 / 0x00400000 | Objekte mit GUID, Render-Geometrie (Modus 0) | [V] |
| 0x00800000, 0x40000000 | Objekte (Modus 0). 0x40000000 zusammen mit 0x1000000 ergibt die Sondermaske 0xFFFFFCDB | [T] |
| 0x01000000 | „Nur sichtbare, opake Geometrie“: WMO verwirft Alpha-Materialien (Masken-Bit 0x100), M2-Defs mit `[def+0x25]≠0` werden übersprungen | [T] |
| 0x00000200, 0x00002000, 0x02000000, 0x80000000 | Werden **nicht von TraceLine** ausgewertet, sondern nur von Bewegungs- und Kollisionsabfragen (0x75E3D0, 0x7A2AA0) | [V] |

Einheiten (Units/Player) sind **nicht** kollidierbar. Der Objekt-Rückruf 0x4F6560 lässt nur Typ GameObject (0x20) zu **[V]**. Ein Strahl zur eigenen Gruppe trifft also nie die Figur selbst oder andere Spieler.

### 1.3 Alle Aufrufer [V, Zweck teils T]

| Aufrufstelle | Funktion | Flags | Zweck |
|---|---|---|---|
| 0x4F99F8 | 0x4F9930 (CGWorldFrame) | 0x1000124 bzw. 0x1020124 | Maus-Picking in der Welt: sichtbare WMO-/M2-Geometrie, Gelände, opak |
| 0x4F9B71 | 0x4F9930 | 0x100151 | zweite Probe (Kollision, z. B. Bodenziel) |
| 0x568B5B, 0x568C8E | 0x5689A0 (`CommentatorFrame.cpp`) | 0x100171 | Zuschauer-Kamera |
| 0x603B3B, 0x603BB2 | 0x603A10 (Kamera) | 0x151 | Kamera (Ziel-/Pivot-Prüfung) |
| 0x605F00, 0x6060FE | 0x605D60 (Kamera-Kollision) | 0x100171 (+0x20000 bei `cameraWaterCollision`) | Verfolgerkamera an Wänden einziehen |
| 0x606256 | 0x6061D0 (Kamera) | 0x20000 | Kamera gegen Wasseroberfläche |
| 0x759709 | 0x759580 (Kamera) | `0x5FEC50()` = 0x100171 / 0x120171 | Kamera |
| 0x6FD37C, 0x6FD4F7, 0x6FD5DD | 0x6FCD60 (`UnitMissileTrajectory_C.cpp`) | 0x100111 | Flugbahn-Vorschau; wird auch **aus RenderWorld** gerufen (0x4F8EA0→0x77EFF0→0x79A870→0x6FDA20) |
| 0x700127, 0x700211 | 0x6FFFC0 (`Missile_C.cpp`) | 0x111 | Projektile gegen die Welt |
| 0x714BBD | 0x714B60 (Unit) | 0x100111 | Abstand zum Boden: senkrecht von z+1 nach z−1 |
| 0x75F04B | 0x75EFE0 (Bewegung) | Bewegungsflags & ~0x100000 (Basis 0x100111/0x102111) | Bodenprobe der Bewegung |
| 0x7FBA35 | 0x7FB7F0 (`SpellVisuals.cpp`) | 0x110 | Zaubereffekt platzieren |
| 0x7FC3D8, 0x7FC46C | 0x7FC220 (`SpellVisuals.cpp`) | 0x120111 | Zaubereffekt auf Boden/Wasser |
| 0x9ABD18 | 0x9ABC60 | **0x200112** | Software-Sichtprüfung eines Punkts (Lens-Flare/Lichtquelle) bei CVar `occlusion`=0. Das ist **die Spiel-Analogie zu unserem Vorhaben** |
| 0x77F584 | 0x77F540 (Rückruf, registriert bei 0x78134C) | 0x100111 | Bodenhöhe: 20 yd senkrecht nach unten |
| direkt 0x7A39F0 | 0x77FA00 (0x20100) und 0x795D40 (0x100, aus `CWorld::Update` 0x7831A0) | – | Zonen-/Bodenabfragen ohne Zähler-Inkrement |
| direkt 0x7A30D0 | 0x77FA00 (WMO, 0x10) | – | Zone und WMO unter einem Punkt |

Häufigkeit pro Bild, nur statisch geschätzt und nicht gemessen **[?]**: Kamera 1–4 Aufrufe, Wasser-Kamera 1, `CWorld::Update` 1 (direkt), Maus-Picking 0–2, Lens-Flare 0–n, dazu je aktivem Geschoss bzw. Zaubereffekt. Zusammen typisch **etwa 3–10 pro Bild**, in Kämpfen mehr.

### 1.4 Globale Zustände, Reentranz, Thread [V]

TraceLine und die von ihr gerufenen Funktionen benutzen:

| Global / Feld | Zweck |
|---|---|
| `0xCE04C4` | Abfragezähler (+1 je Aufruf). Mailbox-Marke in `CMapDoodadDef+0x2C` und Objekt-Ref+0x2C, damit nichts doppelt getestet wird. Wird auch von den Bewegungsabfragen 0x7A5DD0/0x7A5F20/0x7ADE10 benutzt |
| `[0xCF4930]`, `0xCE04C8` | Zellpuffer mit Zähler, max. 0x7FC Einträge. **Die achsenparallelen Sammler 0x7A20E0/0x7A2180 prüfen die Grenze nicht**, deshalb Strahlen kurz halten (< 1 000 yd, bei uns < 100) |
| `[0xCD754C]` = Welt-M2-Szene | +0x1C Bitwert 0x2 („Trace läuft“), +0x114 Kandidatenliste, +0x118/+0x11C Puffer, +0x12C Treffer-M2, +0x13C. Diese Felder benutzt nur der Trace-Code (0x81CAxx–0x81E3xx), das Rendern nicht |
| `CM2Model +0x2D4…+0x2E4` | Trace-Modus, Listenverkettung, Def-Zeiger |
| `0xD2DBF8`, `0xD25BF8[]`, `0xD2DBFC`, `0xD29BF8`, `0xCF08F8` | WMO-BSP-Abfrage. Getestete Dreiecke werden **im MOPY-Flagbyte der WMO-Gruppe mit 0x80 markiert** und am Ende zurückgesetzt (0x7C7610) |
| `0xD25498[145]` | gemeinsames Vertex-Raster für den Geländetest (z wird je Zelle eingesetzt) |
| `0xCD7768/0xCD776C` | GUID des zuletzt getroffenen Objekts |

Folgerungen:
- **Nicht reentrant, nicht threadsicher.** Aufruf nur im Hauptthread. Der Objektmanager (0x4D4DB0, 0x4D3790) hängt ohnehin am TLS-Slot `[0xD439BC]` des Hauptthreads.
- Kein Aufruf innerhalb einer anderen Kollisionsabfrage. Das passiert aus unseren Hooks nicht, denn TraceLine ruft keine fremden Rückrufe außer 0x4F6560.
- Das Spiel selbst ruft TraceLine zwischen und während der Render-Schritte (siehe Tabelle). Ein Aufruf aus unseren Render-Hooks wäre also technisch möglich. Der Bild-Hook in Abschnitt 3 ist trotzdem vorzuziehen: Er liefert konsistente Ergebnisse pro Bild, und kein M2- oder WMO-Durchlauf ist gerade halb fertig.
- TraceLine lädt nichts synchron nach. Ungeladene M2 (`[model+0x10]&1`), WMO-Gruppen (0x7AE4C0) und Chunks werden übersprungen. Es gibt also kein Ruckeln, aber am Rand der geladenen Welt sind falsche „frei“-Ergebnisse möglich.
- `[0xCD754C]` existiert ab Programmstart (0x780F50 `CWorld::Initialize`). TraceLine stürzt daher auch ohne geladene Welt nicht ab und liefert dann „kein Treffer“ (emuliert).

### 1.5 Billigere Variante?

Eine reine Ja/Nein-Variante gibt es nicht. TraceLine sucht immer den nächsten Treffer, und Gelände-Zellen werden auch nach einem Treffer weiter getestet. Sparen lässt sich so **[V]**:
- `hitOut = NULL` und `hitInfo = NULL` übergeben (nur minimaler Gewinn).
- **Flags knapp halten:** kein Wasser (0x30000), bei Bedarf auch kein 0x100000. Ohne 0x20/0x2/0x8/0x400000 bleibt M2 auf dem schnellen Weg 0x81E110, also nur Kollisionsnetze.
- **Strecke kürzen**: Das Strahlende wird um einen Rand vor den Zielpunkt gelegt, so sinkt die Zellenzahl. `frac_in < 1` verkürzt nur die Treffer-Annahme, nicht die Arbeit.
- Die internen Pfade 0x7A30D0 (nur WMO) und 0x7A39F0 (nur Gitter) lassen sich zwar einzeln aufrufen (siehe 0x77FA00), sparen aber kaum und verlieren Teile der Geometrie. Nicht empfohlen.

---

## 2. Kosten

Gemessen per Unicorn, Befehlszahl (`emu_cost.py`, `emu_terrain.py`) **[V]**:

| Bestandteil | Befehle |
|---|---|
| Grundlast, leere Welt, Flags 0x100111 | ~1 050 (Flags 0x100: ~300) |
| je geladener WMO-Instanz (AABB verfehlt) | **~88** (linear über alle geladenen Instanzen) |
| je Zelle (4,17 yd) mit Gelände | ~600–800 |
| Strahl 5 / 10 / 20 / 40 / 80 yd, nur Gelände | 1,9k / 5,1k / 8,1k / 12,6k / 22,2k |
| dto. mit 0x100111 (ohne WMO/M2 in der Testwelt) | 2,7k / 5,9k / 9,0k / 13,5k / 23,2k |

Nicht gemessen sind M2-Kandidaten (Hüllentest, dann ~50–80 Befehle je Kollisionsdreieck, nur bei Modellen, deren Hülle der Strahl trifft) und WMO-Gruppen mit BSP (je getroffener Gruppe grob einige 1 000 Befehle) **[?]**.

Schätzung für einen 20–40-yd-Strahl in einer Stadt mit ~150–300 geladenen WMO-Instanzen: **≈ 25–50 k Befehle, also etwa 10–30 µs** (x87-lastiger Code) **[?]**. Es gibt keinen frühen Abbruch bei einem Treffer. Die Kosten wachsen etwa linear mit der Strahllänge und mit der Zahl geladener WMO-Instanzen.

Empfehlung:
- Budget **12–24 Strahlen pro Bild**, das sind ≈ 0,1–0,7 ms.
- 48 Einheiten × 3 Punkte = 144 Strahlen ergeben bei 16 pro Bild einen vollen Umlauf in ~9 Bildern (≈150 ms bei 60 fps). Mit Hysterese ist das unkritisch.
- Den eigenen Charakter jedes Bild prüfen (1–3 Strahlen), die Gruppe reihum.
- Je Einheit zuerst den Brust-Strahl. Ist er blockiert, ist die Einheit „blockiert“; sonst Kopf und Knie, ggf. in späteren Bildern.

---

## 3. Sicherer Hook-Punkt

### 3.1 Bildablauf [V]

`CGWorldFrame::OnFrameRender` (Vtable 0x9F99D8, Slot 0x84 = 0x4FB080) reiht pro Bild den Rückruf **0x4FAF90** in den UI-Render-Batch ein (0x4858E0). Der Rückruf läuft im Hauptthread, einmal pro Bild und nur solange der WorldFrame existiert und sichtbar ist:

```
004FAF90  push ebp / mov ebp,esp / sub esp,0x80 / ... push esi        ; Matrizen sichern
004FB02C  8b7508          mov esi, dword ptr [ebp + 8]                ; ESI = CGWorldFrame*
004FB02F  8bce            mov ecx, esi
004FB031  e8baf5ffff      call 0x4fa5f0      ; OnWorldUpdate: Kamera (0x607B00), Objekte, CWorld::Update (Streaming) ...
004FB036  e845b42e00      call 0x7e6480      ; <== HOOK (Liste 0xAF4704, unkritisch)
004FB03B  8bce            mov ecx, esi
004FB03D  e85edeffff      call 0x4f8ea0      ; RenderWorld (vom Hold-Repeat-Patch am Eintrag gehookt)
004FB042  e8f9a02e00      call 0x7e5140
```

Innerhalb von 0x4FA5F0 ruft `0x4FA7BC call 0x607B00` (`CGCamera::Update(0, cam)`) die Kamerakollision 0x605D60 sowie 0x6061D0 und 0x603A10 auf und schreibt `cam+8` (0x6075A8 ff.). Danach folgen u. a. Objekt-Update (0x4D4B30 mit 0x4F6970), Rückruf-Registrierung `0x77F2B0(0x4F6560)` und `CWorld::Update` 0x7831A0.

### 3.2 Vorschlag A (empfohlen): 0x4FB036, Call umbiegen

- **VA 0x4FB036, Datei 0xFA436, Originalbytes `E8 45 B4 2E 00`** (`call 0x7E6480`, rel32 = 0x002EB445).
- Patch: `E8 <rel32 = Stub − 0x4FB03B>`. Es gibt keinen Sprung in den Bereich 0x4FB037–0x4FB03A (geprüft). Der Ein- und Rücksprung ist ein normales call/ret.
- Stub:
  ```
  stub:   call 0x7E6480            ; Original (rel32 aus Stub-Adresse neu berechnen)
          pushad                   ; optional, sauberer
          call RayFrame            ; eigene Routine (cdecl, keine Argumente)
          popad
          ret                      ; -> 0x4FB03B
  ```
- **Registerzustand bei 0x4FB036**:
  - `ESI` = CGWorldFrame* (wird bei 0x4FB03B als `this` gebraucht).
  - `EBP` = Rahmen von 0x4FAF90; Locals `[ebp-0x80..-4]` sind die gesicherten Matrizen.
  - `EBX`/`EDI`: Werte des Aufrufers von 0x4FAF90. 0x4FAF90 sichert sie **nicht** selbst, also unbedingt erhalten.
  - `EAX`/`ECX`/`EDX` sind frei; 0x7E6480 zerstört sie ohnehin.
  - FPU-Stapel ist leer, und er muss bei Rückkehr wieder leer sein.
  - Steuerwort nicht ändern (das Spiel läuft mit D3D-FPU-Einstellung). Direction-Flag ist gelöscht.
  - Stack ist nur 4-Byte-ausgerichtet.
  - Stack-Bedarf: TraceLine braucht ~6,5 KB, das ist im Hauptthread unkritisch.
- Ergebnis: Die Strahlen laufen **nach** dem kompletten Welt-Update (Kamera, Einheiten, Streaming) und **vor** dem gesamten Weltrendern desselben Bildes. Die Render-Hooks von Patch 68 können die Ergebnisse noch im selben Bild verwenden.
- Konflikte: Das Repository-Skript `apply_patches.ps1` (Stand im Arbeitsbaum) patcht 0x4F8EA0-Eintrag (Hold-Repeat) und 0x4F91E5 (Umrandung), aber nichts bei 0x4FB036, 0x7E6480, 0x4FAF90 oder 0x4FA5F0. Bitte mit dem Dev-Stand gegenprüfen.
- **Emulation (`emu_hook.py`) [V]**: Mit gepatchtem Call und Stub-Skizze (Wächter, Kamera lesen, ein TraceLine-Aufruf) kehrt die Ausführung bei 0x4FB03B zurück. ESI/EDI/EBX/EBP/ESP sind erhalten. Bei gesetztem Ladeflag wird der Strahl ausgelassen.

### 3.3 Vorschlag B (Alternative ohne relative Befehle): 0x4FA7C1

```
004FA7BC  e83fd31000      call 0x607b00                 ; Kamera-Update
004FA7C1  8bb7207e0000    mov esi, dword ptr [edi+0x7e20]   ; <== 6 Byte, nicht relativ
004FA7C7  8b5608          mov edx, dword ptr [esi + 8]
```
- Patch: `E9 <rel32> 90`. Stub: `pushad; pushfd; call RayFrame; popfd; popad; mov esi,[edi+0x7E20]; jmp 0x4FA7C7`.
- Registerzustand: `EDI` = CGWorldFrame*, `EAX` = 1 (Rückgabe von 0x607B00). Am Stack liegen noch 3 DWORDs, die erst `add esp,0xC` bei 0x4FA7DE abräumt; ESP also exakt erhalten. Kein Sprung in 0x4FA7C2–0x4FA7C6 (geprüft).
- Nachteil: Die Stelle liegt vor dem restlichen Welt-Update (Objekte, Streaming). Einheitenpositionen und Modelle können ein Bild alt sein.

### 3.4 Welt geladen, Ladebildschirm, Login

- Der WorldFrame (`[0xB7436C]`) entsteht über die XML-Fabrik 0x50F3F0 (`CGWorldFrame`), also erst mit der Spiel-UI. Im Login und in der Charakterauswahl (Glue-UI) gibt es ihn nicht. **0x4FAF90 läuft dort gar nicht** **[V/T]**.
- Wächter im eigenen Code, alle billig:
  1. `byte [0xBD0792] != 0`: „in der Welt“. Gesetzt in `0x528010` (EnterWorld), gelöscht in `0x528C30` (LeaveWorld) **[V]**.
  2. `byte [0xBD0790] == 0`: Laden aktiv. Gesetzt bei 0x52B00C vor der Ladefunktion 0x52A980, gelöscht bei deren Ende 0x52AE91 **[T]**.
  3. `[0xB7436C] != 0` und `cam = [wf+0x7E20] != 0`.
  4. Aktiver Spieler: `0x4D3790()` liefert in EDX:EAX eine GUID ≠ 0, und `0x4D4DB0(lo,hi,0x10,0,0) != 0`.
- Zusätzlich gilt: TraceLine liefert ohne geladene ADT einfach „kein Treffer“. Ein Fehlaufruf wäre also harmlos (emuliert).

### 3.5 Skizze RayFrame (wie in `emu_hook.py` assembliert und emuliert)

```
rayframe:
    push ebp / mov ebp, esp / sub esp, 0x40
    cmp byte ptr [0xBD0792], 0 / je done          ; in Welt?
    cmp byte ptr [0xBD0790], 0 / jne done         ; Laden aktiv?
    mov eax, [0xB7436C] / test eax,eax / je done  ; WorldFrame
    mov eax, [eax+0x7E20] / test eax,eax / je done; aktive Kamera
    ; start = [eax+8..0x10], end = Zielpunkt (siehe Abschnitt 5), frac = 1.0f
    push 0                 ; hitInfo
    push 0x100111          ; flags (siehe Abschnitt 8)
    lea ecx,[ebp-0x28] / push ecx   ; &frac
    push 0                 ; hitOut = NULL
    lea ecx,[ebp-0x34] / push ecx   ; &end
    lea ecx,[ebp-0x40] / push ecx   ; &start
    call 0x7A3B70          ; oder 0x77F310
    add esp, 0x18          ; AL = blockiert?
done:
    mov esp, ebp / pop ebp / ret
```

---

## 4. Kameraposition [V]

```
004F5960  a16c43b700      mov eax, dword ptr [0xb7436c]     ; GetActiveCamera(): NULL ohne WorldFrame
004F5965  85c0            test eax, eax
004F5969  8b80207e0000    mov eax, dword ptr [eax + 0x7e20]
004F6650  ...             ; GetCameraPosition(C3Vector* out) = [[0xB7436C]+0x7E20]+8 (ohne NULL-Prüfung!)
```
- Kette: `wf = [0xB7436C]`, `cam = [wf + 0x7E20]`, alternativ `call 0x4F5960` (liefert 0, wenn kein WorldFrame).
- Kamera-Struct (Basis-Ctor 0x607C20, CGCamera-Vtable 0xA1EA54):
  - `+0x08` Position x,y,z: **Weltkoordinaten**. Die Weltszene nutzt sie direkt über 0x4F6650 (6 Aufrufer in 0x74…/0x7B…/0x7E…).
  - `+0x14` Blickmatrix 3×3, Zeile 0 = Vorwärts (lokal; `vtbl+4` 0x600C20 rechnet sie bei Transporter `[cam+0xA0/0xA4]` in Welt um).
  - `+0x38` Near, `+0x3C` Far, `+0x40` FOV, `+0x44` Seitenverhältnis.
  - `+0x88/+0x8C` GUID des verfolgten Ziels, `+0x90/+0x94` zweite Ziel-GUID, `+0x48` ≠ 0: Sonderzweig 0x601E90 (Bedeutung [?]).
- Gültigkeitsprüfung: wf ≠ 0, cam ≠ 0, Position endlich (Exponent ≠ 0xFF) und |x|,|y| < 17066,67. Optional Abstand Kamera–Spieler < 100 yd.
- Ob `cam+8` auch **auf Transportern** Weltkoordinaten enthält, ist **[T]**: Die Weltszene und die Kamerakollision benutzen den Wert ohne Umrechnung, nur die Blickrichtung wird transformiert.

---

## 5. Einheiten: Zeiger, Position, Höhe

### 5.1 GUID → Objekt [V]
```
004D4DB0  ClntObjMgrObjectPtr(uint32 guidLo, uint32 guidHi, uint32 typeMask, const char* file, int line)  ; cdecl, add esp,0x14
          -> NULL, wenn kein Objektmanager (TLS), GUID 0, unbekannt, oder ([desc+8] & typeMask) == 0
004D3790  ClntObjMgrGetActivePlayer() -> EDX:EAX = GUID des eigenen Charakters (0, wenn keiner)
```
- `file` und `line` werden nicht benutzt, 0 übergeben ist in Ordnung.
- TypeMask: 0x8 = Unit, deckt NPC und Spieler ab; 0x10 = Player. `OBJECT_FIELD_TYPE` bei `[obj+8]+8`. Spieler haben 0x19.
- **Keine Objektzeiger über Bildgrenzen merken**, nur GUIDs. Den Zeiger jedes Bild neu per 0x4D4DB0 holen; damit sind veraltete Zeiger ausgeschlossen.
- Gruppen-GUIDs: Party `0xBD1948 + 8*i`, i = 0..3 **[V]** (indizierter Zugriff bei 0x52BC61). Raid: dieselbe Lookup-Funktion für jede GUID aus der bekannten Raid-Liste des Patches.
- Hauptthread erforderlich (TLS `fs:[0x2C]`, Slot `[0xD439BC]`).

### 5.2 Weltposition [V]
- Virtuell `[vtbl+0x2C]` = 0x6E6EF0 `GetPosition(C3Vector* out)`, thiscall mit 1 Argument, `ret 4`, gleich in CGUnit_C (0xA34D90) und CGPlayer_C (0xA326C8):
  ```
  006E6EF3  mov ecx, [ecx+0xd8]      ; CMovement* (= obj+0x788)
  006E6EFD  lea eax, [ecx+0x10]      ; lokale Position
  006E6F02  call 0x4f4460            ; Transporter-Transformation ([mov+8/+C] = Transporter-GUID)
  ```
- Roh-Felder: `obj+0x798/0x79C/0x7A0` = Position (bei Transporter lokal!), `obj+0x7A8` Blickrichtung, `obj+0x790/0x794` Transporter-GUID. **Empfohlen ist die virtuelle Funktion.**
- Diese Position ist der Fußpunkt (Boden). Beim Schweben ziehen `[unitfields+0x230]` (HoverHeight) bzw. das Bewegungsflag 0x40000000 ab; das ist für uns unwichtig.

### 5.3 Höhe
- **Empfohlen: `float [obj+0x854]`** (= `CMovement+0xCC`) **[T]**:
  - Wird in `0x6E9570` (`CMovement::SetCollisionBounds`) als Höhe × Skalierung gesetzt. Die Werte kommen aus CreatureDisplayInfo/CreatureModelData (0x725F50, NATIVEDISPLAYID) bzw. bei Spielern aus 0x6D78C0/0x6D7720 (mit Reittier-Skalierung `[obj+0x990]`).
  - Das Spiel nutzt den Wert als Einheitenhöhe: Mitte = 0,5·H (0x7371E3), `0x718080` = H − 1/6 (bei NPCs mindestens 2,0278), Standard 2,0278 yd (Mensch).
  - Plausibilitätsprüfung 0,3 < H < 40, sonst ersatzweise 2,0 × `OBJECT_FIELD_SCALE_X`.
- Skalierung: `OBJECT_FIELD_SCALE_X` = `[[obj+8]+0x10]` (`vtbl+0x3C` = 0x4D5F00) **[V]**.
- Deskriptor, absolute Offsets ab `[obj+8]` **[V]** (Feldtabelle im Exe, relative Indizes ab OBJECT_END: BOUNDINGRADIUS 0x3B, COMBATREACH 0x3C, DISPLAYID 0x3D, MOUNTDISPLAYID 0x3F):
  - `+0x104` BOUNDINGRADIUS (float)
  - `+0x108` COMBATREACH (float)
  - `+0x10C` DISPLAYID, `+0x110` NATIVEDISPLAYID, `+0x114` MOUNTDISPLAYID
  - Achtung: `[obj+0xD0]` zeigt auf `desc+0x18` (Unit-Felder). Relativ dazu sind es also −0x18, z. B. MOUNTDISPLAYID = `[[obj+0xD0]+0xFC]`.
- Alternative über das Modell **[T]**:
  - `model = [obj+0xB4]` (CM2Model), `[[model+0x2C]+8] & 1` = geladen, Header `[[model+0x2C]+0x150]`.
  - Hülle `+0xA0` min / `+0xAC` max, Kugelradius `+0xB8`; Kollisionsnetz `+0xD8…+0xE4` (über 0x81E345 verifiziert).
  - Welt-Matrix 4×4, zeilenweise, Translation in Zeile 3 (`model+0xE4..0xEC`): `model+0xB4` **[T]**.
  - Getter `0x4F5E20` (Hülle) und `0x4F5E80` (Kugel) laden ggf. **synchron nach** (0x823ED0). Deshalb vorher `0x824F00(model, 0, 0)` (thiscall, `ret 8`, wartet nicht) bzw. das Ladebit prüfen.
- Zielpunkte (Vorschlag): Fuß `P = GetPosition()`. Kopf `P + (0,0,0.90·H)`, Brust `P + (0,0,0.60·H)`, Knie `P + (0,0,0.25·H)`.

---

## 6. Beritten

- **[V]** `[obj+0x98C]` = CM2Model des Reittiers (0 = nicht beritten). `vtbl+0xD4` (0x6E6F80) gibt das „Wurzelmodell“ zurück: Reittier, falls vorhanden, sonst `[obj+0xB4]`. Das Reittier steht auf der Einheitenposition; das Reitermodell `[obj+0xB4]` hängt am Reittier.
- **[V]** `[obj+0x990]` = Reittier-Skalierung. Die Kamera multipliziert damit die Zielhöhe (0x604E96) und nutzt die Sequenz-Hüllen des Reittiers (Animation 0x5B „Mount“ über 0x82CED0).
- **[V]** Beritten erkennt man an `[obj+0x98C] != 0` oder an MOUNTDISPLAYID `[[obj+8]+0x114] != 0`.
- Höhe beritten **[T]**: Für Spieler setzt 0x6D7720 die Kollisionshöhe unter Einbeziehung des Reittiers (`[obj+0x990]`, 0x6CF350). `[obj+0x854]` sollte die Gesamthöhe Reittier+Reiter bereits enthalten.
  - Absicherung: Ist beritten und H < 2,5, dann `H = max(H, (MountBox.max.z·s_mount) + 1,6)` mit `s_mount` = Länge der Matrixzeile 2 des Reittier-Modells.
  - Oder den Reiter direkt nehmen: Translation der Welt-Matrix von `[obj+0xB4]` (Sitzpunkt) plus Reiterhöhe; Plausibilität: < 10 yd von `GetPosition`.
- Punkte für Berittene: Knie ≈ Sattelhöhe (0,55·H), Brust 0,75·H, Kopf 0,95·H. Die Beine des Reittiers interessieren nicht.

---

## 7. Unicorn-Tests (Zusammenfassung)

1. `emu_trace.py`: TraceLine mit leerer Welt **[V]**.
   - Aufrufkette 0x7A30D0 → (0x81CAC0, `_alloca`, qsort, 0x7AE140, 0x81DF10) → 0x7A39F0 → Sammler 0x7A2180/0x7A20E0 → 0x7A3570 → 0x81E110 (bei 0x100111) bzw. 0x81DF10 (bei 0x100171, weil 0x20 im Satz 0x16000AE).
   - Rückgabe 0, frac unverändert, EBX/ESI/EDI/EBP erhalten, `ret` ohne Abräumen (cdecl).
   - Zähler 0xCE04C4 +1 je Aufruf, Stack-Bedarf 6 484 Byte (bei Flags nur 0x100: 352 Byte).
2. `emu_cost.py`: +88 Befehle je WMO-Instanz in der Liste `[0xD25440]` **[V]**.
3. `emu_terrain.py`: Rastergitter mit 0x7C3C60 initialisiert, 25 ebene Chunks synthetisch erzeugt. Semantik von frac, hitOut, Rückgabe und Kosten je Länge siehe 1.1 und 2 **[V]**.
4. `emu_hook.py`: Patch bei 0x4FB036 (`e8 45 b4 2e 00` → `e8 <rel>`), Stub ruft 0x7E6480 (OsGetAsyncTimeMs gestubbt) und dann RayFrame auf.
   - Rückkehr bei 0x4FB03B, Register und ESP erhalten.
   - Mit Ladeflag wird kein Strahl abgesetzt **[V]**.

---

## 8. Empfehlungen zur Umsetzung

- **Flags**:
  - Standard **0x100111**: Gelände, WMO-Kollision, M2-Kollisionsnetze, GameObjects. Wie Flugbahn und Bodenprobe des Spiels; schneller M2-Weg.
  - Optisch genauer **0x200112** (wie der Lens-Flare-Sichttest 0x9ABC60: M2-Render-Geometrie, WMO, Gelände, GameObjects). Damit blockiert z. B. Baumlaub, das kostet aber den allgemeinen M2-Weg.
  - Für „sichtbare WMO-Dreiecke“ statt Kollisionsdreiecken 0x20 statt 0x10 setzen.
  - Wasser (0x30000) weglassen.
- **Strahl**: Start = Kamera. Ende = Zielpunkt, um **m ≈ 0,3–0,5 yd zur Kamera hin verkürzt**, damit der Boden direkt an einem eingesunkenen Fuß nicht zählt (siehe Test: Treffer 0,77 yd vor einem 0,5 yd tiefen Ziel). Kein Strahl unter ~1 yd Länge (Ego-Perspektive) und keiner über 150 yd.
- **Budget**: z. B. 16 Strahlen pro Bild. Eigener Charakter jedes Bild, Gruppe reihum mit Index-Zeiger. Reihenfolge Brust → Kopf → Knie, Abbruch beim ersten blockierten.
- **Hysterese**: z. B. „blockiert“ sofort übernehmen; „frei“ erst nach 2–3 aufeinanderfolgenden freien Prüfungen bzw. nach ≥ 150 ms. Zustand pro GUID speichern, nicht pro Zeiger. Einträge, deren GUID 0x4D4DB0 nicht mehr findet, verwerfen.
- **Übergabe an die Render-Hooks**: Ergebnis-Tabelle {GUID, CM2Model* `[obj+0xB4]`, Reittier `[obj+0x98C]`, Modus}. Diese Tabelle im Strahl-Hook pro Bild neu befüllen; dann können die Render-Hooks über den Modellzeiger nachschlagen, und das noch im selben Bild.

---

## 9. Risiken und offene Punkte

- **[?]** Echte Laufzeitkosten in der Spielwelt sind nicht gemessen; es gibt nur emulierte Befehlszahlen. Bitte im Spiel mit `QueryPerformanceCounter` um den Strahlblock messen und das Budget danach einstellen.
- **[T]** Die Bedeutung von `[obj+0x854]` als Gesamthöhe beim Reiten ist nicht vollständig dekodiert (0x6CF350 nicht analysiert). Absicherung siehe Abschnitt 6.
- **[T]** `[0xBD0790]` als Ladeflag ist nur aus dem Kontext abgeleitet. `[0xBD0792]` (in der Welt) ist belegt.
- **[T]** Die MOPY-Bitnamen (F_RENDER, F_DETAIL, F_COLLISION, F_NOCAMCOLLIDE) stammen aus wowdev. Belegt ist nur die Maskenlogik.
- **[?]** Kamera auf Transportern: `cam+8` gilt als Weltposition (siehe Abschnitt 4), nicht im Spiel geprüft.
- Am Rand der geladenen Welt bricht Pfad 2 bei einem ungeladenen Chunk ab, das Ergebnis ist dann „frei“. Für Kamera→Gruppe (< 100 yd) praktisch irrelevant.
- Der Zellpuffer hat keine Grenzprüfung in den achsenparallelen Sammlern. Daher keine sehr langen Strahlen (> 1 000 yd).
- TraceLine schreibt `0xCD7768` (GUID des Trefferobjekts). Das Spiel liest es nur direkt nach seinen eigenen Aufrufen (Maus-Picking 0x4F9A5C/0x4F9BCF), deshalb unkritisch.
- Der Hook-Stub muss EBX/ESI/EDI/EBP sowie den leeren FPU-Stapel erhalten und darf das FPU-Steuerwort nicht ändern.
- Konflikte mit anderen Patches nur gegen `apply_patches.ps1` im Arbeitsbaum geprüft. Den Dev-Stand bitte gegen 0x4FB036 bzw. 0x4FA7C1 prüfen.

---

## Anhang: Disassembly-Ausschnitte

TraceLine-Ende (Trefferpunkt):
```
007A3C8C  84db        test bl, bl
007A3C8E  744b        je 0x7a3cdb
007A3C90  8b4510      mov eax, dword ptr [ebp + 0x10]     ; hitOut
007A3C93  3bc7        cmp eax, edi
007A3C95  7444        je 0x7a3cdb                         ; NULL erlaubt
007A3C97..7A3CD8      hitOut = start + (end - start) * (*frac)
007A3CDD  8ac3        mov al, bl
007A3CE3  c3          ret
```

Flags → WMO-Ablehnungsmaske (0x7AE140):
```
mov eax,0xEE ; if (f&0x80) return 0x2CA
if (f&0x10) eax=0xC6 ; if (f&0x20) eax&=~0x24 ; if (!(f&0x40)) eax&=~0x02
if (!(f&0x4000)) eax&=~0x40 ; if (f&0x1000000) { if (f&0x40000000) return 0xFFFFFCDB; eax|=0x100 }
; BSP-Dreieckstest (0x7C6C45/0x7C7077): Dreieck verworfen, wenn (MOPY.flags & mask) != 0;
; Masken-Bit 0x100 verwirft Alpha-Materialien, 0x200 Dreiecke ohne Material bzw. mit opakem Material.
```

Kamera-Kollisionsflags (0x5FEC50):
```
mov eax,[0xC249B4] (CVar cameraWaterCollision) ; mov eax,[eax+0x30] ; neg/sbb/and 0x20000 ; add eax,0x100171 ; ret
```

Einheit:
```
006E6F80  mov eax,[ecx+0x98c] ; test eax,eax ; jne ret ; mov eax,[ecx+0xb4] ; ret   ; vtbl+0xD4: Wurzelmodell
0073F67A  lea eax,[esi+0x788] ; mov [esi+0xd8],eax                                  ; CMovement eingebettet
0070CBB5  add ebx,0x18 ; mov [esi+0xd0],ebx                                         ; Unit-Felder = desc+0x18
006E960F  fstp dword ptr [esi+0xcc]                                                 ; CMovement+0xCC = Höhe
```
