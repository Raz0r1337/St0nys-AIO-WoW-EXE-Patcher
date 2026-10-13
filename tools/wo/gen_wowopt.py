# Erzeugt die Bytes fuer den wow_optimize-Lader (Nr. 27 in st0ny-dev).
import struct,sys
BASE=0x400C00
IAT={'CloseHandle':0x9DF124,'LoadLibraryA':0x9DF248,'Sleep':0x9DF264,'CreateThread':0x9DF338}
HOOK=0x76E490; HOOK_ORIG=bytes.fromhex('E85B710000'); TARGET=0x7755F0
G={'A1':(0x76EE91,15),'A2':(0x76E4D2,14),'A3':(0x76F1D5,11),
   'B1':(0x76E2A6,10),'B2':(0x76F063,13),'B3':(0x76F331,15),'B4':(0x76F921,15),'B5':(0x76FE91,15)}
def rel(frm,to): return struct.pack('<i',to-(frm+5))
def calli(name): return b'\xFF\x15'+struct.pack('<I',IAT[name])
def piece(name,parts):
    va,size=G[name]; code=b''
    for p in parts:
        if isinstance(p,tuple):   # ('jmp',target) -> E9 rel32
            code+=b'\xE9'+rel(va+len(code),p[1])
        else: code+=p
    assert len(code)<=size,(name,len(code),size)
    return va,code
A1=piece('A1',[b'\x31\xC0',b'\x50',b'\x50',b'\x50',b'\x68'+struct.pack('<I',G['B1'][0]),('jmp',G['A2'][0])])
A2=piece('A2',[b'\x50',b'\x50',calli('CreateThread'),b'\x50',('jmp',G['A3'][0])])
A3=piece('A3',[calli('CloseHandle'),('jmp',TARGET)])
B1=piece('B1',[b'\x68'+struct.pack('<I',3000),('jmp',G['B2'][0])])
B2=piece('B2',[calli('Sleep'),b'\x6A\x00',('jmp',G['B3'][0])])
B3=piece('B3',[b'\x68.dll',b'\x68mize',('jmp',G['B4'][0])])
B4=piece('B4',[b'\x68opti',b'\x68wow_',('jmp',G['B5'][0])])
B5=piece('B5',[b'\x54',calli('LoadLibraryA'),b'\x83\xC4\x14',b'\x33\xC0',b'\xC2\x04\x00'])
HOOKP=(HOOK,b'\xE8'+rel(HOOK,G['A1'][0]))
PIECES=[('A1',A1),('A2',A2),('A3',A3),('B1',B1),('B2',B2),('B3',B3),('B4',B4),('B5',B5)]
def apply(data):
    d=bytearray(data)
    o=HOOK-BASE; assert d[o:o+5]==HOOK_ORIG
    for nm,(va,code) in PIECES:
        o=va-BASE; assert all(b==0xCC for b in d[o:o+len(code)]),nm
    o=HOOK-BASE; d[o:o+5]=HOOKP[1]
    for nm,(va,code) in PIECES: o=va-BASE; d[o:o+len(code)]=code
    return bytes(d)
def ps_bytes(b): return '@(' + ', '.join('0x%02X'%x for x in b) + ')'
if __name__=='__main__':
    for nm,(va,code) in [('HOOK',HOOKP)]+PIECES:
        print(nm,hex(va),'file',hex(va-BASE),len(code),code.hex(' '))
    if len(sys.argv)>2:
        open(sys.argv[2],'wb').write(apply(open(sys.argv[1],'rb').read())); print('written',sys.argv[2])
