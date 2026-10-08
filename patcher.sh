#!/bin/sh
# ============================================================
#  St0nys-AIO-WoW-EXE-Patcher - Startdatei fuer Linux
#  Die gesamte Logik (Sprachwahl, Pruefungen, Patch-Auswahl,
#  Backup, Patchen) steckt in apply_patches.ps1. Noetig ist
#  PowerShell 7 (Befehl "pwsh"), Wine wird nicht gebraucht.
#  Parameter werden durchgereicht, z.B.:
#    ./patcher.sh -Language en -Select default
# ============================================================
cd "$(dirname "$0")" || exit 1
if ! command -v pwsh >/dev/null 2>&1; then
    echo ""
    echo "  [FEHLER/ERROR] PowerShell 7 (pwsh) wurde nicht gefunden / PowerShell 7 (pwsh) not found."
    echo "  Installation: docs/README.de.md / docs/README.md (Linux)"
    exit 1
fi
exec pwsh -NoProfile -File ./apply_patches.ps1 "$@"
