import re,sys
d=sys.argv[1]; P=sys.argv[2] if len(sys.argv)>2 else 'docs/'
src=open(d+'/apply_patches.ps1',encoding='ascii').read()
heads=re.findall(r"(?m)^    @\{ Id = '([^']+)';(.*)$",src)
fl={k:[i+1 for i,(_,h) in enumerate(heads) if k+' = $true' in h] for k in ('BanRisk','PublicUntested','GameUntested','GrowsExe','DllRisky')}
def rng(L):
    out=[];i=0
    while i<len(L):
        j=i
        while j+1<len(L) and L[j+1]==L[j]+1: j+=1
        out+=([str(L[i])] if j==i else ([str(L[i]),str(L[j])] if j==i+1 else ['%d–%d'%(L[i],L[j])])); i=j+1
    return out
def txt(L,und):
    r=rng(L)
    return r[0] if len(r)==1 else ', '.join(r[:-1])+' '+und+' '+r[-1]
for fn,und,nr in ((P+'README.de.md','und','Nr.'),(P+'README.md','and','No.')):
    s=open(d+'/'+fn,encoding='utf-8').read(); flat=re.sub(r'\s*\n\s*',' ',s)
    for k in fl:
        t=nr+' '+txt(fl[k],und)
        print(fn,k,'OK' if t in flat else 'MISSING: '+t, flat.count(t))
