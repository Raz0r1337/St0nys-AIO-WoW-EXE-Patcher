import capstone,sys,struct,pickle
EXE='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
d=open(EXE,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32); md.detail=False
TB=0x400C00
def off(va):
    if 0x401000<=va<0x9DE400: return va-TB
    if 0x9DF000<=va<0xAB6000: return va-0x9DF000+0x5DD800
    if 0xAB6000<=va<0xAB6000+0x78E00: return va-0xAB6000+0x6B4000
    return None
def rd32(va): return struct.unpack_from('<I',d,off(va))[0]
def rdf(va): return struct.unpack_from('<f',d,off(va))[0]
def dis(va,n=0x200,stop_ret=False,out=True):
    o=off(va); res=[]
    for i in md.disasm(d[o:o+n],va):
        s='%08X  %-22s %s %s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str)
        res.append(i)
        if out: print(s)
        if stop_ret and i.mnemonic in('ret',) : break
    return res
calls=pickle.load(open('/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/outline/m2/calls.pkl','rb'))
if __name__=='__main__':
    for a in sys.argv[1:]:
        va,n=a.split(':'); print('---',va); dis(int(va,16),int(n,16) if n.startswith('0x') else int(n))
def fstart(va):
    a=va
    while a>0x401000:
        o=off(a)
        if d[o-1]==0xcc and d[o]!=0xcc and (d[o:o+3]==b'\x55\x8b\xec' or a in calls): return a
        if d[o-1]==0xc3 and d[o:o+3]==b'\x55\x8b\xec' : return a
        a-=1
def ctx(va,before=0x40,after=0x20):
    f=fstart(va); print('== site %x in func %x (callers %s)'%(va,f,[hex(c) for c in calls.get(f,[])][:8]))
    # disasm from function start to va+after, print only last part
    ins=dis(f,va-f+after,out=False)
    for i in ins:
        if i.address>=va-before:
            print('%s %08X  %s %s'%('>' if i.address==va else ' ',i.address,i.mnemonic,i.op_str))
