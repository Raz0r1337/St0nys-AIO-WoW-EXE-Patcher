#!/bin/bash
# Interaktive Tests fuer das Startmenue. Aufruf: itest.sh <Ordner mit apply_patches.ps1> <Lauf-Ordner (neu)>
SRC=$1; R=$2
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/pwsh/pwsh
ICO=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/bt-rmo/test.ico
EXP=aa63a5750d60ef16746c686b3d5e26876d98953eab08b1c026cd0faf78e88cb8
mkdir -p "$R" || exit 1
fails=0
ok() { if eval "$2"; then echo "  OK   $1"; else echo "  FAIL $1"; fails=$((fails+1)); fi; }
newdir() { d="$R/$1"; mkdir -p "$d"; cp "$SRC/apply_patches.ps1" "$ICO" "$d/"; cp "$ORI" "$d/Wow.exe"
  printf 'language=de\nvalue.jump=-9.5\nvalue.doublejump=3\nvalue.clientversion=3.3.6\nvalue.clientbuild=12345\nvalue.clienttitle=TestTitle\nvalue.clientdate=2025-01-02 FR\nvalue.clienticon=test.ico\nvalue.bubblerange=150\n' > "$d/patcher_selection.ini"; }
run() { (cd "$d" && printf "$1" | "$PW" -NoProfile -File ./apply_patches.ps1 $2 > "$d/out_$3.txt" 2>&1; echo $? > "$d/rc_$3.txt"); }
rc() { cat "$d/rc_$1.txt"; }
has() { grep -q -- "$2" "$d/out_$1.txt"; }
sha() { sha256sum "$1" | cut -d' ' -f1; }
unatt() { (cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select "$1" > "$d/u_$1.txt" 2>&1); }

echo "A: erster Start ohne ini -> Sprache, Startmenue, Q"
newdir A; rm -f "$d/patcher_selection.ini"
run '1\n\nQ\n\n' '' a
ok "Exit-Code 2" '[ "$(rc a)" = 2 ]'
ok "Option 1 Patch-Menue" 'has a "1 = Patch-Menue oeffnen"'
ok "Option M" 'has a "M = Patch-Menue oeffnen und das Startmenue"'
ok "Tasten [1/M/Q]" 'has a "\[1/M/Q\]"'
ok "keine Sicherungen gelistet" '! has a "Sicherungen im Ordner"'
ok "Wow.exe unveraendert" '[ "$(sha $d/Wow.exe)" = $EXP ]'

echo "B: M im Startmenue -> Patch-Menue mit Hinweis, startmenu=off gemerkt"
newdir B
run '\nM\nQ\n\n' '' b
ok "Exit-Code 2 (Q im Patch-Menue)" '[ "$(rc b)" = 2 ]'
ok "Hinweis im Patch-Menue" 'has b "Startmenue ausgeschaltet"'
ok "ini startmenu=off" 'grep -qx "startmenu=off" $d/patcher_selection.ini'
ok "Sprache bleibt" 'grep -qx "language=de" $d/patcher_selection.ini'
ok "Hilfezeile M = Startmenue einschalten" 'has b "M = Startmenue einschalten"'

echo "C: startmenu=off -> kein Startmenue, Info-Zeile, M schaltet wieder ein"
run '\nM\nQ\n\n' '' c
ok "Info-Zeile beim Start" 'has c "Startmenue: aus (gemerkt"'
ok "kein Startmenue" '! has c "Was moechtest du tun"'
ok "Meldung eingeschaltet" 'has c "Startmenue eingeschaltet"'
ok "ini startmenu=on" 'grep -qx "startmenu=on" $d/patcher_selection.ini'
run '\nQ\n\n' '' c2
ok "danach wieder Startmenue" 'has c2 "Was moechtest du tun"'

