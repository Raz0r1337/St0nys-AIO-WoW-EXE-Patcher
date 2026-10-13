# Byte-Definitionen der beiden neuen Patches (Datei-Offsets = VA - 0x400C00)
import struct
F=lambda va: va-0x400C00
def rel32(src_next, tgt): return struct.pack('<i', tgt-src_next)

YEAR2031 = []
# 1) Entpacker: Jahr 31 -> 31 statt -1
YEAR2031.append((F(0x76CA1B), bytes([0xEB])))
# 2) Feiertags-Auswertung 0x5BFAB0: Prolog kompakter + Stub (Jahr 31 -> -1)
holi = bytes([
    0x75,0x03,             # 5BFB0F jne 5BFB14
    0x6A,0x18,             # 5BFB11 push 18h
    0x59,                  # 5BFB13 pop ecx
    0x6B,0xC1,0x3C,        # 5BFB14 imul eax,ecx,3Ch
    0x89,0x45,0xEC,        # 5BFB17 mov [ebp-14h],eax
    0x33,0xC0,             # 5BFB1A xor eax,eax
    0x89,0x45,0xF0,        # 5BFB1C mov [ebp-10h],eax
    0xEB,0x0F,             # 5BFB1F jmp 5BFB30
    0x59,                  # 5BFB21 pop ecx
    0x59,                  # 5BFB22 pop ecx
    0x83,0x7B,0x14,0x1F,   # 5BFB23 cmp dword [ebx+14h],1Fh
    0x75,0x25,             # 5BFB27 jne 5BFB4E
    0x83,0x4B,0x14,0xFF,   # 5BFB29 or dword [ebx+14h],-1
    0xEB,0x1F,             # 5BFB2D jmp 5BFB4E
    0x90,                  # 5BFB2F (nie ausgefuehrt)
])
assert len(holi)==0x5BFB30-0x5BFB0F, len(holi)
YEAR2031.append((F(0x5BFB0F), holi))
YEAR2031.append((F(0x5BFB4B), bytes([0xEB,0xD4,0x90])))   # add esp,8 -> jmp 5BFB21 / nop
# 3a) CalendarGetMaxDate: 1.1.2031-1 Tag -> 1.1.2032-1 Tag
YEAR2031.append((F(0x5B82C0), bytes([0x20])))
# 3b) Max-Erstelldatum (0x5B7A80): hoechstens 31.12.2031
mc = bytes([
    0x56,                          # 5B7A83 push esi
    0x8B,0x75,0x08,                # 5B7A84 mov esi,[ebp+8]
    0xA1,0xAC,0x7F,0xD3,0x00,      # 5B7A87 mov eax,[D37FACh]   Jahr
    0x6B,0xC0,0x0C,                # 5B7A8C imul eax,eax,0Ch
    0x03,0x05,0xA8,0x7F,0xD3,0x00, # 5B7A8F add eax,[D37FA8h]   + Monat
    0x83,0xC0,0x0D,                # 5B7A95 add eax,0Dh
    0x3D,0x80,0x01,0x00,0x00,      # 5B7A98 cmp eax,180h        (Jan 2032)
    0x7E,0x05,                     # 5B7A9D jle 5B7AA4
    0xB8,0x80,0x01,0x00,0x00,      # 5B7A9F mov eax,180h
    0x99,                          # 5B7AA4 cdq
    0x6A,0x0C,                     # 5B7AA5 push 0Ch
    0x59,                          # 5B7AA7 pop ecx
    0xF7,0xF9,                     # 5B7AA8 idiv ecx            eax=Jahr edx=Monat
    0x89,0x46,0x14,                # 5B7AAA mov [esi+14h],eax
    0x89,0x56,0x10,                # 5B7AAD mov [esi+10h],edx
    0x6A,0x00,                     # 5B7AB0 push 0
    0x6A,0xFF,                     # 5B7AB2 push -1
    0x8B,0xCE,                     # 5B7AB4 mov ecx,esi
    0xC7,0x46,0x0C,0,0,0,0,        # 5B7AB6 mov dword [esi+0Ch],0
]) 
mc += bytes([0x90])*((0x5B7AC4-0x5B7A83)-len(mc))
assert len(mc)==0x5B7AC4-0x5B7A83
YEAR2031.append((F(0x5B7A83), mc))
# 3c) Jahres-Klemmen 30 -> 31
for va in (0x5B8F33,0x5B8F38,0x5B8F9B,0x5B8F9F,0x5BFF46,0x5BFF5B):
    YEAR2031.append((F(va), bytes([0x1F])))
# 3d) Schleifen "Jahr < 31" -> "Jahr < 32"
for va in (0x5C01FB,0x5C04C1,0x5C2683,0x5C2893):
    YEAR2031.append((F(va), bytes([0x20])))

WOTLKEXT = []
LDR=0x4E5D00
name=b'WotLKExtensions.dll\x00'
ldr = bytes([0xC6,0x05,0x74,0xB4,0xB6,0x00,0x01])            # mov byte [B6B474h],1
ldr += bytes([0x68])+struct.pack('<I',LDR+0x1C)               # push offset name
ldr += bytes([0xFF,0x15,0x48,0xF2,0x9D,0x00])                 # call [LoadLibraryA]
ldr += bytes([0x68,0x70,0xEB,0x5E,0x00])                      # push 5EEB70h (Original-Befehl)
ldr += bytes([0xE9])+rel32(LDR+0x1C, 0x406D75)                # jmp 406D75
assert len(ldr)==0x1C
ldr += name
WOTLKEXT.append((F(0x406D70), bytes([0xE9])+rel32(0x406D75, LDR)))
WOTLKEXT.append((F(0x4DCCF0), bytes([0xB8,0,0,0,0,0xC3])))
WOTLKEXT.append((F(LDR), ldr))

AWESOME=[(0xABD0,bytes([0xE9,0xDB,0xA4,0x0D,0x00,0x90,0x90,0x90])),(0xDC0F0,bytes([0xB8,0,0,0,0,0xC3])),
 (0xE50B0,bytes([0xB8,0x01,0x00,0x00,0x00,0xA3,0x74,0xB4,0xB6,0x00,0x68,0xE0,0x5C,0x4E,0x00,0xE8,0x1C,0x68,0x38,0x00,0x83,0xC4,0x04,0x55,0x8B,0xEC,0xE8,0xA1,0x10,0xF2,0xFF,0xE9,0x04,0x5B,0xF2,0xFF]+[0xCC]*12)+b'AwesomeWotlkLib.dll\x00')]

def apply(data, plist):
    b=bytearray(data)
    for o,bs in plist: b[o:o+len(bs)]=bs
    return b
def ps(plist):
    out=[]
    for o,bs in plist:
        out.append('Patch 0x%X @(%s)'%(o,', '.join('0x%02X'%x for x in bs)))
    return out
if __name__=='__main__':
    for l in ps(YEAR2031): print(l)
    print()
    for l in ps(WOTLKEXT): print(l)
