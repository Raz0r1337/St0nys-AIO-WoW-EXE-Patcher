#!/bin/bash
# Tests: fehlende Wow.exe.ORI/.BAK beim Start anlegen, alte Nr.-4-Stelle. Aufruf: itest_oribak.sh <Ordner mit apply_patches.ps1> <Lauf-Ordner (neu)>
SRC=$1; R=$2
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
OLD=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/9a750ac5-Wow.exe
PW=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/pwsh/pwsh
ICO=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/bt-rmo/test.ico
EXP=aa63a5750d60ef16746c686b3d5e26876d98953eab08b1c026cd0faf78e88cb8
mkdir -p "$R" || exit 1
fails=0
ok() { if eval "$2"; then echo "  OK   $1"; else echo "  FAIL $1"; fails=$((fails+1)); fi; }
newdir() { d="$R/$1"; mkdir -p "$d"; cp "$SRC/apply_patches.ps1" "$ICO" "$d/"; cp "$2" "$d/Wow.exe"
  printf "language=${3:-de}\nvalue.jump=-9.5\nvalue.doublejump=3\nvalue.clientversion=3.3.6\nvalue.clientbuild=12345\nvalue.clienttitle=TestTitle\nvalue.clientdate=2025-01-02 FR\nvalue.clienticon=test.ico\nvalue.bubblerange=150\n" > "$d/patcher_selection.ini"; }
run() { (cd "$d" && printf "$1" | "$PW" -NoProfile -File ./apply_patches.ps1 $2 > "$d/out_$3.txt" 2>&1; echo $? > "$d/rc_$3.txt"); }
rc() { cat "$d/rc_$1.txt"; }
has() { grep -q -- "$2" "$d/out_$1.txt"; }
sha() { sha256sum "$1" | cut -d' ' -f1; }
unatt() { (cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language ${2:-de} -Select "$1" > "$d/u_$1.txt" 2>&1; echo $? > "$d/urc_$1.txt"); }

echo "A: alte Exe (Nr. 4 alte Stelle) ohne Sicherungen -> ORI + BAK beim Start, Q"
newdir A "$OLD"
run '\nQ\n\n' '' a
ok "Exit-Code 2" '[ "$(rc a)" = 2 ]'
ok "Patchstand erkannt" 'has a "Patchstand aus der Exe ermittelt"'
ok "ORI-Meldung" 'has a "Wow.exe.ORI fehlte und wurde aus dem rekonstruierten Original neu angelegt"'
ok "BAK-Meldung" 'has a "Wow.exe.BAK fehlte - die aktuelle Wow.exe wurde als Backup gesichert"'
ok "Tasten [1/3/M/Q] (BAK = Wow.exe, keine 2)" 'has a "\[1/3/M/Q\]" && ! has a "2 = Vorherige"'
ok "BAK als gleicher Stand gelistet" 'has a "Backup:   Wow.exe.BAK (gleicher Stand wie die aktuelle Wow.exe)"'
ok "Abbruch-Meldung Wow.exe" 'has a "Abgebrochen. Die Wow.exe wurde nicht veraendert."'
ok "ORI = Original" '[ "$(sha $d/Wow.exe.ORI)" = $EXP ]'
ok "BAK = alte Exe" '[ "$(sha $d/Wow.exe.BAK)" = "$(sha $OLD)" ]'
ok "Wow.exe unveraendert" '[ "$(sha $d/Wow.exe)" = "$(sha $OLD)" ]'
echo "A2: zweiter Start -> nichts mehr anzulegen"
run '\nQ\n\n' '' a2
ok "keine Anlege-Meldungen" '! has a2 "fehlte" && ! has a2 "Original gesichert als"'
ok "Abbruch-Meldung nichts geaendert" 'has a2 "Abgebrochen. Es wurde nichts geaendert."'
ok "Sicherungen unveraendert" '[ "$(sha $d/Wow.exe.ORI)" = $EXP ] && [ "$(sha $d/Wow.exe.BAK)" = "$(sha $OLD)" ]'
echo "A3: 3 = Original wiederherstellen"
run '\n3\nJ\n\n' '' a3
ok "Wow.exe = Original" '[ "$(sha $d/Wow.exe)" = $EXP ]'

echo "B: alte Exe, -Unattended -Select none -> Original"
newdir B "$OLD"; unatt none
ok "Exit-Code 0" '[ "$(cat $d/urc_none.txt)" = 0 ]'
ok "Wow.exe = Original" '[ "$(sha $d/Wow.exe)" = $EXP ]'
ok "ORI = Original" '[ "$(sha $d/Wow.exe.ORI)" = $EXP ]'
ok "BAK = alte Exe" '[ "$(sha $d/Wow.exe.BAK)" = "$(sha $OLD)" ]'
ok "ORI nur einmal gemeldet" '[ "$(grep -c "Wow.exe.ORI fehlte" $d/u_none.txt)" = 1 ] && grep -q "ist vorhanden und bleibt unveraendert" $d/u_none.txt'

echo "C: alte Exe, -Unattended -Select stony -> neu gepatcht (Nr. 4 neue Stelle), dann zurueck"
newdir C "$OLD"; unatt stony
ok "Exit-Code 0" '[ "$(cat $d/urc_stony.txt)" = 0 ]'
ok "alte Nr.-4-Stelle original" 'python3 -c "import sys; d=open(sys.argv[1],\"rb\").read(); sys.exit(0 if d[0x41C91B:0x41C921]==bytes([0x0F,0x83,0x4D,0x01,0,0]) else 1)" $d/Wow.exe'
ok "neue Nr.-4-Stelle gepatcht (E9)" 'python3 -c "import sys; d=open(sys.argv[1],\"rb\").read(); sys.exit(0 if d[0x41C936]==0xE9 else 1)" $d/Wow.exe'
cp "$d/Wow.exe" "$d/stony.exe"; rm -f "$d/patcher_state.ini"; mv "$d/u_stony.txt" "$d/u_stony1.txt"; unatt stony
ok "Erkennung: keine Aenderung" 'grep -q "Keine Aenderung" $d/u_stony.txt'
unatt none
ok "zurueck: Original" '[ "$(sha $d/Wow.exe)" = $EXP ]'

