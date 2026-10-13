# psasm_tent.py - psasm-style ps_2_0 for the 4x4 tent downsample of the glow (proposed addition to ol2/psasm.py).
# Uses only what ol2/psasm.py already has (reg/dst/src/ins, MOV/ADD/MUL/TEX/DCL/DEF, disasm); ol2/psasm.py is only read.
#
#   ps_2_0
#   def c0, 0.25, 0.25, 0.25, 0.25
#   dcl t1.xy                 ; (u,v) + (a,b)    a = 0.75 / RTW, b = 0.75 / RTH   (mkq: QDU*O1, QDV*O1)
#   dcl t2.xy                 ; (u,v) - (a,b)
#   dcl_2d s0
#   texld r0, t1, s0          ; (+a,+b)
#   texld r1, t2, s0          ; (-a,-b)
#   mov r2.x, t1              ; r2 = (u+a, v-b)
#   mov r2.y, t2
#   mov r3.x, t2              ; r3 = (u-a, v+b)
#   mov r3.y, t1
#   texld r2, r2, s0          ; (+a,-b)   dependent read, level 1
#   texld r3, r3, s0          ; (-a,+b)
#   add r0, r0, r1
#   add r0, r0, r2
#   add r0, r0, r3
#   mul r0, r0, c0.x          ; mean of the 4 bilinear taps = [1 3 3 1]/8 x [1 3 3 1]/8 over 4x4 texels
#   mov oC0, r0
#   end
import os, sys, struct
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(S, 'ol2'))
import psasm
from psasm import reg, dst, src, ins, MOV, ADD, MAD, MUL, TEX, DCL, DEF, f2i, T, C, TX, OC, S as SMP

def tent_ps(k=0.25):
    t = [0xFFFF0200]
    t += ins(DEF, dst(C, 0), f2i(k), f2i(k), f2i(k), f2i(k))
    for i in (1, 2): t += ins(DCL, 0x80000000, dst(TX, i, 0x3))
    t += ins(DCL, 0x90000000, dst(SMP, 0))
    t += ins(TEX, dst(T, 0), src(TX, 1), src(SMP, 0))
    t += ins(TEX, dst(T, 1), src(TX, 2), src(SMP, 0))
    t += ins(MOV, dst(T, 2, 0x1), src(TX, 1))
    t += ins(MOV, dst(T, 2, 0x2), src(TX, 2))
    t += ins(MOV, dst(T, 3, 0x1), src(TX, 2))
    t += ins(MOV, dst(T, 3, 0x2), src(TX, 1))
    t += ins(TEX, dst(T, 2), src(T, 2), src(SMP, 0))
    t += ins(TEX, dst(T, 3), src(T, 3), src(SMP, 0))
    t += ins(ADD, dst(T, 0), src(T, 0), src(T, 1))
    t += ins(ADD, dst(T, 0), src(T, 0), src(T, 2))
    t += ins(ADD, dst(T, 0), src(T, 0), src(T, 3))
    t += ins(MUL, dst(T, 0), src(T, 0), src(C, 0, 'x'))
    t += ins(MOV, dst(OC, 0), src(T, 0))
    t += [0x0000FFFF]
    return struct.pack('<%dI' % len(t), *t)

