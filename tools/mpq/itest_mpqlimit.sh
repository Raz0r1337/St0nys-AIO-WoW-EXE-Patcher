#!/bin/bash
# MPQ-Limit-Fix im Patcher: allein (Bytes, Dateigroesse, PE-Kopf, Emulation des Blocks), mit allen Patches, nicht im
# Reforged-Preset, Erkennen und Zuruecknehmen mit und ohne Zustandsdatei.
# Aufruf: itest_mpqlimit.sh <Ordner mit apply_patches.ps1> <Lauf-Ordner> [Nr. des Patches, Vorgabe 22]
NEW=$1; R=$2; NR=${3:-22}
S=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=$S/pwsh/pwsh; T=$(cd "$(dirname "$0")" && pwd)
EXP=aa63a5750d60ef16746c686b3d5e26876d98953eab08b1c026cd0faf78e88cb8
rm -rf "$R"; mkdir -p "$R"; fails=0
ok() { if eval "$2"; then echo "  OK   $1"; else echo "  FAIL $1"; fails=$((fails+1)); fi; }
h() { sha256sum "$1" | cut -d' ' -f1; }
run() { d="$R/$1"; mkdir -p "$d"; [ -f "$d/Wow.exe" ] || cp "$ORI" "$d/Wow.exe"; cp "$NEW/apply_patches.ps1" "$S/ol2/suite14/test.ico" "$d/"
  [ -f "$d/patcher_selection.ini" ] || printf "value.jump=-9.5\nvalue.doublejump=3\nvalue.clientversion=3.3.6\nvalue.clientbuild=12345\nvalue.clienttitle=TestTitle\nvalue.clientdate=2025-01-02 13:14 FR\nvalue.clienticon=test.ico\nvalue.bubblerange=50\nvalue.outline=hidden,wallsgroup\nlanguage=de\n" > "$d/patcher_selection.ini"
  (cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select "$2" > "out_$3.txt" 2>&1; echo $? > "rc_$3.txt"); }
N=$(grep -c "^    @{ Id = " $NEW/apply_patches.ps1)
LX=$(python3 -c "import re,sys; s=open(sys.argv[1]).read(); print(re.findall(r\"(?m)^    @\{ Id = '([^']+)'\", s).index('mpqlimit')+1)" $NEW/apply_patches.ps1)
[ "$LX" = "$NR" ] || { echo "mpqlimit ist Nr. $LX, erwartet $NR"; exit 1; }
echo "== Nur Nr. $NR (MPQ-Limit-Fix)"
run solo $NR a
ok "Exit-Code 0, 1 Patch eingespielt" '[ "$(cat $R/solo/rc_a.txt)" = 0 ] && grep -q "\[+\] 1/1 - MPQ-Limit-Fix" $R/solo/out_a.txt'
ok "Warnungen: online und ingame ungetestet" 'grep -A3 "nicht auf oeffentlichen Servern getestet" $R/solo/out_a.txt | grep -q "Nr. $NR " && grep -A3 "im Spiel ungetestet" $R/solo/out_a.txt | grep -q "Nr. $NR "'
ok "Dateigroesse und PE-Kopf unveraendert" '[ $(stat -c%s $R/solo/Wow.exe) = $(stat -c%s $ORI) ] && cmp -s <(head -c 1024 $R/solo/Wow.exe) <(head -c 1024 $ORI)'
ok "nur der Block 0x5233-0x5278 geaendert (+ Wasserzeichen)" 'python3 -c "
import sys; a=open(sys.argv[1],\"rb\").read(); b=open(sys.argv[2],\"rb\").read()
d=[i for i in range(len(a)) if a[i]!=b[i] and not 0x72DE20<=i<0x72DE96]
sys.exit(0 if d and all(0x5233<=i<0x5279 for i in d) else 1)" $ORI $R/solo/Wow.exe'
ok "Emulation des Blocks (8 Faelle gegen das Original)" 'python3 -I $T/emu_mpq.py $ORI $R/solo/Wow.exe > $R/emu_solo.txt'
echo "== Alle Patches"
run all all a
ok "Exit-Code 0, alle $N Patches eingespielt" '[ "$(cat $R/all/rc_a.txt)" = 0 ] && grep -q "\[+\] $N/$N" $R/all/out_a.txt'
ok "Emulation des Blocks mit allen Patches" 'python3 -I $T/emu_mpq.py $ORI $R/all/Wow.exe > $R/emu_all.txt'
echo "== Reforged-Preset"
run ref reforged a
ok "Exit-Code 0, MPQ-Limit-Fix nicht dabei" '[ "$(cat $R/ref/rc_a.txt)" = 0 ] && ! grep -q "MPQ-Limit-Fix" $R/ref/out_a.txt'
echo "== Erkennen und Zuruecknehmen"
run solo none b
ok "Nr. $NR mit Zustandsdatei -> Original" '[ "$(h $R/solo/Wow.exe)" = "$EXP" ]'
run wl "$NR" a; rm -f "$R/wl/patcher_state.ini" "$R/wl/Wow.exe.ORI"; run wl none b
ok "ohne Zustandsdatei und ORI: 1 Patch erkannt, zurueck zum Original" 'grep -q "1 Patches erkannt" $R/wl/out_b.txt && [ "$(h $R/wl/Wow.exe)" = "$EXP" ]'
rm -f "$R/all/patcher_state.ini" "$R/all/Wow.exe.ORI"; run all none b
ok "alle $N ohne Zustandsdatei und ohne ORI: $N erkannt, zurueck zum Original" 'grep -q "$N Patches erkannt" $R/all/out_b.txt && [ "$(h $R/all/Wow.exe)" = "$EXP" ]'
run re "$NR" a; run re "$NR" b
ok "gleiche Auswahl nochmal: keine Aenderung (unattended)" 'grep -q "Keine Aenderung gegenueber" $R/re/out_b.txt && [ "$(cat $R/re/rc_b.txt)" = 0 ]'
echo "DONE fails=$fails"
