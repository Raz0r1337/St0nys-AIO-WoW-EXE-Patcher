#!/bin/bash
cd "$(dirname "$0")"
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=../pwsh/pwsh
for s in $(seq 1 72) all; do
  rm -f Wow.exe.ORI Wow.exe.BAK patcher_state.ini patcher_selection.ini
  printf 'value.jump=-9.5\nvalue.doublejump=3\nvalue.clientversion=3.3.6\nvalue.clientbuild=12345\nvalue.clienttitle=TestTitle\nvalue.clientdate=2025-01-02 FR\nvalue.clienticon=test.ico\nlanguage=de\n' > patcher_selection.ini
  cp $ORI Wow.exe
  $PW -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select "$s" > out/$s.txt 2>&1
  echo "$s rc=$?"
  cp Wow.exe out/$s.exe; cp patcher_state.ini out/$s.ini 2>/dev/null
done
echo GENDONE
