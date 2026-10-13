from common import *
import pickle
P=[]  # (va_instr, imm_offset_in_instr, orig_imm_bytes, new_imm_bytes, purpose)
def imm(va,off,ob,nb,purpose):
    fo=va2fo(va)+off
    assert d[fo:fo+len(ob)]==ob,(hex(va),d[fo:fo+len(ob)].hex(),ob.hex())
    i=next(md.disasm(d[va2fo(va):va2fo(va)+16],va))
    P.append((va,i.bytes.hex(),'%s %s'%(i.mnemonic,i.op_str),va+off,fo,ob.hex(),nb.hex(),purpose))
Y=bytes.fromhex('d0070000'); N=bytes.fromhex('ec070000')
for va,off,p in [(0x5B81BD,1,'CalendarGetDate year'),(0x5B827A,1,'CalendarGetMinDate year'),(0x5B8323,1,'CalendarGetMaxDate year'),
 (0x5B83E7,2,'CalendarGetMinHistoryDate year'),(0x5B8474,2,'CalendarGetMaxCreateDate year'),(0x5B9A5E,2,'CalendarGetMonth year'),
 (0x5B9B91,2,'CalendarGetAbsMonth year (out)'),(0x5BA504,2,'CalendarEventGetInviteResponseTime year'),(0x5BDA51,2,'CalendarGetEventInfo event year'),
 (0x5BDAE4,1,'CalendarGetEventInfo lockout year'),(0x5B7EB2,2,'GetInboxText calendar mail FULLDATE year'),(0x6CC4EE,1,'SMSG_GUILD_INFO GUILD_INFO_TEMPLATE year'),
 (0x76CB3B,2,'GetStatistic/GetAchievementCriteriaInfo date quantity "%02d/%02d/%d" (only caller 5B115D)'),
 (0x5B9B4B,2,'CalendarGetAbsMonth year arg (in, sub)'),(0x5BB551,1,'CalendarEventSetDate year (in, sub)'),(0x5BB701,1,'CalendarEventSetLockoutDate year (in, sub)'),(0x5C4439,2,'CalendarSetAbsMonth year arg (in, sub)')]:
    imm(va,off,Y,N,p)
z4=b'\0\0\0\0'
for va,off,ob,p in [(0x5B8206,3,bytes.fromhex('0a000000'),'CalendarGetMinDate month 10->0'),(0x5B820D,3,bytes.fromhex('17000000'),'CalendarGetMinDate day 23->0'),(0x5B8214,3,bytes.fromhex('04000000'),'CalendarGetMinDate year 4->0'),
 (0x5B7B5C,3,bytes.fromhex('0a000000'),'IsCalendarDateValid(5B7B30) min month'),(0x5B7B63,3,bytes.fromhex('17000000'),'IsCalendarDateValid min day'),(0x5B7B6A,3,bytes.fromhex('04000000'),'IsCalendarDateValid min year'),
 (0x5B8F3C,2,b'\x04','MonthOffset clamp (5B8EC0) cmp year,4'),(0x5B8F43,2,bytes.fromhex('04000000'),'5B8EC0 year=4'),(0x5B8F4B,2,b'\x0a','5B8EC0 cmp month,10'),(0x5B8F50,1,bytes.fromhex('0a000000'),'5B8EC0 month=10'),
 (0x5B8FA3,2,b'\x04','AbsMonth clamp (5B8F70) cmp year,4'),(0x5B8FAA,2,bytes.fromhex('04000000'),'5B8F70 year=4'),
 (0x5BFF66,2,b'\x04','Calendar init (5BFF30) cmp year,4'),(0x5BFF6B,2,b'\x0a','5BFF30 cmp month,10'),(0x5BFF6E,1,bytes.fromhex('04000000'),'5BFF30 year=4'),(0x5BFF7A,1,bytes.fromhex('0a000000'),'5BFF30 month=10'),
 (0x5B9B1F,1,bytes.fromhex('04000000'),'opt: default year if no game time (GetAbsMonth)'),(0x5C440D,1,bytes.fromhex('04000000'),'opt: default year (SetAbsMonth)'),(0x5BFBDB,1,bytes.fromhex('04000000'),'opt: default year (holiday expand)')]:
    imm(va,off,ob,b'\0'*len(ob),p)
ach=pickle.load(open('ach_patch.pkl','rb'))
for row in P:
    va,ib,txt,iva,fo,ob,nb,p=row
    print('%06X | %-30s | imm@%06X fo %06X | %s -> %s | %s'%(va,txt,iva,fo,ob,nb,p))
for k,(s,o,n) in ach.items():
    print('%06X | block %d bytes | fo %06X | %s -> %s | %s'%(s,len(o),va2fo(s),o.hex(),n.hex(),k))
import json
out=[]
for va,ib,txt,iva,fo,ob,nb,p in P:
    out.append({'va':hex(iva),'fileoff':hex(fo),'orig':ob,'new':nb,'instr_va':hex(va),'instr':txt,'purpose':p,'optional':p.startswith('opt')})
for k,(s,o,n) in ach.items():
    out.append({'va':hex(s),'fileoff':hex(va2fo(s)),'orig':o.hex(),'new':n.hex(),'purpose':k+' year +28 (2-digit)','optional':False})
json.dump(out,open('y38_patches.json','w'),indent=1)
# verify applying all patches on a copy in memory leaves no overlap and orig bytes match
buf=bytearray(d)
for e in out:
    fo=int(e['fileoff'],16); ob=bytes.fromhex(e['orig']); nb=bytes.fromhex(e['new'])
    assert buf[fo:fo+len(ob)]==ob; buf[fo:fo+len(nb)]=nb
print('ok',len(out))
