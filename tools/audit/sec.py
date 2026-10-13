# python3 sec.py N  - neue Sektionen in run/p_N.exe disassemblieren
import sys, struct, h
from diffrep import target_info
a=sys.argv[1]; new=open(a if not a.isdigit() else 'run/p_%s.exe'%a,'rb').read()
pe=struct.unpack_from('<I',new,0x3c)[0]; nsec=struct.unpack_from('<H',new,pe+6)[0]; optsz=struct.unpack_from('<H',new,pe+20)[0]
sec=pe+24+optsz
for i in range(6,nsec):
    o=sec+i*40; name=new[o:o+8].rstrip(b'\0').decode(); vs,va,rs,ro=struct.unpack_from('<IIII',new,o+8); ch=struct.unpack_from('<I',new,o+36)[0]
    print('== section %s VA %#x vsize %#x raw %#x rsize %#x chars %#x' % (name, 0x400000+va, vs, ro, rs, ch))
    data=new[ro:ro+vs]; base=0x400000+va
    # Disassemblieren bis zum Ende; Daten (viele 00) werden als add erscheinen
    start=int(sys.argv[2],16) if len(sys.argv)>2 else 0
    stop=int(sys.argv[3],16) if len(sys.argv)>3 else vs
    for ins in h.md.disasm(data[start:stop], base+start):
        ti=target_info(ins,new) if ins.address else []
        print('  '+h.fmt(ins)+('   ; '+' | '.join(ti) if ti else ''))