echo "D: gepatcht + Sicherungen -> 2 = vorherige Wow.exe (mit Rueckfrage)"
newdir D; unatt reforged; cp "$d/Wow.exe" "$d/reforged.exe"; unatt stony; cp "$d/Wow.exe" "$d/stony.exe"
ok ".BAK = Reforged-Exe" '[ "$(sha $d/Wow.exe.BAK)" = "$(sha $d/reforged.exe)" ]'
run '\n2\nJ\n\n' '' d
ok "Exit-Code 0" '[ "$(rc d)" = 0 ]'
ok "Sicherungen gelistet" 'has d "Sicherungen im Ordner:" && has d "Original: Wow.exe.ORI" && has d "Backup:   Wow.exe.BAK"'
ok "Tasten [1/2/3/M/Q]" 'has d "\[1/2/3/M/Q\]"'
ok "Rueckfrage" 'has d "Die aktuelle Wow.exe wird durch Wow.exe.BAK ersetzt"'
ok "Wow.exe = .BAK" '[ "$(sha $d/Wow.exe)" = "$(sha $d/reforged.exe)" ]'
ok ".BAK/.ORI unveraendert" '[ "$(sha $d/Wow.exe.BAK)" = "$(sha $d/reforged.exe)" ] && [ "$(sha $d/Wow.exe.ORI)" = $EXP ]'
echo "D2: Rueckfrage mit N -> nichts geaendert"
cp "$d/stony.exe" "$d/Wow.exe"; run '\n3\nN\n\n' '' d2
ok "Exit-Code 2" '[ "$(rc d2)" = 2 ]'
ok "Wow.exe unveraendert (St0ny)" '[ "$(sha $d/Wow.exe)" = "$(sha $d/stony.exe)" ]'
echo "D3: 3 = Original"
run '\n3\nJ\n\n' '' d3
ok "Wow.exe = Original" '[ "$(sha $d/Wow.exe)" = $EXP ]'
echo "D4: 3 bei schon originaler Wow.exe -> nichts zu tun"
run '\n3\n\n' '' d4
ok "Meldung identisch" 'has d4 "ist bereits identisch mit Wow.exe.ORI"'
ok "Exit-Code 0" '[ "$(rc d4)" = 0 ]'
echo "D5: 1 = Patch-Menue mit gepatchter Exe (Stand erkannt)"
cp "$d/stony.exe" "$d/Wow.exe"; run '\n1\nQ\n\n' '' d5
ok "Patch-Menue geoeffnet (Abbruch mit Q)" 'has d5 "PATCH-AUSWAHL" && [ "$(rc d5)" = 2 ]'

echo "E: Wow.exe fehlt -> 1 = neu aus dem Original (letzte Auswahl), komplett patchen"
newdir E; unatt reforged; cp "$d/Wow.exe" "$d/reforged.exe"; rm -f "$d/Wow.exe"
run '\n1\n\n\nJ\n\n' '' e
ok "Meldung keine Wow.exe" 'has e "Keine Wow.exe gefunden, aber Sicherungen im Ordner:"'
ok "Option 1 neu bauen" 'has e "1 = Neue Wow.exe aus dem Original bauen (Patches wie zuletzt"'
ok "kein M" '! has e "M = Patch-Menue oeffnen"'
ok "Exit-Code 0" '[ "$(rc e)" = 0 ]'
ok "neue Wow.exe = letzte (Reforged)" '[ "$(sha $d/Wow.exe)" = "$(sha $d/reforged.exe)" ]'
ok "kein .BAK angelegt" '[ ! -e $d/Wow.exe.BAK ]'

echo "F: Wow.exe fehlt + -Unattended -> Abbruch mit Hinweis"
newdir F; unatt reforged; rm -f "$d/Wow.exe"; unatt saved
ok "Hinweis RestUnatt" 'grep -q "Im Ordner liegen Sicherungen (Wow.exe.ORI)" $d/u_saved.txt && grep -q "Keine Wow.exe gefunden" $d/u_saved.txt'
ok "keine Wow.exe angelegt" '[ ! -e $d/Wow.exe ]'

