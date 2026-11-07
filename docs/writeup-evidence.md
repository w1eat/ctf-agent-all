# 题解、复现步骤与证据归档

题解正文必须能够回到实际命令、文件和观察结果。写作模型负责解释给定材料，程序负责保存产物、渲染命令和插入图片，并检查所有证据引用。

## 求解时保存什么

所有求解后端继续输出 `solution_steps`、`exp_paths` 和 `exp_run_command`。步骤应说明操作目的、具体参数、观察结果和下一步依据；`exp_paths` 登记实际用过的脚本。新增的 `artifact_paths` 登记实际生成的图片、音频或文本证据：

```json
{
  "type": "candidate_found",
  "flag": "FLAG{example}",
  "method": "从附件恢复隐藏区域",
  "solution_steps": ["检查结构，依据实际数据长度恢复隐藏区域，并查看生成的图片"],
  "exp_paths": ["/challenge/workspace/solve.py"],
  "exp_run_command": "python3 /challenge/workspace/solve.py",
  "artifact_paths": ["/challenge/workspace/full.png", "/challenge/workspace/hidden_rows.png"]
}
```

脚本沿用原来的 EXP 捕获限制，不能内嵌完整答案或账号凭据。证据产物允许包含题目中真实出现的 Flag；它们的作用正是保存观察结果。产物在沙箱停止前复制，使用内容哈希存储，保留原始字节和来源信息。

命令证据独立于简短的运行 trace。Pydantic 与 Codex 的 `bash` 工具在显示截断前记录 stdout、stderr 和退出码；Claude SDK 在工具钩子中记录原始操作与返回内容，并通过调用 ID 对应并发结果。来源本身已经截断的内容会明确标记。知识库正文不会进入命令证据。

## 保存位置与边界

```text
writeup.md
exp/                                  实际脚本
solution/manifest.json                确认来源、证据引用、哈希与复现状态
solution/evidence/<编号>/commands.jsonl 命令、参数、目录、观察输出与来源
solution/artifacts/<内容哈希>/          图片、音频与文本证据
solution/replays/<内容哈希>.json        新沙箱复现结果
solution/submissions/<Flag哈希>.json    同一运行中具体 Flag 的提交页面证据
```

每批最多保存 12 个产物，单文件最多 16 MiB，总计最多 48 MiB。支持 PNG、JPEG、GIF、WebP、WAV、MP3，以及 UTF-8 文本、日志、JSON、JSONL、CSV。检查文件签名；PNG 另外检查 chunk 边界和 CRC。拒绝路径穿越、绝对主机路径、符号链接和目录联接。

命令记录每条最多保留 64000 个字符，单个日志最多 8 MiB。写作上下文最多选取 24 条命令，覆盖开始、中间和结尾；正文显示节选并链接到完整的已保留记录。EXP 写作上下文也有长度上限，实际脚本文件不因此被截短。文本沿用凭据脱敏；图片、音频按原始字节保存，图像内的文字不会自动打码。

浏览器在提交操作的锁内保存同一页面的文字并尝试截取当前视口。截图失败时仍保留文字证据，不改变提交结果。截图表示真实页面，不能单凭截图文件存在就声称平台接受。题解只读取与当前 Flag 哈希、运行 ID 都一致的提交证据。

## 正文如何引用证据

写作输出增加 `environment` 和 `detailed_steps`。每个详细步骤包含：

| 字段 | 用途 |
|---|---|
| `title` | 操作标题 |
| `explanation` | 目的、关键推导、参数来源与操作说明 |
| `expected_result` | 供读者核对的预期现象，与实际观察分开 |
| `evidence_ids` | 已提供命令证据的编号 |
| `artifact_ids` | 已归档产物的编号 |

命令、实际输出、文件链接、配图和哈希由程序插入。模型不能新增未提供的证据编号或自行编造图片路径；引用不存在的编号会使本次生成失败。渲染前重新检查产物哈希，文件缺失或发生修改时不会嵌入，并记录待检查原因。代码围栏按真实内容选择长度，避免日志中的围栏截断正文。

旧的四字段写作结果和已有清单仍可读取；旧步骤可以与真实命令、产物附录一起展示。生成版本记录为 `format_version: 2`。同一候选新增证据后可刷新题解；生成编号防止较早的异步写作覆盖较新的材料。人工修改仍由原有哈希保护机制保留。

## 阅读排版

题解使用可独立阅读的 Markdown，顶部展示题型、确认方式、复现状态和材料数量，并提供章节导航。正文按题目与环境、解题思路、详细复现步骤、EXP、验证结果与 Flag、证据附录排列。

