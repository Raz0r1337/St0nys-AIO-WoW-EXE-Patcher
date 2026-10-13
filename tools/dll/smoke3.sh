#!/bin/bash
# Smoke-Test fuer die DLL-riskant-Kennzeichnung. Aufruf: smoke.sh <worktree> <nr_awesome> <nr_wotlkext>
S=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad
WT=$1; ST=$2; AL=$3
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=$S/pwsh/pwsh
EXP=AA63A5750D60EF16746C686B3D5E26876D98953EAB08B1C026CD0FAF78E88CB8
D=$S/dll/sm3-$(basename $WT)
mkdir -p $D
cd $D || exit 1
fail=0

# 1) Bytetabelle neu erzeugen und mit der eingebauten vergleichen
cp $WT/apply_patches.ps1 bt.ps1
cp $ORI orig.exe
$PW -NoProfile -File ./bt.ps1 -BuildTable -Path ./orig.exe > bt.txt 2>&1
if cmp -s bt.ps1 $WT/apply_patches.ps1; then echo "table unchanged"; else echo "TABLE DIFFERS"; fail=1; fi

# 2) Laeufe
cp $WT/apply_patches.ps1 apply_patches.ps1
run() { # sel lang expectDll
  local s=$1 lang=$2 exp=$3
  rm -f Wow.exe.ORI Wow.exe.BAK patcher_state.ini patcher_selection.ini
  printf 'value.jump=-9.5\nvalue.doublejump=3\nvalue.clientversion=3.3.6\nvalue.clientbuild=12345\nvalue.clienttitle=TestTitle\nvalue.clientdate=2025-01-02 FR\nvalue.clienticon=test.ico\nvalue.bubblerange=150\nlanguage=%s\n' $lang > patcher_selection.ini
  cp $ORI Wow.exe
  $PW -NoProfile -File ./apply_patches.ps1 -Unattended -Language $lang -Select "$s" > out.txt 2>&1
  local rc=$?
  rm -f patcher_state.ini
  $PW -NoProfile -File ./apply_patches.ps1 -Unattended -Language $lang -Select "$s" > out2.txt 2>&1
  local det
  if [ "$s" = "none" ]; then det=$(grep -c "bereits original\|already original" out2.txt)
  else det=$(grep -c "Keine Aenderung\|No change compared" out2.txt); fi
  $PW -NoProfile -File ./apply_patches.ps1 -Unattended -Language $lang -Select none > out3.txt 2>&1
  local h=$(sha256sum Wow.exe | cut -d' ' -f1 | tr a-z A-Z)
  local ok=OK
  [ "$h" = "$EXP" ] || ok="$ok REVERT-FAIL"; [ "$det" = "1" ] || ok="$ok DETECT-FAIL"; [ $rc -eq 0 ] || ok="$ok RC=$rc"
  grep -q "HINWEIS: Die eingebaute" out.txt && ok="$ok TABLEWARN"
  # Startwarnung: 7 Zeilen, Zeile 5 neu
  if [ $lang = de ]; then
    grep -q "^  \[DLL riskant\] (Patch sicher, die DLL kann auf oeffentlichen Servern erkannt/blockiert werden)\.$" out.txt || ok="$ok NO-STARTWARN5"
    grep -q "^  Benutzung auf eigene Gefahr\.$" out.txt || ok="$ok NO-STARTWARN7"
    head="HINWEIS: Diese Patches laden eine DLL, die auf oeffentlichen Servern erkannt oder blockiert werden kann:"
    warn="Der Patch selbst ist sicher - die DLL nur auf Servern nutzen, die sie erlauben."
    tag="[DLL riskant]"
  else
    grep -q "^  \[DLL risky\] (the patch is safe, but the DLL may be detected/blocked on public servers)\.$" out.txt || ok="$ok NO-STARTWARN5"
    grep -q "^  Use at your own risk\.$" out.txt || ok="$ok NO-STARTWARN7"
    head="NOTE: These patches load a DLL that may be detected or blocked on public servers:"
    warn="The patch itself is safe - only use the DLL on servers that allow it."
    tag="[DLL risky]"
  fi
  local nh=$(grep -cF "  $head" out.txt) nw=$(grep -cF "  $warn" out.txt) nt=$(grep -F "$tag" out.txt | grep -v "^  \[DLL" | wc -l)
  if [ "$exp" = "0" ]; then
    [ $nh -eq 0 ] && [ $nw -eq 0 ] && [ $nt -eq 0 ] || ok="$ok UNEXPECTED-DLLWARN($nh/$nw/$nt)"
  else
    [ $nh -eq 1 ] && [ $nw -eq 1 ] || ok="$ok DLLWARN($nh/$nw)"
    local nl=$(grep -A3 -F "  $head" out.txt | grep -c "^    - ")
    [ $nl -eq $exp ] || ok="$ok DLLLIST($nl!=$exp)"
    [ $nt -ge $exp ] || ok="$ok TAGS($nt)"
  fi
  local aw=$(grep -c "AwesomeWotlkLib.dll" out.txt)
  case "$s" in
    reforged|default) [ $aw -eq 0 ] || ok="$ok AWESOME-IN-REFORGED($aw)";;
    billy|stony|all) [ $aw -ge 1 ] || ok="$ok AWESOME-MISSING";;
  esac
  echo "$lang $s $ok"
  [ "$ok" = "OK" ] || { fail=1; cp out.txt fail_${lang}_${s//,/_}.txt; }
}
run reforged de 0
run reforged en 0
run default de 0
run billy de 1
run billy en 1
run stony de $ST
run all de $AL
run all en $AL
run none de 0
echo "DONE fail=$fail"
