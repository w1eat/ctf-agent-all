# Safe House 题解

- 分类：Pwn
- 确认方式：平台确认
- 复现状态：自动复现通过


## 题目信息

The safe house processes reports and files notes for the field. Get past the front desk and into the vault.

## 解题原理

题目是一个 fork 型服务：父进程负责解析 SUBMIT/RELAY/NOTE 等命令，子进程持有 flag.txt 的文件描述符并维护一个 16 槽的 vault。漏洞点有两处：一是子进程的 vault 读取处理只用 `cmp eax,0xf; jg` 做上界检查，缺少下界检查，因此负索引可通过；索引 -4 会落到 0x4060b0-0x1030=0x405080，正是预初始化的 4 个 type-2 源条目所在位置，其中 entry0 的 fd 就是 flag.txt，于是可以越界读到 flag。二是父进程的 SUBMIT <size> 把 size 字节读入 0x40 的栈缓冲区（到返回地址偏移 0x48），且父进程的 seccomp 允许 read/write，构成可用的 ROP 条件。配合该 ROP 可先泄漏每连接的 XOR 密钥（keystream 为密钥字节逆序 k3 k2 k1 k0），再把构造好的 type-3 vault frame 写给 fd3 交由子进程处理，触发负索引读取并把 flag 响应排队，最后用 RELAY 让父进程读取并解密打印。

## 关键步骤

1. 连接服务（nc chal.sunshinectf.games 26007 或本地 process('./service')），等待出现 'sh> ' 提示符。
2. 阶段 1：发送 `SUBMIT 255` 触发 0x40 栈缓冲区溢出。ROP 链用 write(1, 0x405060, 3) 与 write(1, 0x405061, 3) 泄漏全部 4 个密钥字节（rdx=3 由处理函数残留提供），再用 MULTIPOP（0x401520）设置 rbx/rbp/r12/r13/r14/r15，并把 rbp 指向 BSS 命令缓冲区，最后返回到命令循环 0x4014d0。
3. 由泄漏结果计算 keystream = leaked_key[::-1]；构造明文帧 plain = {type=3, len=5, pad=0, payload=0xfffffffc, pad}（字节序列 03 00 05 00 fc ff ff ff 00），按 frame[i] = plain[i] ^ keystream[i%4] 得到加密帧。
4. 阶段 2：再次 `SUBMIT 255`，ROP 调用 read(0, ...) 把 9 字节加密帧和 '1\0' 字符串读入 BSS（脚本分 4 次 3 字节读取）。
5. 阶段 3：再次 `SUBMIT 255`，ROP 以 3 次 3 字节 write 把 9 字节帧写入 fd3，交给子进程处理负索引 vault 读取，子进程将 flag 响应排队。
6. 发送 `RELAY 1`，父进程读出已排队的响应并解密打印 flag。

## EXP 与运行方法

文件：`exp/exp.py`

已保存 EXP 为 exp/exp.py，依赖 pwntools。运行方式：本地为 `python3 exp.py`（process('./service')），远程为 `python3 exp.py remote`（remote('chal.sunshinectf.games', 26007)）。脚本内部按 run(io) 顺序执行三个阶段 SUBMIT 255 溢出、发送加密帧与 '1\0'、写入 fd3，最后发送 RELAY 1 并 recv 输出。replay.status 为 verified，记录的命令为 `cd /challenge/workspace && python3 exp.py remote`，退出码 0，stdout 中显示了泄漏的 leak6/key、构造出的 frame 以及最终输出的 flag，说明该 EXP 已在沙箱中自动复现成功。exp 中硬编码了 WRITE=0x401190、READ=0x4011f0、POP_RDI=0x401529、POP_RSI=0x401dd5、MULTIPOP=0x401520、LOOP=0x4014d0、KEY=0x405060 及若干 BSS 地址。

## 验证结果

全新沙箱运行成功，输出与记录的 Flag 一致。

运行命令：`cd /challenge/workspace && python3 exp.py remote`

证据：

- Metadata: Pwn 'Safe House', nc chal.sunshinectf.games 26007, service binary sha256 40c8993c...
- Binary forks: parent reads commands (SUBMIT/RELAY/NOTE), child holds flag.txt fd and serves a 16-slot vault with 4 pre-initialized type-2 source entries at 0x405080 (entry0 fd=flag.txt); slot array base 0x4060b0.
- Child read handler checks index only with `cmp eax,0xf; jg range` (no lower bound), so index=-4 maps to 0x4060b0-0x1030=0x405080 (flag fd) and preads the flag.
- SUBMIT <size> reads `size` bytes into a 0x40 stack buffer (offset 0x48 to return), and seccomp in the parent permits read/write, enabling a ROP chain.
- Leaked the per-connection XOR key via write(1, 0x405060/61, 3) using rdx=3 carried over from the handler; keystream is key bytes reversed (k3 k2 k1 k0).
- Loaded 9-byte encrypted frame [03 00 05 00 fc ff ff ff 00] into BSS and wrote it to fd3, queuing the vault flag response; 'RELAY 1' then made the parent decrypt/print it.

## Flag

`sun{n3gat1ve_h4ndl3s_0pen_s3cret_d00rs}`

## 限制与备注

该利用依赖若干前提：二进制未启用 PIE 才能使用上述硬编码地址；父进程 seccomp 恰好允许 read/write；密钥泄漏依赖处理函数残留的 rdx=3，并且 XOR 密钥是每连接生成的，必须在同一连接内先泄漏再构造帧；负索引 -4 能命中 flag 文件描述符也依赖 0x405080 处预初始化条目的具体布局。replay 状态为 verified 时才可声称 EXP 已自动复现，本材料满足该条件，但换环境（地址随机化、不同版本二进制或服务端改动）后需重新确认。confirmation_source 为 platform_confirmed，flag 已由平台确认。
