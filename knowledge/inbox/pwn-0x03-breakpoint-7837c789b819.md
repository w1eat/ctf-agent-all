---
title: "PWN 0x03: Breakpoint"
source_challenge: "PWN 0x03: Breakpoint"
confirmation_source: independent_quorum
verification_status: verified
run_id: "0cd56e959b7841faa43f9a9202044946"
---

# PWN 0x03: Breakpoint

## 可复用方法

Flag found via Attachment is a 10-page Typora-generated PDF tutorial about GDB/Pwndbg. Extracted text with pdftotext: page 10 contains exactly one visible fenced code block holding the flag. Verified independently by rendering page 10 to PNG and reading it, and by decompressing all PDF streams (only text/font/xref streams, no embedded binary, JS, or alternate flag).: [redacted] | Evidence: `pdftotext -f 10 -l 10 -layout /challenge/distfiles/gdb.pdf -` outputs exactly '[redacted]\n\f' (page 10 of 10). ; `pdftoppm -f 10 -l 10 -r 120 -png gdb.pdf page10` rendered a page showing a single code block: [redacted]. ; Full-text extraction of all 10 pages shows a Chinese GDB/Pwndbg tutorial (breakpoints, info registers, x/nfu, context, vmmap, telescope, checksec, search, canary, heap, bins) ending with the same flag line. ; PDF structure checked: 25 zlib streams only; no /EmbeddedFile, /JavaScript, /OpenAction, /Annot, or second D1NO occurrence. ; metadata.yml confirms attachment mode with only distfiles/gdb.pdf and empty connection_info, so no remote service exists for this challenge. | Independently verified by deepseek/deepseek-flash, deepseek/deepseek-flash#verifier

## 验证步骤

1. 先检查附件：`ls -la /challenge/distfiles` 与 `file gdb.pdf`，确认唯一附件是 PDF 1.7，10 页，由 Typora 生成；metadata.yml 的 connection_info 为空，说明没有远程服务，只能从文件取 flag。
2. 用 `pdftotext -layout gdb.pdf gdb.txt` 提取全文，通读内容为 GDB/Pwndbg 教程（断点、寄存器、内存查看、context、vmmap、telescope、checksec、search、heap、bins 等），文末出现 `[redacted]`。
3. 为了排除文末是正文注释或诱饵，按页提取：`pdftotext -f 10 -l 10 -layout gdb.pdf -`，第 10 页输出恰好只有该 flag 一行，说明它被单独放在最后一页代码块中。
4. 再用 `pdftoppm -f 10 -l 10 -r 120 -png gdb.pdf page10` 渲染第 10 页并用 view_image 查看，页面顶部唯一可见内容为代码框 `[redacted]`，确认不是不可见文字或乱码。
5. 解析 PDF 对象：用 Python zlib 解压全部 25 个 stream，检查是否存在 /EmbeddedFile、/JavaScript、/OpenAction、/Annot 及第二个 D1NO 字符串；结果只有正文文本、TrueType 字体和 xref 流，无其他隐藏 flag，因此该值即真实 flag。
6. 尝试调用 submit_flag 提交，平台提交脚本因未登录/未加入比赛导致挑战详情页 404，找不到 aria-label=Flag 的 textarea 而报错；这不影响从附件中得到的 flag 证据。最终候选 flag 为 `[redacted]`。
