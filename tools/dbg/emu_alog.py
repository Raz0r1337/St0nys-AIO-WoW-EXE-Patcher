#!/usr/bin/env python3
# Emuliert die Hooks des Asset-Debug-Logs (Patch "assetdebug") in einer gepatchten Wow.exe mit unicorn:
# Windows-Funktionen als Attrappen (WriteFile schneidet beide Logs mit), die Originalfunktionen des Clients als
# Stubs. Prueft Logzeilen, Rueckgabewerte, Stack und gesicherte Register - auch den Absturz-Bericht - und das
# Fehler-Log (St0ny): OPEN-FAIL, Absturzbericht und alle umgeleiteten WoW-Fehlermeldungen (WOW-ERROR).
# Aufruf: emu_alog.py <gepatchte Wow.exe>
import sys, os, struct, re, importlib.util
from unicorn import *
from unicorn.x86_const import *
import pefile
d = open(sys.argv[1], 'rb').read(); pe = pefile.PE(data=d)
IB = pe.OPTIONAL_HEADER.ImageBase
mu = Uc(UC_ARCH_X86, UC_MODE_32)
mu.mem_map(IB, (pe.OPTIONAL_HEADER.SizeOfImage + 0xFFF) & ~0xFFF)
mu.mem_write(IB, d[:0x1000])
for s in pe.sections:
    mu.mem_write(IB + s.VirtualAddress, d[s.PointerToRawData:s.PointerToRawData + min(s.SizeOfRawData, s.Misc_VirtualSize or s.SizeOfRawData)])
