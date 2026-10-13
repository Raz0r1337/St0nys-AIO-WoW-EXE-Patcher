#!/bin/bash
# Test: "Keine Aenderung" -> trotzdem neu patchen (J) oder beenden (N).
# Aufruf: itest_redo.sh <Ordner mit altem apply_patches.ps1> <Ordner mit neuem apply_patches.ps1> <Lauf-Ordner (neu)>
OLD=$1; NEW=$2; R=$3
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/pwsh/pwsh
mkdir -p "$R" || exit 1
fails=0
ok() { if eval "$2"; then echo "  OK   $1"; else echo "  FAIL $1"; fails=$((fails+1)); fi; }
h() { sha256sum "$1" | cut -d' ' -f1; }
prep() {   # Ordner $1 mit Original, Sprache $2, mit ALTEM Skript Nr. 68 einspielen, dann NEUES Skript hinlegen
  d="$R/$1"; mkdir -p "$d"; cp "$ORI" "$d/Wow.exe"; printf "language=$2\n" > "$d/patcher_selection.ini"
  cp "$OLD/apply_patches.ps1" "$d/"; (cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Select 68 > out_old.txt 2>&1)
  cp "$NEW/apply_patches.ps1" "$d/"
}
run() { (cd "$d" && printf "$1" | "$PW" -NoProfile -File ./apply_patches.ps1 $2 > "$d/out_$3.txt" 2>&1; echo $? > "$d/rc_$3.txt"); }
# Referenz: frisch mit dem neuen Skript
d="$R/ref"; mkdir -p "$d"; cp "$ORI" "$d/Wow.exe"; printf "language=de\n" > "$d/patcher_selection.ini"; cp "$NEW/apply_patches.ps1" "$d/"
(cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Select 68 > out.txt 2>&1); HNEW=$(h "$d/Wow.exe")
echo "== N: beenden"
prep n de; HOLD=$(h "$d/Wow.exe")
ok "alter und neuer Stand unterscheiden sich" '[ "$HOLD" != "$HNEW" ]'
run '\n1\nN\n' '-Language de -Select 68' n
ok "Keine Aenderung erkannt" 'grep -q "Keine Aenderung gegenueber" "$d/out_n.txt"'
ok "Rueckfrage gestellt" 'grep -q "Trotzdem neu patchen? (J = neu patchen, N = beenden)" "$d/out_n.txt"'
ok "N: Exit-Code 0" '[ "$(cat $d/rc_n.txt)" = 0 ]'
ok "N: Wow.exe unveraendert" '[ "$(h $d/Wow.exe)" = "$HOLD" ]'
ok "N: nicht gepatcht" '! grep -q "\[+\]" "$d/out_n.txt"'
echo "== J: neu patchen"
prep j de; HOLD=$(h "$d/Wow.exe")
run '\n1\nJ\nJ\n' '-Language de -Select 68' j
ok "J: Liste Neu patchen (1)" 'grep -q "Neu patchen (1):" "$d/out_j.txt"'
ok "J: nicht Bleiben unveraendert" '! grep -q "Bleiben unveraendert aktiv" "$d/out_j.txt"'
ok "J: eingespielt" 'grep -q "\[+\] 1/1" "$d/out_j.txt" && grep -q "Gesamt: 1 Patches eingespielt" "$d/out_j.txt"'
ok "J: Exit-Code 0" '[ "$(cat $d/rc_j.txt)" = 0 ]'
ok "J: Wow.exe = frisch mit neuem Skript" '[ "$(h $d/Wow.exe)" = "$HNEW" ]'
ok "J: Wow.exe.BAK = vorheriger Stand" '[ "$(h $d/Wow.exe.BAK)" = "$HOLD" ]'
run '\n1\nN\n' '-Language de -Select 68' j2
ok "danach: wieder Keine Aenderung" 'grep -q "Keine Aenderung gegenueber" "$d/out_j2.txt" && [ "$(h $d/Wow.exe)" = "$HNEW" ]'
echo "== J, aber Bestaetigung N"
prep jn de; HOLD=$(h "$d/Wow.exe")
run '\n1\nJ\nN\n' '-Language de -Select 68' jn
ok "JN: abgebrochen (Exit-Code 2), Wow.exe unveraendert" '[ "$(cat $d/rc_jn.txt)" = 2 ] && [ "$(h $d/Wow.exe)" = "$HOLD" ]'
echo "== Englisch: Y"
prep en en
run '\n1\nY\nY\n' '-Language en -Select 68' en
ok "EN: Rueckfrage" 'grep -q "Patch again anyway? (Y = patch again, N = quit)" "$d/out_en.txt"'
ok "EN: Patch again (1)" 'grep -q "Patch again (1):" "$d/out_en.txt"'
ok "EN: Wow.exe = frisch mit neuem Skript" '[ "$(h $d/Wow.exe)" = "$HNEW" ]'
echo "== Unattended: keine Rueckfrage"
prep u de; HOLD=$(h "$d/Wow.exe")
run '' '-Unattended -Language de -Select 68' u
ok "U: Keine Aenderung, keine Rueckfrage, Exit-Code 0, unveraendert" 'grep -q "Keine Aenderung gegenueber" "$d/out_u.txt" && ! grep -q "Trotzdem neu patchen" "$d/out_u.txt" && [ "$(cat $d/rc_u.txt)" = 0 ] && [ "$(h $d/Wow.exe)" = "$HOLD" ]'
echo "FAILS $fails"
