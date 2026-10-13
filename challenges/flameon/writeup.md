# FlameOn 题解

- 分类：RE
- 确认方式：平台确认
- 复现状态：人工复现


## 题目信息

I seem to have gotten my hands on a weird copy of Super Mario World. The fire flower especially seems to be acting strange. Note: this challenge is a ROM hack patch (bps).

## 解题原理

题目给的是一个 BPS 格式的 ROM hack 补丁（ctf.bps），而非可执行程序本体。BPS（byuu patch / beat patch）是给 SNES ROM（此处为 Super Mario World）打补丁的差分包，因此需要先按 BPS 容器格式解析出源文件大小、目标文件大小与动作序列；其中 TargetRead 动作会在指定输出偏移写入原始字面量。补丁通过覆盖原 ROM 的指令为 JSL（跳转到新增代码区）并追加新增代码段，实现代码注入：0x1C3 处被改写为 22 00 80 10 EA EA（JSL $108000; NOP; NOP），0xC5F9 处被改写为 22 36 80 10 EA（JSL $108036; NOP），把控制流重定向到新增区（文件偏移 0x80000 起）。新增的 65816 例程是一个以 0x5A 为密钥、以 0x00 结尾的字符串解密循环（LDA $8022,X / EOR #$5A / STA $7EC100,X），flag 密文就嵌在同一 TargetRead 字面量中，逐字节异或 0x5A 即可还原明文 flag。

## 关键步骤

1. 按 BPS 变长整数规则解析 ctf.bps：每字节取低 7 位累加到当前位移，最高位为 1 表示该整数结束（STOP）；解析得 source_size=0x80000（512KB 原始 SMW ROM）、target_size=0x100000（扩展为 1MB）、metadata_size=0。
2. 解析动作列表，定位两处 TargetRead 写入：输出偏移 451（0x1C3）写入 22 00 80 10 EA EA，即 JSL $108000 加两条 NOP；输出偏移 50681（0xC5F9）写入 22 36 80 10 EA，即 JSL $108036 加一条 NOP。两处均把原有逻辑重定向到新增代码区（文件偏移 0x80000）。
3. 对新增区（文件偏移 524299 起）的 TargetRead 字面量做 65816 反汇编：5a 48 a2 00 bd 22 80 f0 09 49 5a 9f 00 c1 7e e8 80 f2 68 7a fa ab 6b，可辨识出循环体 LDA $8022,X / EOR #$5A / STA $7EC100,X，即一个用 0x5A 异或、遇 0x00 结束的字符串解密例程。
4. 在同一字面量内提取以 0x00 结尾的内嵌密文 29 2f 34 21 1c 6b 3b 17 69 05 35 14 05 17 6e 28 6b 6a 27 00，逐字节异或 0x5A，得到明文 sun{F1aM3_oN_M4r10}。
5. 提交该 flag，平台页面弹窗显示 Correct（confirm_submission 返回 CORRECT），确认通过。

## EXP 与运行方法

文件：无

没有保存任何 EXP 脚本文件（exp_files 为空），replay.status 为 manual，因此不存在可自动运行的复现命令，只能按上述步骤人工复现：使用 BPS 解析工具/脚本读取 ctf.bps 得到大小与动作序列，再用 65816 反汇编器（或手工解码）分析新增区代码，最后用 Python 等工具对密文字节逐字节异或 0x5A 得到 flag。材料中未给出可直接执行的 EXP 及其命令、退出码或输出。

## 验证结果

没有可自动运行的 EXP；请按题解步骤人工复现。

证据：

- ctf.bps magic = 'BPS1'; 140 bytes
- Correct BPS varint parse (byte&0x7f added at running shift; HIGH bit set = break) gives source_size=0x80000, target_size=0x100000, metadata_size=0
- Actions list includes TargetRead at output offset 451 (22 00 80 10 ea ea = JSL $108000; NOP; NOP) and at 50681 (22 36 80 10 ea = JSL $108036; NOP)
- 65816 disasm of literal at 524299: 5a 48 a2 00 bd 22 80 f0 09 49 5a 9f 00 c1 7e e8 80 f2 68 7a fa ab 6b => loop LDA $8022,X / EOR #$5A / STA $7EC100,X (XOR-0x5A string decryptor)
- Embedded encrypted bytes 29 2f 34 21 1c 6b 3b 17 69 05 35 14 05 17 6e 28 6b 6a 27 00 XOR 0x5A => 'sun{F1aM3_oN_M4r10}'
- Platform page showed alert 'Correct' after submission; confirm_submission returned CORRECT

## Flag

`sun{F1aM3_oN_M4r10}`

## 限制与备注

所有偏移量、字节序列与反汇编结果均来自给定证据中对这一份 ctf.bps（magic 'BPS1'，140 字节）的解析，换用其他补丁文件需重新解析，不能直接套用。人工复现依赖具备 BPS 解析与 65816 反汇编能力的工具或脚本，材料未提供这些工具的具体实现，也未提供可自动运行的 EXP，故无法声称已自动复现（replay.status=manual）。flag 已被平台确认（confirmation_source=platform_confirmed，页面显示 Correct），但密文提取、偏移定位等中间结论仅依据现有证据，若手工操作出现偏差（如变长整数解析时误用符号位扩展、或未正确识别 TargetRead 字面量边界）会导致错误结果，需以解析结果为准复核。
