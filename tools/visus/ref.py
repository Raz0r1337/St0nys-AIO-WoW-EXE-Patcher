# Referenz fuer Visus - St0nyCam: Code und Daten der Sektion fuer eine gegebene Basis V (keystone).
import struct, sys
from keystone import Ks, KS_ARCH_X86, KS_MODE_32
# Feste Lage in der Sektion
O_REG, O_CAM = 0x000, 0x060
D_PH, D_PS, D_PX, D_PY, D_PCAM, D_PVALID = 0x180, 0x184, 0x188, 0x18C, 0x190, 0x194
C_HMAX, C_HMIN, C_SMAX, C_SMIN, C_EPS, C_ZCAP = 0x1A0, 0x1A4, 0x1A8, 0x1AC, 0x1B0, 0x1B4
S_ZERO, S_SPEED, S_HEIGHT, S_SHOULDER = 0x1C0, 0x1C4, 0x1C8, 0x1D8
SIZE = 0x200
def reg_asm(V):
    return f"""
    mov dword ptr [0xC24970], eax
    push 0
    push 0
    push 0
    push 5
    push 0
    push {V+S_ZERO:#x}
    push 0x10
    push 0
    push {V+S_HEIGHT:#x}
    call 0x767FC0
    mov dword ptr [{V+D_PH:#x}], eax
    push 0
    push 0
    push 0
    push 5
    push 0
    push {V+S_ZERO:#x}
    push 0x10
    push 0
    push {V+S_SHOULDER:#x}
    call 0x767FC0
    add esp, 0x48
    mov dword ptr [{V+D_PS:#x}], eax
    jmp 0x5FE2B4
    """
def cam_asm(V):
    return f"""
    mov eax, dword ptr [{V+D_PH:#x}]
    test eax, eax
    je shoulder
    fld dword ptr [eax+0x2C]
    fld dword ptr [{V+C_HMAX:#x}]
    fcomi st(0), st(1)
    fcmovnb st(0), st(1)
    fstp st(1)
    fld dword ptr [{V+C_HMIN:#x}]
    fcomi st(0), st(1)
    fcmovb st(0), st(1)
    fstp st(1)
    fadd dword ptr [ebp-0x2C]
    fstp dword ptr [ebp-0x2C]
shoulder:
    mov eax, dword ptr [{V+D_PS:#x}]
    test eax, eax
    je store
    fld dword ptr [eax+0x2C]
    fld dword ptr [{V+C_SMAX:#x}]
    fcomi st(0), st(1)
    fcmovnb st(0), st(1)
    fstp st(1)
    fld dword ptr [{V+C_SMIN:#x}]
    fcomi st(0), st(1)
    fcmovb st(0), st(1)
    fstp st(1)
    fldz
    fcomip st(0), st(1)
    je pop1
    cmp esi, dword ptr [{V+D_PCAM:#x}]
    jne usefocus
    cmp dword ptr [{V+D_PVALID:#x}], 0
    je usefocus
    fld dword ptr [esi+0xC]
    fsub dword ptr [{V+D_PY:#x}]
    fld dword ptr [esi+8]
    fsub dword ptr [{V+D_PX:#x}]
    jmp haved
usefocus:
    fld dword ptr [esi+0xC]
    fsub dword ptr [ebp-0x30]
    fld dword ptr [esi+8]
    fsub dword ptr [ebp-0x34]
haved:
    fld st(0)
    fmul st(0), st(0)
    fld st(2)
    fmul st(0), st(0)
    faddp st(1), st(0)
    fsqrt
    fld dword ptr [{V+C_EPS:#x}]
    fcomip st(0), st(1)
    jp pop4
    jae pop4
    fdivr st(0), st(3)
    fld st(2)
    fmul st(0), st(1)
    fsubr dword ptr [ebp-0x34]
    fstp dword ptr [ebp-0x34]
    fmul st(0), st(1)
    fadd dword ptr [ebp-0x30]
    fstp dword ptr [ebp-0x30]
    fstp st(0)
    fstp st(0)
    fstp st(0)
    jmp store
pop4:
    fstp st(0)
    fstp st(0)
    fstp st(0)
pop1:
    fstp st(0)
store:
    mov eax, dword ptr [ebp-0x34]
    mov dword ptr [{V+D_PX:#x}], eax
    mov eax, dword ptr [ebp-0x30]
    mov dword ptr [{V+D_PY:#x}], eax
    mov dword ptr [{V+D_PCAM:#x}], esi
    mov dword ptr [{V+D_PVALID:#x}], 1
    fld dword ptr [0x9F1670]
    jmp 0x6070D1
    """
def section(V):
    ks = Ks(KS_ARCH_X86, KS_MODE_32)
    reg, _ = ks.asm(reg_asm(V), V + O_REG)
    cam, _ = ks.asm(cam_asm(V), V + O_CAM)
    sec = bytearray(b'\xCC' * SIZE)
    sec[O_REG:O_REG + len(reg)] = bytes(reg)
    sec[O_CAM:O_CAM + len(cam)] = bytes(cam)
    for o in (D_PH, D_PS, D_PX, D_PY, D_PCAM, D_PVALID): sec[o:o + 4] = b'\0\0\0\0'
    for o, v in ((C_HMAX, 1.0), (C_HMIN, -1.0), (C_SMAX, 2.0), (C_SMIN, -2.0), (C_EPS, 0.01), (C_ZCAP, 100.0)): sec[o:o + 4] = struct.pack('<f', v)
    for o, s in ((S_ZERO, b'0\0'), (S_SPEED, b'20\0'), (S_HEIGHT, b'visusHeight\0'), (S_SHOULDER, b'visusShoulder\0')): sec[o:o + len(s)] = s
    return bytes(sec), len(reg), len(cam)
if __name__ == '__main__':
    V = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0x00E1A000
    sec, lr, lc = section(V)
    print('reg %d Byte (Platz %d), cam %d Byte (Platz %d)' % (lr, O_CAM - O_REG, lc, D_PH - O_CAM))
    from capstone import Cs, CS_ARCH_X86, CS_MODE_32
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    for i in md.disasm(sec[O_CAM:O_CAM + lc], V + O_CAM):
        print('%08X %-22s %s %s' % (i.address, i.bytes.hex(), i.mnemonic, i.op_str))
