#!/bin/bash
# Luxvelum-Lader im Patcher: Bytes und Startkette (Emulation) allein, mit Lexara, mit allen DLL-Ladern, mit dem
# Reforged-Preset (enthaelt ihn) und mit allen Patches; Luxvelums Pruefstellen unberuehrt (ausser lightstay); Build-Datum laesst
# den PE-Zeitstempel mit Luxvelum in Ruhe; Erkennen und Zuruecknehmen.
# Aufruf: itest_luxvelum.sh <Ordner mit apply_patches.ps1> <Lauf-Ordner> [Nr. des Patches, Vorgabe 32]
NEW=$1; R=$2; NR=${3:-32}
S=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=$S/pwsh/pwsh; T=$(cd "$(dirname "$0")" && pwd)
EXP=aa63a5750d60ef16746c686b3d5e26876d98953eab08b1c026cd0faf78e88cb8
rm -rf "$R"; mkdir -p "$R"; fails=0
ok() { if eval "$2"; then echo "  OK   $1"; else echo "  FAIL $1"; fails=$((fails+1)); fi; }
h() { sha256sum "$1" | cut -d' ' -f1; }
run() { d="$R/$1"; mkdir -p "$d"; [ -f "$d/Wow.exe" ] || cp "$ORI" "$d/Wow.exe"; cp "$NEW/apply_patches.ps1" "$S/ol2/suite14/test.ico" "$d/"
  [ -f "$d/patcher_selection.ini" ] || printf "value.jump=-9.5\nvalue.doublejump=3\nvalue.clientversion=3.3.6\nvalue.clientbuild=12345\nvalue.clienttitle=TestTitle\nvalue.clientdate=2025-01-02 13:14 FR\nvalue.clienticon=test.ico\nvalue.bubblerange=50\nvalue.outline=${OUTLINE:-hidden,wallsgroup}\nlanguage=de\n" > "$d/patcher_selection.ini"
  (cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select "$2" > "out_$3.txt" 2>&1; echo $? > "rc_$3.txt"); }
