# Lua-Funktion finden: String-VA -> Registrierungs-Tabelle (Name, Funktion). Aufruf: luafn.py Name [Name...]
import sys, struct
d = open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe', 'rb').read()
def f2va(o):
    if 0x400 <= o < 0x5DD800: return o + 0x400C00
    if 0x5DD800 <= o < 0x6B4000: return o - 0x5DD800 + 0x9DF000
    if 0x6B4000 <= o < 0x72CE00: return o - 0x6B4000 + 0xAB6000
for name in sys.argv[1:]:
    pat = name.encode() + b'\0'
    o = 0
    while True:
        o = d.find(pat, o)
        if o < 0: break
        if d[o - 1] == 0:
            va = f2va(o)
            ref = struct.pack('<I', va); r = 0
            while True:
                r = d.find(ref, r)
                if r < 0: break
                fn = struct.unpack_from('<I', d, r + 4)[0]
                if 0x401000 <= fn < 0x9DE000: print('%-28s str %08X  tab %08X  fn %08X' % (name, va, f2va(r), fn))
                r += 1
        o += 1
