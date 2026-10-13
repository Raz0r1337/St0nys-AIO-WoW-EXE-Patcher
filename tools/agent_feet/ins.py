import pickle, bisect, re
I = pickle.load(open('/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad/agent_cull/insns.pkl', 'rb'))
A = [x[0] for x in I]
def idx(va): return bisect.bisect_left(A, va)
def grep(p):
    r = re.compile(p); return [x for x in I if r.search(x[1])]
def ctx(va, b=10, a=3):
    k = idx(va); return I[max(0, k - b):k + a + 1]
