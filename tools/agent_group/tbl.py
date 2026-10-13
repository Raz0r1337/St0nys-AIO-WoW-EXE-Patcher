import sys,struct
ORI='/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe'
D=open(ORI,'rb').read()
def va2off(v):
    if 0x401000<=v<0x9DF000: return v-0x400C00
    if 0x9DF000<=v<0xAB6000: return v-0x9DF000+0x5DD800
    return v-0xAB6000+0x6B4000
def cstr(v):
    try:
        o=va2off(v); e=D.index(b'\0',o); s=D[o:e]
        if len(s)<60 and all(32<=c<127 for c in s) and s: return s.decode()
    except Exception: pass
    return None
a=int(sys.argv[1],16); n=int(sys.argv[2])
for k in range(n):
    v=a+4*k; d=struct.unpack_from('<I',D,va2off(v))[0]
    print('%08X: %08X %s'%(v,d,cstr(d) or ''))
