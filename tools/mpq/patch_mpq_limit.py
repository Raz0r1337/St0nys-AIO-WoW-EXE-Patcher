"""Fix the MPQ handle-table capacity bug in the supported wow.exe build.

Requires Python 3.12 or later; uses only the standard library.
Usage: python patch_mpq_limit.py [--check | --restore] [executable]
The target may have any filename; the default is wow.exe next to this script.
Immutable backup: <target filename>.before-mpq-fix.bak

Root cause:
The loader at VA 0x405DD0 reserves 64 archive-handle slots, then writes
patch and base-archive handles without checking capacity at each write.
It only grows the table at 0x40624A-0x4062AE, after out-of-bounds writes
may already have corrupted the heap. The observed crash stack reaches
this late reallocation and the release of the damaged allocation.

Binary changes:
Replace MOV EBX,64 at VA 0x405E2E (file offset 0x522E) with a five-byte
relative CALL to a helper in a new executable, read-only .mpqfix section.
Before the original loading loops run, the helper reserves 2*N+64 slots,
where N is the number of discovered patch paths. It uses the client's
existing allocation routine, preserves registers and flags, replays the
replaced MOV instruction, and returns to the original code.
Update the PE section count, code size, image size, and checksum.

Why 2*N+64 is sufficient for this exact build:
There are 28 base-archive descriptors and only one type-3 descriptor
(alternate.MPQ). Each discovered patch can contribute its own handle and
at most one child handle. The remaining 64 slots cover base archives,
optional opens, and the output slot used by a failed open attempt.
The reservation is recomputed on every launch, not fixed at patch time.

Preserved behavior and scope:
The original loading order, archive priorities (including EBX=64), and
final table-size bookkeeping remain unchanged. Simply increasing the
MOV immediate would also change the initial patch priority.
This fixes the premature capacity overflow, not other crash causes or
the memory limits of a 32-bit process. Compatibility is checked using PE
layout, local instruction signatures, mapped addresses, and archive-table
structure, without a whole-file hash. Unrelated binary changes are allowed.
The hook file offset is resolved from the section table, not assumed.
Signed inputs lose their Authenticode directory when patched; restoration
recovers the exact original bytes, including the original signature.
Application is idempotent; restoration uses the verified original backup.
"""
import argparse
import os
from pathlib import Path
import struct

HOOK_VA = 0x405E2E
OLD = bytes.fromhex('bb40000000')

def align(n, a):
    return (n + a - 1) // a * a

