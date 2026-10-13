#!/usr/bin/env python3
# Sammelt eigene Werkzeuge aus dem Scratchpad (ohne Fremd-Repos, Binaerdateien, Dumps).
# Aufruf: collect.py <scratchpad> [--list]
import os, sys, re
S = sys.argv[1]
SKIP_TOP = {'pwsh', 'werkzeug', 'toolsync', 'toolsmoke', 'CameraReforged-Backup', 'tools'}
# CameraReforged-Port (GPL, bis zur Erlaubnis entfernt) und README-Kopien nie mitnehmen
EXCLUDE = {'camera_func.ps1', 'camera_readme.py', 'e78.py', 'dev-c8.md', 'dev-c8.de.md',
           'agent4/camera.py', 'rmcam/rm_camera.py'}
EXT = {'.py', '.sh', '.md', '.ps1', '.json', '.txt', '.c', '.cpp', '.h', '.hlsl', '.glsl', '.js', '.html', '.ini'}
MAXSZ = 400 * 1024
def third_party(dirpath):
    # Repo-Klone/Worktrees und Ordner mit eigener Lizenz
    names = os.listdir(dirpath)
    if '.git' in names: return True
    if any(n.upper().startswith(('LICENSE', 'LICENCE', 'COPYING')) for n in names): return True
    return False
out = []
skipped = {'third': [], 'big': [], 'patcher': [], 'dump': []}
for top in sorted(os.listdir(S)):
    p = os.path.join(S, top)
    if os.path.isfile(p):
        ext = os.path.splitext(top)[1].lower(); low = top.lower(); sz = os.path.getsize(p)
        if ext not in EXT or ext in ('.ini', '.html') or sz > MAXSZ: continue
        if ext == '.ps1' and sz > 150 * 1024: skipped['patcher'].append(top); continue
        if ext == '.txt' and not low.startswith('msg'): skipped['dump'].append(top); continue
        if low.startswith(('gpl', 'license', 'copying')): continue
        out.append(top); continue
    if top in SKIP_TOP or top.startswith('wt-'): continue
    for dirpath, dirnames, filenames in os.walk(p):
        if third_party(dirpath):
            skipped['third'].append(os.path.relpath(dirpath, S)); dirnames[:] = []; continue
        dirnames[:] = [d for d in dirnames if d not in ('__pycache__', 'node_modules') and not d.startswith('wt-')]
        for fn in filenames:
            fp = os.path.join(dirpath, fn); rel = os.path.relpath(fp, S)
            ext = os.path.splitext(fn)[1].lower()
            if ext not in EXT: continue
            sz = os.path.getsize(fp)
            low = fn.lower()
            if ext not in ('.py', '.sh', '.ps1', '.c', '.cpp', '.h') and (
                    re.search(r'(_dis|dis_|disasm|dump|\.log)', low) or low.startswith(('out', 'fail_', 'rc_'))):
                skipped['dump'].append(rel); continue
            if ext == '.txt' and not (low.startswith('msg') or low.endswith(('_ps.txt', '_hdr.txt')) or low in ('info.txt',)):
                skipped['dump'].append(rel); continue
            if sz > MAXSZ: skipped['big'].append((rel, sz)); continue
            if ext == '.ps1' and (fn == 'apply_patches.ps1' or sz > 150 * 1024):
                skipped['patcher'].append(rel); continue
            if ext == '.ini' or ext == '.html': continue
            parts = rel.split('/')
            if any(x in ('docs', 'pyfig', 'pylib', 'verify', '.claude') or re.match(r'(snap_|wt_backup|docs\d|.*_save\d*$)', x) for x in parts[:-1]):
                skipped['dump'].append(rel); continue
            if re.match(r'(README|PATCHES|LIESMICH)[^/]*\.md$', fn) or low.startswith(('gpl', 'license', 'copying')):
                skipped['dump'].append(rel); continue
            if ext == '.json' and sz > 100 * 1024:
                skipped['big'].append((rel, sz)); continue
            out.append(rel)
out = [r for r in out if r not in EXCLUDE]
if '--copy' in sys.argv:
    import shutil
    dst = sys.argv[sys.argv.index('--copy') + 1]
    for r in out:
        os.makedirs(os.path.join(dst, os.path.dirname(r)), exist_ok=True)
        shutil.copy2(os.path.join(S, r), os.path.join(dst, r))
    print('kopiert:', len(out))
elif '--list' in sys.argv:
    for r in out: print(r)
else:
    from collections import Counter
    c = Counter(r.split('/')[0] if '/' in r else '.' for r in out)
    tot = sum(os.path.getsize(os.path.join(S, r)) for r in out)
    print('Dateien:', len(out), 'Groesse: %.1f MB' % (tot / 1e6))
    print(' '.join('%s:%d' % kv for kv in sorted(c.items())))
    print('Fremd/Repo uebersprungen:', len(skipped['third']), sorted(set(s.split('/')[0] for s in skipped['third'])))
    print('zu gross:', len(skipped['big']), [(r, s // 1024) for r, s in skipped['big']][:15])
    print('Patcher-Kopien:', len(skipped['patcher']), ' Dumps/Ausgaben:', len(skipped['dump']))
