from lights import *
from emitps import emit, hx
import struct
s=src(B1)
lines=emit(code,CODE_OFF,s,absf,relf,comment_src=src(B1,sym=True))
d=data()
L=LAB
out=[]
out.append("function Add-MoreLights {")
out.append("    $REJ = 0x834FC7; $EVICT = 0x834FCD; $TL = 0x83510E; $UPM2 = 0x873E85; $UPWMO = 0x7A91A9; $FFCNT = 0x835483; $FFLEA = 0x8354CB")
out.append("    Assert-Bytes ($REJ - 0x400C00) @(0x0F, 0x8A, 0xBF, 0x00, 0x00, 0x00) 'Mehr Lichter'")
out.append("    Assert-Bytes ($EVICT - 0x400C00) @(0x83, 0xFE, 0x04, 0x72, 0x03, 0x83, 0xEE, 0x01) 'Mehr Lichter'")
out.append("    Assert-Bytes ($TL - 0x400C00) @(0x8B, 0x4E, 0x14, 0x83, 0xE1, 0x60) 'Mehr Lichter'")
out.append("    Assert-Bytes ($UPM2 - 0x400C00) @(0xE8, 0x76, 0xEA, 0xFF, 0xFF) 'Mehr Lichter'")
out.append("    Assert-Bytes ($UPWMO - 0x400C00) @(0xE8, 0x52, 0x97, 0x0C, 0x00) 'Mehr Lichter'")
out.append("    Assert-Bytes ($FFCNT - 0x400C00) @(0x8B, 0x9E, 0xA4, 0x00, 0x00, 0x00) 'Mehr Lichter'")
out.append("    Assert-Bytes ($FFLEA - 0x400C00) @(0x8D, 0x84, 0x9E, 0x84, 0x00, 0x00, 0x00) 'Mehr Lichter'")
out.append("    Assert-Bytes 0x%X @(%s) 'Mehr Lichter'"%(RESET_VA-0x400C00,hx(bytes.fromhex(RESET_ORIG))))
for va,orig,new,gxo,c in FF:
    out.append("    Assert-Bytes 0x%X @(%s) 'Mehr Lichter'"%(va-0x400C00,hx(bytes.fromhex(orig))))
out.append("    $loc = Add-CodeSection '.lght' 0x%X -Writable"%len(TPL))
out.append("    $CAVE = $loc[0]")
out.append("    $GX = $CAVE + 0x%X                                        # 8 Gx-Lichtslots zu je 0x48 Byte"%GX)
out.append("    $c = New-Object System.Collections.Generic.List[byte]")
out.append("    for ($i = 0; $i -lt 0x%X; $i++) { $c.Add([byte]0) }                 # Daten, beginnen bei 0"%CODE_OFF)
st=DO['EXTBUF']+8*16
out.append("    # Zusatzlichter c244 (Abschwaechung 0) vor der ersten Benutzung = 1.0")
out.append("    $i = 0x%X; foreach ($b in [byte[]]@(%s)) { $c[$i] = $b; $i++ }"%(st,hx(d[st:st+16])))
assert all(d[k]==0 for k in range(len(d)) if not (st<=k<st+16))
out+=lines
out.append("    if ($c.Count -ne 0x%X) { throw 'Mehr Lichter: Sektion hat die falsche Groesse.' }"%len(TPL))
out.append("    Patch $loc[1] $c.ToArray()")
out.append("    # AddLight: abgewiesenes bzw. verdraengtes 5. Licht in die Zusatzliste")
out.append("    Patch ($REJ - 0x400C00) (Get-Rel32 @(0x0F, 0x8A) $REJ ($CAVE + 0x%X))"%L['cave_reject'])
out.append("    Patch ($EVICT - 0x400C00) ([byte[]]((Get-Rel32 @(0xE8) $EVICT ($CAVE + 0x%X)) + [byte[]](0x90, 0x90, 0x90)))"%L['cave_evict'])
out.append("    # TransformLights: Zusatzlichter ebenfalls in Kamerakoordinaten")
out.append("    Patch ($TL - 0x400C00) ([byte[]]((Get-Rel32 @(0xE9) $TL ($CAVE + 0x%X)) + [byte[]](0x90)))"%L['cave_tl'])
out.append("    # Shader-Weg (Modelle, Gebaeude): Zusatzlichter nach VS c236-c246")
out.append("    Patch ($UPM2 - 0x400C00) (Get-Rel32 @(0xE8) $UPM2 ($CAVE + 0x%X))"%L['cll_ex'])
out.append("    Patch ($UPWMO - 0x400C00) (Get-Rel32 @(0xE8) $UPWMO ($CAVE + 0x%X))"%L['cll_ex'])
out.append("    # Weg ohne Shader: SetupGxLights nimmt die 7 naechsten Lichter (naechstes zuerst)")
out.append("    Patch ($FFCNT - 0x400C00) ([byte[]]((Get-Rel32 @(0xE8) $FFCNT ($CAVE + 0x%X)) + [byte[]](0x90)))"%L['cave_ff'])
out.append("    Patch ($FFLEA - 0x400C00) ([byte[]]([byte[]](0x8D, 0x04, 0x9D) + [BitConverter]::GetBytes([uint32]($CAVE + 0x%X))))"%DO['GXLIST'])
out.append("    # Gx-Geraet: 4 Lichtslots -> 8 Slots im neuen Feld")
rc=reset_code(0x1000000)
# reset code with GX placeholders: two abs values
r1=struct.pack('<I',0x1000000+0x40); r2=struct.pack('<I',0x1000000+0x40+8*0x48)
i1=rc.find(r1); i2=rc.find(r2); assert i1>0 and i2>0
out.append("    $r = New-Object System.Collections.Generic.List[byte]")
out.append("    AddRaw $r @(%s); AddLE32 $r ($GX + 0x40)"%hx(rc[:i1]))
out.append("    AddRaw $r @(%s); AddLE32 $r ($GX + 0x%X)"%(hx(rc[i1+4:i2]),0x40+8*0x48))
out.append("    AddRaw $r @(%s)"%hx(rc[i2+4:]))
out.append("    Patch 0x%X $r.ToArray()                                  # ResetLights: Schleife ueber 8 Slots"%(RESET_VA-0x400C00))
for va,orig,new,gxo,c in FF:
    o=va-0x400C00; ob=bytes.fromhex(orig); nb=bytes.fromhex(new)
    if gxo is None:
        out.append("    Patch 0x%X @(%s)%s# %s"%(o,hx(nb),' '*max(1,40-len(hx(nb))),c))
    else:
        pad=len(ob)-len(nb)-4
        tail=" + [byte[]](%s)"%hx(b'\x90'*pad) if pad else ""
        out.append("    Patch 0x%X ([byte[]]([byte[]](%s) + [BitConverter]::GetBytes([uint32]($GX + 0x%X))%s))   # %s"%(o,hx(nb),gxo,tail,c))
out.append("}")
open('lights_ps.txt','w').write('\n'.join(out)+'\n')
print(len(out))
