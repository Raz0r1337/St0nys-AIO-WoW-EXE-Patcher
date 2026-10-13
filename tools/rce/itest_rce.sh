#!/bin/bash
# Test RCE-Fix v2 (Nr. 10): Wow.exe mit v1 (altes Skript) -> neues Skript erkennt Nr. 10,
# N laesst v1, J spielt v2 ein, Wiederherstellen (Zustandsdatei und Wasserzeichen), 10+11 ohne Ueberfluessig-Hinweis.
# Aufruf: itest_rce.sh <Ordner mit altem apply_patches.ps1> <Ordner mit neuem apply_patches.ps1> <Lauf-Ordner (neu)>
OLD=$1; NEW=$2; R=$3
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/pwsh/pwsh
EXP=aa63a5750d60ef16746c686b3d5e26876d98953eab08b1c026cd0faf78e88cb8
mkdir -p "$R" || exit 1
fails=0
ok() { if eval "$2"; then echo "  OK   $1"; else echo "  FAIL $1"; fails=$((fails+1)); fi; }
h() { sha256sum "$1" | cut -d' ' -f1; }
# Zustand der 8 Stellen: o = original, p = v2-Bytes, ? = etwas anderes; Reihenfolge P0, Robinsch, P1..P6
st() { python3 -c "
import sys; d=open(sys.argv[1],'rb').read()
P=[(0x2A7,'E0','C0'),(0x3D9D7C,'750A','9090'),(0x14A842,'3B3DB0A5BE00','83FF50909090'),(0x14A85C,'83F8027D1F','83F8507F5F'),(0x364D40,'74','EB'),(0x46B8E0,'558BEC','33C0C3'),(0x614A0,'558BEC','33C0C3'),(0x46AC43,'760C','9090')]
s=''
for o,a,b in P:
    c=d[o:o+len(a)//2].hex().upper(); s+='o' if c==a else ('p' if c==b else '?')
print(s)" "$1"; }
prep() {   # Ordner $1: Original, mit ALTEM Skript Auswahl $2 einspielen (v1), dann NEUES Skript hinlegen
  d="$R/$1"; mkdir -p "$d"; cp "$ORI" "$d/Wow.exe"; printf "language=de\n" > "$d/patcher_selection.ini"
  cp "$OLD/apply_patches.ps1" "$d/"; (cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Select $2 > out_old.txt 2>&1)
  cp "$NEW/apply_patches.ps1" "$d/"
}
run() { (cd "$d" && printf "$1" | "$PW" -NoProfile -File ./apply_patches.ps1 $2 > "$d/out_$3.txt" 2>&1; echo $? > "$d/rc_$3.txt"); }
has() { grep -q -- "$2" "$d/out_$1.txt"; }
rc() { cat "$d/rc_$1.txt"; }
ref() {   # frisch mit dem neuen Skript, Auswahl $2
  local r="$R/ref_$1"; mkdir -p "$r"; cp "$ORI" "$r/Wow.exe"; printf "language=de\n" > "$r/patcher_selection.ini"
  cp "$NEW/apply_patches.ps1" "$r/"; (cd "$r" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Select $2 > out.txt 2>&1); h "$r/Wow.exe"
}
HNEW=$(ref v2 10); HNEW11=$(ref v2w 10,11)
echo "== Referenz: neues Skript, Nr. 10 frisch"
ok "v2: alle 8 Stellen gepatcht" '[ "$(st $R/ref_v2/Wow.exe)" = "pppppppp" ]'
ok "v2: Name und Warnungen (orange riskant, nicht rot)" 'grep -q "Remote Code Execution Exploit Fix v2 \[BETA\] \[riskant - ingame ungetestet\]" $R/ref_v2/out.txt && grep -A3 "VORSICHT - riskant" $R/ref_v2/out.txt | grep -q "Nr. 10 Remote Code Execution Exploit Fix v2" && grep -A3 "im Spiel ungetestet" $R/ref_v2/out.txt | grep -q "Nr. 10 Remote Code Execution Exploit Fix v2" && ! grep -q "ACHTUNG - unsicher" $R/ref_v2/out.txt'
ok "v2: Groesse wie Original" '[ "$(stat -c %s $R/ref_v2/Wow.exe)" = "$(stat -c %s $ORI)" ]'
echo "== N: v1 bleibt"
prep n 10; HOLD=$(h "$d/Wow.exe")
ok "altes Skript: v1 (nur P0 + Robinsch)" '[ "$(st $d/Wow.exe)" = "ppoooooo" ] && [ "$HOLD" != "$HNEW" ]'
run '\nN\n' '-Language de -Select 10' n
ok "N: Nr. 10 erkannt (Zustandsdatei), gleiche Patches" 'has n "1 Patches aktiv" && has n "Gleiche Patches wie in der aktuellen Wow.exe." && has n "J = neu patchen"'
ok "N: Exit-Code 0, Wow.exe unveraendert" '[ "$(rc n)" = 0 ] && [ "$(h $d/Wow.exe)" = "$HOLD" ]'
echo "== J: v1 -> v2"
prep j 10; HOLD=$(h "$d/Wow.exe")
run '\nJ\nJ\n' '-Language de -Select 10' j
ok "J: Neu patchen (1), eingespielt" 'has j "Neu patchen (1):" && has j "\[+\] 1/1" && [ "$(rc j)" = 0 ]'
ok "J: Wow.exe = v2 frisch" '[ "$(h $d/Wow.exe)" = "$HNEW" ] && [ "$(st $d/Wow.exe)" = "pppppppp" ]'
ok "J: Wow.exe.BAK = v1" '[ "$(h $d/Wow.exe.BAK)" = "$HOLD" ]'
ok "J: Wow.exe.ORI = Original" '[ "$(h $d/Wow.exe.ORI)" = "$EXP" ]'
echo "== ohne Zustandsdatei (Wasserzeichen): v1 erkannt, J -> v2"
prep wm 10; rm -f "$d/patcher_state.ini"; HOLD=$(h "$d/Wow.exe")
run '\nJ\nJ\n' '-Language de -Select 10' wm
ok "WM: Patchstand aus der Exe (1 erkannt), gleiche Patches" 'has wm "1 Patches erkannt" && has wm "Gleiche Patches wie in der aktuellen Wow.exe."'
ok "WM: Wow.exe = v2 frisch, BAK = v1" '[ "$(h $d/Wow.exe)" = "$HNEW" ] && [ "$(h $d/Wow.exe.BAK)" = "$HOLD" ] && [ "$(rc wm)" = 0 ]'
echo "== v1 zuruecknehmen"
prep r1 10
(cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Select none > out_r1.txt 2>&1)
ok "R1: Zustandsdatei -> Original" '[ "$(h $d/Wow.exe)" = "$EXP" ]'
prep r2 10; rm -f "$d/patcher_state.ini" "$d/Wow.exe.ORI"
(cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Select none > out_r2.txt 2>&1)
ok "R2: Wasserzeichen ohne ORI -> Original" 'grep -q "1 Patches erkannt" $d/out_r2.txt && [ "$(h $d/Wow.exe)" = "$EXP" ]'
echo "== v1 + Nr. 11 dazu: v2 + Warden aus, kein Ueberfluessig-Hinweis"
prep w 10
(cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select 10,11 > out_w.txt 2>&1)
ok "W: kein Ueberfluessig-Hinweis" '! grep -q "ueberfluessig" $d/out_w.txt'
ok "W: rot nur Nr. 11, orange riskant Nr. 10" 'grep -A2 "ACHTUNG - unsicher" $d/out_w.txt | grep -q "Nr. 11 " && ! grep -A3 "ACHTUNG - unsicher" $d/out_w.txt | grep -q "Nr. 10 " && grep -A2 "VORSICHT - riskant" $d/out_w.txt | grep -q "Nr. 10 Remote Code Execution Exploit Fix v2" && grep -q "Im Zweifel die Regeln deines Servers pruefen." $d/out_w.txt'
ok "W: Wow.exe = frisch 10+11, Warden-Stelle gepatcht" '[ "$(h $d/Wow.exe)" = "$HNEW11" ] && [ "$(st $d/Wow.exe)" = "pppppppp" ] && python3 -c "import sys; d=open(sys.argv[1],\"rb\").read(); sys.exit(0 if d[0x3D9C5B:0x3D9C5D]==bytes([0x90,0x90]) else 1)" $d/Wow.exe'
(cd "$d" && rm -f patcher_state.ini && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Select none > out_w2.txt 2>&1)
ok "W: per Wasserzeichen zurueck zum Original" 'grep -q "2 Patches erkannt" $d/out_w2.txt && [ "$(h $d/Wow.exe)" = "$EXP" ]'
echo "== Englisch"
prep en 10
run '\nY\nY\n' '-Language en -Select 10' en
ok "EN: Name, Patch again, v2" 'has en "Remote code execution exploit fix v2 \[BETA\]" && has en "Patch again (1):" && [ "$(h $d/Wow.exe)" = "$HNEW" ]'
ok "EN: risky (orange)" 'has en "risky - untested ingame" && has en "CAUTION - risky: these patches get blocked on some servers:" && ! has en "WARNING - unsafe"'
echo "DONE fails=$fails"
