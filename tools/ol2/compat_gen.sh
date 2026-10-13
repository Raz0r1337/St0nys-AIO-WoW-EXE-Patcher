#!/bin/bash
# Exe mit altem Skript (Commit $1) erzeugen, nur patcher_state.ini + Skript + Ausgabe behalten.
# Aufruf: compat_gen.sh <commit> <Lauf-Ordner> <Auswahl> <Repo>
c=$1; R=$2; SEL=$3; REPO=$4
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/pwsh/pwsh
ICO=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/bt-rmo/test.ico
INI='language=de\nvalue.jump=-9.5\nvalue.doublejump=3\nvalue.clientversion=3.3.6\nvalue.clientbuild=12345\nvalue.clienttitle=TestTitle\nvalue.clientdate=2025-01-02 FR\nvalue.clienticon=test.ico\nvalue.bubblerange=150\n'
g="$R/$c-$SEL"; mkdir -p "$g"
git -C "$REPO" show "$c:apply_patches.ps1" | sed 's/$/\r/' > "$g/apply_patches.ps1"
cp "$ICO" "$g/"; cp "$ORI" "$g/Wow.exe"; printf "$INI" > "$g/patcher_selection.ini"
(cd "$g" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select "$SEL" > gen.txt 2>&1); echo $? > "$g/rc.txt"
sha256sum "$g/Wow.exe" | cut -d' ' -f1 > "$g/hash.txt"
rm -f "$g/Wow.exe" "$g/Wow.exe.ORI" "$g/Wow.exe.BAK"
