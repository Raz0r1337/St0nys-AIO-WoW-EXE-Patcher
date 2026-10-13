import os,pty,sys,time,re,select,fcntl,termios,struct
pw=sys.argv[1]; steps=sys.argv[2:]
pid,fd=pty.fork()
if pid==0:
    os.environ['TERM']='xterm-256color'
    os.execv(pw,[pw,'-NoProfile','-File','./apply_patches.ps1'])
fcntl.ioctl(fd,termios.TIOCSWINSZ,struct.pack('HHHH',50,160,0,0))
allout=b''; buf=b''
def pump(timeout):
    global buf,allout
    r,_,_=select.select([fd],[],[],timeout)
    if not r: return True
    try: data=os.read(fd,65536)
    except OSError: return False
    if not data: return False
    if b'\x1b[6n' in data: os.write(fd,b'\x1b[20;1R')
    buf+=data; allout+=data; return True
def clean(b): return re.sub(rb'\x1b\[[0-9;?]*[a-zA-Z]',b'',b).decode('utf-8','replace').replace('\r','')
log=[]
for st in steps:
    pat,send=st.split('=>',1); ok=False; end=time.time()+60
    while time.time()<end:
        if not pump(0.5): break
        if re.search(pat,clean(buf),re.M): ok=True; break
    log.append((pat,ok)); buf=b''
    if not ok: break
    time.sleep(0.5); os.write(fd,send.encode()+b'\r')
end=time.time()+15
while time.time()<end and pump(0.5): pass
print(log)
lines=[l for l in clean(allout).split('\n') if l.strip()]
print('\n'.join(lines[:4])); print('...'); print('\n'.join(lines[-6:]))
print('exit',os.waitpid(pid,os.WNOHANG))
