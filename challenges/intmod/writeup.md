# IntMod 题解

- 分类：RE
- 确认方式：平台确认
- 复现状态：自动复现通过


## 题目信息

"IntMod?? Do you mean integer modulus??" "No. I do not mean that." "Then what, pretell, could it mean?" "Just put the agent on the case."

## 解题原理

该题二进制是一个基于信号与 ucontext 的自定义 VM：通过 int3/ud2/div 触发 SIGTRAP/SIGILL/SIGFPE，由自身注册的信号 handler 分发 VM 指令。它对 33 字节输入先补 7 个固定 0x07 凑成 40 字节，打包成 5 个 64 位寄存器 r0..r4，再执行固定的 90 步微操作序列（addrol、xorrol、rol、swap、mul 等，均为可逆变换）得到 digest D。校验部分使用模 65521 的多项式哈希：opcode 5 计算 reg[5+i] = (polyhash(reg0..4, seed_lo) - seed_hi) mod 65521，其中 polyhash = Σ byte[k]*base^k mod 65521，对 digest 各字节是线性的；opcode 6 将 (imm ^ reg[5+i]) 累积进 reg9，最终判断 reg9 == 0 决定输出 Correct 还是 Nope。由于哈希对 digest 线性、变换可逆，可由校验条件反解出唯一 digest，再把 digest 逆变换回初始输入，即 flag。

## 关键步骤

1. 静态分析确认主流程：读入 33 字节 -> 打包成 5 个 64 位寄存器（40 字节，后 7 字节固定 0x07）-> 由信号（ucontext）+ int3/ud2/div 触发的自定义 VM 运行 126 条指令 -> 检查 reg9 == 0 决定输出 Correct/Nope。
2. 识别校验本质：opcode 5 计算 reg[5+i] = (poly_hash(reg0..4, seed_lo) - seed_hi) mod 65521，opcode 6 校验 reg[5+i] 与 imm（0x400FA0/0x400E40，p=0xFFF1）的关系；poly_hash = Σ byte[k]*base^k mod 65521，对 40 字节 digest 是线性的。
3. 从 26 组 (op5 seed / op6 target) 建立 40 个模 65521 线性方程，用高斯消元得到唯一 digest D（所有解字节 < 256），D = 7647653d32c8af6c 8b335299eb07dda8 82dd9502a3be9591 d66e926f06c4a36f 77a194bf7b25dff2。
4. 用自写 ptrace tracer 追踪 VM（把 SIGTRAP/SIGILL/SIGFPE 等信号转发给自身的 handler），对多组输入取每一步寄存器状态并求各步微操作的可行集合交集，恢复出固定的 90 步微操作序列（addrol/xorrol/rol/mul/swap）。
5. 按相反顺序对 D 求逆（sub-rol、xor-rol、ror、swap、乘模逆），得到初始 5 个寄存器，拼成 40 字节；前 33 字节即为 flag，后 7 字节恰为 0x07 填充。
6. 验证：`printf 'sun{I_L0v3_Int3rrupts&SelfMod!!!}' | ./intmod` 输出 Correct；平台提交页面返回 Correct 确认。

## EXP 与运行方法

文件：`exp/solve_intmod.py`, `exp/tracer.c`, `exp/runseq.py`

提供的 EXP 为 exp/solve_intmod.py，其中内嵌了通过 ptrace 恢复的 90 步微操作序列（MICRO）以及线性方程组解出的目标 digest D；脚本执行 inverse_transform，逆序对每个微操作求逆（addrol 用 rol 后相减、xorrol 用 rol 后异或、rol 用 ror、swap 交换、mul 乘模逆），再由结构体按小端拼出 40 字节，取前 33 字节并断言后 7 字节为 0x07，最后打印 flag。replay 状态为 verified：在全新沙箱中执行 `cd /challenge/workspace && python3 solve_intmod.py` 退出码 0，stdout 为 sun{I_L0v3_Int3rrupts&SelfMod!!!}，与平台确认的 Flag 一致。另附 exp/tracer.c 与 exp/runseq.py 为恢复微操作序列的辅助工具：tracer 以 ptrace 跟踪 ./intmod 并转发信号，runseq.py 对多组输入采集每步寄存器状态并枚举生成微操作候选，它们用于离线推导，不属于最终一键求解路径的必需部分（MICRO 与 D 已内嵌于求解脚本中）。

## 验证结果

全新沙箱运行成功，输出与记录的 Flag 一致。

运行命令：`cd /challenge/workspace && python3 solve_intmod.py`

证据：

- Binary reads 33 bytes, prints 'Correct'/'Nope'. Verified: `printf 'sun{I_L0v3_Int3rrupts&SelfMod!!!}\n' | /challenge/distfiles/intmod` prints `Correct`.
- The check is a linear system mod 65521: opcode 5 computes reg[5+i] = (polyhash(reg0..4, seed_lo) - seed_hi) mod 65521; opcode 6 ORs (imm ^ reg[5+i]) into reg9, and sub_400DD0 returns (reg9==0). Solved the 40-equation system over GF(65521) to get target digest D = 7647653d32c8af6c 8b335299eb07dda8 82dd9502a3be9591 d66e926f06c4a36f 77a194bf7b25dff2.
- The transform is a fixed 90-step micro-op sequence (exec op + dispatch 'extra' op). Recovered it by ptrace-tracing the VM (forwarding SIGTRAP/SIGILL/SIGFPE so its own handlers run) for 4 inputs and intersecting the per-step op fits; then inverting each op (sub-rol / xor-rol / ror / swap / mul by modular inverse).
- Inverse transform yields 40 bytes: 73756e7b495f4c3076335f496e74337272757074732653656c664d6f642121217d07070707070707 == 'sun{I_L0v3_Int3rrupts&SelfMod!!!}' + 0x07*7 (the VM's fixed padding).
- Platform submission page returned a 'Correct' alert for this exact flag (confirmed).

## Flag

`sun{I_L0v3_Int3rrupts&SelfMod!!!}`

## 限制与备注

1) 解题依赖先通过 ptrace 动态追踪恢复 VM 的固定微操作序列；若运行环境禁用 ptrace 或不转发信号，tracer 与 runseq.py 无法工作。2) digest D 的求解依赖 mod 65521 线性系统的唯一解且所有字节 < 256 这一前提，材料中未给出方程组的冗余度或唯一性证明，仅报告求解结果。3) 最终答案包含 33 字节 flag 加 7 字节 0x07 固定填充，脚本以断言方式检查填充，若 VM 填充方式不同该断言会失败。4) 材料未逐条给出 opcode 表、seed/imm 常量与 VM 指令的完整反汇编对应关系，opcode 5/6 的语义依据 findings 与 evidence 描述。5) 平台确认与 replay 成功均来自材料记录，本说明不重新执行命令验证。
