# Welche Undo-Bereiche einer alten patcher_state.ini deckt die Original-Byte-Tabelle eines Skripts nicht ab?
# Aufruf: undo_cover.py <apply_patches.ps1> <patcher_state.ini>
import sys, re
s = open(sys.argv[1], encoding='ascii').read().replace('\r\n', '\n')
a = re.search(r'(?m)^# BEGIN ORIGINAL-BYTES$', s).start(); z = re.search(r'(?m)^# END ORIGINAL-BYTES$', s).start()
cov = {}
ids_now = set(re.findall(r"(?m)^    @\{ Id = '([^']+)'", s))
for line in s[a:z].split('\n'):
    m = re.match(r'^([a-z0-9]+);([0-9A-F]+);([0-9A-F]*);([01])$', line)
    if not m: continue
    off = int(m.group(2), 16); b = bytes.fromhex(m.group(3))
    for i in range(len(b)): cov.setdefault(off + i, []).append(m.group(1))
st = open(sys.argv[2], encoding='utf-8').read().split('\n')
pids = []
miss = []
for line in st:
    if line.startswith('patches='): pids = line[8:].split(',')
    m = re.match(r'^undo=0x([0-9A-F]+):([0-9A-F]*)$', line.strip())
    if not m: continue
    off = int(m.group(1), 16); n = len(m.group(2)) // 2
    un = [off + i for i in range(n) if off + i not in cov]
    if un: miss.append((off, n, len(un), un[0]))
print('Patches nicht mehr im Skript:', [p for p in pids if p not in ids_now])
for off, n, k, first in miss:
    print('undo 0x%X (%d Byte): %d Byte nicht in der Tabelle, erstes 0x%X' % (off, n, k, first))
print('fertig, %d Bereiche ohne volle Abdeckung' % len(miss))
