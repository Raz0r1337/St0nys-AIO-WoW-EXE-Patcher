import difflib,sys,re
d,m=sys.argv[1],sys.argv[2]
D=open(d,'rb').read().decode('ascii').split('\r\n'); M=open(m,'rb').read().decode('ascii').split('\r\n')
tab=lambda L:[('#TABLE#' if re.match(r'^[a-z0-9]+;',x) else x) for x in L]
sm=difflib.SequenceMatcher(None,tab(M),tab(D),autojunk=False)
for i,(op,a1,a2,b1,b2) in enumerate([o for o in sm.get_opcodes() if o[0]!='equal']):
    print('#%d %s main[%d:%d] dev[%d:%d]'%(i,op,a1+1,a2,b1+1,b2))
    for x in M[a1:a2][:3]: print('   - '+x[:110])
    for x in D[b1:b2][:3]: print('   + '+x[:110])
