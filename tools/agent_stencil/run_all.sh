#!/bin/bash
# Reproduces all results of agent_stencil (nothing outside this directory is written).
#  1) D3D9 test on Wine (wined3d/llvmpipe): stenciltest.exe without and with 4x MSAA -> out_ms0/, out_ms4/
#  2) contact sheets out_ms0/sheet*.png
#  3) proposed generator fix (U bit, recommended) and two-pass alternative, built into a Wow.exe copy and run
#     through the adapted unicorn test suites -> emu/test_fix.log, emu/test_fix_r1.log (baseline: emu/test_base.log)
set -e
A=$(cd "$(dirname "$0")" && pwd); S=$(dirname "$A")
cd "$A"
export PYTHONDONTWRITEBYTECODE=1
x86_64-w64-mingw32-gcc -O2 -Wall -Wno-unused-variable -o stenciltest.exe stenciltest.c -ld3d9 -lgdi32 -luser32
pgrep -f "Xvfb :87" > /dev/null || { nohup Xvfb :87 -screen 0 1024x768x24 > xvfb.log 2>&1 & sleep 2; }
for m in 0 4; do
  mkdir -p out_ms$m
  WINEPREFIX="$A/wineprefix" DISPLAY=:87 WINEDEBUG=-all timeout 600 wine stenciltest.exe $m out_ms$m > out_ms$m/run.log 2> out_ms$m/err.log
  echo "stenciltest ms=$m: $(tail -1 out_ms$m/run.log)"
done
python3 -I -B sheet.py out_ms0
mkdir -p emu
python3 -B buildexe.py outline10 emu/Wow_base.exe
python3 -B "$S/ol2/test_outline10.py" emu/Wow_base.exe > emu/test_base.log 2>&1 || true
python3 -B mkfix.py && python3 -B mkps.py && python3 -B mkoutline10_fix.py
python3 -B buildexe.py outline10_fix emu/Wow_fix.exe && python3 -B mktest.py
python3 -B test_fix.py emu/Wow_fix.exe > emu/test_fix.log 2>&1 || true
python3 -B mkfix_r1.py && python3 -B buildexe.py outline10_fix_r1 emu/Wow_fix_r1.exe && python3 -B mktest_r1.py
python3 -B test_fix_r1.py emu/Wow_fix_r1.exe > emu/test_fix_r1.log 2>&1 || true
for f in base fix fix_r1; do echo "unicorn $f: $(grep -c '^OK' emu/test_$f.log) OK, $(tail -1 emu/test_$f.log)"; done
