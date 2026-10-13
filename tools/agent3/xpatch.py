"""Cross-patch analysis: branch targets of new code, overlaps, same-function writes, original branches into ranges."""
from a3 import *
import struct, re, sys

MINE = {37:'customitem',38:'climb',39:'jump',40:'airforward',41:'airlateral',42:'airturn',43:'doublejump',44:'farclip',45:'horizon',46:'envdetail',47:'grounddist',48:'sliders',49:'goscale',50:'cat0',51:'occluder',52:'bluemoon',53:'notransparency',54:'nofade',55:'hdportraits'}
tab = load_table()
# menu number -> id for all patches
num2id = {}
for n in range(1, 73):
    try:
        for line in open(f'{S}/rev/out/{n}.ini'):
            if line.startswith('patches='): num2id[n] = line.strip().split('=', 1)[1]
    except FileNotFoundError: pass
id2num = {v: k for k, v in num2id.items()}
TEXT_LO, TEXT_HI = 0x400, 0x400 + 0x5DD3B3

def in_text(off): return TEXT_LO <= off < 0x5DD800

def fn_start(d, off):
    """scan backwards for int3 padding (>=2 CC) or start of .text"""
    s = off
    while s > TEXT_LO + 2 and not (d[s-1] == 0xCC and d[s-2] == 0xCC): s -= 1
    return s

def fn_end(d, off):
    e = off
    while e < 0x5DD7B3 and not (d[e] == 0xCC and d[e+1] == 0xCC): e += 1
    return e

def sweep(d, s, e):
    """linear sweep file [s,e) -> list of capstone insns"""
    va = f2v(s)
    return list(md.disasm(d[s:e], va))

def branch_targets(insns, lo_off, hi_off):
    """targets of branch insns overlapping file range [lo,hi)"""
    res = []
    for i in insns:
        io = v2f(i.address)
        if io is None or io >= hi_off or io + i.size <= lo_off: continue
        if i.mnemonic.startswith('j') or i.mnemonic in ('call', 'loop', 'loope', 'loopne'):
            m = re.match(r'^0x([0-9a-f]+)$', i.op_str)
            if m: res.append((i.address, i.mnemonic, int(m.group(1), 16), i.bytes.hex()))
    return res

# all ranges: (id, off, len, excl)
allr = []
for pid, rows in tab.items():
    for off, orig, ex in rows: allr.append((pid, off, len(orig) // 2, ex))

def overlaps(a0, a1, b0, b1): return a0 < b1 and b0 < a1

images = {}
def img(n):
    if n not in images: images[n] = load_patched(n)
    return images[n]

report = []
for n, pid in MINE.items():
    P = img(n)
    rows = tab[pid]
    print(f'\n######## {n} {pid}')
    for off, orig, ex in rows:
        L = len(orig) // 2
        va = f2v(off)
        vas = f'{va:X}' if va else 'n/a'
        print(f'-- range file {off:X}..{off+L:X} (VA {vas}) len {L} excl={ex}')
        # 1. overlap with other patches' ranges
        for (pid2, off2, L2, ex2) in allr:
            if pid2 == pid: continue
            if overlaps(off, off + L, off2, off2 + L2):
                print(f'   OVERLAP with {pid2} ({id2num.get(pid2)}) at {off2:X} len {L2}')
        if not in_text(off):
            # data range: list other patches touching same 64-byte neighbourhood
            for (pid2, off2, L2, ex2) in allr:
                if pid2 != pid and overlaps(off - 0x40, off + L + 0x40, off2, off2 + L2):
                    print(f'   NEAR (data) {pid2} ({id2num.get(pid2)}) at {off2:X} len {L2}')
            continue
        if off >= 0x5DD7B3:  # cave at end of .text
            s, e = 0x5DD7B3, 0x5DD800
        else:
            s = fn_start(ORIG, off); e = fn_end(ORIG, off + L)
        # 2. other patches in same function
        for (pid2, off2, L2, ex2) in allr:
            if pid2 != pid and overlaps(s, e, off2, off2 + L2):
                print(f'   SAME-FUNCTION ({f2v(s):X}..{f2v(e):X}) write by {pid2} ({id2num.get(pid2)}) at {off2:X} (VA {f2v(off2):X}) len {L2}')
        # 3. branch targets of new code in this range (patched image sweep from fn start)
        ins_p = sweep(P, s, max(e, off + L))
        bt = branch_targets(ins_p, off, off + L)
        bset_p = {i.address for i in ins_p}
        for (src, mn, tgt, hx) in bt:
            toff = v2f(tgt)
            note = ''
            if toff is None:
                # maybe into appended section
                note = 'target outside mapped orig sections (appended section?)'
            else:
                # is target an instruction boundary in patched image? sweep target's function
                if TEXT_LO <= toff < 0x5DD800:
                    ts = fn_start(P, toff) if toff < 0x5DD7B3 else 0x5DD7B3
                    te = fn_end(P, toff) if toff < 0x5DD7B3 else 0x5DD800
                    tb = {i.address for i in sweep(P, ts, max(te, toff + 1))}
                    note = 'boundary OK' if tgt in tb else 'NOT A BOUNDARY in patched sweep'
                    # does target lie in another patch's range?
                    for (pid2, off2, L2, ex2) in allr:
                        if pid2 != pid and off2 <= toff < off2 + L2:
                            note += f'; target inside range of {pid2} ({id2num.get(pid2)}) {off2:X}+{L2}' + (' (at start)' if toff == off2 else ' (STRICTLY INSIDE)')
                else:
                    note = 'target not in .text'
            print(f'   new {mn:4s} at {src:X} -> {tgt:X}  [{hx}]  {note}')
        # 4. original branches landing strictly inside the range
        hits = scan_branches_into(va + 1, va + L)
        ins_o = sweep(ORIG, s, e)
        bset_o = {i.address for i in ins_o}
        for kind, src, tgt, hx in hits:
            valid = src in bset_o or (fn_start(ORIG, v2f(src)) != s)  # if from another fn, check its own sweep
            if fn_start(ORIG, v2f(src)) != s:
                ss = fn_start(ORIG, v2f(src)); ee = fn_end(ORIG, v2f(src))
                valid = src in {i.address for i in sweep(ORIG, ss, ee)}
            if valid:
                ok = 'boundary in patched' if tgt in bset_p else 'MID-INSTRUCTION in patched'
                print(f'   ORIG {kind} at {src:X} -> {tgt:X} [{hx}] lands strictly inside range: {ok}')
        # 5. other patches' NEW code branching into this range
        for (pid2, off2, L2, ex2) in allr:
            if pid2 == pid or not in_text(off2) or pid2 not in id2num: continue
            P2 = img(id2num[pid2])
            s2 = fn_start(P2, off2) if off2 < 0x5DD7B3 else 0x5DD7B3
            e2 = fn_end(P2, off2 + L2) if off2 < 0x5DD7B3 else 0x5DD800
            for (src, mn, tgt, hx) in branch_targets(sweep(P2, s2, max(e2, off2 + L2)), off2, off2 + L2):
                t = v2f(tgt)
                if t is not None and off <= t < off + L:
                    print(f'   OTHER-PATCH {pid2} ({id2num[pid2]}) new {mn} at {src:X} -> {tgt:X} lands in this range' + (' (at start)' if t == off else ' (STRICTLY INSIDE)'))
