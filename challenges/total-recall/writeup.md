# Total Recall 题解

- 分类：Pwn
- 确认方式：平台确认
- 复现状态：人工复现


## 题目信息

Can you recall how to get out of this one? Binary: https://sunshinectf.games/files/54cf6a/total_recall

## 解题原理

目标是一个静态链接、仅使用原始 syscall 的极小 x86-64 二进制。程序先用 write(1, rsp, 8) 泄露 8 字节栈指针，然后 read(0, rsp-0x40, 0x18)，再执行 read(0, rsp-0x80, 0x400)，向 128 字节栈缓冲区写入最多 0x400 字节，构成栈溢出。栈为 rw-p（NX），因此 ret2shellcode 不可行。解题思路是 SROP（sigreturn-oriented programming）：利用栈泄露定位栈地址，覆盖保存的返回地址重新进入读取例程；read 的返回值会落在 rax，第二次 read 只发送恰好 15 字节使 rax=15（rt_sigreturn 系统调用号），再返回到 0x401069 处的 syscall;ret，由内核执行 rt_sigreturn，恢复事先布置好的 SigreturnFrame（rax=59 即 execve、rdi 指向栈上的 /bin/sh、rsi=0、rdx=0、rip 指向 syscall gadget），从而获得 shell。

## 关键步骤

1. 从 https://sunshinectf.games/files/54cf6a/total_recall 获取二进制；该文件为静态、已 stripped、仅用 syscall 实现功能。
2. 反汇编确认：0x401016 处通过 write(1, rsp, 8) 泄露栈地址；0x40104f 处的函数执行 read(0, rsp-0x80, 0x400)，是 128 字节缓冲区上的栈溢出；/proc/pid/maps 显示栈为 rw-p，即 NX。
3. 可用 gadget：0x401069 处 syscall;ret、0x40104e 处 ret、0x40104f 处读取函数入口。
4. 利用栈泄露得到栈地址，覆盖 f2 的返回地址为 0x40104f 以再次进入读取函数，并在其后放置伪造的 SigreturnFrame（rax=59 execve、rdi 为栈上 /bin/sh 的指针、rsi=0、rdx=0、rip=0x401069 的 syscall;ret）。
5. 第二次 read 恰好发送 15 字节，使 read() 返回 15，从而 rax=15（rt_sigreturn）；返回到 0x401069 触发 rt_sigreturn，内核恢复该帧并执行 execve(/bin/sh)。
6. 本地（setarch -R）与远程均获得 shell；远程 shell 的 uid 为 1337(total_recall)，执行 cat /flag* 得到 sun{r3caLl_ev3Ry_reGist3r_sR0p}；材料记录平台提交返回 CORRECT（页面提示 Correct）。

## EXP 与运行方法

文件：`exp/exp2.py`, `exp/exp.py`

材料附带两个 pwntools 脚本。exp/exp2.py 是有效的 SROP 版本：定义 RET=0x40104e、SYSCALL_RET=0x401069、F2=0x40104f；先 recvn(8) 取栈泄露，计算缓冲区基址 B=S-0x80 与 /bin/sh 地址 B+0x20；构造 buf 在 0x80 偏移写 F2、在 0x88 偏移写 SYSCALL_RET、随后写入 SigreturnFrame，并把 /bin/sh\x00 放在偏移 0x20；交互上先 send 0x18 字节，再发大 payload，再发恰好 15 字节（b'BBBBBBBBBBBBBBB'）使 rax=15，最后 sendline 执行 echo PWNED_MARKER_$((6*7)); id; ls -la /; cat /flag* flag*。脚本通过 args.REMOTE 选择 remote('chal.sunshinectf.games', 26003) 或本地 process(BIN)。exp/exp.py 则是用 shellcraft.sh() 生成 shellcode 覆盖返回地址的 ret2shellcode 尝试，因栈 NX 预期不可行，仅作对照。replay.status 为 manual（原因：提供的 EXP 运行命令不符合安全的单脚本格式，需人工复现），replay.command 为空、无 exit_code/stdout/stderr，因此本材料不能声称 EXP 已自动复现；只能由人工按上述脚本内容自行运行，本地复现可参考证据中的 setarch -R 用法。

## 验证结果

提供的 EXP 运行命令不符合安全的单脚本格式，需人工复现。

证据：

- Disassembly: 0x401016 leaks stack via write(1,rsp,8); 0x40104f does read(0,rsp-0x80,0x400) = stack overflow; /proc/pid/maps shows stack is rw-p (NX).
- Gadgets: syscall;ret at 0x401069, ret at 0x40104e, read-func entry at 0x40104f.
- Two-stage SROP: first big read stages SigreturnFrame at leaked stack address; second read of exactly 15 bytes makes read() return 15 so rax=15 = rt_sigreturn.
- Local reproduction with setarch -R produced a root shell (PWNED_MARKER_42).
- Remote run gave uid=1337(total_recall) shell and printed flag: sun{r3caLl_ev3Ry_reGist3r_sR0p}.
- Platform submission returned CORRECT (page alert Correct).

## Flag

`sun{r3caLl_ev3Ry_reGist3r_sR0p}`

## 限制与备注

材料未给出可用的自动运行命令（replay.command 为空、exit_code 为 null），replay.status 为 manual，因此只能人工复现，无法据此声称脚本已自动验证通过。exp2.py 依赖 pwntools 与 amd64 上下文，并依赖正确的 8 字节栈泄露；脚本使用固定 time.sleep 分隔多次 send，交互时序较脆弱，网络或加载延迟可能导致失败。SigreturnFrame 的布置与 /bin/sh 字符串偏移（0x20）必须与 payload 布局一致，否则 rt_sigreturn 恢复出错。本地复现依赖 setarch -R 关闭 ASLR 以便稳定命中地址。exp.py 采用 ret2shellcode，与证据显示的 NX 栈相矛盾，不能作为有效利用路径。flag sun{r3caLl_ev3Ry_reGist3r_sR0p} 与远程 shell 行为已由材料记录，且确认来源为平台确认（Platform submission returned CORRECT），不属于未验证的候选值。
