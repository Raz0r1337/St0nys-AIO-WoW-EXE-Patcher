# Prueft, dass die vom echten Patcher erzeugte Exe exakt unsere getesteten Bytes enthaelt
import sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','ml'))
import h
from patches import *
p=sys.argv[1]; want=sys.argv[2].split(',')
d=open(p,'rb').read()
plist=[]
if 'year2031' in want: plist+=YEAR2031
if 'wotlkext' in want: plist+=WOTLKEXT
exp=bytes(apply(h.d,plist))
diff=[i for i in range(len(exp)) if exp[i]!=d[i]]
# erlaubte Abweichungen: Wasserzeichen-Bereich (0x72DE20..) und LAA-Flag 0x126 falls laa gewaehlt
rest=[i for i in diff if not (0x72DE00<=i<0x72E000)]
print('bytes differing outside watermark:',len(rest), [hex(i) for i in rest[:10]])