num() { python3 - "$NEW/apply_patches.ps1" "$@" <<'EOF'
import sys, re
s = open(sys.argv[1], encoding='ascii').read()
ids = re.findall(r"(?m)^    @\{ Id = '([^']+)'", s)
want = []
for a in sys.argv[2:]:
    if a == 'reforged': want += re.findall(r"'(\w+)'", re.search(r'(?m)^\$PRESET_REFORGED = @\((.*?)\n\)', s, re.S).group(1))
    else: want.append(a)
print(','.join(str(ids.index(i) + 1) for i in dict.fromkeys(want)))
EOF
}
ts() { python3 -c "import sys,struct; d=open(sys.argv[1],'rb').read(); e=struct.unpack_from('<I',d,0x3C)[0]; print('%08X %08X' % (struct.unpack_from('<I',d,e+8)[0], struct.unpack_from('<I',d,e+52)[0]))" "$1"; }   # TimeDateStamp, ImageBase
LX=$(num luxvelum); LEX=$(num lexara); DLLS=$(num wowoptimize awesome wotlkext lexara lux luxvelum voicedll); REFN=$(num reforged | tr , '\n' | wc -l); CD=$(num clientdate)
[ "$LX" = "$NR" ] || { echo "luxvelum ist Nr. $LX, erwartet $NR"; exit 1; }
echo "== Nur Nr. $NR (Luxvelum-Lader)"
run solo $NR a
ok "Exit-Code 0, 1 Patch eingespielt" '[ "$(cat $R/solo/rc_a.txt)" = 0 ] && grep -q "\[+\] 1/1 - Luxvelum.dll beim Start laden" $R/solo/out_a.txt'
ok "Warnungen: nur DLL riskant (Patch sicher)" '! grep -q "nicht auf oeffentlichen Servern getestet" $R/solo/out_a.txt && ! grep -q "im Spiel ungetestet" $R/solo/out_a.txt && grep -A3 "DLL, die auf" $R/solo/out_a.txt | grep -q "Nr. $NR "'
ok "Dateigroesse gleich, PE-Kopf gleich (TimeDateStamp 4C2452FE, ImageBase 00400000)" '[ $(stat -c%s $R/solo/Wow.exe) = $(stat -c%s $ORI) ] && cmp -s <(head -c 1024 $R/solo/Wow.exe) <(head -c 1024 $ORI) && [ "$(ts $R/solo/Wow.exe)" = "4C2452FE 00400000" ]'
ok "nur Aufruf am Einstiegspunkt, Code-Luecke und Namens-Luecke geaendert (+ Wasserzeichen)" 'python3 -c "
import sys; a=open(sys.argv[1],\"rb\").read(); b=open(sys.argv[2],\"rb\").read()
d=[i for i in range(len(a)) if a[i]!=b[i] and not 0x72DE20<=i<0x72DE96]
sys.exit(0 if d and all(0x401<=i<0x405 or 0x2D2480<=i<0x2D2490 or 0x2D1463<=i<0x2D1470 for i in d) else 1)" $ORI $R/solo/Wow.exe'
ok "Startkette: Luxvelum.dll" 'python3 -I $T/emu_entry.py $R/solo/Wow.exe Luxvelum.dll'
ok "Startkette ohne DLL laeuft durch" 'python3 -I $T/emu_entry.py $R/solo/Wow.exe Luxvelum.dll fehlt'
ok "Luxvelums Pruefstellen unberuehrt" 'python3 -I $T/check_sites.py $ORI $R/solo/Wow.exe > $R/sites_solo.txt'
echo "== Mit Lexara (Nr. $LEX)"
run lex "$LEX,$NR" a
ok "Exit-Code 0" '[ "$(cat $R/lex/rc_a.txt)" = 0 ]'
ok "Startkette: erst Luxvelum.dll, dann Lexara.dll" 'python3 -I $T/emu_entry.py $R/lex/Wow.exe Luxvelum.dll,Lexara.dll'
echo "== Alle DLL-Lader ($DLLS)"
run dlls "$DLLS" a
ok "Exit-Code 0" '[ "$(cat $R/dlls/rc_a.txt)" = 0 ]'
ok "Startkette: Luxvelum, Lexara, wow_optimize-Thread, LuxShoulderCam, voice.dll" 'python3 -I $T/emu_entry.py $R/dlls/Wow.exe Luxvelum.dll,Lexara.dll,THREAD,LuxShoulderCam.dll,voice.dll'
ok "Startkette ohne DLLs laeuft durch" 'python3 -I $T/emu_entry.py $R/dlls/Wow.exe Luxvelum.dll,Lexara.dll,THREAD,LuxShoulderCam.dll,voice.dll fehlt'
echo "== Reforged-Preset (enthaelt Luxvelum)"
run ref reforged a
ok "Exit-Code 0, $REFN Patches inkl. Luxvelum-Lader" '[ "$(cat $R/ref/rc_a.txt)" = 0 ] && grep -q "\[+\] $REFN/$REFN" $R/ref/out_a.txt && grep -q "\[+\] [0-9]*/$REFN - Luxvelum.dll beim Start laden" $R/ref/out_a.txt'
ok "Startkette: Luxvelum, Lexara, LuxShoulderCam" 'python3 -I $T/emu_entry.py $R/ref/Wow.exe Luxvelum.dll,Lexara.dll,LuxShoulderCam.dll'
ok "Luxvelums Pruefstellen unberuehrt (lightstay ist nicht im Preset)" 'python3 -I $T/check_sites.py $ORI $R/ref/Wow.exe > $R/sites_ref.txt'
echo "== Alle Patches"
run all all a
ok "Exit-Code 0, alle Patches eingespielt" '[ "$(cat $R/all/rc_a.txt)" = 0 ] && grep -q "\[+\] $(grep -c "^    @{ Id = " $NEW/apply_patches.ps1)/$(grep -c "^    @{ Id = " $NEW/apply_patches.ps1)" $R/all/out_a.txt'
ok "Startkette mit allen Patches" 'python3 -I $T/emu_entry.py $R/all/Wow.exe Luxvelum.dll,Lexara.dll,THREAD,LuxShoulderCam.dll,voice.dll'
ok "Luxvelums Pruefstellen: nur lightstay (0x81E548, gewollt)" 'python3 -I $T/check_sites.py $ORI $R/all/Wow.exe 0x81E548 > $R/sites_all.txt && grep -q "erlaubt 0x0081E548" $R/sites_all.txt'
ok "Build-Datum mit Luxvelum: PE-Zeitstempel bleibt 4C2452FE, Datumstext geaendert" '[ "$(ts $R/all/Wow.exe)" = "4C2452FE 00400000" ] && [ "$(dd if=$R/all/Wow.exe bs=1 skip=$((0x5F39F4)) count=11 2>/dev/null)" = "Jan 02 2025" ]'
OUTLINE=self,raid,walls,react run allopt all a
ok "alle Patches, Umrandung mit allen Optionen: Pruefstellen nur lightstay" '[ "$(cat $R/allopt/rc_a.txt)" = 0 ] && python3 -I $T/check_sites.py $ORI $R/allopt/Wow.exe 0x81E548 > $R/sites_allopt.txt'
echo "== Build-Datum ohne Luxvelum"
run cd "$CD" a
ok "PE-Zeitstempel geaendert, Datumstext geaendert" '[ "$(cat $R/cd/rc_a.txt)" = 0 ] && [ "$(ts $R/cd/Wow.exe | cut -d" " -f1)" != "4C2452FE" ] && [ "$(dd if=$R/cd/Wow.exe bs=1 skip=$((0x5F39F4)) count=11 2>/dev/null)" = "Jan 02 2025" ]'
run cdlx "$CD,$NR" a
ok "mit Luxvelum: Zeitstempel bleibt, Datumstext geaendert" '[ "$(cat $R/cdlx/rc_a.txt)" = 0 ] && [ "$(ts $R/cdlx/Wow.exe)" = "4C2452FE 00400000" ] && [ "$(dd if=$R/cdlx/Wow.exe bs=1 skip=$((0x5F39F4)) count=11 2>/dev/null)" = "Jan 02 2025" ]'
echo "== Erkennen und Zuruecknehmen"
run solo none b
ok "Nr. $NR mit Zustandsdatei -> Original" '[ "$(h $R/solo/Wow.exe)" = "$EXP" ]'
run wl "$NR" a; rm -f "$R/wl/patcher_state.ini" "$R/wl/Wow.exe.ORI"; run wl none b
ok "ohne Zustandsdatei und ORI: 1 Patch erkannt, zurueck zum Original" 'grep -q "1 Patches erkannt" $R/wl/out_b.txt && [ "$(h $R/wl/Wow.exe)" = "$EXP" ]'
rm -f "$R/lex/patcher_state.ini" "$R/lex/Wow.exe.ORI"; run lex none b
ok "Lexara + Luxvelum ohne Zustandsdatei und ORI: 2 erkannt, zurueck zum Original" 'grep -q "2 Patches erkannt" $R/lex/out_b.txt && [ "$(h $R/lex/Wow.exe)" = "$EXP" ]'
rm -f "$R/all/patcher_state.ini" "$R/all/Wow.exe.ORI"; run all none b
N=$(grep -c "^    @{ Id = " $NEW/apply_patches.ps1)
ok "alle $N ohne Zustandsdatei und ohne ORI: $N erkannt, zurueck zum Original" 'grep -q "$N Patches erkannt" $R/all/out_b.txt && [ "$(h $R/all/Wow.exe)" = "$EXP" ]'
run re "$NR" a; run re "$NR" b
ok "gleiche Auswahl nochmal: keine Aenderung (unattended)" 'grep -q "Keine Aenderung gegenueber" $R/re/out_b.txt && [ "$(cat $R/re/rc_b.txt)" = 0 ]'
echo "DONE fails=$fails"
