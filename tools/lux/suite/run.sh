#!/bin/bash
cd "$(dirname "$0")"
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/pwsh/pwsh
EXP=AA63A5750D60EF16746C686B3D5E26876D98953EAB08B1C026CD0FAF78E88CB8
fail=0
sels="all none billy stony reforged default"
for i in $(seq 1 89); do sels="$sels $i"; done
sels="$sels 4,57,63 4,63 57,58,59 51,64,80,57 1,2,3,4,5,6,7,8,9,10,11,12,13,14 25,26,28,29,30,32,33,34,35,36,37,38,39,40 26,28,29,30 2,45 44,45,46 18,41 41,43 79,80,81 86,87 22,23 34,35,36,37 28,30 28,29,30 5,6 5,30 12,28,30 6,7,8,9 5,6,7,8,9 73,74,75,76 53 7,9,28,30 4,64,7,9 1,2,3,4,5,6,7,8,9 71,72,73,74,75,76,77,78,79 9,52,65,66,76,82 76,28,30 65,66 74,75 29,30 77 76,77 77,78,79 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,28,29,30,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89 9,52,65,66,67,77,83 67,77,83 65,67 67 30 30,32 28,29,30,32 9,53,66,67,77,83 27 27,30 27,32 27,30,32 1-89 26,27,28 31 30,31 31,32 27,31 27,30,31,32 28,29,30,31,32 27,28,29,30,31,32 31,83 9,31"
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
