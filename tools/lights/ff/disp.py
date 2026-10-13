import re,sys
lo,hi=int(sys.argv[1],16),int(sys.argv[2],16)
for line in open('../../outline/d3d/text.asm'):
    for m in re.finditer(r'\[([^\]]*)\]|(?:, |\s)(0x[0-9a-f]+)\b',line):
        if m.group(1):
            for t in re.findall(r'0x[0-9a-f]+',m.group(1)):
                if lo<=int(t,16)<hi: print(line.rstrip()); break
        elif m.group(2) and lo<=int(m.group(2),16)<hi and not line.split()[1].startswith(('call','j','push')):
            print(line.rstrip()+'   (imm)')
