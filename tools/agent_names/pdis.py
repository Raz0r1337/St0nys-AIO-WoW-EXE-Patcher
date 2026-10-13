import sys,capstone,struct
P=sys.argv[1]
D=open(P,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
e=struct.unpack_from('<I',D,0x3C)[0]; n=struct.unpack_from('<H',D,e+6)[0]; opt=struct.unpack_from('<H',D,e+20)[0]
secs=[]
for i in range(n):
    so=e+24+opt+40*i
    nm=D[so:so+8].rstrip(b'\0').decode()
    vs,va,rs,ro=struct.unpack_from('<IIII',D,so+8)
    secs.append((nm,0x400000+va,vs,rs,ro))
def va2off(v):
    for nm,va,vs,rs,ro in secs:
        if va<=v<va+max(vs,rs): return v-va+ro
    raise Exception(hex(v))
if sys.argv[2]=='secs':
    for s in secs: print(s[0],hex(s[1]),hex(s[2]),hex(s[3]),hex(s[4]))
    sys.exit()
va=int(sys.argv[2],16); cnt=int(sys.argv[3]) if len(sys.argv)>3 else 40
o=va2off(va)
for i in md.disasm(D[o:o+cnt*10],va):
    print('%08X  %-22s %s %s'%(i.address,i.bytes.hex()[:22],i.mnemonic,i.op_str)); cnt-=1
    if cnt<=0: break
