from emu import *
def cstr(E,a):
    s=b''
    while True:
        c=bytes(E.mu.mem_read(a,1))
        if c==b'\0': return s.decode()
        s+=c; a+=1
def mk(data):
    E=Emu(data)
    STUB=0x30010000
    E.w32(0x9DF248,STUB)                       # IAT LoadLibraryA -> Stub
    E.mu.mem_write(STUB,b'\xC2\x04\x00')
    def s_lla(E,a):
        E.log.append(('LoadLibraryA',cstr(E,a[0]))); return 0   # DLL fehlt -> NULL
    E.stub(STUB,s_lla,1,4)
    stop={}
    def at(E): 
        sp=E.reg(UC_X86_REG_ESP)
        E.log.append(('reached 406D75',hex(E.r32(sp)),hex(E.r32(sp+4)), E.reg(UC_X86_REG_EBP)))
        E.mu.emu_stop()
    E.watch_at(0x406D75,at)
    return E
def run(plist,start):
    E=mk(bytes(apply(ORIG,plist)))
    E.log=[]
    E.mu.mem_write(0xB6B474,b'\x00\x00\x00\x00')
    sp=0x200F0000; E.mu.reg_write(UC_X86_REG_ESP,sp); E.mu.reg_write(UC_X86_REG_EBP,0x44444444)
    E.w32(sp,0x31000000)   # Ruecksprung
    E.w32(sp+4,0x12345678) # Argument von StartAddress
    E.mu.emu_start(start,0x31000000,count=10000)
    return E.log, bytes(E.mu.mem_read(0xB6B474,4)), E.reg(UC_X86_REG_ESP)-sp
print('nur WotLKExt, Einstieg ueber StartAddress 0x40B7D0:')
print(run(WOTLKEXT,0x40B7D0))
print('Nr.23 awesome + WotLKExt:')
print(run(AWESOME+WOTLKEXT,0x40B7D0))
print('nur Nr.23 awesome (Kontrolle):')
print(run(AWESOME,0x40B7D0))
