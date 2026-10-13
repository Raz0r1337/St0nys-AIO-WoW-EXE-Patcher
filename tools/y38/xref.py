import pickle,sys,re,json,bisect
ins=pickle.load(open('/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/y38/ins.pkl','rb'))
lm=json.load(open('/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/y38/luamap.json'))
# function starts: after int3/ret padding with push ebp; mov ebp,esp OR call targets
calls={}
starts=set()
for a,s,mn,op in ins:
    if mn in('call','jmp') and op.startswith('0x'):
        t=int(op,16); calls.setdefault(t,[]).append((a,mn))
        if mn=='call': starts.add(t)
for f in lm: starts.add(int(f,16))
starts=sorted(starts)
def func_of(a):
    i=bisect.bisect_right(starts,a)-1
    return starts[i] if i>=0 else None
def name(f):
    v=lm.get(hex(f)); return v[0][0] if v else ''
if __name__=='__main__':
    depth=int(sys.argv[1])
    for t in sys.argv[2:]:
        t=int(t,16)
        seen=set()
        def rec(t,lvl):
            for a,mn in calls.get(t,[]):
                f=func_of(a)
                print('  '*lvl+'%s %08X in %08X %s'%(mn,a,f,name(f)))
                if lvl<depth and f not in seen:
                    seen.add(f); rec(f,lvl+1)
        print('== %08X %s'%(t,name(t)))
        rec(t,0)
