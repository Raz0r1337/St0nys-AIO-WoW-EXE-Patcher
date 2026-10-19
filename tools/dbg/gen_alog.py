#!/usr/bin/env python3
# Erzeugt die PowerShell-Funktion Add-AssetDebugLog fuer apply_patches.ps1 aus FineWolfs make_debug_exe.py
# (gleicher Ordner): derselbe Assembler-Code, dieselben Daten, dieselben Hook-Stellen - nur legt der Patcher
# die Sektion an. Eine Zeile je Befehl; Adressen in der eigenen Sektion als ($CAVE + Offset), Sprungziele im
# Client als rel32 (Ziel - ($CAVE + Folgeoffset)). Die Einordnung kommt aus dem Vergleich zweier Basisadressen,
# das Ergebnis wird gegen Keystones Ausgabe fuer beide Basen geprueft.
# Aufruf: gen_alog.py <originale Wow.exe>   -> PowerShell auf stdout
import sys, os, re, struct, importlib.util, ctypes
import keystone, pefile
spec = importlib.util.spec_from_file_location('mde', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'make_debug_exe.py'))
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
raw = open(sys.argv[1], 'rb').read()
pe = pefile.PE(data=raw)
iat = {}
for e in pe.DIRECTORY_ENTRY_IMPORT:
    for imp in e.imports:
        if imp.name and imp.name.decode() in M.IMPORTS: iat[imp.name.decode()] = imp.address
assert sorted(iat) == sorted(M.IMPORTS), iat
def align(x, a): return (x + a - 1) & ~(a - 1)
LABELS = re.findall(r'(?m)^(\w+):', M.CODE)
def layout(base):
    """Wie make_debug_exe.main: Symbole und Datenblock fuer eine Sektion bei VA base."""
    data_va = base + 0x1000; sym = {}; data = bytearray(); offs = []
    for v in M.VARS: sym[v] = data_va + len(data); data += b'\0' * 4
    data += b'\0' * (align(len(data), 16) - len(data)); var_end = len(data)
    for k, s in M.STRINGS.items():
        sym[k] = data_va + len(data); offs.append((k, len(data), s)); data += s.encode('ascii') + b'\0'
    sym['S_SESSION_LEN'] = len(M.STRINGS['S_SESSION'])
    data += b'\0' * (align(len(data), 16) - len(data)); str_end = len(data)
    sym['RING'] = data_va + len(data); data += b'\0' * (M.RING_SLOTS * M.RING_SLOT_SIZE)
    sym.update(iat)
    sym.update(RING_MASK=M.RING_SLOTS - 1, RING_SLOTS=M.RING_SLOTS, RING_SLOT_SIZE=M.RING_SLOT_SIZE,
               RING_SLOT_SIZE_M1=M.RING_SLOT_SIZE - 1, WOW_FILTER=M.WOW_FILTER, MAP_DIR=M.MAP_DIR, MAP_NAME=M.MAP_NAME)
    S = M.SITES
    sym['SFileOpenFileEx_RESUME'] = S['SFileOpenFileEx'][0] + 9
    sym['CM2Scene_CreateModel_RESUME'] = S['CM2Scene::CreateModel'][0] + 6
    sym['CMapObj_Create_RESUME'] = S['CMapObj::Create'][0] + 7
    sym['M2_DRAW_RESUME'] = S['CM2Scene batch loop'][0] + 6
    sym['TEX_RESUME'] = S['TextureCreate cache miss'][0] + 6
    sym['TERRAIN_RESUME'] = S['Terrain chunk loop'][0] + 7
    return sym, bytes(data), offs, var_end, str_end
ORIG = {'SFileOpenFileEx_ORIG': 'SFileOpenFileEx', 'CM2Scene_CreateModel_ORIG': 'CM2Scene::CreateModel',
        'CMapObj_Create_ORIG': 'CMapObj::Create', 'TEX_ORIG': 'TextureCreate cache miss', 'TERRAIN_ORIG': 'Terrain chunk loop'}
def source(sym):
    fmt = {k: '%#x' % v for k, v in sym.items()}
    for key, site in ORIG.items(): fmt[key] = '.byte ' + ', '.join('%#x' % b for b in bytes.fromhex(M.SITES[site][1]))
    return M.CODE.format(**fmt)
def strip(l): return l.split(';')[0].rstrip()
def assemble(base):
    sym = layout(base)[0]
    src = '\n'.join(strip(l) for l in source(sym).splitlines() if strip(l).strip())
    ks = keystone.Ks(keystone.KS_ARCH_X86, keystone.KS_MODE_32)
    enc, _ = ks.asm(src + '\n' + '\n'.join('.long ' + l for l in LABELS), base)
    code = bytes(enc[:-4 * len(LABELS)])
    lab = dict(zip(LABELS, struct.unpack_from('<%dI' % len(LABELS), bytes(enc), len(code))))
    return code, lab, sym