# Exact local instruction signatures, not a whole-file fingerprint.
# Changes elsewhere in the executable do not affect compatibility.
# Whole routines are checked to cover stack layout, branch targets, and operands.
CODE_SIGNATURES = (
    # MPQ loader and stack layout: VA 0x00405DD0 through 0x00406488.
    (0x405DD0, bytes.fromhex(
        "558bec81ec50040000e8b2cdfffff6d81bc0f7d883c0018945ec33c98d642400c6817461ab000083c11081f9c0010000"
        "72eea802741268001f9e00e8301636008b402883c404eb05b870289e005356576a00508d4dd48945fce882fcffffbb40"
        "00000033ff391d3cfab200733c391d38fab20073348b0d44fab20085c9750d53b938fab200e8e6a11c008bc833d28bc3"
        "f7f18bf385d274062bca03cb8bf156b938fab200e877d9ffff8b75dc85f6891d3cfab2007654eb088da4240000000090"
        "a140fab2008b4de08b54b1fc8d04b85068000c00005352e8a4ba010085c074258b45e08b4cb0fc6864289e0051e8ae98"
        "360083c40885c07406891d6461ab0083c70183c30183ee0175b6897df033f69083be6c61ab000375258b55fc8b866861"
        "ab00525753e836eaffff83c40c84c0740d83c701c6867461ab000183c30183c61081fec001000072c733c03945f08945"
        "f80f8604010000eb078da424000000008b0d40fab2008b14818955e833f68bff83be6c61ab00030f85bd00000080be74"
        "61ab0000755c8b45fc68ffffff7f685c289e0050e81788360085c074458b4dfc68ffffff7f6854289e0051e800883600"
        "85c0742e8b55fc68ffffff7f684c289e0052e8e987360085c074178b45fc68ffffff7f6844289e0050e8d287360085c0"
        "75588b8e6861ab006800010000518d95b4feffff52e8568d36008d85b4feffff50e85a8e36008b1540fab2008d8db4fe"
        "ffff83e904c60408008b4de88d04ba506a00538d85b4feffff5051e810ba010085c0740683c70183c30183c61081fec0"
        "0100000f8227ffffff8b45f883c0013b45f08945f80f8205ffffff893d14fab200c745f83f000000893d18fab20033f6"
        "8b1540fab200c704ba000000008b866c61ab0083f8030f848801000083f8040f847f01000083f8028b45ec0f9445f785"
        "867061ab000f95c3e8c3c0010085c0740d83be6c61ab0002750433c0eb05b80100000084c30f84390100008b5dfc8b4d"
        "f88b866861ab00535751e881e8ffff83c40c84c00f851a0100003845f70f85110100008b966861ab00a15861ab005250"
        "68d01a9e008d8db0fdffff680401000051e88a8f36008d95b0fdffff68c81a9e0052e80996360083c41c85c0741e8bff"
        "8b0b8d95b0fdffff68c81a9e00528908e8eb95360083c40885c075e4e82fc001008bd868000100008d85b4feffff50e8"
        "acb6360050e846b93600f60550f0b20001742a8d8db4feffff516859f0b2005368c0279e00e846c9360083c41083c701"
        "836df801c6867461ab0001eb7a8b966861ab005268a0279e008d85b0fbffff680001000050e8e68e360083c41068ffff"
        "ff7f6884279e008d8db0fcffff51e87d8b36008d95b0fcffff528d85b0fbffff506a006a02e8e664460083c40450e81d"
        "65460083c410e815b6360050e86fd8360083c40483c701836df801c6867461ab0001eb0383c70183c61081fec0010000"
        "0f824afeffffe845bf010085c07407c745f840000000e825bf010085c0743b8b5dfc33f683be6c61ab000475228b4df8"
        "8b866861ab00535751e802e7ffff83c40c84c0740ac6867461ab000183c70183c61081fec001000072ca3b3d3cfab200"
        "76613b3d38fab20076598b0d44fab20085c9753283ff408bcf731c8d47ff23c774098bc88d41ff23c175f783f9017316"
        "b901000000eb0fc70544fab20040000000b94000000033d28bc7f7f18bf785d274062bca03cf8bf156b938fab200e83d"
        "d5ffffa140fab2008b0d18fab200893d3cfab200837c8840007409c605e1f9b20002eb0e837c883c000f95c28815e1f9"
        "b200e8696e0b008bf8687c279e0057e84c750b0083c40885c00f84610100006a00689cf9b2006874279e006868279e00"
        "57e80a700b006a006a108d45b450685c279e006868279e0057e882700b0083c42c85c00f84270100006a006a108d4dc4"
        "516854279e006868279e0057e85f700b0083c41885c00f84040100008d55c4528d45b45068d01a9e006a056848feb200"
        "e8fb8c360083c41433c0be48feb20033c98a1684d274130fbed2c1e00883c10103c283c60183f90472e768ffffff7f68"
        "48feb200684c279e00a3d08cb300e8cd83360085c00f94c333f68d9b000000008b04b5e02fad0068ffffff7f506848fe"
        "b200e8a983360085c0742984db741b8b0cb5e02fad0068ffffff7f516844279e00e88a83360085c0740a83c60183fe09"
        "7cbeeb5c89359cdec50083c6ff83fe0777160fb69698644000ff24958c6440006a01eb066a02eb026a00e8d118410083"
        "c404f645ec01742868001f9e00e8fe0f360083c4046a016a006a006a016848feb2008bc8e867043600c745fc48feb200"
        "57e8da580b008b75fc566a01e87fa72a0056e8e9caffff83c4108d4dd4e8eef8ffff5f5e5b8be55dc3"
    )),
    # Native handle-table allocator: VA 0x004037F0 through 0x0040387F.
    (0x4037F0, bytes.fromhex(
        "558bec8b45085356576a106afe8bf18b5e08688c63ab008d3c850000000057538906e8c9ad360085c0894608755b506a"
        "fe688c63ab0057e814ad360085db89460874468b46048b7d083bf872028bf833d285ff7625eb098da424000000008bff"
        "8b46088d0c950000000003c174058b0c19890883c2013bd772e66a006afe688c63ab0053e827ad36005f5e5b5dc20400"
    )),
    # Patch path enumeration: VA 0x00405AB0 through 0x00405D63.
    (0x405AB0, bytes.fromhex(
        "558bec81ecfc030000b8010000005333dbba280d9e00568bf1b938279e0057899510ffffff898d24ffffff89852cffff"
        "ff899538ffffff898540ffffff898d4cffffff898554ffffff898558ffffff899560ffffff898568ffffff89856cffff"
        "ff898d74ffffff89857cffffff894580895588894590894594894d9c8945a48945a8ba1c0d9e008945b88945bcb92c27"
        "9e008945cc8945d08945e08945e4bf1c279e008d8504feffff895e04895e08895e0c895e10899d04ffffff899d08ffff"
        "ff889d0cffffffc78514ffffff10279e00899d18ffffff899d1cffffff889d20ffffffc78528ffffff00279e00899d30"
        "ffffff889d34ffffffc7853cfffffff4269e00899d44ffffff889d48ffffff89bd50ffffff889d5cffffffc78564ffff"
        "ffe8269e00889d70ffffffc78578ffffffd8269e00885d84c7458ccc269e00885d98c745a0bc269e00885dac8955b0c7"
        "45b4b0269e00885dc0894dc4c745c8a0269e00885dd48955d8c745dcf4269e00885de8894dec897df08906e820ceffff"
        "33c9385d0c8945f40f95c1895d0c894df8eb0d8da424000000008d9b000000008dbd08ffffffc745fc0c0000008d4900"
        "8b550c3957fc0f85b10000008b45f83b070f85a60000008b4d088b570851528d8504feffff680001000050e8e0933600"
        "8b4d088b570c51528d8504fdffff680001000050e8c793360083c420385f0474538b45f43818744c8d8d04feffff5150"
        "68d01a9e008d9504fcffff680001000052e89a93360083c41468000100008d8504fcffff508d8d04feffff51e82f9036"
        "008b06535668105a40008d9504fdffff5250eb118b16535668105a40008d8d04fdffff5152e8e6c2050083c41483c714"
        "836dfc010f8536ffffff395d0c75188b46088b4e0c5368001240006a045051e8bc5a070083c4148b450c83c00183f801"
        "89450c0f8ef7feffff5f8bc65e5b8be55dc20800"
    )),
    # Base archive opening: VA 0x00404930 through 0x004049E0.
    (0x404930, bytes.fromhex(
        "558bec81ec080100005356578bf8c745fc000000008b4510508b45fcbb040100008db5f8feffffe844e1ffff83c40484"
        "c0745a8b0d40fab2008b750c8b55088d04b15068000c0000528d85f8feffff50e8cbcf010085c0754f8b0d40fab20089"
        "04b1e849ce36003d830000007711742f83f805742a83f826742583f86ceb0c3d6c00108574193d8300108574128b45fc"
        "83c00183f8038945fc0f8c76ffffff5f5e32c05b8be55dc35f5eb0015b8be55dc3"
    )),
)

