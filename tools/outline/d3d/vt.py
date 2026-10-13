import struct,sys
d=open('/root/.claude/uploads/49e16a66-3a63-5e77-ae4f-92ef019273b7/4b28656a-Wow.exe','rb').read()
def va2off(va):
    if 0x401000<=va<0x9DF000: return va-0x400C00
    if 0x9DF000<=va<0xAB6000: return va-0x9DF000+0x5DD800
    if 0xAB6000<=va<0xAB6000+0x78E00: return va-0xAB6000+0x6B4000
va=int(sys.argv[1],16); n=int(sys.argv[2])
for i in range(n):
    v=struct.unpack_from('<I',d,va2off(va+4*i))[0]
    print('%3d +0x%03X %08X'%(i,4*i,v))
