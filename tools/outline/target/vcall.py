import pickle,re,sys
ins=pickle.load(open('sweep.pkl','rb'))
disp=sys.argv[1]
lo=int(sys.argv[2],16) if len(sys.argv)>2 else 0; hi=int(sys.argv[3],16) if len(sys.argv)>3 else 1<<32
pat=re.compile(r'^(e..), dword ptr \[(e..) \+ %s\]$'%disp)
for k,(a,s,m,o) in enumerate(ins):
    if not(lo<=a<hi): continue
    if m=='call' and o.startswith('dword ptr [e') and o.endswith('+ %s]'%disp):
        print(hex(a),m,o); continue
    if m=='mov':
        mm=pat.match(o)
        if mm:
            r=mm.group(1)
            for j in range(k+1,min(k+6,len(ins))):
                a2,s2,m2,o2=ins[j]
                if m2=='call' and o2==r:
                    # check prior instruction loads vtable: mov base,[ecx] etc
                    print(hex(a),o,'call@',hex(a2)); break
                if m2=='call': break
