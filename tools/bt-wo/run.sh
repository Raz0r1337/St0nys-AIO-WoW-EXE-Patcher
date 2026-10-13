#!/bin/bash
cd "$(dirname "$0")"
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=../pwsh/pwsh
EXP=AA63A5750D60EF16746C686B3D5E26876D98953EAB08B1C026CD0FAF78E88CB8
fail=0
sels="all none billy stony reforged default"
for i in $(seq 1 88); do sels="$sels $i"; done
sels="$sels 4,56,62 4,62 56,57,58 50,63,79,56 1,2,3,4,5,6,7,8,9,10,11,12,13,14 25,26,28,29,30,31,32,33,34,35,36,37,38,39 26,28,29,30 2,44 43,44,45 18,40 40,42 78,79,80 85,86 22,23 33,34,35,36 28,30 28,29,30 5,6 5,30 12,28,30 6,7,8,9 5,6,7,8,9 72,73,74,75 52 7,9,28,30 4,63,7,9 1,2,3,4,5,6,7,8,9 70,71,72,73,74,75,76,77,78 9,51,64,65,75,81 75,28,30 64,65 73,74 29,30 76 75,76 76,77,78 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88 9,51,64,65,66,76,82 66,76,82 64,66 66 30 30,31 28,29,30,31 9,52,65,66,76,82 27 27,30 27,31 27,30,31 1-88 26,27,28"
for s in $sels; do
  rm -f Wow.exe.ORI Wow.exe.BAK patcher_state.ini patcher_selection.ini
  printf 'value.jump=-9.5\nvalue.doublejump=3\nvalue.clientversion=3.3.6\nvalue.clientbuild=12345\nvalue.clienttitle=TestTitle\nvalue.clientdate=2025-01-02 FR\nvalue.clienticon=test.ico\nvalue.bubblerange=150\nlanguage=de\n' > patcher_selection.ini
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
