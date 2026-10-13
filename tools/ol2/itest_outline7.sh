#!/bin/bash
# Interaktive Tests fuer die Einstellungen der Umrandung (Nr. 68, J/N-Fragen).
# Aufruf: itest_outline.sh <Ordner mit apply_patches.ps1> <Lauf-Ordner (neu)>
SRC=$1; R=$2
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/pwsh/pwsh
EXP=aa63a5750d60ef16746c686b3d5e26876d98953eab08b1c026cd0faf78e88cb8
mkdir -p "$R" || exit 1
fails=0
ok() { if eval "$2"; then echo "  OK   $1"; else echo "  FAIL $1"; fails=$((fails+1)); fi; }
newdir() { d="$R/$1"; mkdir -p "$d"; cp "$SRC/apply_patches.ps1" "$d/"; cp "$ORI" "$d/Wow.exe"; printf "language=$2\n" > "$d/patcher_selection.ini"; }
run() { (cd "$d" && printf "$1" | "$PW" -NoProfile -File ./apply_patches.ps1 $2 > "$d/out_$3.txt" 2>&1; echo $? > "$d/rc_$3.txt"); }
rc() { cat "$d/rc_$1.txt"; }
has() { grep -q -- "$2" "$d/out_$1.txt"; }
cnt() { grep -c -- "$2" "$d/out_$1.txt"; }
sha() { sha256sum "$1" | cut -d' ' -f1; }
flags() { python3 -c "
import sys; d=open(sys.argv[1],'rb').read()
print(''.join('1' if d[o]==1 else ('-' if d[o]==0xCC else '?') for o in (0x2AABDF,0x2AAEAF,0x2AB22F,0x2AB28F,0x2AB33F,0x2AB25F)))" "$1"; }
ini() { grep '^value.outline=' "$d/patcher_selection.ini" | cut -d= -f2; }

echo "A: erstes Patchen, nur Nr. 68, Fragen mit J, ENTER, ungueltig, N, Y"
newdir A de
# ENTER Start, 1 Patch-Menue, N alle aus, 68 an, ENTER; Fragen: j, ENTER, x+J, n, y, ENTER; J bestaetigen; ENTER Ende
run '\n1\nN\n68\n\nj\ny\n\nx\nJ\nn\n\nJ\n\n' '' a
ok "Exit-Code 0" '[ "$(rc a)" = 0 ]'
ok "Kopf mit Vorschlag Standard (nur verdeckt)" 'has a "Umrandung fuer Ziel und Mouseover \[BETA\] (nur gxApi d3d9) \[ungetestet - Exe wird groesser\] -> Vorschlag: eigener Charakter nur verdeckt"'
ok "Frage nur verdeckt mit [J]" 'has a "Eigener Charakter nur dort umrandet, wo er verdeckt ist? (J/N) \[J\]"'
ok "Reihenfolge: Waende, nur verdeckt, immer umrandet, Gruppe, Schlachtzug, Gesinnung" 'grep -o "Durch Waende sichtbar\|nur dort umrandet\|Charakter immer umrandet\|5er-Gruppe immer\|Schlachtzug immer\|Gesinnungsfarbe statt" $d/out_a.txt | tr "\n" "|" | grep -q "^Durch Waende sichtbar|nur dort umrandet|Charakter immer umrandet|5er-Gruppe immer|5er-Gruppe immer|Schlachtzug immer|Gesinnungsfarbe statt|"'
ok "Frage Waende mit (J/N) [N]" 'has a "Durch Waende sichtbar? (unsicher, Bann-Gefahr) (J/N) \[N\]"'
ok "sechs Fragen + Wiederholung" '[ "$(cnt a "(J/N) \[")" = 7 ]'
ok "ungueltige Eingabe gemeldet" 'has a "Bitte J oder N eingeben"'
ok "Zusammenfassung in Kurzform" 'has a "- Umrandung fuer Ziel und Mouseover \[BETA\] (nur gxApi d3d9) \[ungetestet - Exe wird groesser\]: durch Waende, eigener Charakter nur verdeckt, 5er-Gruppe"'
ok "rote Warnung fuer durch Waende" 'has a "Nr. 68 Umrandung fuer Ziel und Mouseover \[BETA\] (nur gxApi d3d9): durch Waende"'
ok "Schalter in der Exe" '[ "$(flags $d/Wow.exe)" = "1-1-1-" ]'
ok "ini value.outline" '[ "$(ini)" = "walls,hidden,party" ]'
echo "B: Einstellungen aendern (Vorschlag = aktueller Stand)"
run '\n1\n\n\n\nj\nn\n\nj\nJ\n\n' '' b
ok "Exit-Code 0" '[ "$(rc b)" = 0 ]'
ok "Kopf aktuell" 'has b "-> aktuell: durch Waende, eigener Charakter nur verdeckt, 5er-Gruppe"'
ok "Vorschlag J bei Waende" 'has b "Durch Waende sichtbar? (unsicher, Bann-Gefahr) (J/N) \[J\]"'
ok "Wert aendern alt -> neu" 'has b "~ Umrandung fuer Ziel und Mouseover \[BETA\] (nur gxApi d3d9) \[ungetestet - Exe wird groesser\]: durch Waende, eigener Charakter nur verdeckt, 5er-Gruppe -> durch Waende, eigener Charakter nur verdeckt, eigener Charakter, Gesinnungsfarbe"'
ok "Schalter neu" '[ "$(flags $d/Wow.exe)" = "11--11" ]'
ok "ini neu" '[ "$(ini)" = "walls,hidden,self,react" ]'
echo "C: alles ENTER -> keine Aenderung"
run '\n1\n\n\n\n\n\n\n\n\n' '' c
ok "Keine Aenderung" 'has c "Keine Aenderung gegenueber der aktuellen Wow.exe"'
ok "Schalter gleich" '[ "$(flags $d/Wow.exe)" = "11--11" ]'
echo "C2: patcher_state.ini mit alter Reihenfolge (self vor hidden) -> keine Aenderung"
sed -i 's/^value.outline=.*/value.outline=walls,self,hidden,react/' "$d/patcher_state.ini"
run '\n1\n\n\n\n\n\n\n\n\n' '' c2
ok "Keine Aenderung trotz alter Reihenfolge" 'has c2 "Keine Aenderung gegenueber der aktuellen Wow.exe" && has c2 "Patches aktiv"'
echo "D: ohne patcher_state.ini -> Einstellungen aus der Exe erkannt"
rm -f "$d/patcher_state.ini"
run '\n1\n\n\n\n\n\n\n\n\n' '' d
ok "Patchstand aus der Exe" 'has d "Patchstand aus der Exe ermittelt"'
ok "aktuell aus der Exe" 'has d "-> aktuell: durch Waende, eigener Charakter nur verdeckt, eigener Charakter, Gesinnungsfarbe"'
ok "Keine Aenderung" 'has d "Keine Aenderung gegenueber der aktuellen Wow.exe"'
echo "E: alles N, keine rote Warnung"
run '\n1\n\nn\nn\nn\nn\nn\nn\nJ\n\n' '' e
ok "Wert aendern -> alles N" 'has e "-> alles N"'
ok "keine rote Warnung" '! has e "ACHTUNG - unsicher"'
ok "Schalter alle CC" '[ "$(flags $d/Wow.exe)" = "------" ]'
ok "ini none" '[ "$(ini)" = "none" ]'
echo "F: Nr. 68 abwaehlen -> Original"
run '\n1\n68\n\nJ\n\n' '' f
ok "Exit-Code 0" '[ "$(rc f)" = 0 ]'
ok "keine Fragen" '! has f "(J/N) \["'
ok "Original wiederhergestellt" '[ "$(sha $d/Wow.exe)" = $EXP ]'

echo "G: Englisch"
newdir G en
run '\n1\nN\n68\n\ny\n\n\n\n\n\nY\n\n' '' g
ok "Exit-Code 0" '[ "$(rc g)" = 0 ]'
ok "Frage englisch (Y/N) [N]" 'has g "Visible through walls? (unsafe, ban risk) (Y/N) \[N\]"'
ok "Kopf englisch" 'has g "-> suggestion: own character only hidden"'
ok "Zusammenfassung englisch" 'has g "Outline for target and mouseover \[BETA\] (gxApi d3d9 only) \[untested - exe grows\]: through walls, own character only hidden"'
ok "Schalter" '[ "$(flags $d/Wow.exe)" = "1---1-" ]'

echo "H: unbeaufsichtigt"
newdir H de
(cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select 68 > u1.txt 2>&1); echo "rc $?" > "$d/u1rc.txt"
ok "ohne gemerkten Wert: Standard nur verdeckt" '[ "$(flags $d/Wow.exe)" = "----1-" ] && grep -q "Umrandung.*: eigener Charakter nur verdeckt" $d/u1.txt'
printf 'language=de\nvalue.outline=React, self\n' > "$d/patcher_selection.ini"
(cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select 68 > u2.txt 2>&1)
ok "gemerkter Wert vereinheitlicht" '[ "$(flags $d/Wow.exe)" = "-1---1" ] && grep -q "eigener Charakter, Gesinnungsfarbe" $d/u2.txt'
printf 'language=de\nvalue.outline=bogus\n' > "$d/patcher_selection.ini"
(cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select 68 > u3.txt 2>&1); r3=$?
ok "ungueltiger gemerkter Wert: Abbruch" '[ $r3 = 1 ] && grep -q "Ungueltiger gemerkter Wert" $d/u3.txt && [ "$(flags $d/Wow.exe)" = "-1---1" ]'

echo "FAILS $fails"
