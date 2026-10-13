import capstone, struct, sys, re, os
ORI = '/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
OUT = '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/rev/out'
TBL = '/home/user/St0nys-WoW-EXE-Patcher/apply_patches.ps1'
IB = 0x400000
# (name, VA, vsize, rawoff, rawsize)
SECS = [('.text', 0x401000, 0x5DD3B3, 0x400, 0x5DD400),
        ('.rdata', 0x9DF000, 0xD6679, 0x5DD800, 0xD6800),
        ('.data', 0xAB6000, 0x78E00, 0x6B4000, 0x78E00),
        ('.zdata', 0x9D1000, 0x1000, 0x72CE00, 0x1000),
        ('.tls', 0x9D2000, 0x200, 0x72DE00, 0x200),
        ('.rsrc', 0x9D3000, 0x29AD0, 0x72E000, 0x29C00)]

d = open(ORI, 'rb').read()
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
md.detail = True


def load(n):
    return open(os.path.join(OUT, '%s.exe' % n), 'rb').read()


def v2f(v):
    for nm, va, vs, ro, rs in SECS:
        if va <= v < va + max(vs, rs):
            return ro + v - va
    return None


def f2v(o):
    for nm, va, vs, ro, rs in SECS:
        if ro <= o < ro + rs:
            return va + o - ro
    return None


def cstr(data, v):
    o = v2f(v)
    if o is None or o >= len(data):
        return None
    e = data.find(b'\0', o)
    s = data[o:e]
    if 0 < len(s) < 200 and all(32 <= c < 127 or c in (9, 10, 13) for c in s):
        return s
    return None


def dis(data, vstart, n, out=None, mark=None, fileoff=None):
    """disassemble n bytes at VA vstart (or file offset fileoff). mark = (start_va, end_va) range to tag with '*'."""
    if fileoff is not None:
        o = fileoff
        vstart = f2v(o) if f2v(o) is not None else vstart
    else:
        o = v2f(vstart)
    lines = []
    for i in md.disasm(data[o:o + n], vstart):
        tag = ' '
        if mark and mark[0] <= i.address < mark[1]:
            tag = '*'
        s = '%s %08X  %-26s %s %s' % (tag, i.address, i.bytes.hex(), i.mnemonic, i.op_str)
        for tok in re.findall(r'0x[0-9a-fA-F]+', i.op_str):
            v = int(tok, 16)
            c = cstr(data, v) if v >= 0x9D0000 else None
            if c:
                s += '   ; "%s"' % c.decode()
        lines.append(s)
    txt = '\n'.join(lines)
    if out is None:
        print(txt)
    return txt


def find_func_start(data, va, maxback=0x400):
    """walk back to a plausible function start: previous CC/C3 padding boundary followed by non-CC byte."""
    o = v2f(va)
    for k in range(1, maxback):
        p = o - k
        b = data[p]
        if b == 0xCC and data[p + 1] != 0xCC:
            return f2v(p + 1)
    return va - 0x40


def table_rows(ids=None):
    src = open(TBL, 'r', encoding='utf-8', errors='replace').read()
    a = src.rindex('# BEGIN ORIGINAL-BYTES')
    z = src.rindex('# END ORIGINAL-BYTES')
    rows = []
    for ln in src[a:z].splitlines():
        ln = ln.strip()
        parts = ln.split(';')
        if len(parts) == 4 and re.match(r'^[0-9A-Fa-f]+$', parts[1]):
            pid, off, hx, excl = parts
            if ids is None or pid in ids:
                rows.append((pid, int(off, 16), bytes.fromhex(hx), int(excl)))
    return rows


def ini_undo(n):
    res = []
    for ln in open(os.path.join(OUT, '%s.ini' % n), encoding='utf-8', errors='replace'):
        ln = ln.strip()
        if ln.startswith('undo='):
            off, hx = ln[5:].split(':')
            res.append((int(off, 16), bytes.fromhex(hx)))
    return res


def diff_ranges(a, b):
    """list of (off, len) where a and b differ (over min len) plus tail."""
    n = min(len(a), len(b))
    res = []
    i = 0
    while i < n:
        if a[i] != b[i]:
            j = i
            while j < n and a[j] != b[j]:
                j += 1
            res.append((i, j - i))
            i = j
        else:
            i += 1
    if len(a) != len(b):
        res.append((n, abs(len(a) - len(b))))
    return res


def branch_targets(data, lo_f=0x400, hi_f=0x400 + 0x5DD3B3):
    """Linear scan of .text bytes for E8/E9 rel32, 0F 8x rel32, 7x/EB/E3 rel8 opcodes. Returns dict target_va -> list of (src_va, kind).
    Note: linear byte scan (not a true disassembly) -> false positives possible; used to find candidates."""
    res = {}
    o = lo_f
    end = hi_f
    while o < end:
        b = data[o]
        va = f2v(o)
        if b in (0xE8, 0xE9) and o + 5 <= end:
            rel = struct.unpack('<i', data[o + 1:o + 5])[0]
            t = va + 5 + rel
            res.setdefault(t, []).append((va, 'call' if b == 0xE8 else 'jmp'))
        elif b == 0x0F and o + 6 <= end and 0x80 <= data[o + 1] <= 0x8F:
            rel = struct.unpack('<i', data[o + 2:o + 6])[0]
            t = va + 6 + rel
            res.setdefault(t, []).append((va, 'jcc32'))
        elif (0x70 <= b <= 0x7F or b in (0xEB, 0xE3, 0xE0, 0xE1, 0xE2)) and o + 2 <= end:
            rel = struct.unpack('<b', data[o + 1:o + 2])[0]
            t = va + 2 + rel
            res.setdefault(t, []).append((va, 'jcc8' if b != 0xEB else 'jmp8'))
        o += 1
    return res


_BT = None


def bt():
    global _BT
    if _BT is None:
        _BT = branch_targets(d)
    return _BT


def targets_into(lo_va, hi_va, strict=False):
    """all scanned branch sources whose target lies in [lo,hi) (strict: (lo,hi))."""
    t = bt()
    res = []
    for tv, srcs in t.items():
        if (lo_va < tv < hi_va) if strict else (lo_va <= tv < hi_va):
            for s in srcs:
                res.append((tv, s[0], s[1]))
    return sorted(res)


def verify_disasm_branch(data, src_va):
    """check that a candidate branch source is on an instruction boundary by disassembling from the function start."""
    fs = find_func_start(data, src_va)
    o = v2f(fs)
    for i in md.disasm(data[o:o + (src_va - fs) + 16], fs):
        if i.address == src_va:
            return True, fs
        if i.address > src_va:
            return False, fs
    return False, fs
