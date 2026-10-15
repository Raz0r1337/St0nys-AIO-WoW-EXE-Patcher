#!/bin/bash
# RCE-Fix v2 in Zweigen ohne "Neu patchen"-Abfrage: v1-Exe (altes Skript) wird vom neuen Skript als Nr. 10 erkannt,
# bleibt bei gleicher Auswahl unveraendert, laesst sich zuruecknehmen und ueber none -> 10 auf v2 bringen; Nr. 10+11; Englisch.
# Aufruf: itest_rce_old.sh <Ordner mit altem apply_patches.ps1> <Ordner mit neuem apply_patches.ps1> <Lauf-Ordner (neu)>
OLD=$1; NEW=$2; R=$3
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/pwsh/pwsh
EXP=aa63a5750d60ef16746c686b3d5e26876d98953eab08b1c026cd0faf78e88cb8
mkdir -p "$R" || exit 1
fails=0
ok() { if eval "$2"; then echo "  OK   $1"; else echo "  FAIL $1"; fails=$((fails+1)); fi; }
h() { sha256sum "$1" | cut -d' ' -f1; }
st() { python3 -c "
import sys; d=open(sys.argv[1],'rb').read()
P=[(0x2A7,'E0','C0'),(0x3D9D7C,'750A','9090'),(0x14A842,'3B3DB0A5BE00','83FF50909090'),(0x14A85C,'83F8027D1F','83F8507F5F'),(0x364D40,'74','EB'),(0x46B8E0,'558BEC','33C0C3'),(0x614A0,'558BEC','33C0C3'),(0x46AC43,'760C','9090')]
s=''
for o,a,b in P:
    c=d[o:o+len(a)//2].hex().upper(); s+='o' if c==a else ('p' if c==b else '?')
print(s)" "$1"; }
prep() { d="$R/$1"; mkdir -p "$d"; cp "$ORI" "$d/Wow.exe"; printf "language=de\n" > "$d/patcher_selection.ini"
  cp "$OLD/apply_patches.ps1" "$d/"; (cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Select $2 > out_old.txt 2>&1); cp "$NEW/apply_patches.ps1" "$d/"; }
run() { (cd "$d" && printf "$1" | "$PW" -NoProfile -File ./apply_patches.ps1 $2 > "$d/out_$3.txt" 2>&1; echo $? > "$d/rc_$3.txt"); }
has() { grep -q -- "$2" "$d/out_$1.txt"; }
rc() { cat "$d/rc_$1.txt"; }
r="$R/ref_v2"; mkdir -p "$r"; cp "$ORI" "$r/Wow.exe"; printf "language=de\n" > "$r/patcher_selection.ini"; cp "$NEW/apply_patches.ps1" "$r/"
(cd "$r" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select 10 > out.txt 2>&1); HNEW=$(h "$r/Wow.exe")
echo "== Referenz: neues Skript, Nr. 10 frisch"
ok "v2: alle 8 Stellen gepatcht, Groesse wie Original" '[ "$(st $r/Wow.exe)" = "pppppppp" ] && [ "$(stat -c %s $r/Wow.exe)" = "$(stat -c %s $ORI)" ]'
ok "v2: Name orange riskant, Hinweise, nicht rot" 'grep -q "Remote Code Execution Exploit Fix v2 \[BETA\] \[riskant - ingame ungetestet\]" $r/out.txt && grep -A2 "VORSICHT - riskant" $r/out.txt | grep -q "Nr. 10 " && grep -A2 "im Spiel ungetestet" $r/out.txt | grep -q "Nr. 10 " && ! grep -q "ACHTUNG - unsicher" $r/out.txt'
echo "== v1-Exe mit neuem Skript: gleiche Auswahl -> Keine Aenderung"
prep same 10; HOLD=$(h "$d/Wow.exe")
ok "altes Skript: v1 (P0 + Robinsch)" '[ "$(st $d/Wow.exe)" = "ppoooooo" ]'
run '\n' '-Language de -Select 10' same
ok "Nr. 10 erkannt (Zustandsdatei), Keine Aenderung, unveraendert" 'has same "1 Patches aktiv" && has same "Keine Aenderung gegenueber" && [ "$(rc same)" = 0 ] && [ "$(h $d/Wow.exe)" = "$HOLD" ]'
rm -f "$d/patcher_state.ini"; run '\n' '-Language de -Select 10' wm
ok "ohne Zustandsdatei: Patchstand aus der Exe (1 erkannt), Keine Aenderung" 'has wm "1 Patches erkannt" && has wm "Keine Aenderung gegenueber" && [ "$(h $d/Wow.exe)" = "$HOLD" ]'
echo "== v1 -> Original -> v2 (der Weg ohne Neu-patchen-Abfrage)"
run '' '-Unattended -Language de -Select none' r1
ok "none: Original" '[ "$(h $d/Wow.exe)" = "$EXP" ]'
run '' '-Unattended -Language de -Select 10' up
ok "10: Wow.exe = v2 frisch" '[ "$(h $d/Wow.exe)" = "$HNEW" ] && has up "\[+\] 1/1"'
prep r2 10; rm -f "$d/patcher_state.ini" "$d/Wow.exe.ORI"
run '' '-Unattended -Language de -Select none' r2
ok "Wasserzeichen ohne ORI: none -> Original" 'has r2 "1 Patches erkannt" && [ "$(h $d/Wow.exe)" = "$EXP" ]'
echo "== v1 + Nr. 11 dazu"
prep w 10; run '' '-Unattended -Language de -Select 10,11' w
ok "W: v2 + Warden-Stelle, kein Ueberfluessig-Hinweis, rot nur Nr. 11" '[ "$(st $d/Wow.exe)" = "pppppppp" ] && python3 -c "import sys; d=open(sys.argv[1],\"rb\").read(); sys.exit(0 if d[0x3D9C5B:0x3D9C5D]==bytes([0x90,0x90]) else 1)" $d/Wow.exe && ! has w "ueberfluessig" && grep -A2 "ACHTUNG - unsicher" $d/out_w.txt | grep -q "Nr. 11 " && ! grep -A3 "ACHTUNG - unsicher" $d/out_w.txt | grep -q "Nr. 10 "'
rm -f "$d/patcher_state.ini"; run '' '-Unattended -Language de -Select none' w2
ok "W: per Wasserzeichen (2 erkannt) zurueck zum Original" 'has w2 "2 Patches erkannt" && [ "$(h $d/Wow.exe)" = "$EXP" ]'
echo "== Englisch"
prep en 10; run '' '-Unattended -Language en -Select none' en0; run '' '-Unattended -Language en -Select 10' en
ok "EN: Name, risky (orange), v2" 'has en "Remote code execution exploit fix v2 \[BETA\] \[risky - untested ingame\]" && has en "CAUTION - risky: these patches get blocked on some servers:" && ! has en "WARNING - unsafe" && [ "$(h $d/Wow.exe)" = "$HNEW" ]'
echo "DONE fails=$fails"
