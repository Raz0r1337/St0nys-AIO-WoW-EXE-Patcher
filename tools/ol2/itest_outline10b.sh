#!/bin/bash
# Interaktive Tests fuer die Umrandung (Nr. 68): sicherer Standard oder Umschalter (eigener Charakter, Gruppe/Schlachtzug, Durch Waende, Farbe).
# Aufruf: itest_outline10.sh <Ordner mit apply_patches.ps1> <Lauf-Ordner (neu)>
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
sha() { sha256sum "$1" | cut -d' ' -f1; }
# Schalter: Waende, selbst, Gruppe, Schlachtzug, nur verdeckt, Gesinnung, Waende nur Gruppe
flags() { python3 -c "
import sys; d=open(sys.argv[1],'rb').read()
print(''.join('1' if d[o]==1 else ('-' if d[o]==0xCC else '?') for o in (0x2AABDF,0x2AAEAF,0x2AB22F,0x2AB28F,0x2AB33F,0x2AB25F,0x2AB42F)))" "$1"; }
ini() { grep '^value.outline=' "$d/patcher_selection.ini" | cut -d= -f2; }
N='Umrandung fuer Ziel und Mouseover \[BETA\] (nur gxApi d3d9) \[ungetestet - Exe wird groesser\]'

echo "A: erstes Patchen, nur Nr. 68: ungueltig + Optionen, immer, ungueltig + 5er-Gruppe, alle durch Waende, ENTER"
newdir A de
run '\n1\nN\n68\n\nx\n2\n3\nx\n2\n3\n\nJ\n\n' '' a
ok "Exit-Code 0" '[ "$(rc a)" = 0 ]'
ok "Kopf mit Vorschlag" 'has a "$N -> Vorschlag: eigener Charakter nur verdeckt, durch Waende nur Gruppe/Schlachtzug"'
ok "sicherer Standard / Optionen, Vorschlag 1" 'has a "1 = sicheren Standard anwenden (eigener Charakter nur verdeckt, durch Waende nur Gruppe/Schlachtzug)" && has a "2 = Patch-Optionen aufrufen (Achtung: das kann den Patch unsicher machen)" && has a "Auswahl \[1\]"'
ok "ungueltige Wahl gemeldet" 'has a "Bitte eine Zahl von 1 bis 2 eingeben"'
ok "Hinweis Zahl eingeben" 'has a "Je Punkt eine Zahl eingeben, ENTER = Vorschlag in Klammern."'
ok "eigener Charakter [2]" 'has a "Eigener Charakter:" && has a "1 = aus   2 = nur wo verdeckt   3 = immer \[2\]"'
ok "Gruppe mit FPS-Hinweis [1]" 'has a "Gruppe / Schlachtzug immer umrandet:" && has a "(Schlachtzug kostet viele FPS)" && has a "1 = aus   2 = 5er-Gruppe   3 = ganzer Schlachtzug \[1\]"'
ok "Waende zweizeilig [2]" 'has a "^    1 = nie   2 = nur Gruppe/Schlachtzug$" && has a "3 = alle (unsicher, Bann-Gefahr) \[2\]"'
ok "Farbe [1]" 'has a "1 = Klassenfarbe   2 = Gesinnungsfarbe \[1\]"'
ok "ungueltige Eingabe gemeldet" 'has a "Bitte eine Zahl von 1 bis 3 eingeben"'
ok "Zusammenfassung" 'has a "$N: eigener Charakter, 5er-Gruppe, durch Waende"'
ok "rote Warnung durch Waende" 'has a "Nr. 68 Umrandung fuer Ziel und Mouseover \[BETA\] (nur gxApi d3d9): durch Waende"'
ok "Schalter" '[ "$(flags $d/Wow.exe)" = "111----" ]'
ok "ini" '[ "$(ini)" = "self,party,walls" ]'
echo "B: aendern: nur verdeckt, Gruppe bleibt, Waende nur Gruppe, Gesinnungsfarbe"
run '\n1\n\nE\n\n2\n\n2\n2\nJ\n\n' '' b
ok "Gleiche Patches: Abfrage vor den Werten" 'has b "Gleiche Patches wie in der aktuellen Wow.exe." && has b "Auswahl \\[E\\]"'
ok "Exit-Code 0" '[ "$(rc b)" = 0 ]'
ok "eigene Einstellung: Vorschlag 2" 'has b "Auswahl \[2\]"'
ok "Kopf aktuell" 'has b "$N -> aktuell: eigener Charakter, 5er-Gruppe, durch Waende"'
ok "Vorschlag aktueller Stand [3]" 'has b "3 = immer \[3\]"'
ok "alt -> neu" 'has b "~ $N: eigener Charakter, 5er-Gruppe, durch Waende -> eigener Charakter nur verdeckt, 5er-Gruppe, durch Waende nur Gruppe/Schlachtzug, Gesinnungsfarbe"'
ok "keine rote Warnung" '! has b "ACHTUNG - unsicher"'
ok "Schalter" '[ "$(flags $d/Wow.exe)" = "--1-111" ]'
ok "ini" '[ "$(ini)" = "hidden,party,wallsgroup,react" ]'
echo "C: alles ENTER -> keine Aenderung"
run '\n1\n\n\n\n\n\n\n\n' '' c
ok "Keine Aenderung (ENTER = E), keine zweite Frage" 'has c "Keine Aenderung gegenueber der aktuellen Wow.exe" && has c "Gleiche Patches wie" && ! has c "Trotzdem neu patchen"'
echo "C2: patcher_state.ini mit alter Reihenfolge und Doppelwahl (self+hidden) -> keine Aenderung"
sed -i 's/^value.outline=.*/value.outline=react,wallsgroup,self,party,hidden/' "$d/patcher_state.ini"
run '\n1\n\n\n\n\n\n\n\n' '' c2
ok "Keine Aenderung" 'has c2 "Keine Aenderung gegenueber der aktuellen Wow.exe" && has c2 "Patches aktiv"'
echo "D: ohne patcher_state.ini -> aus der Exe gelesen"
rm -f "$d/patcher_state.ini"
run '\n1\n\n\n\n\n\n\n\n' '' d
ok "aktuell aus der Exe" 'has d "$N -> aktuell: eigener Charakter nur verdeckt, 5er-Gruppe, durch Waende nur Gruppe/Schlachtzug, Gesinnungsfarbe"'
ok "Keine Aenderung" 'has d "Keine Aenderung gegenueber der aktuellen Wow.exe"'
echo "E: alles 1 -> alles aus"
run '\n1\n\nE\n\n1\n1\n1\n1\nJ\n\n' '' e
ok "-> alles aus" 'has e "-> alles aus"'
ok "Schalter alle CC" '[ "$(flags $d/Wow.exe)" = "-------" ]'
ok "ini none" '[ "$(ini)" = "none" ]'
echo "E2: 1 = sicheren Standard anwenden"
run '\n1\n\nE\n1\nJ\n\n' '' e2
ok "Vorschlag 2 (alles aus ist nicht der Standard)" 'has e2 "Auswahl \[2\]"'
ok "keine Umschalter" '! has e2 "Je Punkt eine Zahl"'
ok "-> sicherer Standard" 'has e2 "~ $N: alles aus -> eigener Charakter nur verdeckt, durch Waende nur Gruppe/Schlachtzug"'
ok "keine rote Warnung" '! has e2 "ACHTUNG - unsicher"'
ok "Schalter" '[ "$(flags $d/Wow.exe)" = "----1-1" ]'
ok "ini" '[ "$(ini)" = "hidden,wallsgroup" ]'
echo "E3: Standard ist aktiv -> Vorschlag 1, ENTER -> keine Aenderung"
run '\n1\n\n\n\n' '' e3
ok "Vorschlag 1" 'has e3 "Auswahl \[1\]"'
ok "Keine Aenderung" 'has e3 "Keine Aenderung gegenueber der aktuellen Wow.exe"'
echo "F: Nr. 68 abwaehlen -> Original"
run '\n1\n68\n\nJ\n\n' '' f
ok "keine Fragen" '! has f "Je Punkt eine Zahl" && ! has f "sicheren Standard"'
ok "Original" '[ "$(sha $d/Wow.exe)" = $EXP ]'

echo "G: Englisch"
newdir G en
run '\n1\nN\n68\n\n2\n\n\n3\n\nY\n\n' '' g
ok "Exit-Code 0" '[ "$(rc g)" = 0 ]'
ok "englisch: sicherer Standard / Optionen" 'has g "1 = apply the safe default (own character only hidden, through walls party/raid only)" && has g "2 = open the patch options (caution: this can make the patch unsafe)" && has g "Choice \[1\]"'
ok "englische Wahlen" 'has g "Own character:" && has g "1 = off   2 = only where hidden   3 = always \[2\]" && has g "3 = all (unsafe, ban risk) \[2\]"'
ok "Kopf englisch" 'has g "-> suggestion: own character only hidden, through walls party/raid only"'
ok "Zusammenfassung englisch" 'has g "Outline for target and mouseover \[BETA\] (gxApi d3d9 only) \[untested - exe grows\]: own character only hidden, through walls"'
ok "Schalter" '[ "$(flags $d/Wow.exe)" = "1---1--" ]'

echo "H: unbeaufsichtigt"
newdir H de
(cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select 68 > u1.txt 2>&1)
ok "ohne Wert: sicherer Standard" '[ "$(flags $d/Wow.exe)" = "----1-1" ] && grep -q "Umrandung.*: eigener Charakter nur verdeckt, durch Waende nur Gruppe/Schlachtzug" $d/u1.txt'
printf 'language=de\nvalue.outline=React, self\n' > "$d/patcher_selection.ini"
(cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select 68 > u2.txt 2>&1)
ok "gemerkter Wert vereinheitlicht" '[ "$(flags $d/Wow.exe)" = "-1---1-" ] && grep -q "eigener Charakter, Gesinnungsfarbe" $d/u2.txt'
printf 'language=de\nvalue.outline=self,hidden,party,raid,walls,wallsgroup\n' > "$d/patcher_selection.ini"
(cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select 68 > u3.txt 2>&1)
ok "Doppelwahlen: Prio (nur verdeckt, Schlachtzug, alle)" '[ "$(flags $d/Wow.exe)" = "1--11--" ] && grep -q "eigener Charakter nur verdeckt, Schlachtzug, durch Waende" $d/u3.txt'
printf 'language=de\nvalue.outline=bogus\n' > "$d/patcher_selection.ini"
(cd "$d" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select 68 > u4.txt 2>&1); r4=$?
ok "ungueltiger Wert: Abbruch" '[ $r4 = 1 ] && grep -q "Ungueltiger gemerkter Wert" $d/u4.txt && grep -q "wallsgroup" $d/u4.txt'

echo "FAILS $fails"
