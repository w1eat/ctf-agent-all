# RoboCall 题解

- 分类：RE
- 确认方式：平台确认
- 复现状态：人工复现


## 题目信息

Welcome to robocall! Let's see how nimbly you navigate this stack.

## 解题原理

本题是一个逆向 + 未初始化栈变量泄露的组合题。place_flag() 会读取 flag.txt，并把 Flag 按 4 字节一块、共 13 块散写到自身 0x2020 字节缓冲区的栈上，偏移为 local_2028[0x19dc - CHUNK_DEPTH[i]]（CHUNK_DEPTH = 0x400,0x480,0x520,0x570,0x5a0,0x640,0x690,0x6c0,0x760,0x7b0,0x7e0,0x800,0x880）。而 cancel_plan 中的第二个提示解析结果存放在 local_20c（rbp-0x204）；当两次读取均为空时，raw_parse_int 不会写入该变量，随后 raw_print_int 直接打印这块未初始化的栈内存，从而把先前 place_flag 遗留在栈上的 Flag 分块泄露出来。由于两个函数栈帧的相对距离（rbp_place - rbp_cancel）由调用路径上各层函数的栈帧大小决定（步长 step = sub_rsp + 0x10），通过选择菜单选项构造调用链，使 rbp_place - rbp_cancel = 0x440 + CHUNK_DEPTH[i]，就能让 cancel_plan 泄露出的 4 字节恰好对齐到第 i 个 Flag 分块。逐块读出并拼接，即可还原完整 Flag。

## 关键步骤

1. 逆向 place_flag：确认它读取 flag.txt，并把 Flag 的 13 个 4 字节分块写到相对自身缓冲区的偏移 0x19dc - CHUNK_DEPTH[i] 处，CHUNK_DEPTH 为材料给出的 13 个固定值。
2. 在 cancel_plan 中确认泄露点：local_20c 位于 rbp-0x204，第二次提示会被解析到该变量；若两次输入都为空，raw_parse_int 不写入该变量，raw_print_int 打印的是残留栈值（即 Flag 分块）。
3. 对菜单驱动的状态机（SP/IC/RO/BD/TS/UC/OI/SPEAK）建模，各步栈帧大小记为 step = sub_rsp + 0x10；基准路径的 T 为 0x440，目标是让 T = 0x440 + CHUNK_DEPTH[i]。
4. 用 DFS 搜索（gen.py 所示方式）在菜单选项空间中找出 13 个目标深度各自对应的输入序列。
5. 先在本地用已知的测试 flag.txt 对 13 个分块逐一验证，确认对齐与泄露逻辑正确。
6. 再用相同的交互序列对 nc sunshinectf.games 26199 复现，逐块泄露远程 Flag 字节并拼接。
7. 提交重构出的 Flag；材料中 confirmation_source 为 platform_confirmed，即该 Flag 已被平台确认。

## EXP 与运行方法

文件：`exp/decompiled.c`, `exp/gen.py`

replay.status 为 manual，因此不能声称 EXP 已自动复现。材料中保存的 exp/decompiled.c 只是反编译产物（且 raw_parse_int 部分内容被截断），并非可直接执行的攻击脚本；exp/gen.py 是一个 DFS 搜索脚本，用于在状态机上遍历菜单选项并打印每个目标深度是否有解以及首个可用的输入序列。实际使用方式只能是人工复现：运行 gen.py 得到各 CHUNK_DEPTH 对应的输入序列，再按这些序列与目标服务交互，并以空输入触发 cancel_plan 的未初始化变量泄露，逐块读取 Flag。材料未提供可自动完成泄露与拼接的单一脚本，其运行命令也不符合安全的单脚本格式，故给出的 command 为空。

## 验证结果

提供的 EXP 运行命令不符合安全的单脚本格式，需人工复现。

证据：

- Flag bytes are scattered onto the stack by place_flag() at local_2028[0x19dc - CHUNK_DEPTH[i]] for 13 chunks (CHUNK_DEPTH = 0x400,0x480,0x520,0x570,0x5a0,0x640,0x690,0x6c0,0x760,0x7b0,0x7e0,0x800,0x880).
- In cancel_plan, the second prompt parses into local_20c at rbp-0x204; if both reads are empty, raw_parse_int does not write it and raw_print_int prints the stale stack value (the flag chunk).
- Choosing menu paths so that rbp_place - rbp_cancel = 0x440 + CHUNK_DEPTH[i] aligns the leaked 4 bytes with each flag chunk; a DFS model found input sequences for all 13 depths.
- Locally verified all 13 chunks against flag.txt, then leaked remotely: sun{ you_ must _be_ some _sor t_of _nim ble_ spac e_na viga tor}

## Flag

`sun{you_must_be_some_sort_of_nimble_space_navigator}`

## 限制与备注

1) 泄露成立的前提是 place_flag 已在同一进程、更早的调用路径中执行过，使 Flag 分块已写入该栈区域；调用顺序不同则取不到。2) 依赖二进制与本地一致、CHUNK_DEPTH 与各函数栈帧步长（step = sub_rsp + 0x10）与模型完全吻合；rbp 之间的差值是相对偏移、不受 ASLR 影响，但模型误差会导致对齐失败。3) 依赖 flag.txt 能被 place_flag 打开读取。4) 材料中 decompiled.c 在 raw_parse_int 处被截断，无法据此完整核对该函数的全部分支行为。5) replay.status 为 manual，未自动复现，也未提供完整的逐块泄露脚本与运行记录，远程泄露结果只能依据 findings_summary 中的记载，不能声称由已保存的 EXP 自动跑通。
