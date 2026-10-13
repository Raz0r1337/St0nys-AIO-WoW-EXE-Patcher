import struct,sys,pickle,os
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
cache='/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/outline/frame/calls.pkl'
if os.path.exists(cache):
    m=pickle.load(open(cache,'rb'))
else:
    m={}
    for off in range(0x400,0x5DD800-5):
        b=d[off]
        if b==0xE8 or b==0xE9:
            r=struct.unpack_from('<i',d,off+1)[0]
            va=off+0x400C00; tg=(va+5+r)&0xffffffff
            if 0x401000<=tg<0x9DF000:
                m.setdefault(tg,[]).append((va,b))
    pickle.dump(m,open(cache,'wb'))
for a in sys.argv[1:]:
    v=int(a,16)
    print(a,' '.join('%s%x'%('c' if b==0xE8 else 'j',va) for va,b in m.get(v,[])))
