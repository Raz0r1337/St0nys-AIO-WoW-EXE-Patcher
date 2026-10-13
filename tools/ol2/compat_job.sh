#!/bin/bash
# Ein Kompatibilitaetslauf: Exe mit altem Skript (Commit $1) patchen, mit neuem Skript zuruecknehmen.
# Aufruf: compat_job.sh <commit> <Lauf-Ordner> <neues Skript> <Auswahl> <Repo>
c=$1; R=$2; NEW=$3; SEL=$4; REPO=$5
ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
PW=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/pwsh/pwsh
ICO=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/bt-rmo/test.ico
EXP=aa63a5750d60ef16746c686b3d5e26876d98953eab08b1c026cd0faf78e88cb8
INI='language=de\nvalue.jump=-9.5\nvalue.doublejump=3\nvalue.clientversion=3.3.6\nvalue.clientbuild=12345\nvalue.clienttitle=TestTitle\nvalue.clientdate=2025-01-02 FR\nvalue.clienticon=test.ico\nvalue.bubblerange=150\n'
g="$R/$c-$SEL/gen"; k="$R/$c-$SEL/chk"; mkdir -p "$g" "$k"
git -C "$REPO" show "$c:apply_patches.ps1" | sed 's/$/\r/' > "$g/apply_patches.ps1"
cp "$ICO" "$g/"; cp "$ORI" "$g/Wow.exe"; printf "$INI" > "$g/patcher_selection.ini"
(cd "$g" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select "$SEL" > gen.txt 2>&1); grc=$?
gh=$(sha256sum "$g/Wow.exe" | cut -d' ' -f1)
cp "$g/Wow.exe" "$NEW" "$ICO" "$k/"; printf "$INI" > "$k/patcher_selection.ini"
(cd "$k" && "$PW" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select none > chk.txt 2>&1); krc=$?
kh=$(sha256sum "$k/Wow.exe" | cut -d' ' -f1)
res=OK
[ $grc -eq 0 ] || res="GEN-RC=$grc"
[ "$gh" = "$EXP" ] && res="$res GEN-UNPATCHED"
[ "$kh" = "$EXP" ] || res="$res REVERT-FAIL"
[ $krc -eq 0 ] || res="$res CHK-RC=$krc"
grep -q "Patchstand aus der Exe ermittelt" "$k/chk.txt" || res="$res NOSCAN"
oh=$(sha256sum "$k/Wow.exe.ORI" 2>/dev/null | cut -d' ' -f1); [ "$oh" = "$EXP" ] || res="$res ORI-BAD"
bh=$(sha256sum "$k/Wow.exe.BAK" 2>/dev/null | cut -d' ' -f1); [ "$bh" = "$gh" ] || res="$res BAK-BAD"
d=$(git -C "$REPO" log -1 --format='%ad' --date=format:'%Y-%m-%d %H:%M' "$c")
echo "$c $d $SEL ${gh:0:12} $res"
rm -f "$g/Wow.exe" "$k/Wow.exe" "$k/Wow.exe.ORI" "$k/Wow.exe.BAK" "$g/Wow.exe.ORI" "$g/Wow.exe.BAK"
