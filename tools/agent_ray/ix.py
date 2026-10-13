import pickle, bisect, re, struct, wx
I = pickle.load(open('/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/agent_ray/insns.pkl', 'rb'))
A = [x[0] for x in I]
def idx(va): return bisect.bisect_left(A, va)
def grep(p, lo=0, hi=1<<32):
    r = re.compile(p); return [x for x in I if lo <= x[0] < hi and r.search(x[2])]
def callers(tgt):
    s = 'call 0x%x' % tgt; j = 'jmp 0x%x' % tgt
    return [(x[0], x[2]) for x in I if x[2] == s or x[2] == j]
def refs(val):
    s = '0x%x' % val
    r = re.compile(r'(?<![0-9a-fx])' + s + r'(?![0-9a-f])')
    return [x for x in I if r.search(x[2])]
def funcstart(va):
    # walk back to find typical prologue after int3/ret padding
    k = idx(va)
    while k > 0:
        a, sz, t = I[k]
        p = I[k-1][2]
        if t.startswith('push ebp') and (p.startswith('int3') or p.startswith('ret') or p.startswith('nop') or p.startswith('jmp')):
            return a
        k -= 1
    return None
def pr(lst):
    for x in lst: print('%08X  %s' % (x[0], x[-1]))
