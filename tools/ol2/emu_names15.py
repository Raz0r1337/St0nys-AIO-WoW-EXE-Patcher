# Emulation: what does the outline patch's DrawIndexedPrimitive hook (dip) do to the
# floating unit names?  Runs the REAL patched code (ensure, classify, dip, post) of a
# patched Wow.exe in unicorn, with a fake CGxDevice / IDirect3DDevice9 that records every
# SetRenderState / DrawIndexedPrimitive.  A tiny software rasterizer then applies the
# recorded D3D stencil/depth state per pixel, so we can see whether the name text survives.
#
# Frame modelled after CGWorldFrame::Render 0x4F8EA0:
#   pass 0 (0x823CB0(0)): terrain/other M2 (plain), then the outlined units' opaque parts
#            (moved to the end of pass 0 by sortp/draw2) -> dip with CUR = category
#   pass 1/2 (0x823CB0(1/2)): transparent M2 batch (ZWRITE 0, blend), then the name callback
#            0x8230D0 -> 0x7E6090 -> 0x7E5640 -> font batch 0x6C53A0 (3D: DepthTest 1,
#            DepthWrite 1, AlphaRef 1, blend 2) -> 0x6C48D0 -> CGxDevice::Draw(batch, 1)
#            0x6A3620 -> DrawIndexedPrimitive 0x6A36CF (hooked -> dip), then raid icon (ZWRITE 0)
#   post (0x4F91E5)
# Usage: python3 emu_names.py <patched Wow.exe> <outline module name: outline9|outline10>
import sys, struct
S = '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad'
sys.path.insert(0, S + '/tm'); sys.path.insert(0, S + '/ol2'); sys.path.insert(0, S + '/gen')
from emu2 import *
import importlib
EXE = sys.argv[1]
OM = importlib.import_module(sys.argv[2] if len(sys.argv) > 2 else 'outline9')
FIX = '--fix' in sys.argv
D = open(EXE, 'rb').read()
so = [s for s in sections(D) if s[0] == '.outl'][0]
OUT = so[1]
assert so[2] == len(OM.TPL), 'section size mismatch: exe has %X, %s has %X' % (so[2], OM.__name__, len(OM.TPL))

RS = {7: 'ZENABLE', 14: 'ZWRITE', 15: 'ATEST', 22: 'CULL', 23: 'ZFUNC', 24: 'AREF', 27: 'ABLEND', 52: 'STENCILENABLE',
      53: 'SFAIL', 54: 'SZFAIL', 55: 'SPASS', 56: 'SFUNC', 57: 'SREF', 58: 'SMASK', 59: 'SWMASK', 168: 'COLORWRITE',
      19: 'SRCBLEND', 20: 'DESTBLEND', 28: 'FOG', 171: 'BLENDOP', 206: 'SEPALPHA'}
CMPN = {1: 'NEVER', 2: 'LESS', 3: 'EQUAL', 4: 'LESSEQUAL', 5: 'GREATER', 6: 'NOTEQUAL', 7: 'GREATEREQUAL', 8: 'ALWAYS'}
OPN = {1: 'KEEP', 2: 'ZERO', 3: 'REPLACE'}
# hw cache index -> D3DRS (from WoW's SetHwState table 0x6A3C40/0x6A403C/0x6A3FAC)
HW = {14: 0xAB, 168: 0xAC, 27: 0xA7, 15: 0xA8, 24: 0xA9, 28: 0xAA, 22: 0xAF, 23: 0xB1}
W, H = 64, 40


