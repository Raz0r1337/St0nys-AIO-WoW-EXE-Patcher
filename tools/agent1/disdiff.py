from lib import *
# (menu, id, file offset, length, window-before, window-after)
R=[(3,'itemcache',0x2689FD,2,0x60,0x40),
   (4,'worldcrash-hook',0x41C91B,6,0x0B,0x40),
   (4,'worldcrash-cave',0x5DD7B3,38,0,0x30),
   (5,'rce-warden',0x3D9D7C,2,0x50,0x40),
   (6,'wardenoff',0x3D9C5B,2,0x0B,0x40),
   (8,'noserverpatch',0xDA2A8,3,0x40,0x40),
   (9,'nosurvey',0xDA2BD,5,0x40,0x40),
   (10,'skipbnet',0x2B1F48,1,0x40,0x30),
   (11,'skiprdp',0x36AE40,1,0x40,0x30),
   (12,'nohttp',0x46F28F,4,0x40,0x30),
   (13,'afk-1',0x12A3AF,6,0x30,0x30),
   (13,'afk-2',0x12A64C,5,0x30,0x30),
   (13,'afk-cave',0x54AD02,24,0,0x20),
   (14,'glue-1',0x1F41BF,1,0x30,0x30),
   (14,'glue-2',0x415A25,1,0x25,0x30),
   (14,'glue-3',0x415A3F,1,0x10,0x20),
   (14,'glue-4',0x415A95,1,0x30,0x20),
   (14,'glue-5',0x415B46,1,0x30,0x30),
   (14,'glue-6',0x415B5F,7,0x30,0x20),
   (15,'mpqsig',0x21350,22,0,0x60),
   (17,'localdata',0x1F2A,7,0x30,0x30),
   (18,'luaunlock',0x1185E7,14,0x40,0x40)]
import sys
sel=[int(a) for a in sys.argv[1:]] if len(sys.argv)>1 else None
for n,name,off,ln,wb,wa in R:
    if sel and n not in sel: continue
    pb=load_patched(n)
    va=f2v(off)
    fs=find_func_start(d,off)
    print('#'*100)
    print('%d %s  file 0x%X  VA 0x%X  len %d   func_start(VA)=%s (%d bytes before)'%(n,name,off,va,ln,'0x%X'%f2v(fs) if fs else None, off-fs if fs else -1))
    start=va-wb
    if fs and off-fs<0x300: start=f2v(fs)
    end=va+ln+wa
    A=dis(d,start,end,(va,va+ln)); B=dis(pb,start,end,(va,va+ln))
    import difflib
    print('--- ORIGINAL'); 
    for l in A: print(l)
    print('--- PATCHED')
    for l in B: print(l)
    print('--- DIFF')
    for l in difflib.unified_diff(A,B,lineterm='',n=1):
        if l.startswith(('---','+++','@@')): continue
        print(l)
