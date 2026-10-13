# Unicorn-Test: vorgeschlagener Hook bei 0x4FB036 (call 0x7E6480 -> call stub) mit Skizze RayFrame.
# Emuliert ab 0x4FB036 bis 0x4FB03B (Ruecksprung), mit Attrappen fuer WorldFrame/Kamera; Welt leer.
import struct, keystone
from unicorn import *
from unicorn.x86_const import *
import wx
D = wx.D
CAVE = 0x01000000
DATA = CAVE + 0x800
SRC = '''
stub:
    call 0x7E6480
    pushad
    call rayframe
    popad
    ret
rayframe:
    push ebp
    mov ebp, esp
    sub esp, 0x40
    cmp byte ptr [0xBD0792], 0
    je done
    cmp byte ptr [0xBD0790], 0
    jne done
    mov eax, dword ptr [0xB7436C]
    test eax, eax
    je done
    mov eax, dword ptr [eax + 0x7E20]
    test eax, eax
    je done
    mov ecx, dword ptr [eax + 8]
    mov dword ptr [ebp - 0x40], ecx
    mov ecx, dword ptr [eax + 0xC]
    mov dword ptr [ebp - 0x3C], ecx
    mov ecx, dword ptr [eax + 0x10]
    mov dword ptr [ebp - 0x38], ecx
    mov ecx, dword ptr [0x%X]
    mov dword ptr [ebp - 0x34], ecx
    mov ecx, dword ptr [0x%X]
    mov dword ptr [ebp - 0x30], ecx
    mov ecx, dword ptr [0x%X]
    mov dword ptr [ebp - 0x2C], ecx
    mov dword ptr [ebp - 0x28], 0x3F800000
    push 0
    push 0x100111
    lea ecx, [ebp - 0x28]
    push ecx
    push 0
    lea ecx, [ebp - 0x34]
    push ecx
    lea ecx, [ebp - 0x40]
    push ecx
    call 0x7A3B70
    add esp, 0x18
    mov byte ptr [0x%X], al
    inc dword ptr [0x%X]
done:
    mov esp, ebp
    pop ebp
    ret
''' % (DATA, DATA + 4, DATA + 8, DATA + 12, DATA + 16)
ks = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32)
code = bytes(ks.asm(SRC, CAVE)[0])
mu = Uc(UC_ARCH_X86, UC_MODE_32)
mu.mem_map(0x400000, 0xA00000)
for nm, va, vs, ro, rs in wx.SECS: mu.mem_write(va, D[ro:ro + min(rs, vs if vs else rs)])
mu.mem_map(CAVE, 0x1000); mu.mem_write(CAVE, code)
STK = 0x20000000; mu.mem_map(STK, 0x100000)
HEAP = 0x30000000; mu.mem_map(HEAP, 0x100000)
w32 = lambda a, v: mu.mem_write(a, struct.pack('<I', v & 0xffffffff))
r32 = lambda a: struct.unpack('<I', mu.mem_read(a, 4))[0]
wf = lambda a, *v: mu.mem_write(a, struct.pack('<%df' % len(v), *v))
# Patch: call 0x7E6480 bei 0x4FB036 -> call CAVE
rel = CAVE - (0x4FB036 + 5)
orig = bytes(mu.mem_read(0x4FB036, 5))
mu.mem_write(0x4FB036, b'\xE8' + struct.pack('<i', rel))
print('Originalbytes 0x4FB036:', orig.hex(' '), '-> Patch:', bytes(mu.mem_read(0x4FB036, 5)).hex(' '))
# Attrappen
w32(0xCD754C, HEAP + 0x1000); w32(0xCF4930, HEAP + 0x10000)
wfr = HEAP + 0x20000; cam = HEAP + 0x40000
w32(0xB7436C, wfr); w32(wfr + 0x7E20, cam); wf(cam + 8, 1000.0, 2000.0, 60.0)
wf(DATA, 1010.0, 2005.0, 52.0)  # Zielpunkt (z. B. Brust einer Einheit)
mu.mem_write(0xBD0792, b'\x01'); mu.mem_write(0xBD0790, b'\x00')
# 0x86AE20 (OsGetAsyncTimeMs, wird von 0x7E6480 gerufen) -> sofort zurueck mit eax=0
def hook_code(uc, addr, size, ud):
    if addr == 0x86AE20:
        esp = uc.reg_read(UC_X86_REG_ESP); ret = r32(esp)
        uc.reg_write(UC_X86_REG_EAX, 0); uc.reg_write(UC_X86_REG_ESP, esp + 4); uc.reg_write(UC_X86_REG_EIP, ret)
mu.hook_add(UC_HOOK_CODE, hook_code, begin=0x86AE20, end=0x86AE20)
def bad(uc, acc, addr, size, val, ud):
    print('  !! ungueltig', hex(addr), 'EIP', hex(uc.reg_read(UC_X86_REG_EIP))); return False
mu.hook_add(UC_HOOK_MEM_READ_UNMAPPED | UC_HOOK_MEM_WRITE_UNMAPPED | UC_HOOK_MEM_FETCH_UNMAPPED, bad)
# Registerzustand wie bei 0x4FB036: ESI = CGWorldFrame*, EBP = Rahmen von 0x4FAF90
esp0 = STK + 0x80000
regs = {UC_X86_REG_ESP: esp0, UC_X86_REG_EBP: esp0 + 0x84, UC_X86_REG_ESI: wfr, UC_X86_REG_EDI: 0x7777, UC_X86_REG_EBX: 0x5555}
for r, v in regs.items(): mu.reg_write(r, v)
for run in range(2):
    if run == 1:
        mu.mem_write(0xBD0790, b'\x01')  # Ladebildschirm aktiv -> Strahl muss entfallen
    mu.reg_write(UC_X86_REG_ESP, esp0)
    mu.emu_start(0x4FB036, 0x4FB03B, count=1_000_000)
    ok = all(mu.reg_read(r) == v for r, v in regs.items())
    print('Lauf %d: zurueck bei 0x4FB03B, ESI/EDI/EBX/EBP/ESP erhalten=%s, Treffer-Byte=%d, Strahlzaehler=%d'
          % (run + 1, ok, mu.mem_read(DATA + 12, 1)[0], r32(DATA + 16)))
print('Stub-Bytes (%d):' % len(code), code[:16].hex(' '), '...')
