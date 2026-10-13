#!/bin/bash
# Test: gleiche Patches wie in der Wow.exe -> gleich nach der Auswahl (vor den Werten):
# J = neu patchen mit den aktuellen Einstellungen, E = Einstellungen aendern, N = beenden.
# Aufruf: itest_redo2.sh <Ordner mit altem apply_patches.ps1> <Ordner mit neuem apply_patches.ps1> <Lauf-Ordner (neu)>
OLD=$1; NEW=$2; R=$3
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/pwsh/pwsh
mkdir -p "$R" || exit 1
fails=0
ok() { if eval "$2"; then echo "  OK   $1"; else echo "  FAIL $1"; fails=$((fails+1)); fi; }
h() { sha256sum "$1" | cut -d' ' -f1; }
flags() { python3 -c "
import sys; d=open(sys.argv[1],'rb').read()
print(''.join('1' if d[o]==1 else ('-' if d[o]==0xCC else '?') for o in (0x2AABDF,0x2AAEAF,0x2AB22F,0x2AB28F,0x2AB33F,0x2AB25F,0x2AB42F)))" "$1"; }
prep() {   # Ordner $1 mit Original, Sprache $2, Wert $3 (leer = Standard): mit ALTEM Skript Nr. 68 einspielen, dann NEUES Skript hinlegen
  d="$R/$1"; mkdir -p "$d"; cp "$ORI" "$d/Wow.exe"; printf "language=$2\n" > "$d/patcher_selection.ini"
  [ -n "$3" ] && printf "value.outline=$3\n" >> "$d/patcher_selection.ini"
  cp "$OLD/apply_patches.ps1" "$d/"; (cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Select 68 > out_old.txt 2>&1)
  cp "$NEW/apply_patches.ps1" "$d/"
}
run() { (cd "$d" && printf "$1" | "$PW" -NoProfile -File ./apply_patches.ps1 $2 > "$d/out_$3.txt" 2>&1; echo $? > "$d/rc_$3.txt"); }
has() { grep -q -- "$2" "$d/out_$1.txt"; }
rc() { cat "$d/rc_$1.txt"; }
ref() {   # frisch mit dem neuen Skript, Wert $2
  local r="$R/ref_$1"; mkdir -p "$r"; cp "$ORI" "$r/Wow.exe"; printf "language=de\n" > "$r/patcher_selection.ini"
  [ -n "$2" ] && printf "value.outline=$2\n" >> "$r/patcher_selection.ini"
  cp "$NEW/apply_patches.ps1" "$r/"; (cd "$r" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Select 68 > out.txt 2>&1); h "$r/Wow.exe"
}
HNEW=$(ref std ''); HNEW2=$(ref val 'self,party,react')
VQ='sicheren Standard anwenden'   # Text der Werte-Abfrage von Nr. 68
echo "== N: beenden, ohne Werte-Abfrage"
prep n de ''; HOLD=$(h "$d/Wow.exe")
ok "alter und neuer Stand unterscheiden sich" '[ "$HOLD" != "$HNEW" ]'
run '\nN\n' '-Language de -Select 68' n
ok "Abfrage gleich nach der Auswahl" 'has n "Gleiche Patches wie in der aktuellen Wow.exe." && has n "J = neu patchen mit den aktuellen Einstellungen" && has n "E = Einstellungen aendern" && has n "N = beenden" && has n "Auswahl \[E\]"'
ok "Hinweis Neu patchen" 'has n "Neu patchen spielt alle gewaehlten Patches frisch auf das Original"'
ok "N: keine Werte-Abfrage" '! has n "$VQ"'
ok "N: Exit-Code 0, Wow.exe unveraendert, nicht gepatcht" '[ "$(rc n)" = 0 ] && [ "$(h $d/Wow.exe)" = "$HOLD" ] && ! has n "\[+\]"'
echo "== J: neu patchen mit den aktuellen Einstellungen"
prep j de ''; HOLD=$(h "$d/Wow.exe")
run '\nJ\nJ\n' '-Language de -Select 68' j
ok "J: keine Werte-Abfrage" '! has j "$VQ"'
ok "J: Liste Neu patchen (1) mit Wert" 'has j "Neu patchen (1):" && has j "+ Umrandung fuer Ziel.*: eigener Charakter nur verdeckt, durch Waende nur Gruppe/Schlachtzug"'
ok "J: nicht Bleiben unveraendert, nicht Keine Aenderung" '! has j "Bleiben unveraendert aktiv" && ! has j "Keine Aenderung gegenueber"'
ok "J: eingespielt, Exit-Code 0" 'has j "\[+\] 1/1" && has j "Gesamt: 1 Patches eingespielt" && [ "$(rc j)" = 0 ]'
ok "J: Wow.exe = frisch mit neuem Skript" '[ "$(h $d/Wow.exe)" = "$HNEW" ]'
ok "J: Wow.exe.BAK = vorheriger Stand" '[ "$(h $d/Wow.exe.BAK)" = "$HOLD" ]'
echo "== J mit eigener Einstellung (gemerkter Wert inzwischen anders): Einstellung der Wow.exe bleibt"
prep jv de 'self,party,react'; FOLD=$(flags "$d/Wow.exe")
sed -i 's/^value.outline=.*/value.outline=hidden/' "$d/patcher_selection.ini"
run '\nJ\nJ\n' '-Language de -Select 68' jv
ok "JV: Einstellung bleibt (Schalter wie vorher)" '[ "$(flags $d/Wow.exe)" = "$FOLD" ] && [ "$FOLD" = "-11--1-" ] && has jv "+ Umrandung fuer Ziel.*: eigener Charakter, 5er-Gruppe, Gesinnungsfarbe"'
ok "JV: Wow.exe = frisch mit neuem Skript und diesem Wert" '[ "$(h $d/Wow.exe)" = "$HNEW2" ]'
echo "== J, aber Bestaetigung N"
prep jn de ''; HOLD=$(h "$d/Wow.exe")
run '\nJ\nN\n' '-Language de -Select 68' jn
ok "JN: abgebrochen (Exit-Code 2), Wow.exe unveraendert" '[ "$(rc jn)" = 2 ] && [ "$(h $d/Wow.exe)" = "$HOLD" ]'
echo "== E: Einstellungen aendern, nichts geaendert -> Keine Aenderung, keine zweite Frage"
prep e de ''; HOLD=$(h "$d/Wow.exe")
run '\nE\n1\n' '-Language de -Select 68' e
ok "E: Werte-Abfrage kommt" 'has e "$VQ"'
ok "E: Keine Aenderung, Exit-Code 0, unveraendert" 'has e "Keine Aenderung gegenueber" && [ "$(rc e)" = 0 ] && [ "$(h $d/Wow.exe)" = "$HOLD" ]'
ok "E: keine zweite Frage" '[ "$(grep -c "Gleiche Patches wie" $d/out_e.txt)" = 1 ] && ! has e "Trotzdem neu patchen"'
echo "== ENTER = E"
run '\n\n\n' '-Language de -Select 68' ent
ok "ENTER: Werte-Abfrage, dann Keine Aenderung" 'has ent "$VQ" && has ent "Keine Aenderung gegenueber" && [ "$(rc ent)" = 0 ]'
echo "== ungueltige Taste -> erneut gefragt"
run '\nX\nN\n' '-Language de -Select 68' x
ok "X: zweimal gefragt, dann beendet" '[ "$(grep -o "Auswahl \[E\]" $d/out_x.txt | wc -l)" = 2 ] && [ "$(rc x)" = 0 ] && ! has x "$VQ"'
echo "== Englisch: Y und S"
prep en en ''
run '\nY\nY\n' '-Language en -Select 68' en
ok "EN: Abfrage" 'has en "Same patches as in the current Wow.exe." && has en "Y = patch again with the current settings" && has en "S = change settings" && has en "N = quit" && has en "Choice \[S\]"'
ok "EN: Patch again (1), frisch" 'has en "Patch again (1):" && [ "$(h $d/Wow.exe)" = "$HNEW" ]'
run '\nS\n1\n' '-Language en -Select 68' en2
ok "EN: S -> Werte, dann No change" 'has en2 "apply the safe default" && has en2 "No change compared to the current Wow.exe" && [ "$(rc en2)" = 0 ]'
echo "== Auswahl geaendert (Patch dazu): keine Abfrage"
prep add de ''
run '\n1\nJ\n\n' '-Language de -Select 68,1' add
ok "ADD: keine Gleiche-Patches-Abfrage, Werte-Abfrage kommt" '! has add "Gleiche Patches wie" && has add "$VQ" && has add "Neu einspielen (1):"'
echo "== Unattended: keine Rueckfrage"
prep u de ''; HOLD=$(h "$d/Wow.exe")
run '' '-Unattended -Language de -Select 68' u
ok "U: Keine Aenderung, keine Rueckfrage, Exit-Code 0, unveraendert" 'has u "Keine Aenderung gegenueber" && ! has u "Gleiche Patches wie" && [ "$(rc u)" = 0 ] && [ "$(h $d/Wow.exe)" = "$HOLD" ]'
echo "FAILS $fails"
