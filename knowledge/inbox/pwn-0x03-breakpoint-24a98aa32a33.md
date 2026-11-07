---
title: "PWN 0x03: Breakpoint"
source_challenge: "PWN 0x03: Breakpoint"
confirmation_source: independent_quorum
verification_status: verified
run_id: "0cd56e959b7841faa43f9a9202044946"
---

# PWN 0x03: Breakpoint

## 可复用方法

Flag found via 附件 gdb.pdf 为 Typora 导出的 GDB/Pwndbg 教程 PDF；用 pdftotext 提取正文（非流内乱码），在最后一页代码块中发现明文字符串 [redacted]，并用 pdftoppm 渲染第 10 页做视觉复核。: [redacted] | Evidence: `pdftotext -layout /challenge/distfiles/gdb.pdf gdb.txt` 得到的第 568 行即最后一行：`[redacted]`（前文为 Pwndbg 命令速查表，末尾单独一个代码块）。 ; `pdftotext -f 10 -l 10 gdb.pdf page10.txt` 显示第 10 页整页只有该 flag 代码块。 ; `pdftoppm -f 10 -l 10 -r 100 -png gdb.pdf page10` 渲染后用 view_image 目视确认页面顶部灰色代码块文字为 `[redacted]`。 ; pdfinfo 显示 PDF 由 Typora/Electron 生成、10 页、无 JavaScript/EmbeddedFile，flag 属正文内容而非隐藏对象流。 ; 尝试调用 submit_flag 三次均返回平台侧配方错误 `Invalid arguments for tool "browser_wait_for": expected number, received null`，未能获得 ACCEPTED 页面证据；flag 本身来自附件可复现文本，但仍属未经平台确认的独立提取结果。 | Independently verified by deepseek/deepseek-flash, deepseek/deepseek-flash#verifier

## 验证步骤

1. 先确认附件类型：`file /challenge/distfiles/gdb.pdf` 显示 PDF 1.7；用 `pdfinfo` 得知 10 页、Typora 生成、无 JS/无嵌入文件/未加密。
2. 直接提取文本：`pdftotext -layout gdb.pdf gdb.txt`。注意 PDF 里的二进制度量流会含随机 `[redacted]` 噪声，所以要读正文而非在原始字节里 grep。
3. 通读 gdb.txt：前 9 页讲解 GDB 的 run/break/x/info registers、Pwndbg 的 context/vmmap/telescope/checksec/search/heap/bins 等命令，符合题面描述；文本最后一行是单独的代码块 `[redacted]`。
4. 交叉验证不是拼接噪声：`pdftotext -f 10 -l 10 gdb.pdf -` 单页输出同样只有该字符串；再用 `pdftoppm -f 10 -l 10 -r 100 -png gdb.pdf page10` 渲染并用 view_image 目视，第 10 页顶部灰底代码块确为同一字符串。
5. 编写可复现脚本 /challenge/workspace/extract_flag.py（pdftotext 文本 + 正则 `[A-Za-z0-9_]{2,}\{[^}\n]{4,}\}`），运行 `python3 extract_flag.py /challenge/distfiles/gdb.pdf` 输出唯一 flag，说明无需真正连接远程 PWN 服务——本题为 recon 子任务，flag 藏在教程附件中。
6. 保存证据：gdb.txt（全文）、page10.txt（第 10 页文本）、page10-10.png（第 10 页渲染图）、flag_extracted.txt（脚本输出）到 /challenge/workspace/。
7. 最后用 submit_flag 尝试提交，但连续三次均因平台浏览器配方 bug（browser_wait_for 参数为 null 的错误）而失败，因此无法取得平台接收证据；提取结果本身可完全本地复现。