def blur_soft_ps(w0, w1, w2, k):
    # vertical blur pass with the glow curve: TEX1 = 1-(1-sat(k*blur))^2 = y*(2-y), y = sat(k*blur), per channel
    # (premultiplied: RGB = f(col*x), A = f(x) as before). The composite then runs with gain 1 (comp_ps(1.0)).
    t = [0xFFFF0200]
    t += ins(DEF, dst(C, 0), f2i(w0), f2i(w1), f2i(w2), 0)
    t += ins(DEF, dst(C, 1), f2i(k), f2i(-1.0), f2i(2.0), 0)
    for i in range(5): t += ins(DCL, 0x80000000, dst(TX, i, 0x3))
    t += ins(DCL, 0x90000000, dst(SMP, 0))
    for i in range(5): t += ins(TEX, dst(T, i), src(TX, i), src(SMP, 0))
    t += ins(MUL, dst(T, 0), src(T, 0), src(C, 0, 'x'))
    t += ins(ADD, dst(T, 1), src(T, 1), src(T, 2))
    t += ins(MAD, dst(T, 0), src(T, 1), src(C, 0, 'y'), src(T, 0))
    t += ins(ADD, dst(T, 3), src(T, 3), src(T, 4))
    t += ins(MAD, dst(T, 0), src(T, 3), src(C, 0, 'z'), src(T, 0))
    t += ins(MUL, dst(T, 0, sat=True), src(T, 0), src(C, 1, 'x'))       # y = sat(k * x)
    t += ins(MAD, dst(T, 1), src(T, 0), src(C, 1, 'y'), src(C, 1, 'z'))  # 2 - y
    t += ins(MUL, dst(T, 0), src(T, 0), src(T, 1))                      # y * (2 - y)
    t += ins(MOV, dst(OC, 0), src(T, 0))
    t += [0x0000FFFF]
    return struct.pack('<%dI' % len(t), *t)

BLUR_SOFT_ASM = '''ps_2_0
def c0, 0.227027, 0.3162162, 0.0702703, 0
def c1, 2.5, -1, 2, 0
dcl t0.xy
dcl t1.xy
dcl t2.xy
dcl t3.xy
dcl t4.xy
dcl_2d s0
texld r0, t0, s0
texld r1, t1, s0
texld r2, t2, s0
texld r3, t3, s0
texld r4, t4, s0
mul r0, r0, c0.x
add r1, r1, r2
mad r0, r1, c0.y, r0
add r3, r3, r4
mad r0, r3, c0.z, r0
mul_sat r0, r0, c1.x
mad r1, r0, c1.y, c1.z
mul r0, r0, r1
mov oC0, r0
'''

ASM_TEXT = '''ps_2_0
def c0, 0.25, 0.25, 0.25, 0.25
dcl t1.xy
dcl t2.xy
dcl_2d s0
texld r0, t1, s0
texld r1, t2, s0
mov r2.x, t1
mov r2.y, t2
mov r3.x, t2
mov r3.y, t1
texld r2, r2, s0
texld r3, r3, s0
add r0, r0, r1
add r0, r0, r2
add r0, r0, r3
mul r0, r0, c0.x
mov oC0, r0
'''

