import sys
exec(open('/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/dis2.py').read().split("if __name__")[0])
def fstart(va):
    o=va-0x400C00
    while o>0:
        if d[o:o+3]==b'\x55\x8b\xec' and d[o-1] in (0xCC,0xC3,0x90): return o+0x400C00
        o-=1
if __name__=='__main__':
    va=int(sys.argv[1],16); n=int(sys.argv[2],0) if len(sys.argv)>2 else None
    s=fstart(va); print('start',hex(s))
    if n is None: n=va-s+0x40
    dis(d,s-0x400C00,n)
