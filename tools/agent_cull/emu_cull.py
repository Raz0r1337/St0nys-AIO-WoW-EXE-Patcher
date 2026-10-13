# Emulation test of the cull hook: runs the REAL 0x793450 (plus the real 0x823F10, 0x983D20,
# 0x6DED60 it calls) with the hook from cullhook.py installed at 0x7934C6, on fake entities/models.
import sys, struct, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unicorn import *
from unicorn.x86_const import *
import keystone
import cullhook as CH

ORI = '/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
D = open(ORI, 'rb').read()
ks = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32)
CAVE = 0x40000000; DATA = 0x40200000; HEAP = 0x30000000; STK = 0x20000000; SENT = 0x31000000
GMODE = DATA + 0x0; GRPN = DATA + 0x4; UNITS = DATA + 0x10
OTHERCB = CAVE + 0xF00          # a non-object entity callback (returns 1)
CB = 0x4F9F70                   # object entity callback (stubbed)


def build(gmode, grpn, guids):
    mu = Uc(UC_ARCH_X86, UC_MODE_32)
    mu.mem_map(0x400000, 0x9DF000 - 0x400000); mu.mem_write(0x400000, D[:0x400]); mu.mem_write(0x401000, D[0x400:0x400 + 0x5DD400])
    mu.mem_map(0x9DF000, 0xAB6000 - 0x9DF000); mu.mem_write(0x9DF000, D[0x5DD800:0x5DD800 + 0xD6800])
    mu.mem_map(0xAB6000, 0xDD1000 - 0xAB6000); mu.mem_write(0xAB6000, D[0x6B4000:0x6B4000 + 0x78E00])
    for b in (STK, HEAP, CAVE, DATA, SENT): mu.mem_map(b, 0x100000 if b != SENT else 0x1000)
    src = CH.CULL.replace('{GMODE}', '0x%X' % GMODE).replace('{GRPN}', '0x%X' % GRPN).replace('{UNITS}', '0x%X' % UNITS)
    src += '\nensure:\n  mov eax,0x0BADBAD1\n  mov ecx,0x0BADBAD2\n  mov edx,0x0BADBAD3\n  ret\n'
    code = bytes(ks.asm(src, CAVE)[0]); mu.mem_write(CAVE, code)
    mu.mem_write(OTHERCB, bytes([0xB8, 1, 0, 0, 0, 0xC3]))
    # patch the site
    assert bytes(mu.mem_read(CH.SITE, 5)) == CH.ORIG
    mu.mem_write(CH.SITE, b'\xE9' + struct.pack('<i', CAVE - (CH.SITE + 5)))
    w = lambda a, v: mu.mem_write(a, struct.pack('<I', v & 0xFFFFFFFF))
    wf = lambda a, v: mu.mem_write(a, struct.pack('<f', v))
    w(GMODE, gmode); w(GRPN, grpn)
    for k, (lo, hi) in enumerate(guids): w(UNITS + 24 * k, lo); w(UNITS + 24 * k + 4, hi)
    # TSLists (link offset 0xC8): not-visible 0xCDB0A4, visible 0xCDB098
    for L in (0xCDB0A4, 0xCDB098): w(L, 0xC8); w(L + 4, L + 4); w(L + 8, (L + 4) | 1)
    w(0xCD8798, 0)                                    # frustum stack depth
    for i, (a, b, c) in enumerate([(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]):
        for j, v in enumerate((a, b, c, 1000.0)): wf(0xCDB168 + 16 * i + 4 * j, v)
    for a in (0xCD8F5C, 0xCD8F60, 0xCD8F64): wf(a, 0.0)   # camera position
    return mu, w, wf


def r32(mu, a): return struct.unpack('<I', bytes(mu.mem_read(a, 4)))[0]


def run(gmode, grpn, guids, ents):
    mu, w, wf = build(gmode, grpn, guids)
    calls = []
    scene = HEAP + 0x80000
    def hook(uc, addr, size, ud):
        if addr == CB:
            sp = uc.reg_read(UC_X86_REG_ESP)
            ret, a0, reason, lo, hi, a4 = struct.unpack('<6I', bytes(uc.mem_read(sp, 24)))
            calls.append((reason, lo, hi))
            uc.reg_write(UC_X86_REG_EAX, 1); uc.reg_write(UC_X86_REG_ESP, sp + 4); uc.reg_write(UC_X86_REG_EIP, ret)
    mu.hook_add(UC_HOOK_CODE, hook, begin=CB, end=CB)
    E = []
    for i, e in enumerate(ents):
        ea = HEAP + 0x1000 * i; ma = HEAP + 0x40000 + 0x1000 * i
        w(ea + 0x34, ma); wf(ea + 0x38, e['pos'][0]); wf(ea + 0x3C, e['pos'][1]); wf(ea + 0x40, e['pos'][2]); wf(ea + 0x44, 1.0)
        mu.mem_write(ea + 0x25, bytes([e.get('st', 2)]))
        w(ea + 0x7C, e.get('f7c', 0x8800)); w(ea + 0x90, e.get('cb', CB)); w(ea + 0x94, 0)
        w(ea + 0x98, e['guid'][0]); w(ea + 0x9C, e['guid'][1]); w(ea + 0xA0, 0)
        w(ma + 0x4, 0); w(ma + 0x10, 0x1 | 0x2000); w(ma + 0x28, scene); w(ma + 0x48, e.get('parent', 0))
        E.append((ea, ma))
        # link into not-visible list with the game's own TSList append (0x6DED60, thiscall, ret 4)
        sp = STK + 0xF0000; mu.mem_write(sp - 8, struct.pack('<II', SENT, ea))
        mu.reg_write(UC_X86_REG_ESP, sp - 8); mu.reg_write(UC_X86_REG_ECX, 0xCDB0A4)
        mu.emu_start(0x6DED60, SENT, count=10000)
    # run 0x793450 (cdecl, no args)
    sp = STK + 0xF0000; mu.mem_write(sp - 4, struct.pack('<I', SENT))
    regs = {UC_X86_REG_EBX: 0x11111111, UC_X86_REG_ESI: 0x22222222, UC_X86_REG_EDI: 0x33333333, UC_X86_REG_EBP: 0x44444444}
    for r, v in regs.items(): mu.reg_write(r, v)
    mu.reg_write(UC_X86_REG_ESP, sp - 4)
    mu.emu_start(0x793450, SENT, count=200000)
    ok = mu.reg_read(UC_X86_REG_ESP) == sp and all(mu.reg_read(r) == v for r, v in regs.items())
    # results
    res = []
    vis = []
    x = r32(mu, 0xCDB098 + 8)
    while not (x & 1) and x: vis.append(x); x = r32(mu, x + 0xC8 + 4)
    upd = []
    x = r32(mu, scene + 0x28)
    while x: upd.append(x); x = r32(mu, x + 0x44)
    for i, (ea, ma) in enumerate(E):
        res.append(dict(i=i, flags='%05X' % r32(mu, ma + 0x10), st=bytes(mu.mem_read(ea + 0x25, 1))[0],
                        in_visible=ea in vis, in_update=ma in upd, light=(r32(mu, ma + 0x2AC) == 0x780CD0)))
    notvis_empty = (r32(mu, 0xCDB0A4 + 8) & 1) == 1
    return ok, calls, res, notvis_empty


G1, G2, G3, G4 = (0x1001, 0), (0x1002, 0), (0x1003, 0), (0x1004, 0)
ents = [dict(guid=G1, pos=(50, 0, 0)),                 # 0 forced, in frustum, far (>33 yd)
        dict(guid=G4, pos=(10, 0, 0)),                 # 1 not in list, near (<33 yd)
        dict(guid=G2, pos=(5000, 0, 0), st=1),         # 2 in list but outside frustum (beyond "far plane")
        dict(guid=G1, pos=(60, 0, 0), cb=OTHERCB),     # 3 same GUID but not an object entity
        dict(guid=G3, pos=(70, 0, 0)),                 # 4 GUID at index >= GRPN (target/mouseover entry)
        dict(guid=G2, pos=(20, 0, 0), parent=0x30090000)]  # 5 forced, attached root model -> 0x80/0x20000
for title, gm in (('GMODE=1 (through walls, party/raid)', 1), ('GMODE=0 (no group through walls)', 0)):
    ok, calls, res, empty = run(gm, 2, [G1, G2, G3], ents)
    print('==', title, '| regs/stack preserved:', ok, '| not-visible list drained:', empty)
    print('   callback calls (reason, guid):', [(r, hex(lo)) for r, lo, hi in calls])
    for r in res: print('   ', r)


# ---- part 2: after 0x793450, run the game's visible-list pass 0x793980 (real code) and check that the
# forced model's "offscreen" flag 0x2000 (which makes 0x823930 skip its geometry batches at 0x823A00)
# is recomputed. Stubs: 0x824F00 (loaded+textures) -> 1, 0x825A60 (model AABB) -> box around entity,
# 0x4D4DB0 (ObjectPtr) -> 0, 0x422130 -> 0. Entity flags 0x8000 (no 0x800: skips the blob-shadow branch).
def run2():
    ents2 = [dict(guid=G1, pos=(50, 0, 0), f7c=0x8000), dict(guid=G4, pos=(60, 0, 0), f7c=0x8000)]
    mu, w, wf = build(1, 2, [G1, G2, G3])
    scene = HEAP + 0x80000
    def stub(addr, ret, pop, fn=None):
        def h(uc, a, s, ud):
            sp = uc.reg_read(UC_X86_REG_ESP); r = struct.unpack('<I', bytes(uc.mem_read(sp, 4)))[0]
            if fn: fn(uc, sp)
            uc.reg_write(UC_X86_REG_EAX, ret); uc.reg_write(UC_X86_REG_ESP, sp + 4 + pop); uc.reg_write(UC_X86_REG_EIP, r)
        mu.hook_add(UC_HOOK_CODE, h, begin=addr, end=addr)
    def box(uc, sp):
        out = struct.unpack('<I', bytes(uc.mem_read(sp + 4, 4)))[0]
        uc.mem_write(out, struct.pack('<6f', 49, -1, -1, 51, 1, 1))
    stub(CB, 1, 0); stub(0x824F00, 1, 8); stub(0x825A60, 0, 8, box); stub(0x4D4DB0, 0, 0); stub(0x422130, 0, 0)
    E = []
    for i, e in enumerate(ents2):
        ea = HEAP + 0x1000 * i; ma = HEAP + 0x40000 + 0x1000 * i
        w(ea + 0x34, ma); wf(ea + 0x38, e['pos'][0]); wf(ea + 0x3C, 0); wf(ea + 0x40, 0); wf(ea + 0x44, 1.0)
        mu.mem_write(ea + 0x25, bytes([2])); w(ea + 0x7C, e['f7c']); w(ea + 0x90, CB)
        w(ea + 0x98, e['guid'][0]); w(ea + 0x9C, e['guid'][1])
        w(ma + 0x10, 0x1 | 0x2000); w(ma + 0x28, scene)
        E.append((ea, ma))
        sp = STK + 0xF0000; mu.mem_write(sp - 8, struct.pack('<II', SENT, ea))
        mu.reg_write(UC_X86_REG_ESP, sp - 8); mu.reg_write(UC_X86_REG_ECX, 0xCDB0A4); mu.emu_start(0x6DED60, SENT, count=10000)
    for fn in (0x793450, 0x793980):
        sp = STK + 0xF0000; mu.mem_write(sp - 4, struct.pack('<I', SENT)); mu.reg_write(UC_X86_REG_ESP, sp - 4)
        mu.emu_start(fn, SENT, count=500000)
        print('   after %X: flags forced=%05X other=%05X' % (fn, r32(mu, E[0][1] + 0x10), r32(mu, E[1][1] + 0x10)))
print('== part 2: visible-list pass 0x793980 recomputes 0x2000 for the forced model only')
run2()
