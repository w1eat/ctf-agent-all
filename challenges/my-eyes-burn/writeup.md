# my eyes burn 题解

- 分类：Forensics
- 确认方式：平台确认
- 复现状态：自动复现通过


## 题目信息

anon hasn't been outside in years, so he put the sun in his keyboard. find the flag he types to bring it out.

## 解题原理

题目给出的 boardwriter.klc 是 Windows MSKLC 键盘布局源文件（UTF-16LE 编码），其中的 DEADKEY 段定义了「死键组合」规则：某死键（基础字符）与之后键入的字符组合后，会输出另一个字符，并且该输出字符又可以作为下一级死键继续组合。本题把整条死键链首尾相接，从初始死键 U+0060（反引号 `）一路推进，最终组合出 U+2600（☀，太阳），呼应题面「把太阳放进键盘」。而沿途每一步键入的基字符按顺序拼起来，恰好构成玩家需要敲出的 flag 文本。

## 关键步骤

1. 以 UTF-16 方式读取并解码 boardwriter.klc，逐行解析所有 `DEADKEY <base>` 行与随后的 `<key> <result>@` 条目，构建「死键 -> {基字符: 组合结果}」的映射表。
2. 从初始死键 U+0060（`）出发，沿映射链逐步前进：当前死键 + 一个基字符 -> 下一个死键。
3. 记录链上被键入的基字符，链依次为 `→s→u→n→{→p→r→a→i→s→e→t→h→e→s→u→n→}，最终组合到 U+2600 ☀（太阳）。
4. 拼接被键入的字符得到 '`sun{praisethesun}'，去掉作为起始死键的反引号，即得可读 flag：sun{praisethesun}。
5. 用 /challenge/workspace/solve.py 复现该破译过程，并在平台提交。

## EXP 与运行方法

文件：`exp/solve.py`

已保存 EXP 为 exp/solve.py。脚本以二进制方式读取 /challenge/distfiles/boardwriter.klc，用 UTF-16 解码，遍历各行：遇到以 DEADKEY 开头的行则用其第二个字段（十六进制）作为当前死键并初始化子字典；随后每行按空白切分成两段时，把 (基字符十六进制, 结果字符十六进制) 记入当前死键的映射。之后从 cur = 0x0060、typed = '`' 开始，只要当前值还在映射表中，就取该死键的一项（next(iter(...))），把基字符追加到 typed 并把结果设为新的 cur，循环结束后打印最终组合字符与去掉反引号的可读 flag。运行方式：`cd /challenge/workspace && python3 solve.py`，退出码 0，stdout 为 `typed to produce U+2600: '`sun{praisethesun}'` 与 `readable flag: sun{praisethesun}`。replay.status 为 verified，说明该 EXP 已在全新沙箱中自动复现成功，输出与记录的 flag 一致；confirmation_source 为 platform_confirmed，即平台提交页面已确认该 flag 正确（返回提示为 “Correct but you already solved this”，题目行显示 Solved，397 分）。

## 验证结果

全新沙箱运行成功，输出与记录的 Flag 一致。

运行命令：`cd /challenge/workspace && python3 solve.py`

证据：

- File is UTF-16LE MSKLC .klc keyboard layout (SunshineCTF 2026, native_id 27, Forensics).
- Parsed DEADKEY chain: 0060(')+0073(s)->02d0, 02d0+0075(u)->02ed, 02ed+006e(n)->02b4, 02b4+007b({)->02ef, 02ef+0070(p)->02ba, 02ba+0072(r)->02c9, 02c9+0061(a)->02d3, 02d3+0069(i)->02e9, 02e9+0073(s)->02bd, 02bd+0065(e)->02cd, 02cd+0074(t)->02e4, 02e4+0068(h)->02d8, 02d8+0065(e)->02ee, 02ee+0073(s)->02d4, 02d4+0075(u)->02e1, 02e1+006e(n)->02b0, 02b0+007d(})->2600 (SUN).
- Script /challenge/workspace/solve.py outputs: typed to produce U+2600: '`sun{praisethesun}' ; readable flag: sun{praisethesun}.
- Platform submission page returned alert 'Correct but you already solved this'; challenge row shows '✦ Solved' (397 pts, 289 solves).

## Flag

`sun{praisethesun}`

## 限制与备注

本说明仅依据给定材料，未执行任何命令。EXP 正常工作依赖以下条件：/challenge/distfiles/boardwriter.klc 路径存在且文件确为 UTF-16 编码的 MSKLC .klc 布局；脚本对每个死键只取映射中的第一项（next(iter(...))），因此隐含假设该布局中每个死键只有一个后续组合，若实际文件存在多分支映射，脚本可能选中错误分支。同理，解析逻辑在遇到 ENDKBD 或非两段行时依赖特定格式，格式变化会导致解析失败。平台确认信息来自提交页面返回的提示与题目状态，材料中未提供独立的题目唯一 ID 或更详细的判题回执，无法进一步交叉核对。若没有该 EXP，只能人工解析 .klc 文件中的 DEADKEY 段并沿链手工推导，过程与本 EXP 一致。
