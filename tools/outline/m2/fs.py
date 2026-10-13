import pickle,sys
calls=pickle.load(open('/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/outline/m2/calls.pkl','rb'))
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
def fstart(va):
    a=va&~0xf
    while True:
        o=a-0x400C00
        if a in calls and (d[o-1] in (0xcc,0xc3,0x90) ): return a
        if d[o-1]==0xcc and d[o]!=0xcc and d[o:o+3]==b'\x55\x8b\xec': return a
        a-=16
if __name__=='__main__':
    for x in sys.argv[1:]:
        va=int(x,16); f=fstart(va)
        print(hex(va),'func',hex(f),'callers',[hex(c) for c in calls.get(f,[])][:10])
