#!/bin/bash
cd "$(dirname "$0")"
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/pwsh/pwsh
for i in $(seq 1 88) all; do
  rm -f Wow.exe.ORI Wow.exe.BAK patcher_state.ini patcher_selection.ini
  printf 'value.jump=-11.25\nvalue.doublejump=1\nvalue.clientversion=3.3.6\nvalue.clientbuild=12345\nvalue.clienttitle=TestTitle\nvalue.clientdate=2025-01-02 03:04:05\nvalue.clienticon=test.ico\nvalue.bubblerange=50\nlanguage=de\n' > patcher_selection.ini
  cp $ORI Wow.exe
  $PW -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select "$i" > log_$i.txt 2>&1
  echo "$i rc=$? size=$(stat -c %s Wow.exe)"
  mv Wow.exe p_$i.exe
done
echo GENDONE
