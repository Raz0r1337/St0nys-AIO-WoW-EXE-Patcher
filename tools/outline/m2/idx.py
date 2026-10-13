# build call index for whole .text: callers[target] = [callsites]
import struct,pickle
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
T0=0x400; T1=0x5DD800
calls={}
for o in range(T0,T1-5):
    if d[o]==0xE8:
        rel=struct.unpack_from('<i',d,o+1)[0]
        tgt=o+0x400C00+5+rel
        if 0x401000<=tgt<0x9DE400:
            calls.setdefault(tgt,[]).append(o+0x400C00)
pickle.dump(calls,open('calls.pkl','wb'))
print(len(calls))
