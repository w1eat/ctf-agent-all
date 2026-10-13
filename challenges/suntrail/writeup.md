# suntrail 题解

- 分类：Forensics
- 确认方式：平台确认
- 复现状态：自动复现通过


## 题目信息

im lost, but you can find the way!

## 解题原理

题目是一个 Windows 键盘布局文件（.klc，ASCII，头部 KBD\tkbdusx\t"US"）。该文件被改造成「寻路图」：LAYOUT 行格式为 '<scancode>\t<VK>\t0\t<state0_char>\t<state1_char>\t-1'，其中 SHIFTSTATE 0 列本应存放普通字符，这里却被替换为 Unicode 箭头字符，用来表示在键盘网格上的行进方向——U+2198(↘)、U+2192(→)、U+2196(↖) 分别对应向下一步、向右一步、向上一步，U+25A0(■) 表示终点；SHIFTSTATE 1 列则给出每个键对应的字符。把键盘按 3 行网格（QWERT / ASDFGH / ZXCVBN）排列，从 Q 出发沿箭头逐键行走，会形成一条经过全部 17 个键、每键只走一次的哈密顿路径；按路径顺序读出每个键的 state1 字符，即可拼出 flag。

## 关键步骤

1. 用 file/xxd 等确认 suntrail.klc 是 ASCII 的 Windows 键盘布局文件（头部 KBD\tkbdusx\t"US"），属于 Forensics 分析对象。
2. 解析 LAYOUT 段，每行按 '<scancode>\t<VK>\t0\t<state0_char>\t<state1_char>\t-1' 拆分，分别取出 state0 与 state1 两列。
3. 识别 state0 列中出现的 Unicode 字符：U+2198(↘)、U+2192(→)、U+2196(↖) 作为行进方向，U+25A0(■) 作为终点标记。
4. 识别 state1 列为每个按键对应的字符，形成 Key→char 映射，例如 Q=s、W=w、E=e、R=s、T=u、A=u、S=q、D=r、F=_、G=c、H=}、Z=n、X={、C=t、V=y、B=k、N=s。
5. 把键盘排成 3 行网格：QWERT、ASDFGH、ZXCVBN，从 Q 出发，按每个键给出的方向逐键移动，遇到 U+25A0 即停止。
6. 得到一条覆盖全部 17 个键且每键恰好访问一次的哈密顿路径：Q→A→Z→X→S→W→E→D→C→V→F→R→T→G→B→N→H。
7. 按路径顺序读出各键 state1 字符，依次为 s、u、n、{、q、w、e、r、t、y、_、s、u、c、k、s、}，拼接得到 sun{qwerty_sucks}。
8. 提交该 flag，平台页面返回 Correct，确认 flag 正确（confirmation_source 为 platform_confirmed）。

## EXP 与运行方法

文件：`exp/solve.py`, `exp/exp_suntrail.py`, `exp/brute.py`

replay.status 为 verified，材料记录 EXP 已在全新沙箱自动复现成功：执行 'cd /challenge/workspace && python3 solve.py'，exit_code 为 0，stdout 输出路径 'Q(s) -> A(u) -> Z(n) -> X({) -> S(q) -> W(w) -> E(e) -> D(r) -> C(t) -> V(y) -> F(_) -> R(s) -> T(u) -> G(c) -> B(k) -> N(s) -> H(})' 与 'FLAG: sun{qwerty_sucks}'。exp/solve.py 与 exp/exp_suntrail.py 内容相同，均以硬编码的 3 行网格和 M={'DR':(1,0),'R':(0,1),'UL':(-1,0)} 的移动映射来模拟走位并拼接 flag。exp/brute.py 是辅助脚本：它枚举 DR、R、UL 三类移动的多种可能，筛选末尾为 '}' 且长度达标的路径并排序输出；材料未给出 brute.py 的独立复现结果，它只用于交叉参考。

## 验证结果

全新沙箱运行成功，输出与记录的 Flag 一致。

运行命令：`cd /challenge/workspace && python3 solve.py`

证据：

- suntrail.klc is an ASCII Windows Keyboard Layout Creator file (header KBD\tkbdusx\t"US"), category Forensics.
- LAYOUT rows are '<scancode>\t<VK>\t0\t<state0_char>\t<state1_char>\t-1'. State0 chars: U+2198(↘), U+2192(→), U+2196(↖), U+25A0(■) -> trail directions. State1 chars are ASCII letters.
- Key->char map (state1): Q=s W=w E=e R=s T=u A=u S=q D=r F=_ G=c H=} Z=n X={ C=t V=y B=k N=s.
- Applying directions (down/right/up) on the grid yields path Q->A->Z->X->S->W->E->D->C->V->F->R->T->G->B->N->H, visiting all 17 keys exactly once.
- Letters along the path = 'sun{qwerty_sucks}'.
- Submission via platform returned alert 'Correct' confirming the flag.

## Flag

`sun{qwerty_sucks}`

## 限制与备注

解题结论依赖若干解析假设：键盘必须按材料所述的 3 行网格（QWERT / ASDFGH / ZXCVBN）排列，且箭头方向按 U+2198=下、U+2192=右、U+2196=上、U+25A0=终点来解释；若布局行顺序、扫描码含义或方向映射不同，路径与结果会变化。state0 列被替换为箭头字符是偏离常规 .klc 用法的改造点，解析时不能默认该列是普通文本。exp/brute.py 的枚举结果未被单独复现验证，只能作为辅助信息。题目 flag 已由平台确认（platform_confirmed 且 replay 为 verified），但依据现有证据无法确认该解法在不同键盘布局文件或其他平台环境下的通用性。