echo "D: originale Exe -> nur ORI, kein BAK"
newdir D "$ORI"
run '\nQ\n\n' '' d
ok "ORI-Meldung" 'has d "Original gesichert als:"'
ok "ORI = Original" '[ "$(sha $d/Wow.exe.ORI)" = $EXP ]'
ok "kein BAK" '[ ! -e $d/Wow.exe.BAK ]'
ok "Abbruch-Meldung Wow.exe" 'has d "Abgebrochen. Die Wow.exe wurde nicht veraendert."'

echo "E: gepatchte Exe, nur ORI fehlt (BAK da) -> nur ORI"
newdir E "$ORI"; unatt reforged; cp "$d/Wow.exe" "$d/reforged.exe"; unatt stony; rm -f "$d/Wow.exe.ORI" "$d/patcher_state.ini"; cp "$d/Wow.exe.BAK" "$d/bak_vorher.exe"
run '\nQ\n\n' '' e
ok "ORI-Meldung" 'has e "Wow.exe.ORI fehlte"'
ok "keine BAK-Meldung" '! has e "Wow.exe.BAK fehlte"'
ok "ORI = Original" '[ "$(sha $d/Wow.exe.ORI)" = $EXP ]'
ok "BAK unveraendert" '[ "$(sha $d/Wow.exe.BAK)" = "$(sha $d/bak_vorher.exe)" ]'

echo "F: gepatchte Exe, nur BAK fehlt -> nur BAK"
newdir F "$ORI"; unatt reforged; rm -f "$d/Wow.exe.BAK"; cp "$d/Wow.exe" "$d/reforged.exe"
run '\nQ\n\n' '' f
ok "BAK-Meldung" 'has f "Wow.exe.BAK fehlte"'
ok "keine ORI-Meldung" '! has f "Wow.exe.ORI fehlte" && ! has f "Original gesichert als"'
ok "BAK = aktuelle Exe" '[ "$(sha $d/Wow.exe.BAK)" = "$(sha $d/reforged.exe)" ]'
ok "schneller Weg (state)" 'has f "zuletzt von diesem Patcher erzeugte Datei"'
ok "Leerzeile nach Meldung" 'grep -A1 "Wow.exe.BAK fehlte" $d/out_f.txt | tail -1 | grep -qx "\s*"'
echo "F2: danach patchen -> BAK = vorheriger Stand, Option 2 wieder da"
unatt stony
run '\nQ\n\n' '' f3
ok "BAK = Reforged (vorher)" '[ "$(sha $d/Wow.exe.BAK)" = "$(sha $d/reforged.exe)" ]'
ok "Option 2 + Stand vor dem letzten Patchen" 'has f3 "2 = Vorherige Wow.exe" && has f3 "Wow.exe.BAK (Stand vor dem letzten Patchen)"'

echo "G: unbrauchbare Exe -> nichts anlegen"
newdir G "$ORI"; printf '\x90' | dd of="$d/Wow.exe" bs=1 seek=4096 conv=notrunc 2>/dev/null
run '\nQ\n\n' '' g
ok "Fehler" 'has g "\[FEHLER\]"'
ok "keine Sicherung" '[ ! -e $d/Wow.exe.ORI ] && [ ! -e $d/Wow.exe.BAK ]'

echo "H: ORI kann nicht angelegt werden (Ordner gleichen Namens) -> Hinweis, weiter"
newdir H "$OLD"; mkdir "$d/Wow.exe.ORI"
run '\nQ\n\n' '' h
ok "Hinweis" 'has h "HINWEIS: Sicherung konnte nicht angelegt werden"'
ok "BAK trotzdem" '[ "$(sha $d/Wow.exe.BAK)" = "$(sha $OLD)" ]'
ok "Startmenue da" 'has h "Was moechtest du tun"'
ok "Tasten [1/M/Q]" 'has h "\[1/M/Q\]"'

echo "I: Englisch"
newdir I "$OLD" en
run '\nQ\n\n' '' i
ok "ORI EN" 'has i "Wow.exe.ORI was missing and has been recreated"'
ok "BAK EN" 'has i "Wow.exe.BAK was missing - the current Wow.exe has been saved as the backup"'
ok "Abbruch EN" 'has i "Aborted. Wow.exe has not been modified."'
ok "BAK EN gleicher Stand" 'has i "Backup:   Wow.exe.BAK (same state as the current Wow.exe)"'

echo "J: Kleinschreibung wow.exe (Linux) -> wow.exe.ORI/.BAK"
newdir J "$OLD"; mv "$d/Wow.exe" "$d/wow.exe"
run '\nQ\n\n' '' j
ok "wow.exe.ORI + wow.exe.BAK" '[ "$(sha $d/wow.exe.ORI)" = $EXP ] && [ "$(sha $d/wow.exe.BAK)" = "$(sha $OLD)" ]'
ok "keine Wow.exe.* (gross)" '[ ! -e $d/Wow.exe.ORI ] && [ ! -e $d/Wow.exe.BAK ]'

echo "DONE fails=$fails"
