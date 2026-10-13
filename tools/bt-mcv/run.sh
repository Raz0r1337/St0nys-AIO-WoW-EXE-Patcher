#!/bin/bash
cd "$(dirname "$0")"
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=../pwsh/pwsh
EXP=AA63A5750D60EF16746C686B3D5E26876D98953EAB08B1C026CD0FAF78E88CB8
fail=0
sels="all none billy stony reforged default"
for i in $(seq 1 84); do sels="$sels $i"; done
sels="$sels 4,53,59 4,59 53,54,55 47,60,76,53 1,2,3,4,5,6,7,8,9,10,11,12,13,14 25,26,27,28,29,30,31,32,33,34,35,36 26,27,28 2,41 40,41,42 18,37 37,39 75,76,77 81,82 22,23 30,31,32,33 27 27,28 5,6 5 12,27 6,7,8,9 5,6,7,8,9 69,70,71,72 49 7,9,27 4,60,7,9 1,2,3,4,5,6,7,8,9 67,68,69,70,71,72,73,74,75 9,48,61,62,72,78 72,27 61,62 70,71 28 73 72,73 73,74,75 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84 9,48,61,62,63,73 63,73 61,63 63 9,49,62,63,73 1-84 27,28,29 28,29 78,79"
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
