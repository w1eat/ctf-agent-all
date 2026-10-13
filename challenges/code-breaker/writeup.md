# Code Breaker 题解

- 分类：Pwn
- 确认方式：平台确认
- 复现状态：人工复现


## 题目信息

CodeBreaker: enterprise-grade encrypted key-value storage. All traffic is encrypted with our proprietary cipher. Your data has never been safer.

## 解题原理

该题是一个带自研加密协议的键值存储服务（Pwn）。服务端首先发送明文初始包 [len=0x0011][0x01][16 字节随机数 R]，要求客户端完成两步握手：先发 0x02 包并携带自选的 16 字节 B，再发 0x03 包并携带用会话密钥流加密的校验值 v。密钥由自定义 key schedule 从 R||B 推出：S[k] = rol8(T[buf[(8o+k)%32] ^ S[k]] ^ buf[3o+k], 3)，共 4 轮外层循环；随后的流密码密钥流为 keystream[i] = T[(counter + i + S[i%16]) & 0xff]，其中 T 是文件中偏移 0x2040 处 256 字节的替换表。只要逆向出该算法即可伪造合法握手包，使服务端进入 KV-store 命令循环。进入业务协议后，clone/free 的引用计数逻辑存在缺陷：clone 出的条目与源条目共享同一指针，但每个条目各自维护计数，导致可以对同一块内存重复释放（use-after-free / double-free），进而形成 tcache double free。利用链上：先通过 0x16 info 命令泄露位于 0x40c0 的函数指针（0x1390 偏移）得到 PIE 基址；再从被释放 chunk 的 safe-linking 编码 next 指针泄露堆偏移 p>>12；随后 tcache poisoning 把分配目标改到 PIE+0x40c0，写入 system@plt（PIE+0x1150）覆盖该函数指针；最后 0x15 'run' 命令会以攻击者可控字符串调用 [0x40c0]，从而获得命令执行并读出 flag。

## 关键步骤

1. 从题目二进制文件偏移 0x2040 处取出 256 字节 T 表，并逆向下标 0x1670 处的 key schedule 函数，确认自定义密钥调度算法。
2. 读取服务端发来的 17 字节初始包（[len][0x01][16 字节随机数 R]），自选 16 字节 B；发送 0x02+B 包，按 key_schedule(R, B) 计算 S，再用 counter=0 的流密码加密 0x03+v 校验包发送，完成握手。
3. 进入 KV-store 协议，维护收发计数器（密钥流解密/加密）：根据材料，握手后入站计数器为 17、出站计数器为 2，后续每个包都按此偏移加解密。
4. 用 0x16 info 命令泄露 0x40c0 处的函数指针（0x1390 偏移），计算 PIE 基址；再通过被释放 chunk 的 safe-linking 编码 next 指针泄露堆偏移 p>>12。
5. 利用 clone/free 计数缺陷制造 tcache double free（材料脚本对同一缓冲区做三次 clone，再配合 write/free 操作完成），把 tcache next 指针改写指向 PIE+0x40c0，分配该地址处的 chunk 并写入 system@plt（PIE+0x1150）。
6. 发送 0x15 'run' 命令并附带命令字符串，触发 [0x40c0] 被调用为 system()，在远端执行 'cat flag*' 读取 flag。

## EXP 与运行方法

文件：`exp/solve.py`, `exp/exploit.py`

已保存两个 EXP 脚本，均需人工运行（replay.status 为 manual，未由平台自动复现）。exp/solve.py：从 /challenge/distfiles/code-breaker 读取 T 表，实现 rol8、key_schedule、vbytes、keystream 与 Conn 类，负责完成握手并可通过 connect() 建立会话；作为脚本运行时（python3 solve.py [host] [port]）会打印握手响应，并发送 0x16 info 命令打印响应内容用于泄露验证。exp/exploit.py：从 solve 导入 Conn/connect/keystream，实现 do_alloc/do_read/do_write/do_free/do_clone/do_info 等协议封装，按上述思路完成 PIE 泄露、堆偏移泄露、tcache poisoning 与函数指针覆盖，最后发送 0x15 命令并读取原始输出。运行方式为 python3 exploit.py <host> <port>（需 pwn 库提供 p64/u64，缺失时有内置回退实现）；不带参数时走本地分支，通过 process 启动 ld-linux-x86-64.so.2 与 code-breaker 二进制。脚本中 final_cmd 默认为 b"cat /flag*;cat flag*;ls -la /;id"，flag 由其中的 cat flag* 取得。注意：replay 记录显示运行命令所引用的脚本不在已保存 EXP 中，因此当前只能人工复现。

## 验证结果

运行命令引用的脚本不在已保存的 EXP 中，需人工复现。

证据：

- Remote service sent an initial plaintext packet [len=0x0011][0x01][16 random bytes] and required a 0x02 handshake packet followed by a 0x03 verification packet.
- Reversed the custom key schedule: S[k] = rol8(T[buf[(8o+k)%32] ^ S[k]] ^ buf[3o+k], 3) over 4 outer rounds, and the stream cipher keystream[i] = T[(counter + i + S[i%16]) & 0xff]. Produced valid handshake packets so the server proceeded into the KV-store command loop.
- Found a use-after-free/double-free in the clone/free refcount logic (clone shares ptr but each entry has its own count), enabling a tcache double-free.
- Leaked the PIE base from the 0x16 info command (function pointer 0x1390 at 0x40c0), leaked the heap shift p>>12 from the freed chunk's safe-linked next pointer, then tcache-poisoned to allocate a chunk at 0x40c0 and overwrite the function pointer with system@plt (PIE+0x1150).
- The 0x15 'run' command calls [0x40c0] with attacker-controlled string, giving RCE; running 'cat flag*' on the remote returned sun{cr4ck_tHe_ciPh3r_fr33_thE_heaP}.

## Flag

`sun{cr4ck_tHe_ciPh3r_fr33_thE_heaP}`

## 限制与备注

1) replay.status 为 manual，材料未提供自动复现记录（command/exit_code/stdout 为空），因此不能声称 EXP 已自动跑通或平台已按 EXP 验证，只能说明按脚本人工复现的方式。2) T 表与各偏移（0x1390、0x40c0、0x1150、文件偏移 0x2040、0x1670）均针对本题特定二进制，换版本即失效。3) 堆偏移泄露依赖 glibc safe-linking 的编码形式（next ^ (p>>12)），若目标 glibc 或分配行为不同需调整。4) 利用依赖远端服务保持存活且行为与本地一致，连接信息 nc chal.sunshinectf.games 26005 为材料所给。5) confirmation_source 为 platform_confirmed，flag 值 sun{cr4ck_tHe_ciPh3r_fr33_thE_heaP} 按材料视为平台确认；除此之外的攻击细节均由 EXP 与证据描述支撑，未额外扩展。6) 脚本中 final_cmd 同时尝试多个路径（/flag*、flag*）并附带 ls 与 id，实际命中来源依据现有材料无法逐一区分。