class Frame:
    """One emulated frame with fresh emulator + software framebuffer."""

    def __init__(self, flags, hover, target=False):
        e = self.e = Emu2(D)
        try: e.mu.mem_map(OUT, 0x2000)
        except UcError: pass
        blob = bytearray(D[so[4]:so[4] + so[2]])
        if FIX:
            # SMODE block in dip: SRS(52,1) then SRS(56,2): push 1; push 0x34; push esi; mov eax,[esi]; call [eax+0xE4]; push 2; push 0x38
            pat = bytes.fromhex('6a016a34568b06ff90e40000006a026a38')
            k = blob.find(pat, OM.LAB['dip'])
            assert k > 0 and k < OM.LAB['dip'] + 0x60, hex(k)
            blob[k + 14] = 8                     # STENCILFUNC LESS -> ALWAYS (never discard)
            self.fixed_at = OUT + k + 14
        e.mu.mem_write(OUT, bytes(blob))
        self.DO = {k: OUT + v for k, v in OM.DO.items()}
        self.LAB = {k: OUT + v for k, v in OM.LAB.items()}
        for k, a in OM.FLAGS.items():
            e.mu.mem_write(a, b'\x01' if k in flags else b'\xCC')
        HH = 0x30000000; e.mu.mem_write(HH, b'\0' * 0x100000)
        self.DEV = DEV = HH + 0x10000; self.D3D = D3D = HH + 0x1000; VT = HH + 0x2000; STUBS = HH + 0x3000; GPU = HH + 0x30000
        e.w32(0xC5DF88, DEV); e.w32(DEV, 0xA2E718); e.w32(DEV + 0x1CC, 5); e.w32(DEV + 0x397C, D3D); e.w32(DEV + 0x2900, GPU)
        e.w32(D3D, VT)
        self.d3d = {7: 1, 14: 1, 23: 4, 27: 0, 52: 0, 53: 1, 54: 1, 55: 1, 56: 8, 57: 0, 58: 0xFF, 59: 0xFF, 168: 0xF, 15: 0, 24: 0}
        self.log = []
        self.cur_obj = None
        self.dip_idx = 0
        self.vsc = None
        names = {0x148: ('DIP', 7), 0xE4: ('SRS', 3), 0x178: ('SetVSConst', 4), 0x1A8: ('CreatePS', 3), 0x170: ('SetVS', 2),
                 0x1AC: ('SetPS', 2), 0x164: ('SetFVF', 2), 0x14C: ('DPUP', 5), 0xAC: ('Clear', 7), 0xBC: ('SetVP', 2)}
        for off, (nm, n) in names.items():
            a = STUBS + off; e.w32(VT + off, a)
            e.stub(a, self._mk(nm), n, 4 * n)
        # projection rows c2..c5 (WoW's VS constant shadow at 0xC5EFE8 + 16*reg)
        P = [1.5, 0, 0, 0, 0, 2.0, 0, 0, 0, 0, 1.001, -0.1, 0, 0, 1.0, 0]
        e.mu.mem_write(0xC5F008, struct.pack('<16f', *P))
        e.mu.mem_write(self.DO['VP'], struct.pack('<4I2f', 0, 0, W, H, 0.0, 1.0))
        # units: me 0x333 (player), mouseover NPC 0x222
        POBJ = HH + 0x42000; MOBJ = HH + 0x41000; TOBJ = HH + 0x40000
        self.PM = HH + 0x55000; self.MM = HH + 0x52000; self.TM = HH + 0x50000; self.OTHER = HH + 0x54000
        e.w32(POBJ + 0xB4, self.PM); e.w32(MOBJ + 0xB4, self.MM); e.w32(TOBJ + 0xB4, self.TM)
        PF = HH + 0x57000; e.w32(POBJ + 0xD0, PF); e.mu.mem_write(PF + 0x45, b'\x08')
        OBJ = {0x333: POBJ, 0x222: MOBJ, 0x111: TOBJ}

        def objptr(em, a):
            if a[2] == 0x10: return OBJ.get(a[0], 0) if a[0] == 0x333 else 0
            return OBJ.get(a[0], 0)
        e.stub(0x4D4DB0, objptr, 5, 0)
        e.stub(0x521BF0, lambda em, a: em.w32(a[1], 0xFFFFFF00), 3, 0)
        e.stub(0x4D3790, lambda em, a: (em.mu.reg_write(UC_X86_REG_EDX, 0x0F000000), 0x333)[1], 0, 0)
        MG = HH + 0xF0000; e.w32(MG + 0xA4, 0x38); e.w32(MG + 0xAC, (MG + 0xA8) | 1); e.stub(0x4D3730, lambda em, a: MG, 0, 0)   # leere Objektliste
        e.stub(0x685970, lambda em, a: None, 1, 4)
        e.stub(0x685A70, lambda em, a: None, 0, 0)
        e.stub(0x4F6F90, lambda em, a: None, 0, 0)
        GTC = HH + 0x3800; e.w32(0x9DF174, GTC); e.stub(GTC, lambda em, a: 0, 0, 0)
        e.w32(0xCD754C, HH + 0x60000)
        def guid(a, lo): e.w32(a, lo); e.w32(a + 4, 0x0F000000 if lo else 0)
        guid(0xBD07B0, 0x222 if target else 0)
        guid(0xBD07A0, 0x222 if hover else 0)
        for i in range(4): guid(0xBD1948 + 8 * i, 0)
        e.w32(0xBEB608, 0)
        e.w32(0xD43020, 1)                       # shaders on
        # software framebuffer
        self.stencil = [[0] * W for _ in range(H)]
        self.depth = [[1.0] * W for _ in range(H)]
        self.color = [['.'] * W for _ in range(H)]

    # ---- fake D3D -----------------------------------------------------------------------
    def _mk(self, nm):
        def f(em, args):
            if nm == 'SRS':
                self.d3d[args[1]] = args[2]
                self.log.append(('SRS', RS.get(args[1], args[1]), args[2]))
            elif nm == 'SetVSConst':
                self.vsc = struct.unpack('<16f', bytes(em.mu.mem_read(args[2], 64)))
                self.log.append(('SetVSConst', args[1]))
            elif nm == 'DIP':
                self.log.append(('DIP', self.cur_obj, self.dip_idx, dict(self.d3d)))
                self.raster(dict(self.d3d))
                self.dip_idx += 1
            else:
                self.log.append((nm,) + tuple(args[1:3]))
            return 0
        return f

    # ---- WoW-side state application (what 0x6A5940 -> 0x6A4C30 handlers would send) --------
    def wow_state(self, **st):
        m = {'zwrite': 14, 'ablend': 27, 'zfunc': 23, 'atest': 15, 'aref': 24, 'colorwrite': 168}
        for k, v in st.items():
            rs = m[k]
            cache = self.DEV + 0x3BC4 + 4 * HW[rs]
            if self.e.r32(cache) != v:
                self.d3d[rs] = v
                self.e.w32(cache, v)
                self.log.append(('wowSRS', RS[rs], v))

    # ---- objects (pixel coverage, depth, glyph) ----------------------------------------------
    def rect(self, x0, y0, x1, y1): return {(x, y) for y in range(y0, y1) for x in range(x0, x1)}

    def raster(self, st):
        o = self.cur_obj
        cov = o['cov']
        if o.get('outlined') and self.vsc is not None and self.dip_idx > 0:
            # copy: shift = c5*FX added to c2 row; P has c5 = (0,0,1,0) -> FX = MAT[2]
            fx = self.vsc[2]; fy = self.vsc[6]
            dx = int(round(fx * W / 2)); dy = int(round(-fy * H / 2))
            if dx or dy: cov = {(x + dx, y + dy) for (x, y) in o['cov']}
        def cmp(f, a, b):
            return {1: False, 2: a < b, 3: a == b, 4: a <= b, 5: a > b, 6: a != b, 7: a >= b, 8: True}[f]
        def op(code, old, ref, wm):
            new = {1: old, 2: 0, 3: ref}[code]
            return (old & ~wm) | (new & wm)
        for (x, y) in cov:
            if not (0 <= x < W and 0 <= y < H): continue
            s = self.stencil[y][x]
            if st[52]:
                ref, msk, wm = st[57], st[58], st[59]
                if not cmp(st[56], ref & msk, s & msk):
                    self.stencil[y][x] = op(st[53], s, ref, wm)
                    continue                                  # stencil fail -> pixel discarded
            zf = st[23] if st.get(7, 1) else 8
            if not cmp(zf, o['z'], self.depth[y][x]):
                if st[52]: self.stencil[y][x] = op(st[54], s, st[57], st[59])
                continue
            if st[52]: self.stencil[y][x] = op(st[55], s, st[57], st[59])
            if st[14]: self.depth[y][x] = o['z']
            if st[168]: self.color[y][x] = o['ch']

    def call(self, name, **regs):
        r = {}
        if 'eax' in regs: r[UC_X86_REG_EAX] = regs['eax']
        return self.e.call(self.LAB[name], (), regs=r)[0]

    def draw(self, obj, cur=0):
        """One WoW DrawIndexedPrimitive through the hook (push edx; call dip)."""
        self.cur_obj = obj; self.dip_idx = 0; self.vsc = None
        self.e.w32(self.DO['CUR'], cur)
        self.e.call(self.LAB['dip'], (self.D3D, 4, 0, 0, 100, 0, 50))
        self.e.w32(self.DO['CUR'], 0)


