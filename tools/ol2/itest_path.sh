#!/bin/bash
# Tests: Pfad zur Wow.exe (Startmenue P, wowpath= in patcher_selection.ini, -Path), Sicherungen im Patcher-Ordner.
# Aufruf: itest_path.sh <Ordner mit apply_patches.ps1> <Lauf-Ordner (neu)>
SRC=$1; R=$2
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/pwsh/pwsh
ICO=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/bt-rmo/test.ico
EXP=aa63a5750d60ef16746c686b3d5e26876d98953eab08b1c026cd0faf78e88cb8
mkdir -p "$R" || exit 1
fails=0
ok() { if eval "$2"; then echo "  OK   $1"; else echo "  FAIL $1"; fails=$((fails+1)); fi; }
P="$R/patcher"; W="$R/wow dir"; W2="$R/wow2"
mkdir -p "$P" "$W" "$W2"; cp "$SRC/apply_patches.ps1" "$ICO" "$P/"; cp "$ORI" "$W/Wow.exe"
printf 'language=de\nvalue.jump=-9.5\nvalue.doublejump=3\nvalue.clientversion=3.3.6\nvalue.clientbuild=12345\nvalue.clienttitle=TestTitle\nvalue.clientdate=2025-01-02 FR\nvalue.clienticon=test.ico\nvalue.bubblerange=150\n' > "$P/patcher_selection.ini"
run() { (cd "$P" && printf "$1" | "$PW" -NoProfile -File ./apply_patches.ps1 $2 > "$R/out_$3.txt" 2>&1; echo $? > "$R/rc_$3.txt"); }
rc() { cat "$R/rc_$1.txt"; }
has() { grep -q -- "$2" "$R/out_$1.txt"; }
sha() { sha256sum "$1" | cut -d' ' -f1; }
ini() { grep '^wowpath=' "$P/patcher_selection.ini" | cut -d= -f2-; }

echo "A: keine Wow.exe, keine Sicherung -> Startmenue mit P/Q statt Abbruch"
run '\nQ\n\n' '' a
ok "Fehlermeldung + Hinweis" 'has a "Keine Wow.exe gefunden:" && has a "gib mit P ihren Pfad an"'
ok "Tasten [P/Q]" 'has a "\[P/Q\]"'
ok "Exit-Code 2" '[ "$(rc a)" = 2 ]'

echo "B: P -> Ordner mit Leerzeichen, in Anfuehrungszeichen (Drag & Drop)"
run "\nP\n\"$W\"\nQ\n\n" '' b
ok "gemerkt-Meldung" 'has b "Gemerkt - der Patcher nimmt jetzt diese Wow.exe: $W/Wow.exe"'
ok "ini wowpath" '[ "$(ini)" = "$W/Wow.exe" ]'
ok "Zeile Wow.exe: Pfad" 'has b "Wow.exe: $W/Wow.exe (Sicherungen im Patcher-Ordner)"'
ok "Pruefung original" 'has b "\[OK\] Wow.exe ist original"'
ok "ORI im Patcher-Ordner, nicht im WoW-Ordner" '[ "$(sha "$P/Wow.exe.ORI")" = $EXP ] && [ ! -e "$W/Wow.exe.ORI" ]'
ok "Tasten [1/3/M/P/Q]" 'has b "\[1/3/M/P/Q\]"'
ok "neue Seite (Banner nach P)" '[ "$(grep -c "_____ _    ___" "$R/out_b.txt")" = 3 ]'

echo "C: unbeaufsichtigt mit gemerktem Pfad -> Exe im WoW-Ordner gepatcht"
(cd "$P" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select stony > "$R/u_c.txt" 2>&1); echo $? > "$R/urc_c.txt"
ok "Exit-Code 0" '[ "$(cat $R/urc_c.txt)" = 0 ]'
ok "Exe im WoW-Ordner gepatcht" '[ "$(sha "$W/Wow.exe")" != $EXP ] && grep -q "St0nys AIO" "$W/Wow.exe"'
ok "state im Patcher-Ordner, nichts im WoW-Ordner" '[ -e "$P/patcher_state.ini" ] && [ "$(ls "$W")" = "Wow.exe" ]'
cp "$W/Wow.exe" "$R/stony.exe"

