from common import *
import sys,json
lm=json.load(open('/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/y38/luamap.json'))
def dis(va,n):
    fo=va2fo(va)
    for i in md.disasm(d[fo:fo+n],va):
        ann=''
        for tok in re.findall(r'0x[0-9a-f]+',i.op_str):
            v=int(tok,16)
            if v>=0x9DF000:
                c=cstr(v)
                if c: ann+='  ; "%s"'%c
            if hex(v) in lm: ann+='  ; LUA '+lm[hex(v)][0][0]
        print('%08X  %-22s %s %s%s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str,ann))
        if i.mnemonic=='int3': break
if __name__=='__main__':
    for a in sys.argv[1:]:
        va,n=a.split(':'); print('--- %s %s'%(va, lm.get(hex(int(va,16)),''))); dis(int(va,16),int(n,0))