def run(title, flags, hover, target=False, show=False):
    f = Frame(flags, hover, target)
    f.call('ensure')
    n = f.e.r32(f.DO['NUNITS'])
    cat_me = f.call('classify', eax=f.PM); cat_npc = f.call('classify', eax=f.MM)
    # scene: terrain behind everything (z 0.9), me at left, NPC at right, NPC name above NPC
    terrain = dict(name='terrain', cov=f.rect(0, 0, W, H), z=0.9, ch=',')
    me = dict(name='me', cov=f.rect(6, 20, 12, 38), z=0.4, ch='M', outlined=cat_me != 0)
    npc = dict(name='npc', cov=f.rect(34, 18, 40, 38), z=0.5, ch='N', outlined=cat_npc != 0)
    trans = dict(name='transparent M2', cov=f.rect(54, 2, 60, 6), z=0.3, ch='t')
    # name text: 3 rows, 4..7 px above the NPC's head (outside the 2/4/6 px ring) - like in game
    nm = dict(name='NAME', cov=f.rect(29, 8, 45, 11), z=0.5, ch='#')
    icon = dict(name='raid icon', cov=f.rect(2, 1, 4, 3), z=0.1, ch='*')
    # --- pass 0 ---
    f.wow_state(zwrite=1, ablend=0, zfunc=4, colorwrite=0xF)
    f.draw(terrain)
    f.wow_state(zwrite=1, ablend=0, zfunc=4, colorwrite=0xF)
    f.draw(me, cat_me)
    f.wow_state(zwrite=1, ablend=0, zfunc=4, colorwrite=0xF)
    f.draw(npc, cat_npc)
    marked = f.e.r32(f.DO['MARKED'])
    # --- pass 1/2 ---
    f.wow_state(zwrite=0, ablend=1, zfunc=4, colorwrite=0xF)
    f.draw(trans)
    log0 = len(f.log)
    # 3D font batch 0x6C53A0: DepthTest 1 (ZFUNC LESSEQUAL), DepthWrite 1, AlphaRef 1, blend 2, cull none
    f.wow_state(zwrite=1, ablend=1, zfunc=4, atest=1, aref=1, colorwrite=0xF)
    f.draw(nm)
    name_log = f.log[log0:]
    # raid icon 0x7E58A8..: DepthTest 0 (ZFUNC ALWAYS), DepthWrite 0
    f.wow_state(zwrite=0, ablend=1, zfunc=8, atest=1, aref=1)
    f.draw(icon)
    smode_after = f.e.r32(f.DO['SMODE'])
    st_name = [x for x in name_log if x[0] == 'DIP'][0][3]
    drawn = sum(1 for (x, y) in nm['cov'] if f.color[y][x] == '#')
    print('=== %s' % title)
    print('    flags=%s hover=%s target=%s  units=%d cat(me)=%d cat(npc)=%d  MARKED before names=%d' % (
        ','.join(flags) or 'none', hover, target, n, cat_me, cat_npc, marked))
    print('    calls between WoW state and name DIP: %s' % [x[:3] for x in name_log if x[0] in ('SRS', 'wowSRS')])
    print('    D3D state at name DIP: STENCILENABLE=%d SFUNC=%s SREF=%d SMASK=0x%X SPASS=%s SFAIL=%s ZWRITE=%d ZFUNC=%s ABLEND=%d' % (
        st_name[52], CMPN[st_name[56]], st_name[57], st_name[58], OPN.get(st_name[55]), OPN.get(st_name[53]), st_name[14],
        CMPN[st_name[23]], st_name[27]))
    print('    name pixels drawn: %d of %d   (SMODE left on after frame: %d)' % (drawn, len(nm['cov']), smode_after))
    if show:
        for y in range(H - 18): print('      ' + ''.join(f.color[y]) + '   ' + ''.join('%X' % min(15, v >> 4) if v >= 0x10 else ('%d' % v if v else '.') for v in f.stencil[y]))
    return drawn, len(nm['cov'])


if __name__ == '__main__':
    print('exe: %s  (%s)%s' % (EXE, OM.__name__, '  WITH FIX: SMODE STENCILFUNC=ALWAYS' if FIX else ''))
    run('A: no options (target+mouseover only), not hovering', [], hover=False)
    run('B: no options, HOVERING the NPC', [], hover=True, show=True)
    run('C: hidden (dev default), not hovering', ['FHIDDEN'], hover=False)
    run('D: hidden, hovering', ['FHIDDEN'], hover=True)
    run('E: hidden,wallsgroup, hovering', ['FHIDDEN', 'FWALLSGRP'], hover=True)
    run('F: hidden,raid,walls, hovering', ['FHIDDEN', 'FRAID', 'FWALLS'], hover=True, show=True)
    run('G: no options, NPC is the target (not hovered)', [], hover=False, target=True)
