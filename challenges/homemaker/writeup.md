# Homemaker 题解

- 分类：Pwn
- 确认方式：平台确认
- 复现状态：自动复现通过


## 题目信息

A SERVANT IN EVERY HOME, BY 1975! APEX ATOMIC HOUSEHOLD INDUSTRIES, INC IS PROUD TO ANNOUNCE THE MODEL 7 HOMEMAKER DOMESTIC AUTOMATON.

## 解题原理

该题为 Pwn（栈溢出结合自定义协议解析缺陷）。程序使用一套自定义的 RETRO-ASCII / 打孔卡风格帧协议：帧格式为 ESC[ Lh Ll <L 字节 body> <crc8> ESC\，body[0] 为命令（1=open、2=write、3=show、4=exit、5=system echo），crc8 采用 MSB-first、多项式 0x2f。漏洞链为：(1) open 命令在 key == 0x1337c35f 校验通过后把 state[0x100] 设为 0x100(256)，该字段被当作后续 write 的索引上界与 show 的长度边界；(2) write 处理器把 len-1 字节拷贝进位于 rbp-0x110 的栈缓冲 state，仅检查 idx <= state[0x100]，当一次写入 257 字节时，crc 校验字节会落在 state[256]，即直接改写 state[0x100] 这个边界字段，若爆破数据使 crc == 0xff，则 state[0x100] 变为 0x1ff(511)，边界被放大；(3) show 处理器按 state[0..state[0x100]-1] 输出，从而越界读出栈上的 canary（偏移 264）、saved rbp（272）与返回地址（280 = pie+0x1a9f），由此同时泄露栈保护 cookie 与 PIE 基址；(4) 再次 write 时因边界可达 511，可以覆盖 canary 与返回地址，用 ROP 链 pop rdi;ret -> system@plt 并把 rdi 指向位于可写 .bss 输入缓冲区的 "/bin/sh" 字符串，最终调用 system 获得 shell。核心成因是长度/边界字段与数据缓冲区处于同一可越界写入的栈区域，属于典型的 off-by-one/边界字段被覆写导致的越界读写。

## 关键步骤

1. 用 IDA/objdump 逆向，确认这是一个使用自定义帧协议（ESC[ len body crc8 ESC\）的菜单程序，命令为 1=插入钥匙(open)、2=写(state)、3=显示(state)、4=退出、5=system(echo)。
2. open 需要 key == 0x1337c35f（.text:1289 处校验），成功后 .text:167c 将 state[0x100] 置为 0x100(256)。
3. write 处理器（.text:174c）将 len-1 字节拷入栈缓冲 state（rbp-0x110），只检查 idx <= state[0x100]；发送 257 字节的 write，使 crc 字节落在 state[256]，爆破数据令 crc8 = 0xff，从而把 state[0x100] 改成 0x1ff(511)。
4. 用 show（.text:1810）输出 state[0..state[0x100]-1]，得到 canary（偏移 264）、saved rbp（272）、返回地址（280，= pie+0x1a9f），据此计算出 canary 与 PIE 基址。
5. 第二次 write（idx 上限已达 511）覆盖 canary 与返回地址，布置 ROP：pop rdi;ret (pie+0x12aa) -> "/bin/sh"(位于 .bss 输入缓冲区，pie+0x4865) -> ret (pie+0x101a，用于栈对齐) -> system@plt (pie+0x10c0)。
6. 用带 "/bin/sh" 的 exit 帧（命令 4）把该字符串写入 .bss 输入缓冲区，然后触发函数返回执行 ROP 链。
7. 拿到 shell 后执行 cat /flag* 等命令读取 flag，得到 sun{the_future_is_now_today_well_wait_how_are_you_reading_this}。

## EXP 与运行方法

文件：`exp/exp.py`

已保存的 EXP 为 exp/exp.py（Python 3 + pwntools）。脚本内定义 crc8() 与 frame() 复现协议封包，常量 POP_RDI=0x12aa、RET=0x101a、SYSTEM=0x10c0、RET_MAIN=0x1a9f、BSS_IN=0x4860（payload 指针为 buf+4）。运行方式：默认 process('./homemaker') 本地调试，传入参数 remote 时连接 remote('sunshinectf.games', 26008)。实际自动复现命令为：cd /challenge/workspace && python3 exp.py remote，退出码 0。脚本按「open -> 爆破 crc 的 257 字节 write -> show 泄露 -> 覆盖返回地址的 write -> 携带 /bin/sh 的 exit -> 发送 cat /flag* 等命令」的顺序执行。replay.status 为 verified，说明该 EXP 已在全新沙箱中自动复现成功，输出与记录的 Flag 一致（远端 uid=1337(homemaker)）。执行流程会进入 io.interactive()。

## 验证结果

全新沙箱运行成功，输出与记录的 Flag 一致。

运行命令：`cd /challenge/workspace && python3 exp.py remote`

证据：

- Protocol: frames = ESC[ Lh Ll <L-byte body> <crc8> ESC\ where body[0] is a command (1=open,2=write,3=show,4=exit,5=system echo); crc8 = MSB-first poly 0x2f.
- .text:1289 checks key == 0x1337c35f; .text:167c sets state[0x100]=0x100 on success.
- .text:174c 'write' copies len-1 bytes into stack buffer (state, rbp-0x110) after checking idx<=state[0x100]; writing 257 bytes makes state[256]=crc byte, so forcing crc==0xff sets state[0x100]=0x1ff=511.
- .text:1810 'show' emits state[0..state[0x100]-1] -> leak of canary (offset 264), saved rbp (272), return addr into main (280 = pie+0x1a9f).
- ROP: pop rdi;ret @ pie+0x12aa, ret @ pie+0x101a, system@plt @ pie+0x10c0; '/bin/sh' placed in .bss input buffer (pie+0x4864+1) via the final exit frame body.
- Local shell confirmed (uid=0) then remote run returned: sun{the_future_is_now_today_well_wait_how_are_you_reading_this} with uid=1337(homemaker).
- Platform submission returned CORRECT for this exact flag.

## Flag

`sun{the_future_is_now_today_well_wait_how_are_you_reading_this}`

## 限制与备注

1) 该 EXP 依赖本地存在同名二进制 ./homemaker 用于本地复现，且所有偏移（canary 264、saved rbp 272、返回地址 280、RET_MAIN=0x1a9f、POP_RDI/RET/SYSTEM/BSS_IN 等）均与当前题目版本严格绑定，换版本即失效。2) 改写 state[0x100] 需要对 crc8 结果进行最多 256 次爆破，属于概率性步骤，但脚本中循环遍历 v 至多 256 次可保证命中，依赖协议实现未被修改。3) ROP 链要求 system@plt 已存在于 PLT、.bss 输入缓冲区可写且地址固定（相对 PIE 偏移），并需要 PIE 基址与 canary 泄露成功，任一泄露失败即无法利用。4) 取 flag 依赖目标环境存在 /flag* 等路径；本次已由平台确认该 Flag 正确（confirmation_source 为 platform_confirmed）。5) 复现需要能连通 sunshinectf.games:26008，网络不可达时只能本地复现。6) 依据现有证据无法确认其他环境（不同 libc、不同编译选项）下的稳定性。