def check_ps20(b):
    """structural ps_2_0 checks (limits of the ps_2_0 profile): <= 64 arithmetic + 32 texture instruction slots,
    <= 12 temps, t0-t7 / s0-s15 / c0-c31, oC0 written once with full mask as the last write, texld coordinates t#/r#
    without swizzle/modifier, at most 4 levels of dependent reads, no read of an unwritten temp component."""
    tk = list(struct.unpack('<%dI' % (len(b) // 4), b)); assert tk[0] == 0xFFFF0200 and tk[-1] == 0x0000FFFF
    i = 1; alu = tex = 0; written = {}; level = {}; dcl_t = {}; oc = 0; maxdep = 0; errs = []
    rt = psasm.rtype
    while tk[i] != 0x0000FFFF:
        op = tk[i] & 0xFFFF; n = (tk[i] >> 24) & 0xF; a = tk[i + 1:i + 1 + n]; i += 1 + n
        if op == DEF:
            if not (rt(a[0]) == C and (a[0] & 0x7FF) < 32): errs.append('def register')
            continue
        if op == DCL:
            r = a[1]
            if rt(r) == TX: dcl_t[r & 0x7FF] = (r >> 16) & 0xF
            elif rt(r) == SMP: pass
            else: errs.append('dcl type')
            continue
        d = a[0]; srcs = a[1:]
        dm = (d >> 16) & 0xF
        def readmask(s):
            sw = (s >> 16) & 0xFF; comps = set()
            for c in range(4):
                if op == TEX or dm >> c & 1: comps.add((sw >> (2 * c)) & 3)
            return comps
        lv = 0
        for k, s in enumerate(srcs):
            t_, nn = rt(s), s & 0x7FF
            if op == TEX and k == 1:
                if t_ != SMP: errs.append('texld sampler')
                continue
            comps = readmask(s) if not (op == TEX and k == 0) else {0, 1}     # 2D texld reads .xy of the coordinate
            if t_ == T:
                miss = comps - written.get(nn, set())
                if miss: errs.append('read of unwritten r%d.%s' % (nn, ''.join('xyzw'[c] for c in sorted(miss))))
                lv = max(lv, level.get(nn, 0))
            elif t_ == TX:
                miss = comps - {c for c in range(4) if dcl_t.get(nn, 0) >> c & 1}
                if miss: errs.append('read of undeclared t%d.%s' % (nn, ''.join('xyzw'[c] for c in sorted(miss))))
            elif t_ == C:
                if nn >= 32: errs.append('c index')
            if op == TEX and k == 0:
                if ((s >> 16) & 0xFF) != 0xE4 or (s >> 24) & 0xF: errs.append('texld coordinate swizzle/modifier')
                if t_ not in (T, TX): errs.append('texld coordinate register type')
        if op == TEX:
            tex += 1
            dep = (level.get(srcs[0] & 0x7FF, 0) + 1) if rt(srcs[0]) == T else 0
            maxdep = max(maxdep, dep)
            if dm != 0xF: errs.append('texld write mask')
            written[d & 0x7FF] = written.get(d & 0x7FF, set()) | {0, 1, 2, 3}; level[d & 0x7FF] = dep
        else:
            alu += 1
            if rt(d) == OC:
                oc += 1
                if dm != 0xF: errs.append('oC0 mask')
            elif rt(d) == T:
                nn = d & 0x7FF
                if nn >= 12: errs.append('temp index')
                written[nn] = written.get(nn, set()) | {c for c in range(4) if dm >> c & 1}
                level[nn] = max(level.get(nn, 0) if dm != 0xF else 0, lv)
            else: errs.append('dst type')
    if oc != 1: errs.append('oC0 written %d times' % oc)
    if alu > 64: errs.append('alu %d > 64' % alu)
    if tex > 32: errs.append('tex %d > 32' % tex)
    if maxdep > 4: errs.append('dependent read levels %d > 4' % maxdep)
    return dict(alu=alu, tex=tex, dep_levels=maxdep, errors=errs, bytes=len(b))

if __name__ == '__main__':
    b = tent_ps()
    print('\n'.join(psasm.disasm(b)))
    print(check_ps20(b))
    for nm, bb in (('blur_ps', psasm.blur_ps(0.2270270, 0.3162162, 0.0702703)), ('comp_ps', psasm.comp_ps(4.0))):
        print(nm, check_ps20(bb))
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tent_ps.bin'), 'wb').write(b)
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tent_ps.asm'), 'w').write(ASM_TEXT)
    print(b.hex())
    v = blur_soft_ps(0.2270270, 0.3162162, 0.0702703, 2.5)
    print('\n'.join(psasm.disasm(v))); print('blur_soft_ps', check_ps20(v))
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blur_soft_ps.bin'), 'wb').write(v)
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blur_soft_ps.asm'), 'w').write(BLUR_SOFT_ASM)
    c1 = psasm.comp_ps(1.0); print('comp_ps(1.0)', check_ps20(c1))
    import struct as _s
    def arr(name, bb):
        d = _s.unpack('<%dI' % (len(bb) // 4), bb); o = 'static const DWORD %s[%d] = {\n' % (name, len(d))
        for i in range(0, len(d), 6): o += '  ' + ', '.join('0x%08X' % x for x in d[i:i + 6]) + ',\n'
        return o + '};\n'
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tent_ps.h'), 'w').write(
        '/* generated by psasm_tent.py: tent_ps(), blur_soft_ps(0.2270270,0.3162162,0.0702703,2.5), psasm.comp_ps(1.0) */\n' +
        arr('TPSCODE', b) + arr('VPSCODE', v) + arr('CPS1CODE', c1))
