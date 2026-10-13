import capstone, struct, re, os, sys
S = '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad'
ORIG_PATH = '/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
ORIG = open(ORIG_PATH, 'rb').read()
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = True

# section map (orig): (VA rva, vsize, raw off, raw size)
SECS = [('.text', 0x1000, 0x5DD3B3, 0x400, 0x5DD400),
        ('.rdata', 0x5DF000, 0xD6679, 0x5DD800, 0xD6800),
        ('.data', 0x6B6000, 0x31A508, 0x6B4000, 0x78E00),
        ('.zdata', 0x9D1000, 0x1000, 0x72CE00, 0x1000),
        ('.tls', 0x9D2000, 0x19, 0x72DE00, 0x200),
        ('.rsrc', 0x9D3000, 0x29AD0, 0x72E000, 0x29C00)]

def v2f(va):
    r = va - 0x400000
    for nm, rva, vs, ro, rs in SECS:
        if rva <= r < rva + max(vs, rs):
            o = ro + r - rva
            if o < ro + rs: return o
    return None

def f2v(off):
    for nm, rva, vs, ro, rs in SECS:
        if ro <= off < ro + rs:
            return 0x400000 + rva + off - ro
    return None

def load_patched(n):
    return open(f'{S}/rev/out/{n}.exe', 'rb').read()

def cstr(d, v):
    o = v2f(v)
    if o is None or o >= len(d): return None
    e = d.find(b'\0', o); s = d[o:e]
    return s if 0 < len(s) < 160 and all(32 <= c < 127 for c in s) else None

def fl32(d, v):
    o = v2f(v)
    if o is None: return None
    return struct.unpack_from('<f', d, o)[0]

def dis(d, va, n, out=print, hl=None, foff=None):
    """disassemble n bytes at VA va of image d. hl=(start,end) file range to mark with *"""
    o = v2f(va) if foff is None else foff
    for i in md.disasm(d[o:o + n], va):
        mark = ' '
        if hl:
            io = o + (i.address - va)
            if io < hl[1] and io + i.size > hl[0]: mark = '*'
        s = '%s %08X  %-24s %s %s' % (mark, i.address, i.bytes.hex(), i.mnemonic, i.op_str)
        for tok in re.findall(r'0x[0-9a-f]+', i.op_str):
            v = int(tok, 16)
            if v > 0x9D0000:
                c = cstr(d, v)
                if c: s += '   ; "%s"' % c.decode()
                else:
                    f = fl32(d, v)
                    if f is not None and i.mnemonic.startswith('f'): s += '   ; float %r' % f
        out(s)

def dis_both(n, va, nbytes, ranges, foff=None):
    """print original and patched disassembly for window; ranges = list of (fileoff,len) patched"""
    p = load_patched(n)
    o = v2f(va) if foff is None else foff
    print(f'--- ORIGINAL VA {va:X} (file {o:X}) ---')
    for r in ranges:
        dis(ORIG, va, nbytes, hl=(r[0], r[0] + r[1]), foff=foff) if len(ranges) == 1 else None
    if len(ranges) != 1:
        dis(ORIG, va, nbytes, foff=foff)
    print(f'--- PATCHED {n} ---')
    if len(ranges) == 1:
        dis(p, va, nbytes, hl=(ranges[0][0], ranges[0][0] + ranges[0][1]), foff=foff)
    else:
        dis(p, va, nbytes, foff=foff)

def load_table():
    tab = {}
    for line in open(S + '/agent3/table.txt'):
        line = line.strip()
        parts = line.split(';')
        if len(parts) != 4: continue
        pid, off, orig, ex = parts
        tab.setdefault(pid, []).append((int(off, 16), orig.upper(), ex))
    return tab

def load_ini(n):
    undo = []
    for line in open(f'{S}/rev/out/{n}.ini'):
        m = re.match(r'undo=0x([0-9A-Fa-f]+):([0-9A-Fa-f]*)', line.strip())
        if m: undo.append((int(m.group(1), 16), m.group(2).upper()))
    return undo

def diff_ranges(n):
    """byte diff between orig and patched n (first len(ORIG) bytes); returns list of (off,len)"""
    p = load_patched(n)
    L = min(len(p), len(ORIG))
    res = []
    i = 0
    while i < L:
        if p[i] != ORIG[i]:
            j = i
            while j < L and p[j] != ORIG[j]: j += 1
            res.append((i, j - i)); i = j
        else: i += 1
    return res, len(p) - len(ORIG)

def scan_branches_into(lo_va, hi_va, strict_inside_of=None):
    """scan .text of ORIG for rel8/rel32 branches whose target lies in [lo_va,hi_va).
    Linear disassembly of the whole .text in chunks (resync on instruction boundaries is approximate),
    plus raw opcode byte scan (E8/E9/0F8x/7x/EB) which is boundary-independent."""
    hits = []
    text_o, text_len = 0x400, 0x5DD3B3
    d = ORIG
    # raw scan
    for o in range(text_o, text_o + text_len):
        b = d[o]
        src = f2v(o)
        if b in (0xE8, 0xE9) and o + 5 <= text_o + text_len:
            rel = struct.unpack_from('<i', d, o + 1)[0]
            t = src + 5 + rel
            if lo_va <= t < hi_va: hits.append(('rel32', src, t, d[o:o + 5].hex()))
        if b == 0x0F and o + 6 <= text_o + text_len and 0x80 <= d[o + 1] <= 0x8F:
            rel = struct.unpack_from('<i', d, o + 2)[0]
            t = src + 6 + rel
            if lo_va <= t < hi_va: hits.append(('jcc32', src, t, d[o:o + 6].hex()))
        if (0x70 <= b <= 0x7F or b == 0xEB or b in (0xE0, 0xE1, 0xE2, 0xE3)) and o + 2 <= text_o + text_len:
            rel = struct.unpack_from('<b', d, o + 1)[0]
            t = src + 2 + rel
            if lo_va <= t < hi_va: hits.append(('rel8', src, t, d[o:o + 2].hex()))
    return hits
