# Cache Money 题解

- 分类：Pwn
- 确认方式：平台确认
- 复现状态：人工复现


## 题目信息

The arcade's credit manager tracks every wallet in the house. The books haven't been audited in years, so help yourself.

## 解题原理

题目是一个堆内存管理器（cache-money），目标程序无 PIE、部分 RELRO，运行于 glibc 2.39。钱包结构大致为 {name[16]; balance; ledger*; size; active}。核心漏洞在 transfer 操作：它先 free(src->ledger)，随后仍把已释放的指针写入 dst->ledger，造成 use-after-free（悬垂指针可读可写），并且同一 chunk 可以被反复释放，形成 tcache double-free。

由此可组合出完整利用链：
1）Withdraw 会打印 ledger 内容，可用 unsorted bin 中的 fd/bk 泄露 libc 基址（偏移 0x203b20）；
2）用悬垂钱包读取被释放 chunk 的 fd，得到 safe-linking 编码值（chunk>>12），从而泄露堆地址；
3）glibc 2.39 的 tcache 在 +8 处写 key 做 double-free 检查，通过悬垂钱包向该 chunk 写 0（deposit 零字节）清掉 key，即可绕过检查再次释放同一 chunk；
4）随后毒化 tcache fd，使其为 目标地址 ^ (chunk>>12)，两次 malloc 即可返回任意地址；将其指向 .bss 上的钱包表 0x4040C0，伪造 wallet[0] 使其 ledger 指向 strtol@GOT(0x404040)、size=8；
5）通过 deposit 把 system 地址写入 strtol@GOT，再在菜单输入 '/bin/sh' 触发 strtol() 变成 system()，获得远程 shell 读取 flag。

## 关键步骤

1. 分析 cache-money 的菜单式堆管理器与钱包结构 {name[16]; balance; ledger*; size; active}。
2. 识别转移（transfer）逻辑漏洞：先 free(src->ledger)，再把该已释放指针复制给 dst->ledger，得到 UAF 读写与原语并且可重复释放（double-free）。
3. 泄露 libc：先填满 0x110 大小的 tcache（7 次释放），再把第 8 个 0x100 的 ledger 释放进 unsorted bin，用 withdraw 读取其 fd 得到 libc 地址，减去偏移 0x203b20 得到 libc 基址。
4. 泄露堆：把一个 0x80 的 ledger 转移进空的 0x90 tcache bin，读取被 safe-linking 编码的 fd（即 chunk>>12）。
5. 绕过 tcache double-free 检查：通过悬垂钱包 deposit 写入 0 覆盖被释放 chunk 的 fd/key（+8 处的 key），使第二次释放不被检测。
6. 毒化 tcache fd：写入 fd = 目标地址 ^ (chunk>>12)，两次分配后即可返回攻击者指定的地址。
7. 把某次分配指向 0x4040C0（.bss 上的 wallets 表），伪造 wallet[0]，令其 ledger=0x404040（strtol@GOT）、size=8。
8. deposit(p64(system)) 将 system 写入 strtol@GOT；随后在菜单输入 '/bin/sh' 让 strtol 调用变成 system，触发命令执行。
9. 在远程 shell 中执行 id、cat /flag*、cat /ctf/flag.txt 等读取 flag（材料记录为 uid=1337(cache_money)，并读到给定 flag）。

## EXP 与运行方法

文件：`exp/cm/exp_sync.py`

材料中提供了脚本 exp/cm/exp_sync.py，replay.status 为 manual，即只能人工复现，未被自动验证通过。脚本使用 pwn 库，需要同目录下的 libc.so.6 与 ld-linux-x86-64-so.2。运行方式为：python3 exp/cm/exp_sync.py local 用 ld 加载本地 ./cache-money 进行本地调试；python3 exp/cm/exp_sync.py <其它参数> 时用 remote('chal.sunshinectf.games', 26004) 连接远程（对应 nc chal.sunshinectf.games 26004）。脚本内关键常量与流程：LEAK_OFF=0x203b20、SYSTEM=libc.symbols['system']、TARGET=0x4040C0、STRTOL_GOT=0x404040；先发送 setup_batch() 布置堆状态（8 个 256 字节 ledger、释放 1~7 填满 tcache、转移 1->2、withdraw 2 触发泄露），读取 0x100 与 0x80 两段泄露，计算 libc_base 与 safe-linking 位移；随后 deposit(2) 清零 fd/key，再 open C、transfer 2->3 触发 double-free，deposit(3) 写入毒化 fd，open P1/P2 得到目标地址、deposit(5) 伪造 wallets 表，deposit(0) 写入 system 覆盖 strtol@GOT，最后发送 '/bin/sh' 触发并执行 id、cat /flag* 等读取 flag。

## 验证结果

提供的 EXP 运行命令不符合安全的单脚本格式，需人工复现。

证据：

- Withdraw prints ledger bytes -> unsorted bin fd/bk leak gives libc base (offset 0x203b20)
- Transfer bug frees source ledger but copies the (freed) pointer into destination -> use-after-free read/write
- Withdraw on the dangling wallet leaks the safe-linking-encoded fd = chunk>>12 -> heap leak
- Clearing the freed chunk's tcache key (offset +8) bypasses the glibc tcache double-free check
- Second transfer frees the same chunk again; poison its fd to 0x4040C0(.bss wallets) -> next malloc returns the wallet table
- Craft a fake wallet with ledger = strtol@GOT (0x404040) and size 8
- Deposit system address into strtol@GOT, then feed '/bin/sh' as the menu option so strtol() becomes system()
- Shell as uid=1337(cache_money); `id` and reading the flag printed sun{s4fe_l1nk1ng_w0nt_s4ve_y0ur_tc4che}; /ctf/flag.txt present

## Flag

`sun{s4fe_l1nk1ng_w0nt_s4ve_y0ur_tc4che}`

## 限制与备注

1）利用高度依赖目标环境：需 glibc 2.39，需配套的 libc.so.6 与 ld-linux-x86-64-so.2，无 PIE、部分 RELRO；libc 版本或偏移变化时 LEAK_OFF=0x203b20、strtol@GOT、.bss 钱包表地址等都需重新确认。2）safe-linking 与 tcache key 与 glibc 版本强相关，换版本可能失效。3）replay.status 为 manual、command 为空、exit_code 与 stdout 均为空，因此不能声称 EXP 已自动复现；材料里的利用过程与 flag 读取结果来自已保存脚本与人工记录，需人工在相同环境中执行脚本复核。4）confirmation_source 为 platform_confirmed，flag 为平台确认值，可视为该题的正确 flag；但本地复现不保证一次成功，脚本中 time.sleep 等时序依赖可能在不同环境下需要调整。5）脚本会自动执行 cat /flag*、find 等命令，人工复现时应确认目标与授权范围，避免在非授权环境运行。
