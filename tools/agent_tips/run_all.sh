#!/bin/bash
# Reproduces the agent_tips study and fix (writes only inside agent_tips/).
#  1) simulation (tiplib/tipstudy/tipstudy2/lookstudy): thin features (ears, spikes, thin bars) under sub-pixel motion,
#     straight-edge pumping per angle, look (line thickness, glow) - no MSAA ('bin') and 4x MSAA ('ms4')
#  2) Wine D3D9 (wined3d/llvmpipe, Xvfb :93, own wineprefix): old vs new pipeline, metrics, images, timing, shader checks
#  3) generator (gen_fix): diffs against base/ (= ol2 snapshot, md5 in gen_fix/base_md5.txt), Add-Outline text,
#     patched Wow.exe via apply_patches.ps1 (build15 copy + edit_script8.py, pwsh), unicorn emulation suite
set -e
A=$(cd "$(dirname "$0")" && pwd); S=$(dirname "$A"); cd "$A"
export PYTHONDONTWRITEBYTECODE=1
# 1) simulation
python3 tipstudy.py > tipstudy.txt
python3 run4.py > run4.txt; python3 run5.py > run5.txt; python3 run6.py > run6.txt
python3 runlook3.py > runlook3.txt; python3 runlook4.py > runlook4.txt; python3 runlook5.py > runlook5.txt; python3 runlook_final.py > runlook_final.txt
# 2) Wine D3D9
cd gpu
pgrep -f "Xvfb :93" > /dev/null || { nohup Xvfb :93 -screen 0 1024x768x24 > xvfb.log 2>&1 & sleep 2; }
export WINEPREFIX=$PWD/wineprefix DISPLAY=:93 WINEDEBUG=-all
[ -d wineprefix ] || wineboot -i > wineboot.log 2>&1
python3 gen_frames2.py && python3 gen_shaders.py
x86_64-w64-mingw32-gcc -O2 -Wall -Wno-misleading-indentation -o tips_test.exe tips_test.c -ld3d9 -lgdi32 -luser32
x86_64-w64-mingw32-gcc -O2 -o shadercheck.exe shadercheck.c -ld3d9 -lgdi32 -luser32
for m in 0 4; do for v in old new nsq; do mkdir -p out/${v}_ms$m; wine tips_test.exe $m $v out/${v}_ms$m > out/${v}_ms$m/run.log 2>&1; done; done
python3 gpu_metrics2.py > gpu_metrics2.txt
python3 -c "import gpu_images as g; g.strip(1, 'sub', (47, 63, 28, 62), range(0, 5), 'strip_bar_sub.png', z=7); g.strip(1, 'rot', (66, 90, 74, 98), range(0, 5), 'strip_spike_rot.png', z=7)"
for k in LPSCODE LCPSCODE VPSNEW; do wine shadercheck.exe $k.bin $k.asm > shadercheck_$k.txt 2>&1; done
mkdir -p out/bench; : > out/bench/bench.txt
for rep in 1 2 3; do for ms in 0 4; do for n in 1 8 40; do for v in old nsq; do wine tips_test.exe $ms $v out/bench 1920 1080 20 $n | grep BENCH >> out/bench/bench.txt; done; done; done; done
cd "$A"
# 3) generator, patched exe, emulation tests
cd gen_fix
python3 mkoutline10.py
for f in outline10 psasm mkoutline10 test_outline10; do diff -u ../base/$f.py $f.py > $f.diff || true; done
cd ../build
cp "$S/ol2/build15/apply_patches.ps1" apply_patches_base15.ps1; cp apply_patches_base15.ps1 apply_patches.ps1
python3 edit_script8.py apply_patches.ps1 ../gen_fix/outline10_ps.txt
rm -rf exe; mkdir exe; cp "$S/ol2/exe14/Wow.exe.ORI" exe/Wow.exe; cp apply_patches.ps1 exe/; printf 'language=de\nvalue.outline=none\n' > exe/patcher_selection.ini
(cd exe && "$S/pwsh/pwsh" -NoProfile -File ./apply_patches.ps1 -Unattended -Language de -Select 68 -Path ./Wow.exe > out.txt 2>&1)
cd ../gen_fix; mkdir -p emu; cp ../build/exe/Wow.exe emu/Wow_fix.exe; cp "$S/ol2/exe15/Wow.exe" emu/Wow_base15.exe
python3 test_outline10.py emu/Wow_fix.exe > emu/test_fix.log 2>&1 || true
(cd ../base && python3 test_outline10.py ../gen_fix/emu/Wow_base15.exe > ../gen_fix/emu/test_base15.log 2>&1 || true)
echo "emulation fix: $(grep -c '^OK' emu/test_fix.log) OK, $(tail -1 emu/test_fix.log) | base: $(grep -c '^OK' emu/test_base15.log) OK, $(tail -1 emu/test_base15.log)"