# Sektionsanfang aus dem Hook: der Push bei 0x772B20 zeigt auf hk_filter im ersten Code-Page der Sektion, die
# auf 0x1000 ausgerichtet beginnt. So geht es auch, wenn der Patcher mangels freier Sektionskoepfe die letzte
# Sektion erweitert hat (dann gibt es keine eigene .alog).
o = pe.get_offset_from_rva(0x772B21 - IB)
CAVE = struct.unpack_from('<I', d, o)[0] & ~0xFFF
assert d[pe.get_offset_from_rva(0x772B20 - IB)] == 0x68 and CAVE >= IB + 0x9FD000, hex(CAVE)
assert d[pe.get_offset_from_rva(CAVE + 0x1040 - IB):].startswith(b'Logs\\AssetDebug.log\0'), 'Datenblock nicht bei +0x1000'
spec = importlib.util.spec_from_file_location('mde', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'make_debug_exe_st0ny.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
mu.mem_map(0, 0x1000)                      # fs:[0] (SEH-Kette) liest Adresse 0
STK = 0x100000; mu.mem_map(STK, 0x100000)
HEAP = 0x300000; mu.mem_map(HEAP, 0x100000)
STUB = 0x2000000; mu.mem_map(STUB, 0x10000); mu.mem_write(STUB, b'\xF4' * 0x10000)
TRAP = STUB + 0xFF00
hp = [HEAP]
def alloc(b):
    a = hp[0]; mu.mem_write(a, b); hp[0] = (a + len(b) + 15) & ~15; return a
def cstr(s): return alloc(s.encode() + b'\0')
def r32(a): return struct.unpack('<I', mu.mem_read(a, 4))[0]
def w32(a, v): mu.mem_write(a, struct.pack('<I', v & 0xFFFFFFFF))
def rstr(a, n=512):
    b = bytes(mu.mem_read(a, n)); return b.split(b'\0')[0].decode('latin-1')
LOG = []; ELOG = []; FILES = []; ODS = []; STATE = {'fail': set()}
H_LOG, H_ELOG = 0x100, 0x200
def mapped(a, n):
    for b, e, _ in mu.mem_regions():
        if b <= a and a + n - 1 <= e: return True
    return False
def wsprintf(buf, fmt, argp):
    f = rstr(fmt, 1024); out = ''; i = 0
    for m in re.finditer(r'%(0?)(\d*)([sudiXx%])|[^%]+', f):
        if not m.group(3): out += m.group(0); continue
        t = m.group(3)
        if t == '%': out += '%'; continue
        v = r32(argp + 4 * i); i += 1
        w = int(m.group(2) or 0); z = m.group(1) == '0'
        if t == 's': x = rstr(v) if v else '(null)'
        elif t == 'u': x = str(v)
        elif t in 'di': x = str(v - 2**32 if v & 0x80000000 else v)
        elif t == 'X': x = '%X' % v
        else: x = '%x' % v
        if t != 's' and w: x = x.rjust(w, '0' if z else ' ')
        out += x
    out = out[:1024]
    mu.mem_write(buf, out.encode('latin-1') + b'\0'); return len(out)
API = {}   # Name -> (Anzahl Argumente (stdcall) oder None (cdecl), Funktion(args) -> eax)
def api(name, n):
    def deco(f): API[name] = (n, f); return f
    return deco
@api('CreateFileA', 7)
def _(a):
    n = rstr(a[0]); FILES.append(n)
    if n in STATE['fail']: return 0xFFFFFFFF
    return H_ELOG if 'AssetErrors' in n else H_LOG
@api('SetFilePointer', 4)
def _(a): return 0
@api('WriteFile', 5)
def _(a):
    assert a[0] in (H_LOG, H_ELOG)
    (LOG if a[0] == H_LOG else ELOG).append(bytes(mu.mem_read(a[1], a[2])).decode('latin-1'))
    if a[3]: w32(a[3], a[2])
    return 1
@api('FlushFileBuffers', 1)
def _(a): (LOG if a[0] == H_LOG else ELOG).append('<flush>'); return 1
@api('GetTickCount', 0)
def _(a): return 1234567
@api('GetCurrentThreadId', 0)
def _(a): return 0xA1C
@api('Sleep', 1)
def _(a): return 0
@api('IsBadReadPtr', 2)
def _(a): return 0 if mapped(a[0], a[1]) else 1
@api('OutputDebugStringA', 1)
def _(a): ODS.append(rstr(a[0])); return 0
@api('wsprintfA', None)
def _(a): return wsprintf(a[0], a[1], STATE['esp'] + 12)
stubs = {}
for e in pe.DIRECTORY_ENTRY_IMPORT:
    for imp in e.imports:
        if imp.name and imp.name.decode() in API:
            sa = STUB + 0x10 * len(stubs); stubs[sa] = imp.name.decode(); w32(imp.address, sa)
assert len(stubs) == len(API), stubs
# Originalfunktionen des Clients als Stubs: Ergebnis setzen und wie das Original zurueckkehren
ORIG = {}
def orig(va):
    def deco(f): ORIG[va] = f; return f
    return deco
@orig(0x424B59)                  # Rest von SFileOpenFileEx: Prolog (push ebp/mov ebp,esp) lief schon
def _():
    ebp = mu.reg_read(UC_X86_REG_EBP); name = rstr(r32(ebp + 12))
    ok = 0 if 'Missing' in name else 1
    if ok: w32(r32(ebp + 20), 0xF11E)
    return ok, 'leave', 0x10
@orig(0x81F8F6)                  # Rest von CM2Scene::CreateModel
def _(): return 0x1A2B3C40, 'leave', 8
@orig(0x7B0CC7)                  # Rest von CMapObj::Create (push ebx lief schon)
def _(): return 0x0BADF00D, 'popebx_leave', 0
@orig(0x772760)                  # WoWs eigener Ausnahme-Filter
def _():
    esp = mu.reg_read(UC_X86_REG_ESP); STATE['filter'] = (r32(esp), r32(esp + 4)); return 1, 'ret', 4
def hook(uc, addr, size, ud):
    if addr in stubs:
        n, f = API[stubs[addr]]; esp = uc.reg_read(UC_X86_REG_ESP); STATE['esp'] = esp
        args = [r32(esp + 4 + 4 * i) for i in range(n if n is not None else 2)]
        eax = f(args); ret = r32(esp)
        uc.reg_write(UC_X86_REG_EAX, eax & 0xFFFFFFFF)
        uc.reg_write(UC_X86_REG_ESP, esp + 4 + 4 * (n or 0)); uc.reg_write(UC_X86_REG_EIP, ret)
    elif addr in ORIG:
        eax, how, pop = ORIG[addr]()
        esp = uc.reg_read(UC_X86_REG_ESP); ebp = uc.reg_read(UC_X86_REG_EBP)
        if how == 'popebx_leave': uc.reg_write(UC_X86_REG_EBX, r32(esp)); how = 'leave'
        if how == 'leave': esp = ebp; uc.reg_write(UC_X86_REG_EBP, r32(esp)); esp += 4
        ret = r32(esp); uc.reg_write(UC_X86_REG_EAX, eax)
        uc.reg_write(UC_X86_REG_ESP, esp + 4 + pop); uc.reg_write(UC_X86_REG_EIP, ret)
    elif addr == TRAP:
        uc.emu_stop()
mu.hook_add(UC_HOOK_CODE, hook)
fails = 0
def ok(what, cond):
    global fails
    print('  %s %s' % ('OK  ' if cond else 'FAIL', what)); fails += 0 if cond else 1
REGS = {'ebx': UC_X86_REG_EBX, 'esi': UC_X86_REG_ESI, 'edi': UC_X86_REG_EDI, 'ebp': UC_X86_REG_EBP}
def call(va, args, ecx=None, cdecl=False):
    """Ruft va wie der Client auf und prueft Stack und gesicherte Register."""
    esp0 = STK + 0xF0000
    for k, (r, v) in enumerate(REGS.items()): mu.reg_write(v, 0x11110000 + k)
    if ecx is not None: mu.reg_write(UC_X86_REG_ECX, ecx)
    esp = esp0
    for v in reversed(args): esp -= 4; w32(esp, v)
    esp -= 4; w32(esp, TRAP); mu.reg_write(UC_X86_REG_ESP, esp)
    mu.emu_start(va, TRAP + 1, count=200000)
    exp = esp0 - (4 * len(args) if cdecl else 0)
    keep = all(mu.reg_read(v) == 0x11110000 + k for k, v in enumerate(REGS.values()))
    return mu.reg_read(UC_X86_REG_EAX), mu.reg_read(UC_X86_REG_ESP) == exp and keep
def logtext(): return ''.join(LOG)
print('== SFileOpenFileEx (0x424B50): Datei gefunden')
out = alloc(b'\0' * 4)
eax, clean = call(0x424B50, [0x1234, cstr('Creature\\Foo\\Foo.m2'), 0, out])
ok('Rueckgabe 1, Handle geschrieben, Stack (ret 10h) und ebx/esi/edi/ebp unveraendert', eax == 1 and r32(out) == 0xF11E and clean)
ok('Log in Logs\\AssetDebug.log geoeffnet, Sitzungszeile', FILES == ['Logs\\AssetDebug.log'] and LOG[0] == '==== AssetDebug session start ====\r\n')
ok('Fehler-Log ohne Fehler nicht geoeffnet', ELOG == [])
ok('Zeile "OPEN      Creature\\Foo\\Foo.m2 (flags=0)"', LOG[1] == '0001234567 [0A1C] OPEN      Creature\\Foo\\Foo.m2 (flags=0)\r\n')
print('== SFileOpenFileEx: Datei fehlt')
eax, clean = call(0x424B50, [0x1234, cstr('Creature\\Foo\\Missing01.skin'), 2, alloc(b'\0' * 4)])
ok('Rueckgabe 0, Stack sauber', eax == 0 and clean)
ok('Zeile "OPEN-FAIL ... (flags=2)"', LOG[-1] == '0001234567 [0A1C] OPEN-FAIL Creature\\Foo\\Missing01.skin (flags=2)\r\n')
ok('Fehler-Log beim ersten Fehler geoeffnet (Logs\\AssetErrors.log), Sitzungszeile, dieselbe OPEN-FAIL-Zeile',
   FILES == ['Logs\\AssetDebug.log', 'Logs\\AssetErrors.log'] and ELOG == ['==== AssetErrors session start ====\r\n', LOG[-1]])
print('== CM2Scene::CreateModel (0x81F8F0, thiscall)')
eax, clean = call(0x81F8F0, [cstr('Creature\\Foo\\Foo.m2'), 0], ecx=0x5CE7E)
ok('Rueckgabe Modell, Stack (ret 8) und Register sauber', eax == 0x1A2B3C40 and clean)
ok('Zeile "M2-CREATE  Creature\\Foo\\Foo.m2 -> model=1A2B3C40"', LOG[-1].endswith('M2-CREATE  Creature\\Foo\\Foo.m2 -> model=1A2B3C40\r\n'))
print('== CMapObj::Create (0x7B0CC0, cdecl)')
eax, clean = call(0x7B0CC0, [cstr('World\\wmo\\Bar\\Bar.wmo')], cdecl=True)
ok('Rueckgabe Objekt, Stack (cdecl) und Register sauber', eax == 0x0BADF00D and clean)
ok('Zeile "WMO-CREATE World\\wmo\\Bar\\Bar.wmo -> mapobj=0BADF00D"', LOG[-1].endswith('WMO-CREATE World\\wmo\\Bar\\Bar.wmo -> mapobj=0BADF00D\r\n'))
print('== TextureCreate, nicht im Cache (0x4B9853 bis zum jle 0x4B9859)')
frame = STK + 0x80000; w32(frame - 4, 5)
for o, v in ((8, cstr('Textures\\Foo\\Bar.blp')), (0xC, 0x22), (0x10, 0), (0x14, 0x7)): w32(frame + o, v)
mu.reg_write(UC_X86_REG_EBP, frame); mu.reg_write(UC_X86_REG_ESP, frame - 0x200); mu.reg_write(UC_X86_REG_EAX, 0)
mu.emu_start(0x4B9853, 0x4B9859)
ef = mu.reg_read(UC_X86_REG_EFLAGS)
ok('am jle angekommen, [ebp-8] = eax, Vergleich [ebp-4]=5 mit 0 -> jle nicht genommen (ZF=0, SF=OF)', mu.reg_read(UC_X86_REG_EIP) == 0x4B9859 and r32(frame - 8) == 0 and not ef & 0x40 and bool(ef & 0x80) == bool(ef & 0x800))
ok('Zeile "TEX-LOAD   Textures\\Foo\\Bar.blp (gxflags=22 createflags=7)"', LOG[-1].endswith('TEX-LOAD   Textures\\Foo\\Bar.blp (gxflags=22 createflags=7)\r\n'))
ok('M2-CREATE, WMO-CREATE und TEX-LOAD nicht im Fehler-Log', len(ELOG) == 2)
print('== Zeichnen: M2-Schleife, WMO-Gruppen, Gelaende (nur im Speicher)')
n_log = len(LOG)
V = {n: CAVE + 0x1000 + 4 * i for i, n in enumerate(M.VARS)}
shared = alloc(b'\0' * 0x3C + b'Creature\\Foo\\Foo.m2\0' + b'\0' * 300)
model = alloc(b'\0' * 0x2C + struct.pack('<I', shared) + b'\0' * 0x300)
st = alloc(b'\0' * 0x100)
mu.reg_write(UC_X86_REG_EAX, model); mu.reg_write(UC_X86_REG_ESI, st); mu.reg_write(UC_X86_REG_ESP, STK + 0x70000)
mu.emu_start(0x823A20, 0x823A26)
ok('M2: [esi+68h] = shared wie im Original, M2_MODEL/M2_SHARED gemerkt, SEQ 1', r32(st + 0x68) == shared and r32(V['M2_MODEL']) == model and r32(V['M2_SHARED']) == shared and r32(V['SEQ']) == 1 == r32(V['M2_SEQ']))
mapobj = alloc(b'\0' * 0x1C + b'World\\wmo\\Bar\\Bar.wmo\0' + b'\0' * 300)
group = alloc(b'\0' * 0x18C + struct.pack('<I', mapobj) + b'\0' * 16)
w32(0xCFBECC, STUB + 0x800); w32(0xCFBEC4, STUB + 0x810)
mu.mem_write(STUB + 0x800, b'\xC3'); mu.mem_write(STUB + 0x810, b'\xC3')
for site, nxt in ((0x7ABFF0, 0x7ABFF6), (0x7AC011, 0x7AC017)):
    mu.reg_write(UC_X86_REG_ESI, group); mu.reg_write(UC_X86_REG_EAX, 0x77); mu.reg_write(UC_X86_REG_ESP, STK + 0x70000)
    mu.emu_start(site, nxt)
    ok('WMO 0x%X: Gruppe gemerkt, eax/esp unveraendert, weiter bei 0x%X' % (site, nxt), r32(V['WMO_GROUP']) == group and mu.reg_read(UC_X86_REG_EAX) == 0x77 and mu.reg_read(UC_X86_REG_ESP) == STK + 0x70000)
chunk = alloc(b'\0' * 0x34 + struct.pack('<ii', 32 * 16 + 5, 48 * 16 + 9) + b'\0' * 64)
mu.mem_write(0xCE07D0, b'World\\Maps\\Azeroth\0'); mu.mem_write(0xCE06D0, b'Azeroth\0')
frame = STK + 0x60000
mu.reg_write(UC_X86_REG_EBX, chunk); mu.reg_write(UC_X86_REG_EAX, 0x4242); mu.reg_write(UC_X86_REG_EBP, frame); mu.reg_write(UC_X86_REG_ESP, frame - 0x40)
mu.emu_start(0x798A6C, 0x798A73)
ok('Gelaende: push 1, ecx = Chunk, [ebp-10h] = eax wie im Original, Chunk gemerkt', r32(mu.reg_read(UC_X86_REG_ESP)) == 1 and mu.reg_read(UC_X86_REG_ESP) == frame - 0x44 and mu.reg_read(UC_X86_REG_ECX) == chunk and r32(frame - 0x10) == 0x4242 and mu.reg_read(UC_X86_REG_EAX) == 0x4242 and r32(V['TER_CHUNK']) == chunk)
ok('beim Zeichnen nichts ins Log geschrieben', len(LOG) == n_log)
print('== Absturz: Filter aus dem Push bei 0x772B20')
filt = r32(0x772B21)
ok('Push zeigt in die .alog-Sektion', CAVE <= filt < CAVE + 0x1000)
rec = alloc(struct.pack('<IIIIIII', 0xC0000005, 0, 0, 0x7ABFF6, 2, 0, 0x0000DEAD) + b'\0' * 64)
ctx = bytearray(0x2CC)
for off, v in ((0x9C, 0xED1), (0xA0, 0xE51), (0xA4, 0xEB1), (0xA8, 0xED2), (0xAC, 0xEC1), (0xB0, 0xEA1), (0xB4, 0xEB2), (0xB8, 0x7ABFF6), (0xC4, 0xE59)):
    struct.pack_into('<I', ctx, off, v)
ctxa = alloc(bytes(ctx)); ptrs = alloc(struct.pack('<II', rec, ctxa))
w32(V['LOCK'], 1)      # Absturz waehrend gehaltener Sperre
n_log = len(LOG); n_elog = len(ELOG)
eax, clean = call(filt, [ptrs])
crash = LOG[n_log:]; ecrash = ELOG[n_elog:]
ok('WoWs Filter danach mit demselben Argument aufgerufen, Stack sauber', STATE.get('filter', (0, 0))[1] == ptrs and clean)
ok('Sperre zurueckgesetzt (sonst Haenger)', r32(V['LOCK']) == 0)
want = ['!!!! CRASH: exception C0000005 at EIP 007ABFF6 (info0=0 info1=0000DEAD)',
        '!!!! EAX=00000EA1 EBX=00000EB1 ECX=00000EC1 EDX=00000ED2 ESI=00000E51 EDI=00000ED1',
        '!!!! EBP=00000EB2 ESP=00000E59',
        '!!!! last M2 drawn        (seq 1): Creature\\Foo\\Foo.m2  [model=%08X shared=%08X]' % (model, shared),
        '!!!! last WMO group drawn (seq 3): World\\wmo\\Bar\\Bar.wmo  [group=%08X mapobj=%08X]' % (group, mapobj),
        '!!!! last terrain chunk drawn (seq 4): World\\Maps\\Azeroth\\Azeroth_32_48.adt chunk (5,9)  [chunk=%08X]' % chunk,
        '!!!! recent open #0: Creature\\Foo\\Foo.m2',
        '!!!! recent open #1: Creature\\Foo\\Missing01.skin']
got = [l[len('0001234567 [0A1C] '):].rstrip('\r\n') for l in crash if l != '<flush>']
for w_ in want: ok('Bericht: ' + w_[:70], w_ in got)
ok('Log am Ende auf die Platte geschrieben (FlushFileBuffers)', crash[-1] == '<flush>')
ok('Fehler-Log: derselbe Bericht (%d Zeilen), am Ende ebenfalls FlushFileBuffers' % (len(crash) - 1), ecrash == crash and len(crash) > len(want))
print('== Fallback: Logs-Ordner fehlt')
LOG.clear(); ELOG.clear(); FILES.clear(); w32(V['HFILE'], 0); w32(V['HFILE2'], 0); STATE['fail'] = {'Logs\\AssetDebug.log', 'Logs\\AssetErrors.log'}
call(0x424B50, [0x1234, cstr('Interface\\x.blp'), 0, alloc(b'\0' * 4)])
ok('zweiter Versuch AssetDebug.log neben der Exe', FILES == ['Logs\\AssetDebug.log', 'AssetDebug.log'] and LOG[0].startswith('====') and 'OPEN      Interface\\x.blp' in LOG[1])
call(0x424B50, [0x1234, cstr('Interface\\Missing.blp'), 0, alloc(b'\0' * 4)])
ok('Fehler-Log: zweiter Versuch AssetErrors.log neben der Exe', FILES[2:] == ['Logs\\AssetErrors.log', 'AssetErrors.log'] and ELOG[0].startswith('==== AssetErrors') and 'OPEN-FAIL Interface\\Missing.blp' in ELOG[1])
print('== Fehler-Log laesst sich gar nicht anlegen')
LOG.clear(); ELOG.clear(); FILES.clear(); w32(V['HFILE2'], 0); STATE['fail'] = {'Logs\\AssetErrors.log', 'AssetErrors.log'}
for i in range(2):
    eax, clean = call(0x424B50, [0x1234, cstr('Missing%d.blp' % i), 0, alloc(b'\0' * 4)])
ok('nur ein Versuch (2 CreateFileA), danach still; Zeilen weiter im grossen Log, Stack sauber',
   FILES == ['Logs\\AssetErrors.log', 'AssetErrors.log'] and ELOG == [] and r32(V['HFILE2']) == 0xFFFFFFFF and 'OPEN-FAIL Missing1.blp' in LOG[-1] and clean)
STATE['fail'] = set()
ok('kein OutputDebugString (ODS aus)', ODS == [])
print('== WoWs eigene Fehlermeldungen: %d umgeleitete Aufrufe von 0x%X' % (len(M.WOWERR_SITES), M.DEBUG_PRINTF))
LOG.clear(); ELOG.clear(); FILES.clear(); w32(V['HFILE'], 0); w32(V['HFILE2'], 0)
HKW = None; bad_site = []
for va, fmt in M.WOWERR_SITES:
    po = pe.get_offset_from_rva(va - 5 - IB)
    tgt = va + 5 + struct.unpack_from('<i', d, po + 6)[0]
    HKW = HKW or tgt
    if not (d[po] == 0x68 and d[po + 5] == 0xE8 and tgt == HKW and CAVE <= tgt < CAVE + 0x1000): bad_site.append(hex(va))
ok('alle Aufrufe gehen auf dieselbe Stelle in der Sektion (hk_wowerr), "push <Text>" davor unveraendert', not bad_site)
def expect(fmt, args):
    out = ''; i = 0
    for m in re.finditer(r'%(0?)(\d*)([sudiXx%])|[^%]+', fmt):
        if not m.group(3): out += m.group(0); continue
        t = m.group(3)
        if t == '%': out += '%'; continue
        v = args[i]; i += 1
        out += v if t == 's' else str(v) if t in 'udi' else ('%X' % v if t == 'X' else '%x' % v)
    return ' '.join(out.split())
ALLR = [UC_X86_REG_EAX, UC_X86_REG_EBX, UC_X86_REG_ECX, UC_X86_REG_EDX, UC_X86_REG_ESI, UC_X86_REG_EDI, UC_X86_REG_EBP]
n_ok = 0; first_open = None
for va, fmt in M.WOWERR_SITES:
    conv = re.findall(r'%[-0-9]*([sudiXx])', fmt)
    pyargs = []; raw = []
    for k, t in enumerate(conv):
        if t == 's': x = 'Arg%d\\Datei%d.m2' % (k, k); pyargs.append(x); raw.append(cstr(x))
        elif t in 'di': pyargs.append(k + 7); raw.append(k + 7)
        elif t == 'u': pyargs.append(40 + k); raw.append(40 + k)
        else: pyargs.append(0xABC0 + k); raw.append(0xABC0 + k)
    esp0 = STK + 0xE0000
    for k, v in enumerate(raw): w32(esp0 + 4 * k, v)
    for k, r in enumerate(ALLR): mu.reg_write(r, 0x51E00000 + k)
    mu.reg_write(UC_X86_REG_EFLAGS, 0x8C7); mu.reg_write(UC_X86_REG_ESP, esp0)
    nl, ne = len(LOG), len(ELOG)
    mu.emu_start(va - 5, va + 5, count=200000)
    want_line = '0001234567 [0A1C] WOW-ERROR %s\r\n' % expect(fmt, pyargs)
    regs = all(mu.reg_read(r) == 0x51E00000 + k for k, r in enumerate(ALLR))
    flags = (mu.reg_read(UC_X86_REG_EFLAGS) & 0xCD5) == 0x8C5
    stack = mu.reg_read(UC_X86_REG_ESP) == esp0 - 4 and mu.reg_read(UC_X86_REG_EIP) == va + 5
    lines = (LOG[nl:] in ([want_line], ['==== AssetDebug session start ====\r\n', want_line])
             and ELOG[ne:] in ([want_line], ['==== AssetErrors session start ====\r\n', want_line]))
    if regs and flags and stack and lines: n_ok += 1
    else: print('    Stelle 0x%X: Register %s, Flags %s, Stack %s, Zeilen %s' % (va, regs, flags, stack, lines), LOG[nl:], ELOG[ne:])
ok('%d/%d Stellen: Zeile "WOW-ERROR <Meldung>" in beiden Logs, alle Register, Flags und Stack wie vorher, weiter hinter dem Aufruf' % (n_ok, len(M.WOWERR_SITES)), n_ok == len(M.WOWERR_SITES))
ok('Fehler-Log einmal geoeffnet, Sitzungszeile vorne', FILES == ['Logs\\AssetDebug.log', 'Logs\\AssetErrors.log'] and ELOG[0] == '==== AssetErrors session start ====\r\n')
smp = {l.split('WOW-ERROR ', 1)[1].rstrip('\r\n') for l in ELOG[1:]}
for w_ in ('Model2: File not found: Arg0\\Datei0.m2', 'Bad zone ID 7', 'Corrupt model sequence data: Arg0\\Datei0.m2 (8)',
           'Error, unknown displayInfo 7 specified for player race 8 sex 9!', 'Error, NO creature display records found',
           '*** WARNING NAN in AnimEventCallback position eventId abc0 eventData 8 model Arg2\\Datei2.m2 unitname Arg3\\Datei3.m2 xyz = abc4 abc5 abc6',
           'XXXX XXXX ERROR!! Sound Kit ID 7 is a looping sound but there is no user handle! This sound will play forever!! XXXX'):
    ok('Beispiel: ' + w_[:80], w_ in smp)
print('DONE fails=%d' % fails)
sys.exit(1 if fails else 0)