class PEImage:
    """Read a fixed-base x86 PE and resolve VAs through its section table."""

    def __init__(self, data):
        self.data = data
        if len(data) < 64 or data[:2] != b'MZ':
            raise ValueError('Invalid DOS header.')
        pe = self.u32(0x3c)
        if self.read(pe, 4) != b'PE\0\0':
            raise ValueError('Invalid PE signature.')
        self.coff = pe + 4
        self.count = self.u16(self.coff + 2)
        self.opt = self.coff + 20
        optsize = self.u16(self.coff + 16)
        self.read(self.opt, optsize)
        if self.u16(self.coff) != 0x14c or optsize < 224 or self.u16(self.opt) != 0x10b:
            raise ValueError('Expected an x86 PE32 executable.')
        self.base = self.u32(self.opt + 28)
        self.sa, self.fa = self.u32(self.opt + 32), self.u32(self.opt + 36)
        self.image_size, self.headers = self.u32(self.opt + 56), self.u32(self.opt + 60)
        if self.base != 0x400000 or self.u16(self.opt + 70) & 0x40:
            raise ValueError('Unsupported image base or ASLR configuration.')
        if self.u32(self.opt + 92) < 6 or any(self.read(self.opt + 136, 8)):
            raise ValueError('Relocatable images are not supported by this fixed-address helper.')
        if not (512 <= self.fa <= 65536 and self.sa >= self.fa and self.sa >= 4096):
            raise ValueError('Unsupported section/file alignment.')
        if self.fa & (self.fa-1) or self.sa & (self.sa-1):
            raise ValueError('Invalid PE alignment.')
        if self.headers > len(data) or self.headers % self.fa or self.image_size % self.sa:
            raise ValueError('Invalid PE header or image size.')
        self.table = self.opt + optsize
        if not 1 <= self.count <= 95 or self.table + self.count*40 > self.headers:
            raise ValueError('Invalid section table.')
        self.sections = []
        for i in range(self.count):
            sh = self.table + i*40
            name, vs, rva, size, raw, _, _, _, _, flags = struct.unpack('<8sIIIIIIHHI', self.read(sh, 40))
            span = max(vs, size)
            if rva % self.sa or rva < align(self.headers, self.sa) or rva+span > self.image_size:
                raise ValueError('Invalid virtual section bounds.')
            if size and (raw < self.headers or raw % self.fa or size % self.fa):
                raise ValueError('Invalid raw section bounds.')
            if size:
                self.read(raw, size)
            for other in self.sections:
                if rva < other['rva']+other['span'] and other['rva'] < rva+span:
                    raise ValueError('Overlapping virtual sections.')
                if size and other['size'] and raw < other['raw']+other['size'] and other['raw'] < raw+size:
                    raise ValueError('Overlapping raw sections.')
            self.sections.append(dict(name=name.rstrip(b'\0'), rva=rva, span=span, size=size, raw=raw, flags=flags))
        cert, cert_size = self.u32(self.opt+128), self.u32(self.opt+132)
        if bool(cert) != bool(cert_size):
            raise ValueError('Invalid certificate directory.')
        if cert_size:
            self.read(cert, cert_size)
            if cert % 8 or cert < max(x['raw']+x['size'] for x in self.sections):
                raise ValueError('Invalid certificate location.')

    def read(self, offset, size):
        if offset < 0 or size < 0 or offset+size > len(self.data):
            raise ValueError('Truncated PE data.')
        return self.data[offset:offset+size]

    def u16(self, offset):
        return struct.unpack('<H', self.read(offset, 2))[0]

    def u32(self, offset):
        return struct.unpack('<I', self.read(offset, 4))[0]

    def section(self, va, size, required_flags):
        rva = va-self.base
        for sec in self.sections:
            if sec['rva'] <= rva and rva+size <= sec['rva']+sec['span']:
                if sec['flags'] & required_flags != required_flags:
                    raise ValueError(f'Wrong section permissions at VA 0x{va:X}.')
                return sec
        raise ValueError(f'Unmapped VA 0x{va:X}.')

    def offset(self, va, size, required_flags=0x40000000):
        sec = self.section(va, size, required_flags)
        delta = va-self.base-sec['rva']
        if delta+size > sec['size']:
            raise ValueError(f'VA 0x{va:X} has no file-backed bytes.')
        return sec['raw']+delta


