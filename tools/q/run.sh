#!/bin/bash
cd "$(dirname "$0")"
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=../pwsh/pwsh
EXP=AA63A5750D60EF16746C686B3D5E26876D98953EAB08B1C026CD0FAF78E88CB8
fail=0
sels="all none billy stony"
for i in $(seq 1 73); do sels="$sels $i"; done
sels="$sels 4,49,55 4,55 49,50,51 44,56,67,49 1-10 21-33 22,23,24 2,38 37,38,39 14,34 34,36 65,66,67 72,73 18,19 27,28,29,30"
for s in 72 71,72,73,74 reforged billy stony all; do
  rm -f Wow.exe.ORI Wow.exe.BAK patcher_state.ini patcher_selection.ini
  printf 'value.jump=-9.5\nvalue.doublejump=3\nvalue.clientversion=3.3.6\nvalue.clientbuild=12345\nvalue.clienttitle=TestTitle\nvalue.clientdate=2025-01-02 FR\nvalue.clienticon=test.ico\nlanguage=de\n' > patcher_selection.ini
  cp $ORI Wow.exe
  $PW -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select "$s" > out.txt 2>&1
  rc=$?
  size=$(stat -c %s Wow.exe)
  # detection: drop state, rerun with same selection -> expect no change
  rm -f patcher_state.ini
  $PW -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select "$s" > out2.txt 2>&1
  det="?"
  if [ "$s" = "none" ]; then det=$(grep -c "bereits original" out2.txt)
  else det=$(grep -c "Keine Aenderung" out2.txt); fi
  # revert via state file path (state exists now from out2 run)
  $PW -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select none > out3.txt 2>&1
  h=$(sha256sum Wow.exe | cut -d' ' -f1 | tr a-z A-Z)
  ok=OK; [ "$h" = "$EXP" ] || ok=REVERT-FAIL; [ "$det" = "1" ] || ok="$ok DETECT-FAIL"; [ $rc -eq 0 ] || ok="$ok RC=$rc"
  grep -q "HINWEIS: Die eingebaute" out.txt && ok="$ok TABLEWARN"
  echo "$s size=$size $ok"
  [ "$ok" = "OK" ] || { fail=1; cp out.txt fail_$s.txt; cp out2.txt fail2_$s.txt; }
done
echo DONE fail=$fail
