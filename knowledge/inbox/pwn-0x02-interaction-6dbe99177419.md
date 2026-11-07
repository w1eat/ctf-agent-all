---
title: "PWN 0x02: Interaction"
source_challenge: "PWN 0x02: Interaction"
confirmation_source: independent_quorum
verification_status: verified
run_id: "0cd56e959b7841faa43f9a9202044946"
---

# PWN 0x02: Interaction

## 可复用方法

Flag found via The challenge attachment is not an ELF binary but a pwntools tutorial PDF (7 pages, 251251 bytes, sha256 f564f2a1...). Extracting its text with `pdftotext` reveals a final section headed 'FLAG' containing the flag verbatim; no exploitation or remote connection is required for this recon-level challenge.: [redacted] | Evidence: /challenge/distfiles/pwntools.pdf identified as 'PDF document, version 1.7', Producer Typora, 7 pages — no ELF/pwn binary is attached, so IDA analysis is not applicable (list_analysis_tools shows file_ids: []). ; `pdftotext /challenge/distfiles/pwntools.pdf -` output ends with the section 'FLAG' followed by the literal line: [redacted] ; grep of workspace dump confirms it at line 328 of pwntools_text.txt. ; Automated re-extraction: /challenge/workspace/extract_flag.sh prints [redacted]; saved to /challenge/workspace/flag.txt. ; Platform submission could not be confirmed: submit_flag returned a tooling error 'browser_wait_for: Invalid input: expected number, received null' on both attempts, so no browser page evidence was produced. | Independently verified by deepseek/deepseek-flash, deepseek/deepseek-flash#verifier

## 验证步骤

1. 检查附件目录 `ls -la /challenge/distfiles/`，发现唯一文件是 `pwntools.pdf`，`file` 显示为 PDF 1.7，说明本关是 recon 性质的资料关，没有可分析的 ELF（`list_analysis_tools` 返回 file_ids 为空，IDA 无匹配二进制）。
2. 对该 PDF 使用 `pdftotext pwntools.pdf -` 提取正文，内容为 Pwntools 教程：安装、send/recv/recvuntil、ELF 解析、p64/u64、shellcraft、GDB 联动和标准 EXP 模板。
3. 阅读到正文最后一节标题为 `FLAG`，其下一行即 `[redacted]`；为排除 PDF 内部隐藏流干扰，另外用 `strings` 与文本转储双重核对（`grep -n D1NO pwntools_text.txt` 命中第 328 行）。
4. 将提取逻辑固化为脚本 `/challenge/workspace/extract_flag.sh`（pdftotext + grep 正则 `[redacted]]*}`），运行输出与 PDF 文本一致，结果写入 /challenge/workspace/flag.txt，并记录 PDF 的 sha256 作为证据锚点。
5. 调用 submit_flag 提交该 flag，工具返回 `browser_wait_for` 参数为 null 的提交配方错误（重试同样失败），因此仅能由附件原文直接验证，未能获得平台页面接受证据。