def validate_original(original):
    """Check every build-specific assumption before generating any changes."""
    image = PEImage(original)
    if any(sec['name'] == b'.mpqfix' for sec in image.sections):
        raise ValueError('Already patched image; its original backup is required.')
    for va, expected in CODE_SIGNATURES:
        off = image.offset(va, len(expected), 0x60000000)
        actual = image.read(off, len(expected))
        if actual != expected:
            delta = next(i for i, pair in enumerate(zip(actual, expected)) if pair[0] != pair[1])
            raise ValueError(f'Unexpected instruction at VA 0x{va+delta:X} (file offset 0x{off+delta:X}).')
    # The helper dereferences this native dynamic-array object at runtime.
    image.section(0xB2FA38, 16, 0xC0000000)
    # The 2*N+64 bound requires exactly 28 descriptors and one type-3 entry.
    table = image.offset(0xAB6168, 28*16, 0xC0000000)
    types = []
    for i in range(28):
        pointer, kind = struct.unpack_from('<II', original, table+i*16)
        types.append(kind)
        image.offset(pointer, 1)
    if types != [3,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,1,2,1,1,2,2,2,2,2,4,4]:
        raise ValueError('Unexpected base-archive descriptors; reservation bound is not valid.')
    pointer = struct.unpack_from('<I', original, table)[0]
    if image.read(image.offset(pointer, 14), 14) != b'alternate.MPQ\0':
        raise ValueError('Unexpected type-3 archive descriptor.')
    sh = image.table + image.count*40
    if sh+40 > image.headers or any(image.read(sh, 40)):
        raise ValueError('No unused header space for the patch section.')
    return image


