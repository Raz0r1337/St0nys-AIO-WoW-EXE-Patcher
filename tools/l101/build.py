import capstone,struct
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
acc0=bytes.fromhex(
 '55'        # push ebp
 '8BEC'      # mov ebp,esp
 '8BC1'      # mov eax,ecx
 '8B480C'    # mov ecx,[eax+0Ch]
 '8B4008'    # mov eax,[eax+8]
 '8B4004'    # mov eax,[eax+4]        stride = rows per column
 '8B5508'    # mov edx,[ebp+8]        row
 '3BD0'      # cmp edx,eax
 '7203'      # jb +3
 '8D50FF'    # lea edx,[eax-1]        row = stride-1
 '0FAF450C'  # imul eax,[ebp+0Ch]     stride*col
 '03C2'      # add eax,edx
 '8B5118'    # mov edx,[ecx+18h]
 '8B5204'    # mov edx,[edx+4]
 '83C118'    # add ecx,18h
 '50'        # push eax
 'FFD2'      # call edx
 'D900'      # fld dword [eax]
 '5D'        # pop ebp
 'C20800')   # ret 8
assert len(acc0)==48, len(acc0)
# twin: re-push args, call accessor 0 (returns eax=record ptr, st0=[eax]); drop st0; fld [eax+4]
twin_va=0x7F69E0
call_site=twin_va+3+6
rel=0x7F69B0-(call_site+5)
twin=bytes.fromhex('55 8BEC FF750C FF7508'.replace(' ',''))+b'\xE8'+struct.pack('<i',rel)+bytes.fromhex('DDD8 D94004 5D C20800'.replace(' ',''))
print('twin len',len(twin))
twin=twin+b'\xCC'*(47-len(twin))
for name,code,va in (('acc0',acc0,0x7F69B0),('twin',twin,0x7F69E0)):
    print('==',name)
    for i in md.disasm(code,va): print('  %08X  %-16s %s %s'%(i.address,i.bytes.hex(),i.mnemonic,i.op_str))
open('acc0.bin','wb').write(acc0); open('twin.bin','wb').write(twin)
print('ps acc0:', ', '.join('0x%02X'%b for b in acc0))
print('ps twin:', ', '.join('0x%02X'%b for b in twin))
