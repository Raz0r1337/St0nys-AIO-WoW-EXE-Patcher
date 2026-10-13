from common import *
import pickle,sys
ins=pickle.load(open('ins.pkl','rb'))
pats=sys.argv[1:]
for a,s,mn,op in ins:
    for p in pats:
        if re.search(p,op):
            print('%08X %-6s %s'%(a,mn,op)); break
