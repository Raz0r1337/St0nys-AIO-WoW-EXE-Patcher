from outline import *
from emitps import emit, hx
import struct
s=src(B1)
lines=emit(code,CODE_OFF,s,absf,relf,comment_src=src(B1,sym=True))
d=data()
out=[]
out.append("function Add-Outline {")
out.append("    $VPSITE = 0x6A9B10; $BATCH = 0x823A81; $DIPSITE = 0x6A36C8; $POSTSITE = 0x4F91E5")
out.append("    Assert-Bytes ($VPSITE - 0x400C00) @(0x8B, 0x86, 0x7C, 0x39, 0x00, 0x00) 'Umrandung'")
out.append("    Assert-Bytes ($BATCH - 0x400C00) @(0x8B, 0xCE, 0xE8, 0x28, 0xC9, 0xFF, 0xFF) 'Umrandung'")
out.append("    Assert-Bytes ($DIPSITE - 0x400C00) @(0x8B, 0x88, 0x48, 0x01, 0x00, 0x00, 0x52, 0xFF, 0xD1) 'Umrandung'")
out.append("    Assert-Bytes ($POSTSITE - 0x400C00) @(0xE8, 0xA6, 0xDD, 0xFF, 0xFF) 'Umrandung'")
out.append("    Assert-Bytes 0x62CCBC @(0x4D) 'Umrandung'")
out.append("    $loc = Add-CodeSection '.outl' 0x%X -Writable"%len(TPL))
out.append("    $CAVE = $loc[0]")
out.append("    $c = New-Object System.Collections.Generic.List[byte]")
# data: emit as rows of 16
nz=[i for i in range(len(d)) if d[i]]
out.append("    for ($i = 0; $i -lt 0x%X; $i++) { $c.Add([byte]0) }                 # Daten, beginnen bei 0"%CODE_OFF)
blocks=[(DO['VERTS'],80,'Viereck (4 Ecken: x, y, z=0, rhw=1, Farbe)'),(DO['OFFS'],64,'Versatz der 8 unsichtbaren Kopien in Pixeln (x, y)'),(DO['PSCODE'],20,'Pixelshader ps_1_1: mov r0, v0'),(DO['TWO'],12,'Konstanten 2.0, -2.0, 0.5')]
for st,n,nm in blocks:
    out.append("    # %s"%nm)
    out.append("    $i = 0x%X; foreach ($b in [byte[]]@(%s)) { $c[$i] = $b; $i++ }"%(st,hx(d[st:st+n])))
assert all(d[k]==0 for k in range(len(d)) if not any(st<=k<st+n for st,n,_ in blocks))
out+=lines
out.append("    Patch $loc[1] $c.ToArray()")
L=LAB
out.append("    Patch ($VPSITE - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $VPSITE ($CAVE + 0x%X)) + [byte[]](0x90)))"%L['vpcap'])
out.append("    Patch ($BATCH - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $BATCH ($CAVE + 0x%X)) + [byte[]](0x90, 0x90)))"%L['batch'])
out.append("    Patch ($DIPSITE - 0x400C00) ([byte[]]([byte[]](0x52) + (Get-Rel32 @(0xE8) ($DIPSITE + 1) ($CAVE + 0x%X)) + [byte[]](0x90, 0x90, 0x90)))"%L['dip'])
out.append("    Patch ($POSTSITE - 0x400C00) (Get-Rel32 @(0xE8) $POSTSITE ($CAVE + 0x%X))"%L['post'])
out.append("    Patch 0x62CCBC @(0x4B)                                     # Tiefenpuffer D24X8 -> D24S8 (mit Stencil)")
out.append("}")
open('outline_ps.txt','w').write('\n'.join(out)+'\n')
print(len(out))