A, B = 0x10000000, 0x20000000
codeA, labA, symA = assemble(A)
codeB, labB, symB = assemble(B)
assert len(codeA) == len(codeB) and len(codeA) <= 0x1000
# Zeile fuer Zeile: symbolische Quelle (fuer Kommentare) und Befehle mit Adresse (Basis A)
symbolic = M.CODE
for key, site in ORIG.items(): symbolic = symbolic.replace('{%s}' % key, '.byte ORIGINAL ' + site)
symbolic = re.sub(r'\{(\w+)\}', r'\1', symbolic)
lines_sym = [strip(l).strip() for l in symbolic.splitlines() if strip(l).strip()]
lines_a = [strip(l).strip() for l in source(symA).splitlines() if strip(l).strip()]
lines_b = [strip(l).strip() for l in source(symB).splitlines() if strip(l).strip()]
assert len(lines_sym) == len(lines_a) == len(lines_b)
import capstone
_md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
def one(line, pos, code, base):
    """Bytes der Quellzeile an pos im fertig assemblierten Code: .byte-Zeilen nach Anzahl, sonst ein Befehl (Capstone)."""
    if line.startswith('.byte '): return code[pos:pos + len(line[6:].split(','))]
    ins = next(_md.disasm(code[pos:pos + 16], base + pos))
    return code[pos:pos + ins.size]
out = []; pos = 0; DELTA = B - A
def hx(bs): return ', '.join('0x%02X' % b for b in bs)
for ls, la, lb in zip(lines_sym, lines_a, lines_b):
    m = re.match(r'^(\w+):$', la)
    if m:
        assert labA[m.group(1)] == A + pos, la
        out.append(('label', m.group(1), pos)); continue
    ba = one(la, pos, codeA, A); bb = one(lb, pos, codeB, B)
    assert len(ba) == len(bb) and ba, la
    parts = []; i = 0; end = pos + len(ba)
    while i < len(ba):
        if ba[i] == bb[i]:
            j = i
            while j < len(ba) and ba[j] == bb[j]: j += 1
            # ein unveraendertes Byte direkt vor einem 4-Byte-Feld gehoert nicht zum Feld
            parts.append(('raw', ba[i:j])); i = j; continue
        # Feld beginnt hoechstens 3 Byte frueher (gleiche Bytes am Feldanfang moeglich)
        k = i
        while k > 0 and (k + 4 > len(ba) or (struct.unpack_from('<I', bb, k)[0] - struct.unpack_from('<I', ba, k)[0]) % 2**32 not in (DELTA % 2**32, (-DELTA) % 2**32)):
            k -= 1
        va = struct.unpack_from('<I', ba, k)[0]; vb = struct.unpack_from('<I', bb, k)[0]
        d = (vb - va) % 2**32
        # raw-Teil vor dem Feld kuerzen
        cut = i - k
        if cut:
            t, b0 = parts[-1]; assert t == 'raw' and len(b0) >= cut; parts[-1] = ('raw', b0[:-cut])
            if not parts[-1][1]: parts.pop()
        if d == DELTA % 2**32:
            parts.append(('abs', va - A))                                   # Adresse in der Sektion
        elif d == (-DELTA) % 2**32:
            assert k + 4 == len(ba), la                                     # rel32 steht am Befehlsende
            tgt = (A + end + struct.unpack_from('<i', ba, k)[0]) % 2**32
            parts.append(('rel', tgt, end))                                 # Ziel im Client
        else:
            raise SystemExit('unklar: ' + la)
        i = k + 4
    out.append(('ins', parts, ls, pos, ba)); pos = end
assert pos == len(codeA)
# Kontrolle: Rekonstruktion fuer beide Basen
for base, code in ((A, codeA), (B, codeB), (0xDFD000, assemble(0xDFD000)[0])):
    r = bytearray()
    for o in out:
        if o[0] != 'ins': continue
        for p in o[1]:
            if p[0] == 'raw': r += p[1]
            elif p[0] == 'abs': r += struct.pack('<I', (base + p[1]) % 2**32)
            else: r += struct.pack('<i', ((p[1] - (base + p[2]) + 2**31) % 2**32) - 2**31)
    assert bytes(r) == code, hex(base)
# ---- PowerShell ausgeben ----
sym, data, offs, var_end, str_end = layout(A)
P = []
w = P.append
SITES = M.SITES
def fo(va): return va - 0x400C00
w('function Add-AssetDebugLog {')
w('    # Hook-Stellen mit den Original-Bytes von 3.3.5a 12340 (wie in make_debug_exe.py geprueft)')
for name, (va, orig) in SITES.items():
    w("    Assert-Bytes 0x%X @(%s) 'Asset-Debug-Log'   # VA 0x%X %s" % (fo(va), hx(bytes.fromhex(orig)), va, name))
