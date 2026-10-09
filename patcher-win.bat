@echo off
REM ============================================================
REM  St0nys-AIO-WoW-EXE-Patcher - Startdatei fuer Windows / Launcher
REM  Die gesamte Logik (Sprachwahl, Pruefungen, Patch-Auswahl,
REM  Backup, Patchen) steckt in apply_patches.ps1.
REM  Parameter werden durchgereicht, z.B.:
REM    patcher-win.bat -Language en -Select default
REM ============================================================
title St0nys-AIO-WoW-EXE-Patcher
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0apply_patches.ps1" %*
if errorlevel 9009 (
    echo.
    echo   [FEHLER/ERROR] PowerShell wurde nicht gefunden / PowerShell not found.
    pause
)
exit /b %errorlevel%
