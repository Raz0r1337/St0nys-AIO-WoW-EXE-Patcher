from lib import *
import sys
# usage: show.py N fileoff len [before after]
n=int(sys.argv[1]); off=int(sys.argv[2],16); ln=int(sys.argv[3])
before=int(sys.argv[4],16) if len(sys.argv)>4 else None
after=int(sys.argv[5],16) if len(sys.argv)>5 else 0x30
p=load(n)
fs=func_start(orig,off) if before is None else off-before
fe=func_end(orig,off+ln)
print(f'range file 0x{off:X}-0x{off+ln-1:X}  VA 0x{off2va(off):X}  func_start f{fs:X} (VA {off2va(fs):X}) func_end(CC pad) f{fe:X} (VA {off2va(fe):X}) funclen {fe-fs}')
start=fs if before is None and off-fs<0x200 else max(off-0x60,fs)
if before is not None: start=off-before
end=min(off+ln+after, fe+2 if fe else off+ln+after)
print('--- ORIGINAL'); print(dis(orig,start,end,[(off,off+ln)]))
print('--- PATCHED'); print(dis(p,start,end,[(off,off+ln)]))
