import os,pty,sys,time,re,select
pw=sys.argv[1]; steps=sys.argv[2:]
pid,fd=pty.fork()
if pid==0:
    os.environ['TERM']='xterm-256color'
    os.execv(pw,[pw,'-NoProfile','-File','./apply_patches.ps1'])
import fcntl,termios,struct
fcntl.ioctl(fd,termios.TIOCSWINSZ,struct.pack('HHHH',50,160,0,0))
buf=b''
def readuntil(pat,timeout=60):
    global buf
    end=time.time()+timeout
    while time.time()<end:
        r,_,_=select.select([fd],[],[],0.5)
        if r:
            try: data=os.read(fd,65536)
            except OSError: return False
            if not data: return False
            buf+=data
            if re.search(pat,re.sub(rb'\x1b\[[0-9;?]*[a-zA-Z]',b'',buf)): return True
    return False
log=[]
for st in steps:
    pat,send=st.split('=>',1)
    ok=readuntil(pat.encode())
    log.append((pat,ok))
    buf=b''
    if not ok: break
    time.sleep(0.3); os.write(fd,send.encode()+b'\r')
readuntil(b'@@never@@',timeout=8)
clean=re.sub(rb'\x1b\[[0-9;?]*[a-zA-Z]',b'',buf).decode('utf-8','replace').replace('\r','')
print(log); print('\n'.join([l for l in clean.split('\n') if l.strip()][-8:]))
try: print('exit',os.waitpid(pid,os.WNOHANG))
except Exception as e: print(e)