正文使用普通 Markdown，目录链接到标题自动生成的位置，不插入 HTML 锚点或折叠标签。这样可避免部分阅读器把 `<a>`、`<details>` 等标签直接显示在正文中。

命令和 EXP 源码使用带语言标记的围栏代码块。短输出直接展示；超过 14 行或 1200 个字符的输出移到文末，通过“查看实际输出与执行记录”跳转。目录、工具、退出码和原始记录一并列入命令附录。完整 EXP 源码单独放在最后一章，每个文件最多展示前 16000 个字符，并链接到完整文件。

图片保留正常 Markdown 图片链接，紧随所属步骤展示，并附说明和来源；核对要点单独突出。完整文件路径与 SHA-256 集中在文末清单。候选警示、证据截断说明、历史来源说明和复现限制保持可见。

## 复现结果的含义

| 状态 | 证据含义 |
|---|---|
| `verified` | 脚本退出 0，输出包含与记录完全一致的 Flag |
| `artifacts_generated` | 脚本退出 0，已保存图片或音频；没有自动识别并匹配 Flag |
| `manual` | 没有符合自动运行条件的 EXP，需要人工操作 |
| `needs_review` | 运行失败、缺少输出、证据有问题或其他待检查情况 |

候选出现时仍立即写题解，不等待新沙箱复现。平台确认来源与 EXP 复现状态独立。图片恢复后可以人工查看，音频恢复后可以收听；这些结果不会自动变成平台确认。

## 检查与升级历史题解

```powershell
uv run ctf-writeup audit
uv run ctf-writeup audit --challenge you-cut-me-off --json
uv run ctf-writeup backfill --run-id RUN_ID --upgrade-format --challenge you-cut-me-off
```

`audit` 不调用模型、不访问网络、不写文件，检查格式、命令记录、配图路径与产物完整性。`--challenge` 可重复，接受题目名称或目录名。

历史补写只使用指定运行的候选和确认；未标记运行的旧 trace 仍需精确的协调器确认来关联题目与 Flag。归档真实的工具调用/结果对，明确标记为历史来源；无法恢复旧日志中已经截去的内容。`--upgrade-format` 会升级旧生成文件，人工编辑仍保留；`--force` 才会强制覆盖。补写会调用配置的写作模型，确认过的记录也可能触发新沙箱复现。

## 已实际复现的三个示例

- [you cut me off](../challenges/you-cut-me-off/writeup.md)：标准库解码器、5 个详细步骤、4 张恢复图、像素交叉核对。
- [Welcome Call!](../challenges/welcome-call!/writeup.md)：4 个详细步骤、原始与校正 WAV、完整 μ-law 解码表交叉核对、历史转录来源。平台关联仍待核对。
- [IntMod](../challenges/intmod/writeup.md)：7 个详细步骤、微操作求逆表、实际 Flag 输出、正向/逆向核对、原始 ELF 对照与动态状态采集。保留从 ELF 重建 MICRO 与 D 的工具链缺口。

这三个维护示例在 2026-10-23 先于本机 Python 运行，随后又在新的 `ctf-sandbox:latest` 容器中复现。容器实际环境为 Linux x86-64、Python 3.10.12、zlib 1.2.11、Scapy 2.7.0、Pillow 12.3.0。完整镜像 ID、命令、输出、退出码与产物写入各自的 `solution/docker-reproduction-20261023.json`，首次本机记录与产物仍保留。

从仓库根目录可重复运行容器验证：

```powershell
uv run python -B tools/verify_writeup_docker.py
uv run python -B tools/verify_writeup_docker.py --challenge intmod
```

该工具使用项目的 `DockerSandbox`，每题启动新容器，运行结束后删除该容器。它保存复现报告、命令日志和证据产物，不调用写作模型，也不自行改写 WP。报告按执行日期保存为 `solution/docker-reproduction-YYYYMMDD.json`；同日重复执行时保留前次执行历史。

本次核对结果：四张恢复 PNG 的压缩字节与 Windows 版本不同，但尺寸和 RGBA 像素完全一致，分别保留两次实际文件哈希；两个 WAV 逐字节一致，256 项 μ-law 解码与样本倒序关系通过。IntMod 恢复值交给原始 ELF 返回 `Correct`，同长度单字节修改输入返回 `Nope`；四组 ptrace 输入各采集到 171 个状态。`check_transform.py` 已兼容沙箱附件路径，并支持 `--input`。

本次没有重新提交平台。音频题继续标记为候选，图片题继续保留人工读取环节；IntMod 的原程序验证与状态采集已实际完成，MICRO 自动推断及 D 矩阵提取仍待补齐。
