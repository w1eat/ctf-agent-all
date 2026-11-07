---
title: "[第六届信安大挑战]shellcode"
source_challenge: "[第六届信安大挑战]shellcode"
confirmation_source: platform_confirmed
verification_status: verified
run_id: "0cd56e959b7841faa43f9a9202044946"
---

# [第六届信安大挑战]shellcode

## 可复用方法

Flag found via 8 字节 shellcode -> 栈指针接管 (mov rsp,rsi) + rt_sigreturn SROP -> read(0, 0x400000, 0x1000) 重写固定 RWX 映射 -> execve("/bin/sh") -> cat /[redacted] | Evidence: 二进制静态分析：main 调用 mmap(0x400000, 0x8000, PROT_READ|WRITE|EXEC, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0)，得到固定地址 0x400000 的 RWX 页（非 PIE 偏移，绝对地址可控） ; 二进制静态分析：read(0, mmap_addr, 0x1000) 后若返回值 > 8 则 puts("Shell too long!") 并 exit —— 第一段 shellcode 只能 8 字节；随后 read(0, rbp-0x810, 0x100) 读入 "name"，再 push 0; jmp 0x400000 ; 进入 shellcode 时寄存器状态：rax = name 读取字节数、rdi = 0、rsi = 栈上 name 缓冲区地址（rbp-0x810）、rdx = 0x100，因此可用 8 字节指令 48 89 f4 6a 0f 58 0f 05（mov rsp,rsi; push 0xf; pop rax; syscall）把 rsp 指向完全可控的 name 缓冲区并触发 rt_sigreturn（rax 取实际 name 长度 0xf8，故显式 push 0xf 保证 rax=15） ; SROP 帧（248 字节，塞进 0x100 的 name 缓冲）设置 rax=0(READ)、rdi=0、rsi=0x400000、rdx=0x1000、rip=0x400006（stage1 中的 syscall）、rsp=0x407f00（RWX 映射内），使 read 直接把第二段 shellcode 写回 0x400000；syscall 返回后从 0x400008 继续执行 ; 第二段 shellcode（偏移 8，前 8 字节填充）为 execve("/bin/sh",0,0)；本地 ./pwn 实测回显 PWNED，证明控制流成立（GNU_STACK RW/NX，故不能直接 jmp rsi，必须 SROP） | Independently verified by deepseek/deepseek-flash, deepseek/deepseek-flash#verifier

## 验证步骤

1. 1. 用 IDA/objdump 分析 ./pwn：main 先 mmap(0x400000,0x8000,7,0x32,-1,0)，得到固定可读写可执行页；read(0,0x400000,0x1000) 若返回 >8 就退出（只允许 8 字节 shellcode）；再 read(0, rbp-0x810, 0x100) 读 name，最后 push 0; jmp 0x400000。
2. 2. checksec/readelf 确认 NX enabled（GNU_STACK RW），所以常见的 `jmp rsi`（2 字节跳栈上 name 缓冲）不可行；但 0x400000 映射是固定的非 PIE 绝对地址，可用作第二段代码/数据区。
3. 3. 关键观察：跳到 shellcode 那一刻 rsi 恰好指向栈上完全可控的 0x100 字节 name 缓冲区，且 rax = name 读取长度、rdi = 0、rdx = 0x100。用 3 字节 `mov rsp, rsi` 把栈指针搬到可控缓冲区，再用 `push 0xf; pop rax; syscall` 触发 15 号系统调用 rt_sigreturn。合计正好 8 字节：4889f46a0f580f05。
4. 4. 构造 pwntools SigreturnFrame（248 字节 < 0x100）：rax=0(READ)、rdi=0、rsi=0x400000、rdx=0x1000、rip=0x400006（stage1 里的 syscall 指令）、rsp=0x407f00（RWX 映射内）。发送顺序严格为：先发 8 字节 stage1，recvuntil 第二个提示以确认第一次 read 已返回且未被 >8 检查杀掉，再发 248 字节 SROP 帧。
5. 5. sigreturn 恢复上下文后执行 read(0,0x400000,0x1000)，把第二段 shellcode 写到 0x400000；syscall 返回后 rip 自然落在 0x400008，也就是新写入数据的第 9 个字节处。因此发送 b'A'*8 + execve('/bin/sh',0,0) shellcode。
6. 6. 本地 `python3 exp_final.py local` 验证 shell 起来（回显 PWNED）。
7. 7. 远端 `python3 exp_final.py remote`（nc noctf.fa1lsnow.com 40070）：ls -la 显示 43 字节的 flag 文件，`cat /flag` 输出 [redacted]；重复三次结果一致（exp2.py 与 exp_final.py 均复现）。