echo "G: unbrauchbare Wow.exe (fremd veraendert) -> Fehler + Startmenue, 3 = Original"
newdir G; unatt reforged; printf '\x90' | dd of="$d/Wow.exe" bs=1 seek=4096 conv=notrunc 2>/dev/null; cp "$d/Wow.exe" "$d/foreign.exe"
python3 -c "import sys; d=open(sys.argv[1],'rb').read(); i=d.find(b'St0nys AIO'); open(sys.argv[1],'wb').write(d[:i]+b'X'+d[i+1:]) if i>=0 else None" "$d/Wow.exe"
run '\n3\nJ\n\n' '' g
ok "Fehlermeldung" 'has g "\[FEHLER\] Die Wow.exe"'
ok "Startmenue nicht verwendbar" 'has g "Die Wow.exe ist nicht verwendbar, es gibt aber Sicherungen im Ordner:"'
ok "Option 1 ersetzt" 'has g "1 = Neue Wow.exe aus dem Original bauen (ersetzt die aktuelle"'
ok "kein M" '! has g "M = Patch-Menue oeffnen"'
ok "Wow.exe = Original" '[ "$(sha $d/Wow.exe)" = $EXP ]'
echo "G2: unbrauchbare Wow.exe + -Unattended -> Abbruch"
cp "$d/foreign.exe" "$d/Wow.exe"; python3 -c "import sys; d=open(sys.argv[1],'rb').read(); i=d.find(b'St0nys AIO'); open(sys.argv[1],'wb').write(d[:i]+b'X'+d[i+1:]) if i>=0 else None" "$d/Wow.exe"; cp "$d/Wow.exe" "$d/foreign2.exe"; unatt saved
ok "Abbruch mit Hinweis" 'grep -q "FEHLER\] Die Wow.exe" $d/u_saved.txt && grep -q "Im Ordner liegen Sicherungen" $d/u_saved.txt'
ok "Wow.exe unveraendert" '[ "$(sha $d/Wow.exe)" = "$(sha $d/foreign2.exe)" ]'
echo "G3: unbrauchbare Wow.exe -> 1 = neu aus dem Original (ersetzt sie)"
run '\n1\n\n\nJ\n\n' '' g3
ok "Exit-Code 0" '[ "$(rc g3)" = 0 ]'
ok "Wow.exe neu gebaut (Wasserzeichen)" 'grep -q "St0nys AIO" $d/Wow.exe'
ok "Fertig-Meldung" 'has g3 "\[FERTIG\]"'

echo "H: -Select ohne -Unattended, Wow.exe ok -> kein Startmenue"
newdir H
run '\n\n' '-Select none' h
ok "kein Startmenue" '! has h "Was moechtest du tun"'
ok "Meldung bereits original" 'has h "bereits original"'

echo "I: kein Wow.exe, keine Sicherung -> Fehler wie bisher"
newdir I; rm -f "$d/Wow.exe"
run '\n\n' '' i
ok "Fehlermeldung" 'has i "Keine Wow.exe gefunden:"'
ok "Exit-Code 1" '[ "$(rc i)" = 1 ]'

echo "J: Auswahl speichern behaelt startmenu=off"
newdir J; printf 'startmenu=off\n' >> "$d/patcher_selection.ini"
run '\n\n\nN\n\n' '' j
ok "ini startmenu=off nach Speichern" 'grep -qx "startmenu=off" $d/patcher_selection.ini && grep -q "^laa=" $d/patcher_selection.ini'

echo "K: Englisch"
newdir K; sed -i 's/^language=de/language=en/' "$d/patcher_selection.ini"; unatt reforged; unatt stony
run '\nQ\n\n' '' k
ok "englisches Startmenue" 'has k "1 = Open the patch menu" && has k "Backups in the folder:" && has k "M = Open the patch menu and skip"'

echo "DONE fails=$fails"
