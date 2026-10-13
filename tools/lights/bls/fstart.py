import pickle,bisect,sys
L=pickle.load(open('lin.pkl','rb')); A=[x[0] for x in L]
def fstart(va):
    i=bisect.bisect_right(A,va)-1
    while i>0:
        if L[i][2]=='push' and L[i][3]=='ebp' and L[i+1][2]=='mov' and L[i+1][3]=='ebp, esp' and L[i-1][2] in ('int3','ret','nop','jmp'): return L[i][0]
        i-=1
if __name__=='__main__':
    for a in sys.argv[1:]: print(a,hex(fstart(int(a,16))))
