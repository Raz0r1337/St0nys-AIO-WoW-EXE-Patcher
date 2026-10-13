#!/bin/bash
# Reproduces the shimmer study (writes only inside agent_shimmer/).
#  1) simulation: straight edges, full figure under sub-pixel / 1 px / rotation / scale motion, error decomposition
#  2) shaders: psasm-style bytecode, structural ps_2_0 check, Wine D3DXAssembleShader/D3DXDisassembleShader/D3DDisassemble,
#     CreatePixelShader
#  3) Wine D3D9 (wined3d/llvmpipe, Xvfb :87): 68 frames x {old, tent, tsv = fix} x {no MSAA, 4x MSAA}, metrics, timing
#  4) generator fix: gen_fix/make_fix.py (diffs against snapshots of ol2/), build Wow.exe copies, unicorn test suites
set -e
A=$(cd "$(dirname "$0")" && pwd); cd "$A"
export PYTHONDONTWRITEBYTECODE=1
W() { WINEPREFIX="$A/wineprefix" DISPLAY=:87 WINEDEBUG=-all timeout 900 wine "$@"; }
pgrep -x Xvfb > /dev/null || { nohup Xvfb :87 -screen 0 1024x768x24 > xvfb.log 2>&1 & sleep 2; }
# 1) simulation
python3 edge_study.py 0 > edge_vertical.txt; python3 edge_study.py 0 --q > edge_vertical_q.txt
python3 edge_study.py 45 26.565 7.125 > edge_slanted.txt
python3 seq_study.py && python3 seq_study2.py && python3 seq_study3.py && python3 decomp_fix.py > decomp_fix.txt
python3 seq_report.py seq_results.json > seq_report.txt; python3 seq_report.py seq_results2.json >> seq_report.txt; python3 seq_report.py seq_results3.json >> seq_report.txt
python3 look_study.py > look_profiles.txt
# 2) shaders
python3 psasm_tent.py > shaders_disasm.txt
x86_64-w64-mingw32-gcc -O2 -o shadercheck.exe shadercheck.c -ld3d9 -lgdi32 -luser32
W shadercheck.exe tent_ps.bin tent_ps.asm > shadercheck_tent.txt 2>&1; W shadercheck.exe blur_soft_ps.bin blur_soft_ps.asm > shadercheck_vblur.txt 2>&1
# 3) Wine D3D9
python3 gen_frames.py
x86_64-w64-mingw32-gcc -O2 -Wall -Wno-misleading-indentation -o shimmer_test.exe shimmer_test.c -ld3d9 -lgdi32 -luser32
for m in 0 4; do for v in old tent tsv; do mkdir -p gpu/${v}_ms$m; W shimmer_test.exe $m $v gpu/${v}_ms$m > gpu/${v}_ms$m/run.log 2>&1; done; done
python3 gpu_check.py > gpu_check.txt; python3 gpu_metrics.py old_ms0 tent_ms0 tsv_ms0 old_ms4 tent_ms4 tsv_ms4 > gpu_metrics.txt
python3 look_images.py
mkdir -p gpu/bench; : > gpu/bench/bench2.txt
for res in "960 540" "1920 1080"; do for rep in 1 2 3 4; do for v in none old tent tsv; do W shimmer_test.exe 0 $v gpu/bench $res 150 | grep BENCH >> gpu/bench/bench2.txt; done; done; done
# 4) generator fix + emulation tests (base snapshot and fix)
cd gen_fix && python3 make_fix.py && python3 mkoutline10.py
mkdir -p base emu && cp outline10_base.py base/outline10.py && cp psasm_base.py base/psasm.py && cp test_outline10_base.py base/test_outline10.py
sed -i "s#^sys.path.insert(0, '.*scratchpad/ol2')#sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))#" base/test_outline10.py
python3 buildexe.py base emu/Wow_base.exe && python3 buildexe.py . emu/Wow_fix.exe
python3 base/test_outline10.py emu/Wow_base.exe > emu/test_base.log 2>&1 || true
python3 test_outline10.py emu/Wow_fix.exe > emu/test_fix.log 2>&1 || true
echo "unicorn base: $(grep -c '^OK' emu/test_base.log) OK, $(tail -1 emu/test_base.log) | fix: $(grep -c '^OK' emu/test_fix.log) OK, $(tail -1 emu/test_fix.log)"
