import re,sys
def rng(s):
    out=[]
    for part in s.split(','):
        part=part.strip()
        if '-' in part:
            a,b=part.split('-'); out+=range(int(a),int(b)+1)
        else: out.append(int(part))
    return out
C2=set(rng("10,11,23,24,41,42,45-50,74,81-85,25"))
C3=set(rng("4,7,8,9,26,29,44,51,62,63,64,68,70,71,72,73,79"))
C4=set(rng("25,4,7,8,9,26,29,44,51,62,63,64,68,70"))
C1=set(rng("1,2,3,5,6,12-22,27,28,30-40,43,52-61,65-67,69,75-78,80"))
allc=C1|C2|C3|C4
assert allc==set(range(1,86)), sorted(set(range(1,86))-allc)
assert not (C1&(C2|C3|C4))
