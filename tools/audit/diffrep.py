# Bericht je Patch auf Basis der ORIGINAL_TABLE-Bereiche (alle Schreibstellen),
# neue Bytes aus der einzeln gepatchten Exe p_N.exe.
import sys, re, os, struct
import h
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_GRP_JUMP, X86_GRP_CALL

S = os.path.dirname(os.path.abspath(__file__))
RUN = S + '/run'
SRC = open(S + '/dev.ps1', encoding='utf-8').read()
ids = re.findall(r"(?m)^    @\{ Id = '([^']+)'", SRC)
_a = SRC.index("\n$ORIGINAL_TABLE = @'\n") + len("\n$ORIGINAL_TABLE = @'\n")
tab = SRC[_a:SRC.index("\n'@", _a)]
TABLE = {}
for line in tab.strip().splitlines():
    parts = line.split(';')
    if parts[0] == 'size' or len(parts) != 4:
        continue
    pid, off, ob, flag = parts
    TABLE.setdefault(pid, []).append((int(off, 16), bytes.fromhex(ob), int(flag)))

def merged(pid):
    rs = sorted((o, len(b), fl) for o, b, fl in TABLE.get(pid, []))
    out = []
    for o, l, fl in rs:
        if out and o <= out[-1][0] + out[-1][1]:
            po, pl, pf = out[-1]
            out[-1] = (po, max(po + pl, o + l) - po, pf and fl)
        else:
            out.append((o, l, fl))
    return out

def target_info(ins, data):
    notes = []
    if ins.group(X86_GRP_JUMP) or ins.group(X86_GRP_CALL):
        for op in ins.operands:
            if op.type == X86_OP_IMM:
                t = op.imm
                sec = h.secname(t)
                if sec != '.text':
                    notes.append('ZIEL AUSSERHALB .text: %#x (%s)' % (t, sec))
                else:
                    o = h.va2off(t)
                    prev = data[o - 1]
                    isfn = prev in (0xCC, 0xC3) or data[o - 3] == 0xC2
                    tdis = h.dis(data[o:o + 12], t, 1)
                    notes.append('-> %#x %s%s' % (t, ('[fn-start] ' if isfn else ''), (tdis[0].mnemonic + ' ' + tdis[0].op_str) if tdis else '??'))
            elif op.type == X86_OP_MEM and op.mem.base == 0 and op.mem.index == 0:
                a = op.mem.disp
                notes.append('[%#x] %s' % (a, h.IMPORTS.get(a, 'KEIN IMPORT' if 0x9DF000 <= a < 0x9DF79C else str(h.secname(a)))))
    else:
        for op in ins.operands:
            if op.type == X86_OP_IMM and 0x400000 <= op.imm < 0xE00000:
                a = op.imm
                o = h.va2off(a)
                s = h.secname(a)
                extra = ''
                if s in ('.rdata', '.data') and o:
                    raw = data[o:o + 16]
                    if all(32 <= c < 127 for c in raw.split(b'\0')[0]) and raw.split(b'\0')[0]:
                        extra = ' "%s"' % raw.split(b'\0')[0].decode()
                notes.append('imm %#x -> %s%s' % (a, s, extra))
            elif op.type == X86_OP_MEM and op.mem.base == 0 and op.mem.index == 0 and 0x400000 <= op.mem.disp < 0xE00000:
                a = op.mem.disp
                notes.append('[%#x] %s' % (a, h.IMPORTS.get(a, str(h.secname(a)))))
    return notes

def report(n, pid):
    p = RUN + '/p_%d.exe' % n
    new = open(p, 'rb').read()
    out = ['#' * 78, '# Nr. %d %s  (size %d -> %d)' % (n, pid, len(h.F), len(new))]
    if len(new) > len(h.F):
        out.append('  angehaengt: %d Byte ab %#x' % (len(new) - len(h.F), len(h.F)))
    for off, ln, fl in merged(pid):
        va = h.off2va(off)
        sec = h.secname(va) if va else None
        changed = h.F[off:off + ln] != new[off:off + ln]
        out.append('-- off %#x len %d VA %s sec %s %s%s' % (off, ln, hex(va) if va else '?', sec, '' if fl else '[geteilt] ', '' if changed else '[UNVERAENDERT]'))
        if ln <= 96:
            out.append('   alt: ' + h.F[off:off + ln].hex(' '))
            out.append('   neu: ' + new[off:off + ln].hex(' '))
        if sec == '.text' and va:
            fs = h.func_start(va)
            if fs and va - fs < 0x3000:
                bounds = h.linear_boundaries(fs, va + ln + 16)
                out.append('   fn-start %#x; Patchanfang auf Instruktionsgrenze: %s; Patchende: %s' % (fs, va in bounds, (va + ln) in bounds))
            else:
                out.append('   fn-start nicht gefunden')
            out.append('   ORIGINAL:')
            for ins in h.dis(h.F[off:off + ln + 16], va):
                if ins.address >= va + ln:
                    break
                ti = target_info(ins, h.F)
                out.append('     ' + h.fmt(ins) + ('   ; ' + ' | '.join(ti) if ti else ''))
            out.append('   NEU:')
            cnt = 0
            end_ok = None
            for ins in h.dis(new[off:off + ln + 32], va):
                ti = target_info(ins, new)
                out.append('     ' + h.fmt(ins) + ('   ; ' + ' | '.join(ti) if ti else ''))
                if ins.address + ins.size == va + ln:
                    end_ok = True
                if ins.address + ins.size > va + ln:
                    if end_ok is None:
                        end_ok = False
                        out.append('     ^^^ INSTRUKTION LAEUFT UEBER DAS PATCHENDE HINAUS (endet %#x, Patchende %#x)' % (ins.address + ins.size, va + ln))
                    cnt += 1
                    if cnt >= 2:
                        break
    return '\n'.join(out)

if __name__ == '__main__':
    sel = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else range(1, len(ids) + 1)
    for n in sel:
        print(report(n, ids[n - 1]))
