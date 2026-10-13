import capstone, struct, sys
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
def sec(off):
    if off<0x400: return 'hdr',None
    if off<0x5DD800: return '.text',off+0x400C00
    if off<0x6B4000: return '.rdata',off-0x5DD800+0x9DF000
    if off<0x72CE00: return '.data',off-0x6B4000+0xAB6000
    if off<0x72DE00: return '.zdata',off-0x72CE00+0x9D1000
    if off<0x72E000: return '.tls',off-0x72DE00+0x9D2000
    if off<0x758E98: return '.rsrc',off-0x72E000+0x9D3000
    return 'appended',None
def dis(b,va):
    out=[]
    for i in md.disasm(b,va): out.append(f'{i.address:08X} {i.bytes.hex():20} {i.mnemonic} {i.op_str}')
    return out
lines=[l.strip() for l in open(sys.argv[1]) if l.strip()]
last=None
for l in lines:
    pid,off,hx=l.split(';'); off=int(off,16); new=bytes.fromhex(hx)
    if pid!=last: print(f'\n===== {pid}'); last=pid
    s,va=sec(off)
    if s=='appended' or off>=len(d): print(f'  [{s}] file 0x{off:X} len {len(new)} (new section)'); continue
    old=d[off:off+len(new)]
    print(f'  [{s}] file 0x{off:X}'+(f' VA 0x{va:X}' if va else '')+f' len {len(new)}')
    if s=='.text':
        n=max(len(new),1)
        # show old with enough bytes to complete the last instruction
        oldx=d[off:off+n+8]
        print('   OLD:'); 
        for x in dis(oldx,va):
            print('     '+x)
            if int(x.split()[0],16)-va+len(bytes.fromhex(x.split()[1]))>=n: break
        print('   NEW:')
        newx=new+d[off+len(new):off+len(new)+8]
        for x in dis(newx,va):
            print('     '+x)
            if int(x.split()[0],16)-va+len(bytes.fromhex(x.split()[1]))>=n: break
    else:
        def fmt(b):
            r=b.hex()
            if len(b)==4: r+=f'  u32={struct.unpack("<I",b)[0]} f32={struct.unpack("<f",b)[0]!r}'
            if len(b)==8: r+=f'  f64={struct.unpack("<d",b)[0]!r}'
            if len(b)==2: r+=f'  u16={struct.unpack("<H",b)[0]}'
            try:
                t=b.decode('ascii')
                if all(32<=ord(c)<127 or c=='\0' for c in t): r+=f'  "{t}"'
            except: pass
            return r
        print('   OLD: '+fmt(old)); print('   NEW: '+fmt(new))
