# Mad Libs 题解

- 分类：Pwn
- 确认方式：平台确认
- 复现状态：人工复现


## 题目信息

Fill in the blanks! Our Mad Libs game prints back whatever you type. Binary: https://sunshinectf.games/files/fbf35f/mad_libs

## 解题原理

题目 mad-libs 是一个 PIE、Partial RELRO、NX、Canary 的 64 位程序，main(0x11c9) 循环 8 次执行 fgets(buf,0x100) 后直接 printf(buf)，用户输入被当作格式化字符串，构成格式化字符串漏洞。由于 Partial RELRO，GOT 可写，因此可以先用 %N$p 位置化参数泄漏栈上残留的 libc 返回地址（arg43 = libc_base+0x2a1ca）与代码指针（arg47 = PIE_base+0x11c9），算出 libc 基址与 PIE 基址；再构造写入型格式化串，用 %hhn 按字节把 printf@GOT（PIE_base+0x4010）改写成 system() 地址（libc_base+0x58740，共 6 字节 / 48 位）。改写后循环中的 printf("(%d) > ") 与 printf(buf) 均解析到 system，发送 /bin/sh 即可获得 shell 并读取 flag。

## 关键步骤

1. 反汇编 mad-libs 的 main(0x11c9)：确认循环 8 次 fgets(buf,0x100) 后 printf(buf)，存在格式化字符串漏洞；二进制为 PIE + Partial RELRO + NX + Canary，GOT 可写，附件提供 libc（GLIBC 2.39）与 ld。
2. 用 patchelf 把解释器指向附件 ld、libc.so.6 指向 libcM-so.6 以复现远程布局；用 %N$p 做位置化探测，确认 arg43=libc_base+0x2a1ca、arg47=PIE_base+0x11c9，两者在环境/栈布局变化下保持稳定（AT_PHDR 位置不稳定，不用）。
3. 第一轮发送 "%43$p|%47$p" 泄漏两个地址，计算 libc_base 与 PIE_base，进而得到 system=libc_base+0x58740、printf@GOT=PIE_base+0x4010。
4. 第二轮构造格式化字符串：把 printf@GOT 的 6 个字节用 %hhn 按字节值升序依次写入；地址放在格式说明符之后（避免地址中的 NUL 字节截断格式串），对齐到 8 字节边界，参数下标 = 8 + 偏移/8（材料中偏移 80，故 base_arg=18）。
5. 第三轮：GOT 中 printf 已被改写为 system，循环开头的 printf("(%d) > ") 变成 system("(%d) > ")，随后的 printf(buf) 变成 system(buf)；发送 /bin/sh 获得 shell。
6. 在 shell 中执行 cat /ctf/flag.txt（也可在 ./flag.txt 读取），得到 flag：sun{f1ll_iN_th3_g0T_eNtry}。

## EXP 与运行方法

文件：`exp/exp.py`, `exp/exploit.py`, `exp/exploit_remote.py`, `exp/leak3.py`

材料提供 4 个 EXP 脚本。exp/exp.py、exp/exploit_remote.py 是完整的远程利用脚本：remote('chal.sunshinectf.games',26001)，先发送 "%43$p|%47$p" 泄漏并计算 libc/pie/system/printf@GOT，再调用 build_write 生成 6×%hhn 写入串覆盖 printf@GOT 为 system，随后发送 /bin/sh 并执行 cat 命令读取 flag。exp/exploit.py 在该逻辑上增加本地/远程分支（本地进程名为 ./mad_patched，需先 patchelf 修补），并含 p.interactive()。exp/leak3.py 仅用于本地偏移探测：以提供的 ldM 与 --library-path 启动 mad-libs，读取 /proc/<pid>/maps 给各 %N$p 泄漏值打标签，用于确定 arg43/arg47。replay.status 为 manual，即 EXP 未由平台自动复现，材料中记录的运行需要人工在具备 pwntools 与对应 libc/ld 的环境下执行；命令字段为空，说明没有可直接复制的单脚本复现命令。

## 验证结果

提供的 EXP 运行命令不符合安全的单脚本格式，需人工复现。

证据：

- mad-libs is a PIE, Partial RELRO, NX, Canary binary; main (0x11c9) loops 8 times doing fgets(buf,0x100) then printf(buf), a classic format-string bug (objdump disasm shows `call 10b0` = printf with user buffer as format).
- Positional leak probing identified: arg43 = libc_base+0x2a1ca (return addr into libc) and arg47 = PIE_base+0x11c9 (code pointer), both stable across env/stack layouts (verified locally with patchelf'd binary using the supplied ldM/libcM and against the remote service).
- Provided libcM-so.6 is GLIBC 2.39; system offset 0x58740, printf@GOT = PIE_base+0x4010 (readelf -r: printf reloc at 0x4010; PLT .plt.sec 0x10b0 -> jmp [rip+0x2f56] = 0x4010).
- Built a 6x %hhn format string writing the 48-bit system() address over printf@GOT (addresses stored after the specifiers so NUL bytes don't truncate the format). After the write, the next printf('(%d) > ') resolves to system() and the following printf(user_input) becomes system(user_input).
- Sent /bin/sh at the appropriate iteration, obtained a root shell, and `cat /ctf/flag.txt` returned: sun{f1ll_iN_th3_g0T_eNtry} (also present at ./flag.txt in /ctf).
- Platform confirmed the submission as CORRECT.

## Flag

`sun{f1ll_iN_th3_g0T_eNtry}`

## 限制与备注

1) 复现依赖附件提供的 libc（GLIBC 2.39）与 ld，以及本地的 patchelf 修补（./mad_patched）；若远程 libc/ld 与附件不一致，system 偏移 0x58740 与 arg43/arg47 的偏移都会失效。2) 泄漏的 arg43/arg47 是材料中经本地与远程验证的稳定位置，但材料同时指出 AT_PHDR 位置随环境变化不可靠，说明位置化参数可能受环境/栈布局影响，需在目标环境重新确认。3) 写入串长度受单行 0x100 缓冲与换行限制（脚本断言 len(buf)<255 且不含 \n），字节值顺序与地址布局必须满足这些约束。4) replay.status 为 manual，EXP 未自动复现，无法据材料声称脚本在目标上必然成功；confirmation_source 为 platform_confirmed，材料记录平台已确认提交正确，但原理与偏移仍以给定附件环境为前提。5) 材料未给出远程服务的完整交互日志，无法逐行核对每一步的输出。
