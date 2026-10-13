import pickle,re,sys
ins=pickle.load(open('ins.pkl','rb'))
# find: mov rA, dword ptr [rB + 0xd0] ; then within N insns, use [rA + OFF]
off=sys.argv[1]; N=int(sys.argv[2]) if len(sys.argv)>2 else 4
r1=re.compile(r'^mov (e[a-z]{2}), dword ptr \[e[a-z]{2} \+ 0xd0\]$')
for k,(a,s) in enumerate(ins):
    m=r1.match(s)
    if not m: continue
    ra=m.group(1)
    for j in range(k+1,min(k+1+N,len(ins))):
        t=ins[j][1]
        if '[%s + %s]'%(ra,off) in t:
            print('%08X %s | %08X %s'%(a,s,ins[j][0],t)); break
        if t.startswith('mov %s,'%ra) or t.startswith('call') or t.startswith('ret'): break
