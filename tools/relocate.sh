#!/bin/bash
# Passt die fest eingetragenen Pfade der Sitzung, in der die Werkzeuge
# entstanden sind, an einen neuen Ort an.
# Aufruf: relocate.sh <Ordner mit einer Kopie von tools> <Original-Wow.exe> [pwsh]
set -e
OLD_S=/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad
OLD_ORI=/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe
[ $# -ge 2 ] || { echo "Aufruf: $0 <Ordner mit einer Kopie von tools> <Original-Wow.exe> [pwsh]"; exit 1; }
DIR=$(cd "$1" && pwd)
ORI=$(readlink -f "$2")
PW=${3:-pwsh}
[ -f "$ORI" ] || { echo "Wow.exe nicht gefunden: $2"; exit 1; }
n=0
while IFS= read -r f; do
  sed -i -e "s#$OLD_S/pwsh/pwsh#$PW#g" -e "s#$OLD_S/ol2/exe14/Wow.exe.ORI#$ORI#g" \
         -e "s#$OLD_ORI#$ORI#g" -e "s#$OLD_S#$DIR#g" "$f"
  n=$((n+1))
done < <(grep -rlI --exclude=relocate.sh -e "$OLD_S" -e "$OLD_ORI" "$DIR" || true)
echo "$n Dateien angepasst."