w('    $e = RU32 $script:f 0x3C')
w('    $nsec = RU16 $script:f ($e + 6)')
w('    $lastSo = $e + 24 + (RU16 $script:f ($e + 20)) + 40 * ($nsec - 1)')
w('    $rva = AlignUp ((RU32 $script:f ($lastSo + 12)) + (RU32 $script:f ($lastSo + 8))) (RU32 $script:f ($e + 24 + 32))')
w('    $CAVE = (RU32 $script:f ($e + 24 + 28)) + $rva          # Code ab $CAVE, Daten ab $CAVE + 0x1000')
w('    $c = New-Object System.Collections.Generic.List[byte]')
LABNAME = {o[2]: o[1] for o in out if o[0] == 'label'}
for o in out:
    if o[0] == 'label':
        w('    # %s:  (+0x%X)' % (o[1], o[2])); continue
    _, parts, ls, at, ba = o
    code = []; 
    for p in parts:
        if p[0] == 'raw': code.append('AddRaw $c @(%s)' % hx(p[1]))
        elif p[0] == 'abs': code.append('AddLE32 $c ($CAVE + 0x%X)' % p[1])
        else: code.append('AddLE32 $c (0x%X - ($CAVE + 0x%X))' % (p[1], p[2]))
    txt = '; '.join(code)
    cm = ls
    if ls.startswith('.byte ORIGINAL'):
        cm = 'urspruengliche Bytes von %s' % ls[len('.byte ORIGINAL '):]
    w('    %-58s # %s' % (txt, cm))
w('    while ($c.Count -lt 0x1000) { [void]$c.Add(0) }')
w('    # Daten (+0x1000): %d Variablen zu 4 Byte (%s), auf 16 Byte aufgefuellt' % (len(M.VARS), ', '.join(M.VARS)))
w('    for ($i = 0; $i -lt 0x%X; $i++) { [void]$c.Add(0) }' % var_end)
for k, o, s in offs:
    crlf = s.endswith('\r\n'); body = s[:-2] if crlf else s
    assert "'" not in body and '\r' not in body and '\n' not in body
    w("    AddAsciiZ $c '%s'%s%s# %s (+0x%X)" % (body, ' -CrLf' if crlf else '', ' ' * max(1, 60 - len(body) - (6 if crlf else 0)), k, 0x1000 + o))
w('    while ($c.Count -lt 0x%X) { [void]$c.Add(0) }' % (0x1000 + str_end))
w('    # Ringpuffer (+0x%X): die letzten %d geoeffneten Dateinamen zu je %d Byte' % (0x1000 + str_end, M.RING_SLOTS, M.RING_SLOT_SIZE))
w('    for ($i = 0; $i -lt %d; $i++) { [void]$c.Add(0) }' % (M.RING_SLOTS * M.RING_SLOT_SIZE))
w('    [void](Add-SectionBlock \'.alog\' $rva $c.Count $c.ToArray() ([uint32]3758096416) 0)   # 0xE0000020 = Code | ausfuehrbar | lesbar | schreibbar')
lab = {o[1]: o[2] for o in out if o[0] == 'label'}
def hook(kind, site, label, length):
    va = SITES[site][0]; op = '0xE9' if kind == 'jmp' else '0xE8'
    nops = ', 0x90' * (length - 5)
    w("    Patch 0x%X ([byte[]]((Get-Rel32 @(%s) 0x%X ($CAVE + 0x%X))%s))   # VA 0x%X %s -> %s %s" % (
        fo(va), op, va, lab[label], (' + @(' + nops[2:] + ')') if nops else '', va, site, kind, label))
hook('jmp', 'SFileOpenFileEx', 'hk_open', 9)
hook('jmp', 'CM2Scene::CreateModel', 'hk_m2create', 6)
hook('jmp', 'CMapObj::Create', 'hk_wmocreate', 7)
hook('jmp', 'CM2Scene batch loop', 'hk_m2draw', 6)
hook('call', 'WMO group render A', 'hk_wmodraw_a', 6)
hook('call', 'WMO group render B', 'hk_wmodraw_b', 6)
hook('jmp', 'TextureCreate cache miss', 'hk_texload', 6)
hook('jmp', 'Terrain chunk loop', 'hk_terrain', 7)
va = SITES['SetUnhandledExceptionFilter(WoW filter)'][0]
w("    Patch 0x%X ([BitConverter]::GetBytes([uint32]($CAVE + 0x%X)))   # VA 0x%X push 0x%X -> push hk_filter" % (fo(va) + 1, lab['hk_filter'], va + 1, M.WOW_FILTER))
w('}')
print('\n'.join(P))
print('# code 0x%X Byte, Daten 0x%X Byte' % (len(codeA), len(data)), file=sys.stderr)
