# Assemble the cull hook inside outline10's own template machinery (without modifying outline10.py):
# src() + CULL, relocation at two bases, label offsets. Verifies placeholders/labels resolve.
import sys, os
S = '/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad'
sys.path.insert(0, S + '/ol2'); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import outline10 as O
import cullhook as CH
orig_src = O.src
def src2(base, sym=False):
    s = orig_src(base, sym)
    A = {k: '0x%X' % ((base or 0) + v) for k, v in O.DO.items()}
    c = CH.CULL
    for k in ('GMODE', 'GRPN', 'UNITS'): c = c.replace('{%s}' % k, A[k])
    return s + c
O.src = src2
code, absf, relf = O.reloc2()
lab = O.label_offsets(src2(O.B1), O.B1 + O.CODE_OFF, ['cull', 'ensure'])
print('code size old %X new %X (+%d bytes), abs fixups %d, rel fixups %d' % (len(O.code), len(code), len(code) - len(O.code), len(absf), len(relf)))
print('cull at section offset %X, ensure at %X' % (O.CODE_OFF + lab['cull'], O.CODE_OFF + lab['ensure']))
from asmgen import dis
off = lab['cull']
dis(code[off:off + 0xD0], O.B1 + O.CODE_OFF + off)
