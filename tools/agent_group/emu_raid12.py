import sys
S='/tmp/claude-0/-home-user-St0nys-WoW-EXE-Patcher/49e16a66-3a63-5e77-ae4f-92ef019273b7/scratchpad'
src=open(S+'/ol2/test_outline10.py').read()
cut=src.index('# 2) Standard')
exec(compile(src[:cut], 'harness', 'exec'))
# 11 bots: GUIDs 0x1001..0x100B, player 0x333
BOTS=[0x1001+i for i in range(11)]
base=H+0xC0000
for i,g in enumerate(BOTS):
    ob=base+i*0x1000; mdl=base+0x800+i*0x1000; fl=base+0x400+i*0x1000
    e.w32(ob+0xB4, mdl); e.w32(ob+0x98C, 0); e.w32(ob+0xD0, fl); e.mu.mem_write(fl+0x45, b'\x01')
    OBJ[g]=ob; PLAYERS.add(g); SELC[g]=0xFF00FF00
# raid list: server order, player appended at end
raid(BOTS+[0x333])
party=BOTS[:4]
for i in range(4): guid(0xBD1948+8*i, party[i])
guid(0xBD07B0, 0); guid(0xBD07A0, 0)
flag('FHIDDEN',1); flag('FWALLSGRP',1); flag('FPARTY',0); flag('FRAID',0); flag('FSELF',0)
newframe(); batch(OTHER)
u=units()
def thins(): return [mu.mem_read(DO['THIN'] + c, 1)[0] for c in range(1, e.r32(DO['NUNITS']) + 1)]
print('units', [hex(x[0]) for x in u]); print('thin ', thins())
print('GMODE',e.r32(DO['GMODE']),'GRPN',e.r32(DO['GRPN']),'WPROT',e.r32(DO['WPROT']),'SELFCAT',e.r32(DO['SELFCAT']))
