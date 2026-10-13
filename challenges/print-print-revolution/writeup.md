# Print Print Revolution 题解

- 分类：Pwn
- 确认方式：平台确认
- 复现状态：人工复现


## 题目信息

The arcade's score printer has been spitting out strange tickets all week. Step up to the renderer and see what it's really printing.

## 解题原理

题目是一个非 PIE、partial RELRO 的 ELF64 程序（revolution），其关键在于二进制内自实现的 printf（0x401330）存在格式串参数解析缺陷。该自定义 printf 对位置参数 N>=6 的处理并非从寄存器/栈取参数，而是直接从攻击者可控的格式缓冲区读取，即第 N 个参数 = format_buf + 8*(N-6) 处的 8 字节。因此攻击者可以通过 %N$s / %N$w 精确控制指针与被写入的值，形成任意地址读（%s 会先 strlen 再 write）和任意地址写 8 字节（%w 对应 `mov [r8],rax`）。由于 .got.plt 在 0x404000+ 且可写，可先泄漏 write@GOT 得到 libc 基址，再把 strlen@GOT 覆写为 system，最后让 %s 的参数指向 libc 中的 "/bin/sh" 字符串，触发 strlen("/bin/sh") 实际调用 system("/bin/sh") 获得 shell。

## 关键步骤

1. 用 file/readelf 确认 revolution 是非 PIE 的 ELF64、partial RELRO，因此 0x404000 起的 .got.plt 可写。
2. 用 objdump/IDA 分析 0x401330 处的自定义 printf：%s 分支先调用 strlen 再 write；%x/%p 打印寄存器/栈参数；%w 分支执行 `mov [r8],rax`，等价于向指定地址写入 8 字节。
3. 实测参数映射：%6$p 输出等于格式缓冲区偏移 0 处的 8 字节，%8$p 输出等于偏移 16 处的 8 字节，即第 N(N>=6) 个参数 = 格式串 buf+8*(N-6)，完全由输入控制。
4. 构造 payload=b'%8$s'+填充到偏移 16+p64(0x404000)，从远端泄漏 write@GOT=0x788ac296a560，得到 libc 基址 base=0x788ac284e000。
5. 用 libc 函数低 12 位指纹（write 0x560 / read 0xa50 / setvbuf 0x540）经 libc.rip 匹配到 libc6_2.39-0ubuntu8，得到 system=0x58740、"/bin/sh"=0x1cb42f。
6. 构造 payload=b'%8$w'+填充+偏移 16 放 p64(0x404008)+偏移 24 放 p64(base+0x58740)，把 strlen@GOT 改写为 system，返回 'ok' 以确认任意写生效。
7. 构造 payload=b'%8$s'+填充+偏移 16 放 p64(base+0x1cb42f)，使 %s 分支内的 strlen(ptr) 被替换为 system(ptr)，从而执行 system("/bin/sh") 并拿到 shell。
8. 在 shell 中执行 cat flag.txt 得到 sun{cust0m_fmtstr_n0_t00ls_4ll0wed}，提交平台返回 CORRECT。

## EXP 与运行方法

文件：`exp/exp.py`

已保存的 EXP 位于 exp/exp.py，采用 pwntools 编写，脚本内含三类构造：build_leak(N, addr) 生成 '%N$s'+填充+p64(addr) 用于任意地址读，build_write(N, addr, val) 生成 '%N$w'+填充+p64(addr)+p64(val) 用于任意地址写 8 字节，run() 依次完成泄漏 write@GOT、把 strlen@GOT 覆写为 system、再以 %s 指向 "/bin/sh" 触发 shell 并读取 flag。脚本通过命令行参数区分目标：mode=local 时 process(['/challenge/distfiles/revolution'])，使用本地偏移 0x1149c0(write)/0x50d70(system)/0x1d8678(binsh)；否则 remote("chal.sunshinectf.games",26002)，使用远端偏移 0x11c560/0x58740/0x1cb42f。当前 replay.status 为 manual，说明需要人工按上述方式运行脚本或手动复现交互，不能声称 EXP 已被自动复现。

## 验证结果

提供的 EXP 运行命令不符合安全的单脚本格式，需人工复现。

证据：

- checksec: ELF64 EXEC (non-PIE), partial RELRO -> .got.plt (0x404000+) writable
- IDA/objdump of 0x401330: custom printf; '%w' handler does `mov [r8],rax` (arbitrary 8-byte write), '%s' handler calls strlen then write
- Empirical arg mapping: %6$p printed buffer[0:8], %8$p printed buffer[16:24] -> arg(N>=6)=qword at format_buf+8*(N-6)
- Remote leak of write@GOT=0x788ac296a560 -> base=0x788ac284e000; low-12 fingerprint (write 0x560/read 0xa50/setvbuf 0x540) matched libc6_2.39-0ubuntu8 via libc.rip (system=0x58740, str_bin_sh=0x1cb42f)
- Payload '%8$w'+pad+p64(0x404008)+p64(base+system) -> returned 'ok' (write primitive confirmed), then '%8$s' -> p64(base+0x1cb42f) spawned shell
- Shell output: uid=1337(revolution); cat flag.txt -> sun{cust0m_fmtstr_n0_t00ls_4ll0wed}
- submit_flag returned CORRECT

## Flag

`sun{cust0m_fmtstr_n0_t00ls_4ll0wed}`

## 限制与备注

1) 复现依赖程序为非 PIE + partial RELRO（.got.plt 可写）以及自定义 printf 对 N>=6 位置参数直接从格式缓冲区取值的特定实现，若目标二进制或偏移变化则不可用。 2) libc 推导依赖 write@GOT 的远程泄漏，并用 write/read/setvbuf 低 12 位指纹匹配到 libc6_2.39-0ubuntu8；这依赖目标运行环境与所匹配 libc 一致，偏移不匹配时 system、"/bin/sh" 地址会失效。 3) EXP 中本地与远端使用不同偏移，说明本地文件与远端环境并非完全相同，本地成功不能直接类推远端。 4) 当前 replay.status 为 manual，原因是提供的 EXP 运行命令不符合安全的单脚本格式，因此只能人工复现；本材料未提供自动复现输出，无法据此确认自动化复现结果。 5) Flag 与提交结果来自题目材料中平台确认的记录（confirmation_source 为 platform_confirmed，submit_flag 返回 CORRECT）；除此之外的细节（如远程 shell 的完整交互日志）在现有证据中不完整，依据现有证据无法进一步确认。
