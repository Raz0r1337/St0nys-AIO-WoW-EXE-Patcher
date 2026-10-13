import capstone,keystone,struct
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
ks=keystone.Ks(keystone.KS_ARCH_X86,keystone.KS_MODE_32)
EXT=0x00E00000  # example address of new 8*0x48 slot array (new section, zero-init)
def ins(va):
    o=va-0x400C00; i=next(md.disasm(d[o:o+16],va)); return i
sites=[
 ('LightGet 0x682FD0',0x682FD9,'lea edx,[eax*8+%#x]'%EXT),
 ('LightEnable 0x683080',0x683089,'lea eax,[eax*8+%#x]'%EXT),
 ('LightSet 0x6847D0',0x6847DD,'lea ecx,[eax*8+%#x]'%EXT),
 ('D3D9 disable loop ptr',0x6A4414,'mov esi,%#x; nop'%(EXT+0x44)),
 ('D3D9 disable loop cnt',0x6A444B,'cmp ebx,8'),
 ('D3D9 SetLight loop ptr',0x6A456E,'mov esi,%#x; nop'%(EXT+0x40)),
 ('D3D9 SetLight loop cnt',0x6A46EC,'cmp ebx,8'),
 ('D3D9Ex disable loop ptr',0x6A8384,'mov esi,%#x; nop'%(EXT+0x44)),
 ('D3D9Ex disable loop cnt',0x6A83BB,'cmp ebx,8'),
 ('D3D9Ex SetLight loop ptr',0x6A84DE,'mov esi,%#x; nop'%(EXT+0x40)),
 ('D3D9Ex SetLight loop cnt',0x6A865C,'cmp ebx,8'),
 ('GL disable loop ptr',0x695689,'mov esi,%#x; nop'%(EXT+0x44)),
 ('GL disable loop cnt',0x6956B0,'cmp edi,8'),
 ('GL light loop ptr',0x6957A2,'mov esi,%#x; nop'%(EXT+0x40)),
 ('GL light loop cnt',0x6957A8,'mov dword ptr [ebp-0x10],8'),
 ('SetupGxLights cap',0x8354E2,'cmp edi,8'),
 ('SetupGxLights cap2',0x835593,'cmp edi,8'),
 ('SetupGxLights disable rest',0x8355B3,'cmp edi,8'),
 ('DefaultLight 0x7A8800 disable 1..3',0x7A8901,'cmp esi,8'),
 ('LightGrid 0x6BBF40 disable rest a',0x6BC0C9,'cmp esi,8'),
 ('LightGrid 0x6BBF40 disable rest b',0x6BC0E1,'cmp esi,8'),
]
print('| site | VA | file off | original bytes | original | new bytes | new |')
print('|---|---|---|---|---|---|---|')
for name,va,new in sites:
    i=ins(va); nb=bytes(ks.asm(new,va)[0])
    assert len(nb)==i.size,(name,len(nb),i.size)
    print('| %s | %08X | %06X | %s | `%s %s` | %s | `%s` |'%(name,va,va-0x400C00,i.bytes.hex(' ').upper(),i.mnemonic,i.op_str,nb.hex(' ').upper(),new))
# reset routine
src='''
mov eax,%#x
L: mov dword ptr [eax],0
mov dword ptr [eax+4],0x00ff00ff
add eax,0x48
cmp eax,%#x
jb L
ret
'''%(EXT+0x40,EXT+0x40+8*0x48)
nb=bytes(ks.asm(src,0x682C50)[0])
print('\nReset 0x682C50 replacement (%d bytes, original body 0x58 bytes up to ret at 0x682CA7):'%len(nb),nb.hex(' ').upper())
for i in md.disasm(nb,0x682C50): print('  %08X %s %s'%(i.address,i.mnemonic,i.op_str))
