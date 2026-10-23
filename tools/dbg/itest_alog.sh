#!/bin/bash
# Asset-Debug-Log im Patcher: Byte-Vergleich mit make_debug_exe_st0ny.py (FineWolfs Skript plus Fehler-Log; nur
# dieser Patch, Original-Exe),
# Emulation der Hooks (allein und mit allen Patches), Erkennen und Zuruecknehmen ueber Zustandsdatei und Tabelle.
# Aufruf: itest_alog.sh <Ordner mit apply_patches.ps1> <Lauf-Ordner> [Nr. des Patches, Vorgabe 94]
NEW=$1; R=$2; NR=${3:-94}
N=$(grep -c "^    @{ Id = " "$NEW/apply_patches.ps1")   # Anzahl aller Patches
S=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=$S/pwsh/pwsh; T=$(cd "$(dirname "$0")" && pwd)
EXP=aa63a5750d60ef16746c686b3d5e26876d98953eab08b1c026cd0faf78e88cb8
rm -rf "$R"; mkdir -p "$R"; fails=0
ok() { if eval "$2"; then echo "  OK   $1"; else echo "  FAIL $1"; fails=$((fails+1)); fi; }
h() { sha256sum "$1" | cut -d' ' -f1; }
run() { d="$R/$1"; mkdir -p "$d"; [ -f "$d/Wow.exe" ] || cp "$ORI" "$d/Wow.exe"; cp "$NEW/apply_patches.ps1" "$S/ol2/suite14/test.ico" "$d/"
  [ -f "$d/patcher_selection.ini" ] || printf 'value.jump=-9.5\nvalue.doublejump=3\nvalue.clientversion=3.3.6\nvalue.clientbuild=12345\nvalue.clienttitle=TestTitle\nvalue.clientdate=2025-01-02 FR\nvalue.clienticon=test.ico\nvalue.bubblerange=50\nlanguage=de\n' > "$d/patcher_selection.ini"
  (cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select "$2" > "out_$3.txt" 2>&1; echo $? > "rc_$3.txt"); }
echo "== Nur Nr. $NR auf der Original-Exe = make_debug_exe_st0ny.py"
run solo $NR a
mkdir -p "$R/fw"; cp "$ORI" "$R/fw/wow.exe"; (cd "$R/fw" && python3 -I "$T/make_debug_exe_st0ny.py" wow.exe -o wow_debug.exe > fw.txt 2>&1)
ok "Patcher Exit-Code 0, 1 Patch eingespielt" '[ "$(cat $R/solo/rc_a.txt)" = 0 ] && grep -q "\[+\] 1/1 - Debug- und Fehler-Log" $R/solo/out_a.txt'
ok "byte-gleich mit make_debug_exe_st0ny.py bis auf das Wasserzeichen (0x72DE20-0x72DE95)" 'python3 -c "
import sys; a=open(sys.argv[1],\"rb\").read(); b=open(sys.argv[2],\"rb\").read()
sys.exit(0 if len(a)==len(b) and all(a[i]==b[i] or 0x72DE20<=i<0x72DE96 for i in range(len(a))) else 1)" $R/solo/Wow.exe $R/fw/wow_debug.exe'
ok "Warnungen: online und ingame ungetestet, Exe wird groesser" 'grep -A3 "nicht auf oeffentlichen Servern getestet" $R/solo/out_a.txt | grep -q "Nr. $NR " && grep -A3 "im Spiel ungetestet" $R/solo/out_a.txt | grep -q "Nr. $NR " && grep -A3 "haengen eine Sektion an" $R/solo/out_a.txt | grep -q "Nr. $NR "'
ok "Emulation der Hooks (allein)" 'python3 -I $T/emu_alog.py $R/solo/Wow.exe > $R/emu_solo.txt 2>&1'
echo "== Alle $N Patches"
run all all a
ok "Exit-Code 0, $N Patches eingespielt" '[ "$(cat $R/all/rc_a.txt)" = 0 ] && grep -q "\[+\] $N/$N" $R/all/out_a.txt'
ok "Emulation der Hooks (mit allen Patches)" 'python3 -I $T/emu_alog.py $R/all/Wow.exe > $R/emu_all.txt 2>&1'
echo "== Erkennen und Zuruecknehmen"
run solo none b
ok "Nr. $NR mit Zustandsdatei -> Original" '[ "$(h $R/solo/Wow.exe)" = "$EXP" ]'
run wm $NR a; rm -f "$R/wm/patcher_state.ini"; run wm none b
ok "ohne Zustandsdatei: 1 Patch erkannt (Tabelle), zurueck zum Original" 'grep -q "1 Patches erkannt" $R/wm/out_b.txt && [ "$(h $R/wm/Wow.exe)" = "$EXP" ]'
rm -f "$R/all/patcher_state.ini" "$R/all/Wow.exe.ORI"; run all none b
ok "alle $N ohne Zustandsdatei und ohne ORI: $N erkannt, zurueck zum Original" 'grep -q "$N Patches erkannt" $R/all/out_b.txt && [ "$(h $R/all/Wow.exe)" = "$EXP" ]'
run re $NR a; run re $NR b
ok "gleiche Auswahl nochmal: keine Aenderung (unattended)" 'grep -q "Keine Aenderung gegenueber" $R/re/out_b.txt && [ "$(cat $R/re/rc_b.txt)" = 0 ]'
echo "DONE fails=$fails"