def build_patch(original):
    image = validate_original(original)
    b = bytearray(original)
    coff, opt, count = image.coff, image.opt, image.count
    base, sa, fa, image_size = image.base, image.sa, image.fa, image.image_size
    sh = image.table + count*40
    hook_offset = image.offset(HOOK_VA, len(OLD), 0x60000000)
    rva = align(image_size, sa)
    va = base + rva
    # Preserve flags and ALL registers; EBP is the loader frame.
    # N = [EBP-0x24], number of discovered patch paths.
    # One type-3 base archive (alternate.MPQ), at most one child per patch.
    # 2*N+64 covers N patches + N children + base/optional slots + failed writes.
    code = bytearray.fromhex('9c 60 8b45dc 8d440040 3b0538fab200 760b 50 b938fab200')
    call_at = va + len(code)
    code += b'\xe8' + struct.pack('<i', 0x4037F0 - (call_at + 5))
    code += bytes.fromhex('61 9d bb40000000 c3')
    raw = align(len(b), fa)
    rawsize = align(len(code), fa)
    b.extend(bytes(raw + rawsize - len(b)))
    b[raw:raw+len(code)] = code
    # Add aligned code storage and a readable/executable PE section header.
    struct.pack_into('<8sIIIIIIHHI', b, sh, b'.mpqfix\0', len(code), rva,
                     rawsize, raw, 0, 0, 0, 0, 0x60000020)
    struct.pack_into('<H', b, coff + 2, count + 1)
    sizecode = struct.unpack_from('<I', b, opt+4)[0]
    struct.pack_into('<I', b, opt+4, sizecode + rawsize)
    struct.pack_into('<I', b, opt+56, align(rva+len(code), sa))
    # Redirect exactly one complete instruction; the helper replays it.
    b[hook_offset:hook_offset+5] = b'\xe8' + struct.pack('<i', va-(HOOK_VA+5))
    # Any binary patch invalidates Authenticode. Clear its directory entry;
    # preserve certificate bytes as inert overlay data for exact backup recovery.
    struct.pack_into('<II', b, opt+128, 0, 0)
    # Recalculate the PE checksum after all header and code modifications.
    checksum_offset = opt + 64
    struct.pack_into('<I', b, checksum_offset, 0)
    checksum = 0
    for i in range(0, len(b), 2):
        word = b[i] | ((b[i+1] if i+1 < len(b) else 0) << 8)
        checksum += word
        checksum = (checksum & 0xffff) + (checksum >> 16)
    checksum = (checksum & 0xffff) + (checksum >> 16)
    struct.pack_into('<I', b, checksum_offset, checksum + len(b))
    return bytes(b)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    actions = ap.add_mutually_exclusive_group()
    actions.add_argument('--check', action='store_true', help='Validate compatibility without modifying the executable.')
    actions.add_argument('--restore', action='store_true', help='Restore the executable from its verified original backup.')
    ap.add_argument('exe', nargs='?', default=str(Path(__file__).with_name('wow.exe')), help='Path to the executable, with any filename (default: wow.exe next to this script).' )
    args = ap.parse_args()
    target = Path(args.exe).absolute()
    if target.is_symlink() or target.is_junction():
        ap.error('Symbolic links and junctions are not allowed.')
    if target.stat().st_nlink != 1:
        ap.error('Hard links are not allowed.')
    # Filename does not determine compatibility; validate code and addresses below.
    current = target.read_bytes()
    backup = target.with_name(target.name + '.before-mpq-fix.bak')
    image = PEImage(current)
    if any(sec['name'] == b'.mpqfix' for sec in image.sections):
        original = backup.read_bytes()
    else:
        original = current
    patched = build_patch(original)
    if current not in (original, patched):
        ap.error('The file was modified by another tool; operation refused.')
    state = 'original' if current == original else 'patched'
    print('Status:', state)
    if args.check:
        print('Instructions, addresses, and PE structure verified.')
        return
    result = original if args.restore else patched
    if result == current:
        print('No changes needed.')
        return
    # Create the backup exclusively and never replace an existing backup.
    if not args.restore:
        if backup.exists():
            if backup.read_bytes() != original:
                ap.error('The existing backup does not match; operation aborted.')
        else:
            with backup.open('xb') as f:
                f.write(original)
                f.flush()
                os.fsync(f.fileno())
    # Atomic replacement avoids a partially written executable.
    temp = target.with_name(target.name + '.mpqfix.tmp')
    created_temp = False
    try:
        with temp.open('xb') as f:
            created_temp = True
            f.write(result)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, target)
    finally:
        if created_temp and temp.exists():
            temp.unlink()
    assert target.read_bytes() == result
    print('Restoration completed.' if args.restore else 'Patch applied; backup: ' + str(backup))

if __name__ == '__main__':
    try:
        main()
    except OSError as exc:
        # Do not echo OS error descriptions, which may use the system language.
        details = f'errno={exc.errno}'
        if getattr(exc, 'winerror', None) is not None:
            details += f', winerror={exc.winerror}'
        paths = ' -> '.join(str(path) for path in (exc.filename, exc.filename2) if path)
        raise SystemExit(f'File operation failed ({details})' + (f': {paths}' if paths else '.'))
    except ValueError as exc:
        raise SystemExit(str(exc))
