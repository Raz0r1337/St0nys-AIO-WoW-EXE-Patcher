# summarize function: size, calls, strings, globals
import sys,re,bisect
sys.path.insert(0,'/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/outline/frame')
from x import *
lines=open('/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/outline/frame/text.lst').read().split('\n')
lines=[l for l in lines if l]
addrs=[int(l.split()[0],16) for l in lines]
def cstr(va):
    o=va2off(va)
    if o is None or not (0x5DD800<=o<0x6B4000): return None
    e=d.find(b'\0',o); s=d[o:e][:60]
    return s.decode('latin1') if len(s)>2 and all(32<=c<127 for c in s) else None
def summ(va,maxn=4000):
    i=bisect.bisect_left(addrs,va); calls=[]; strs=[]; glob=set(); n=0
    end=None
    while i<len(lines) and n<maxn:
        p=lines[i].split(None,2); mn=p[1]; op=p[2] if len(p)>2 else ''
        if mn=='int3' : end=addrs[i]; break
        if mn=='call': calls.append(op)
        for tok in re.findall(r'0x[0-9a-f]+',op):
            v=int(tok,16)
            if v>=0x9DF000:
                c=cstr(v)
                if c: strs.append(c)
                elif v>=0xAB6000 and v<0xE00000: glob.add(hex(v))
        i+=1; n+=1
    return end,calls,strs,glob
if __name__=="__main__":
  for a in sys.argv[1:]:
      va=int(a,16); end,calls,strs,glob=summ(va)
      print('== %X..%s  calls:%s'%(va,hex(end) if end else '?',' '.join(c.replace('0x','') for c in calls)))
      if strs: print('   str:',strs[:8])
      if glob: print('   glob:',sorted(glob)[:12])
