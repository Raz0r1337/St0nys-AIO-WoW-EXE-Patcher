import sys, struct
sys.path.insert(0,'ml'); from h import *
START=0x73E382; END=0x73E3D6
def rel8(src_next, tgt):
    r=tgt-src_next; assert -128<=r<=127, (hex(src_next),hex(tgt)); return r & 0xff
def build():
    # two-pass assembler with labels
    prog=[
     ('raw',[0xF6,0xC1,0x10]),            # test cl,0x10      (LEFT)
     ('jcc',0x75,'L_left'),
     ('raw',[0x8B,0x96,0x38,0x0A,0x00,0x00]), # mov edx,[esi+0xa38]
     ('raw',[0xF6,0xC6,0x08]),            # test dh,0x08      (0x800)
     ('jcc',0x75,'L_left'),
     ('raw',[0xF6,0xC1,0x20]),            # test cl,0x20      (RIGHT)
     ('jcc',0x75,'L_right'),
     ('raw',[0xF6,0xC6,0x10]),            # test dh,0x10      (0x1000)
     ('jcc',0x75,'L_right'),
     ('raw',[0x83,0xF8,0x0B]),            # cmp eax,0xb
     ('jcc',0x74,'L_stand'),
     ('raw',[0x83,0xF8,0x0C]),            # cmp eax,0xc
     ('jcc',0x75,'done'),
     ('lbl','L_stand'), ('raw',[0x33,0xC9]),          # xor ecx,ecx
     ('jcc',0xEB,'L_cmp'),
     ('lbl','L_right'), ('raw',[0x6A,0x0C,0x59]),     # push 0xc; pop ecx
     ('jcc',0xEB,'L_cmp'),
     ('lbl','L_left'),  ('raw',[0x6A,0x0B,0x59]),     # push 0xb; pop ecx
     ('lbl','L_cmp'),   ('raw',[0x3B,0xC1]),          # cmp eax,ecx
     ('jcc',0x74,'done'),
     ('raw',[0x8B,0xCE]),                 # mov ecx,esi
     ('call',0x71DE90),                   # CanShuffle
     ('raw',[0x85,0xC0]),                 # test eax,eax
     ('jcc',0x74,'done'),
     ('raw',[0x8B,0x46,0x08]),            # mov eax,[esi+8]   (descriptors)
     ('raw',[0xF6,0x40,0x08,0x10]),       # test byte [eax+8],0x10  (TYPEMASK_PLAYER)
     ('jcc',0x74,'done'),                 # NPC -> skip (Robinsch-Fix)
     ('raw',[0x6A,0xFF,0x6A,0x00,0x8B,0xCE]), # push -1; push 0; mov ecx,esi
     ('call',0x73AC30),                   # Animation neu bestimmen
    ]
    labels={'done':END}
    for _ in range(2):
        out=[]; pc=START
        for it in prog:
            if it[0]=='lbl': labels[it[1]]=pc; continue
            if it[0]=='raw': out+=it[1]; pc+=len(it[1])
            elif it[0]=='jcc':
                tgt=labels.get(it[2],pc+2); out+=[it[1],rel8(pc+2,tgt) if it[2] in labels else 0]; pc+=2
            elif it[0]=='call':
                r=(it[1]-(pc+5))&0xffffffff; out+=[0xE8]+list(struct.pack('<I',r)); pc+=5
    assert pc<=END, hex(pc)
    out+=[0x90]*(END-pc)
    return out
if __name__=='__main__':
    b=build(); print(len(b), ', '.join('0x%02X'%x for x in b))
    data=bytearray(d); data[v2f(START):v2f(START)+len(b)]=bytes(b)
    dis(0x73E379,0x60,data=bytes(data))
