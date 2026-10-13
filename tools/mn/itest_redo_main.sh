#!/bin/bash
# main: gleiche Patches wie in der Wow.exe -> gleich nach der Auswahl: J = neu patchen (aktuelle Einstellungen), E = Einstellungen, N = beenden.
# Aufruf: itest_redo_main.sh <Ordner mit altem Skript> <Ordner mit neuem Skript> <Lauf-Ordner (neu)>
OLD=$1; NEW=$2; R=$3
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/pwsh/pwsh
mkdir -p "$R" || exit 1
fails=0
ok() { if eval "$2"; then echo "  OK   $1"; else echo "  FAIL $1"; fails=$((fails+1)); fi; }
h() { sha256sum "$1" | cut -d' ' -f1; }
prep() {   # $1 Ordner, $2 Sprache, $3 Auswahl, $4 Zusatzzeile fuer die ini
  d="$R/$1"; mkdir -p "$d"; cp "$ORI" "$d/Wow.exe"; printf "language=$2\n$4" > "$d/patcher_selection.ini"
  cp "$OLD/apply_patches.ps1" "$d/"; (cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Select $3 > out_old.txt 2>&1)
  cp "$NEW/apply_patches.ps1" "$d/"
}
run() { (cd "$d" && printf "$1" | "$PW" -NoProfile -File ./apply_patches.ps1 $2 > "$d/out_$3.txt" 2>&1; echo $? > "$d/rc_$3.txt"); }
has() { grep -q -- "$2" "$d/out_$1.txt"; }
rc() { cat "$d/rc_$1.txt"; }
VQ='Werte fuer die gewaehlten Patches'
B=77   # Sprechblasen-Reichweite (fragt den Wert ab)
echo "== N: beenden ohne Werte-Abfrage"
prep n de $B 'value.bubblerange=150\n'; HOLD=$(h "$d/Wow.exe")
run '\nN\n' "-Language de -Select $B" n
ok "Abfrage nach der Auswahl" 'has n "Gleiche Patches wie in der aktuellen Wow.exe." && has n "J = neu patchen mit den aktuellen Einstellungen" && has n "E = Einstellungen aendern" && has n "N = beenden" && has n "Auswahl \[E\]"'
ok "N: keine Werte-Abfrage, Exit-Code 0, unveraendert" '! has n "$VQ" && [ "$(rc n)" = 0 ] && [ "$(h $d/Wow.exe)" = "$HOLD" ] && ! has n "\[+\]"'
echo "== J: neu patchen, Wert der Exe bleibt (gemerkter Wert inzwischen 200)"
prep j de $B 'value.bubblerange=150\n'; HOLD=$(h "$d/Wow.exe")
sed -i 's/^value.bubblerange=.*/value.bubblerange=200/' "$d/patcher_selection.ini"
run '\nJ\nJ\n' "-Language de -Select $B" j
ok "J: keine Werte-Abfrage, Liste Neu patchen mit 150" '! has j "$VQ" && has j "Neu patchen (1):" && has j "+ Sprechblasen.*: 150"'
ok "J: eingespielt, Exit-Code 0, gleiche Exe wie vorher, BAK = vorheriger Stand" 'has j "\[+\] 1/1" && [ "$(rc j)" = 0 ] && [ "$(h $d/Wow.exe)" = "$HOLD" ] && [ "$(h $d/Wow.exe.BAK)" = "$HOLD" ]'
echo "== E: Einstellungen, ENTER -> Keine Aenderung, keine zweite Frage"
run '\nE\n\n' "-Language de -Select $B" e
ok "E: Werte-Abfrage, Keine Aenderung, Exit-Code 0" 'has e "$VQ" && has e "Keine Aenderung gegenueber" && [ "$(rc e)" = 0 ] && [ "$(grep -c "Gleiche Patches wie" $d/out_e.txt)" = 1 ]'
echo "== Patch ohne Einstellungen (Nr. 1): nur J/N, ENTER = N"
prep o de 1 ''; HOLD=$(h "$d/Wow.exe")
run '\n\n' "-Language de -Select 1" o
ok "ohne Werte: kein E, Vorschlag N, beendet" 'has o "Gleiche Patches wie" && ! has o "E = Einstellungen" && has o "Auswahl \[N\]" && [ "$(rc o)" = 0 ] && [ "$(h $d/Wow.exe)" = "$HOLD" ]'
run '\nJ\nJ\n' "-Language de -Select 1" o2
ok "ohne Werte: J patcht neu" 'has o2 "Neu patchen (1):" && has o2 "\[+\] 1/1" && [ "$(rc o2)" = 0 ]'
echo "== Englisch"
prep en en $B 'value.bubblerange=150\n'
run '\nY\nY\n' "-Language en -Select $B" en
ok "EN: Abfrage und Patch again" 'has en "Same patches as in the current Wow.exe." && has en "S = change settings" && has en "Choice \[S\]" && has en "Patch again (1):"'
echo "== Unattended"
prep u de $B 'value.bubblerange=150\n'
run '' "-Unattended -Language de -Select $B" u
ok "U: Keine Aenderung, keine Rueckfrage" 'has u "Keine Aenderung gegenueber" && ! has u "Gleiche Patches wie" && [ "$(rc u)" = 0 ]'
echo "FAILS $fails"
