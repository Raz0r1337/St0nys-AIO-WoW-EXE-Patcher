import glyph,holdrep
from emitps import *
g=emit(glyph.tpl,0,glyph.SRC,glyph.absf,glyph.relf)
open('glyph_body.ps1','w').write('\n'.join(g)+'\n')
h=emit(holdrep.code,holdrep.CODE_OFF,holdrep.src(B1),holdrep.absf,holdrep.relf,comment_src=holdrep.src0(None))
open('hold_body.ps1','w').write('\n'.join(h)+'\n')
# check geometry in place (fixed addresses)
import capstone
from asmgen import md
lines=[]
srcl=[l.strip() for l in glyph.CHECK.strip().split('\n') if l.strip()]
ins=list(md.disasm(glyph.chk,0x6C7480)); k=0
for t in srcl:
    if t.endswith(':'): lines.append('    # %s'%t); continue
    i=ins[k]; k+=1
    lines.append('    %-58s # %s'%('AddRaw $k @(%s)'%hx(bytes(i.bytes)),' '.join(t.split())))
open('check_body.ps1','w').write('\n'.join(lines)+'\n')
print(glyph.LAB, len(glyph.tpl), holdrep.LAB, hex(len(holdrep.TPL)), len(glyph.chk))
