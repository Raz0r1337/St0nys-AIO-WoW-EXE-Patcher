from lib import *
def win(n,off,ln,before=0x50,after=0x40,start=None):
    p=load(n); fs=func_start(orig,off) if start is None else start; fe=func_end(orig,off+ln)
    lo=max(fs,off-before); hi=min(fe+2,off+ln+after)
    print(f'##### patch {n}: range f{off:X}+{ln} VA {off2va(off):X}; function VA {off2va(fs):X}-{off2va(fe):X} (len {fe-fs})')
    for d,name in ((orig,'ORIGINAL'),(p,'PATCHED')):
        print('---',name)
        for line in dis(d,fs,fe+2,[(off,off+ln)]).splitlines():
            a=int(line[2:10],16)
            if off2va(lo)<=a<off2va(hi): print(line)