echo "D: zweiter Lauf (Auswahl speichern) behaelt wowpath"
run '\n1\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nN\n\n' '' d
ok "ini wowpath bleibt" '[ "$(ini)" = "$W/Wow.exe" ] && grep -q "^laa=" "$P/patcher_selection.ini"'
ok "BAK im Patcher-Ordner" '[ -e "$P/Wow.exe.BAK" ] && [ ! -e "$W/Wow.exe.BAK" ]'

echo "E: 3 = Original in den WoW-Ordner, ohne Kopier-Hinweis"
run '\n3\nJ\n\n' '' e
ok "Wow.exe im WoW-Ordner = Original" '[ "$(sha "$W/Wow.exe")" = $EXP ]'
ok "kein Hinweis zum Kopieren" '! has e "in den WoW-Ordner kopieren"'

echo "F: gemerkte Exe fehlt -> Wiederherstellen dorthin"
rm -f "$W/Wow.exe"
run '\n3\n\n' '' f
ok "Meldung keine Wow.exe + Sicherungen" 'has f "Keine Wow.exe gefunden, aber Sicherungen im Ordner:"'
ok "Original im WoW-Ordner, nicht im Patcher-Ordner" '[ "$(sha "$W/Wow.exe")" = $EXP ] && [ ! -e "$P/Wow.exe" ]'

echo "G: P mit falschem Pfad, dann & '...' (PowerShell-Drag&Drop) auf die Exe"
run "\nP\n$R/gibtsnicht\n& '$W/Wow.exe'\nQ\n\n" '' g
ok "Hinweis falscher Pfad" 'has g "Dort ist keine Wow.exe: $R/gibtsnicht"'
ok "ini wowpath" '[ "$(ini)" = "$W/Wow.exe" ]'

echo "H: P + ENTER -> wieder Patcher-Ordner"
run '\nP\n\nQ\n\n' '' h
ok "Meldung zurueck" 'has h "nimmt wieder die Wow.exe im Patcher-Ordner"'
ok "wowpath entfernt" '! grep -q "^wowpath=" "$P/patcher_selection.ini"'
ok "danach Patcher-Ordner ohne Exe, aber Sicherungen" 'has h "Keine Wow.exe gefunden, aber Sicherungen im Ordner:"'

echo "I: -Path -> Sicherungen im Patcher-Ordner, kein P"
cp "$ORI" "$W2/Wow.exe"; rm -f "$P/Wow.exe.ORI" "$P/Wow.exe.BAK" "$P/patcher_state.ini"
(cd "$P" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select stony -Path "$W2/Wow.exe" > "$R/u_i.txt" 2>&1)
ok "ORI im Patcher-Ordner, nicht neben der Exe" '[ "$(sha "$P/Wow.exe.ORI")" = $EXP ] && [ ! -e "$W2/Wow.exe.ORI" ]'
ok "Exe gepatcht" 'grep -q "St0nys AIO" "$W2/Wow.exe"'
run '\nQ\n\n' "-Path $W2/Wow.exe" i2
ok "kein P bei -Path" '! has i2 "P = Pfad" && has i2 "Wow.exe: $W2/Wow.exe"'

echo "J: Englisch"
sed -i 's/^language=de/language=en/' "$P/patcher_selection.ini"
run "\nP\n$W2\nQ\n\n" '' j
ok "englische Texte" 'has j "P = Set the path to Wow.exe (remembered)" && has j "Remembered - the patcher now uses this Wow.exe: $W2/Wow.exe" && has j "(backups in the patcher folder)"'
sed -i 's/^language=en/language=de/' "$P/patcher_selection.ini"

echo "K: unbeaufsichtigt, gemerkte Exe fehlt, keine Sicherung -> Abbruch"
rm -f "$P/Wow.exe.ORI" "$P/Wow.exe.BAK" "$W2/Wow.exe"
(cd "$P" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select stony > "$R/u_k.txt" 2>&1); r=$?
ok "Exit-Code 1 + Meldung" '[ $r = 1 ] && grep -q "Keine Wow.exe gefunden: $W2/Wow.exe" "$R/u_k.txt"'

echo "DONE fails=$fails"
