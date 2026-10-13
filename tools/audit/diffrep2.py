# python3 diffrep2.py <script.ps1> <patched.exe> <id> - Bericht wie diffrep, fuer andere Zweige
import sys, re, os, struct
import h
from diffrep import target_info

script, exe, pid = sys.argv[1:4]
SRC = open(script, encoding='utf-8').read()
_a = SRC.index("\n$ORIGINAL_TABLE = @'\n") + len("\n$ORIGINAL_TABLE = @'\n")
tab = SRC[_a:SRC.index("\n'@", _a)]
rows = []
for line in tab.strip().splitlines():
    p = line.split(';')
    if len(p) == 4 and p[0] == pid:
        rows.append((int(p[1], 16), len(bytes.fromhex(p[2])), int(p[3])))
rows.sort()
merged = []
for o, l, fl in rows:
    if merged and o <= merged[-1][0] + merged[-1][1]:
        po, pl, pf = merged[-1]; merged[-1] = (po, max(po + pl, o + l) - po, pf and fl)
    else:
        merged.append((o, l, fl))
new = open(exe, 'rb').read()
print('# %s  (size %d -> %d)' % (pid, len(h.F), len(new)))
if len(new) > len(h.F):
    print('  angehaengt: %d Byte ab %#x' % (len(new) - len(h.F), len(h.F)))
for off, ln, fl in merged:
    va = h.off2va(off); sec = h.secname(va) if va else None
    changed = h.F[off:off + ln] != new[off:off + ln]
    print('-- off %#x len %d VA %s sec %s %s%s' % (off, ln, hex(va) if va else '?', sec, '' if fl else '[geteilt] ', '' if changed else '[UNVERAENDERT]'))
    if ln <= 96:
        print('   alt: ' + h.F[off:off + ln].hex(' ')); print('   neu: ' + new[off:off + ln].hex(' '))
    if sec == '.text' and va:
        fs = h.func_start(va)
        if fs and va - fs < 0x3000:
            b = h.linear_boundaries(fs, va + ln + 16)
            print('   fn-start %#x; Patchanfang auf Instruktionsgrenze: %s; Patchende: %s' % (fs, va in b, (va + ln) in b))
        print('   ORIGINAL:')
        for ins in h.dis(h.F[off:off + ln + 16], va):
            if ins.address >= va + ln: break
            ti = target_info(ins, h.F); print('     ' + h.fmt(ins) + ('   ; ' + ' | '.join(ti) if ti else ''))
        print('   NEU:')
        cnt = 0
        for ins in h.dis(new[off:off + ln + 32], va):
            ti = target_info(ins, new); print('     ' + h.fmt(ins) + ('   ; ' + ' | '.join(ti) if ti else ''))
            if ins.address + ins.size > va + ln:
                cnt += 1
                if cnt >= 2: break
