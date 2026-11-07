---
title: "PWN 0x01: Insight"
source_challenge: "PWN 0x01: Insight"
confirmation_source: platform_confirmed
verification_status: verified
run_id: "0cd56e959b7841faa43f9a9202044946"
---

# PWN 0x01: Insight

## 可复用方法

Flag found via The "binary" attachment is actually a 3-page PDF tutorial (Typora-generated). The flag is printed verbatim on page 3 as text. Verified two independent ways: (1) pdftotext text-layer extraction, (2) decoding the raw PDF page-3 content stream glyph IDs through the embedded OpenSans-Regular /ToUnicode CMap (0052 0058 0058 0050 0047 0054 → 'p','v','v','n','e','r'), which rules out an OCR/font artifact — the PDF truly contains two 'v' glyphs ('pvvner', leet for 'pwner', matching the '1earn' leet spelling).: [redacted] | Evidence: file: /challenge/distfiles/IDA Pro.pdf → 'PDF document, version 1.7', 3 pages, Creator: Typora ; pdftotext -raw page 3 output: [redacted] ; Raw PDF content stream of page 3 contains: <0027001400500051005D0043...0046 0041 0052 0058 0058 0050 0047 0054 ...> Tj ; /ToUnicode CMap of /F5 (OpenSans-Regular): bfrange <004D><0052><006B> and <0054><005B><0072>, i.e. 0x52='p', 0x54='r', 0x55='s', 0x56='t', 0x57='u', 0x58='v', 0x59='w' → the two repeated codes 0x0058 are genuinely 'v','v' ; 600-dpi raster of the flag line (crop2.png) visually shows: [redacted]

## 验证步骤

1. 识别附件：ls /challenge/distfiles → 只有一个 'IDA Pro.pdf'；file 命令显示为 PDF 1.7，3 页，Creator=Typora。这不是 ELF 二进制，所谓“用 IDA 分析程序”只是题面背景，真正的 FLAG 直接写在讲义里。
2. 文本层提取：执行 pdftotext -layout 'IDA Pro.pdf' ida.txt，阅读全文，在第 3 页最后一行看到 [redacted]。
3. 怀疑字体/提取误差：pdftotext 给出的 'pvvner' 与常见写法 'pwner' 不符，于是做独立验证。用 pypdf 取出第 3 页 /Contents 原始流，找到该行文字操作符 <0027001400500051005D0043...> Tj（Type0 复合字体，Tj 里是 glyph index 而非 Unicode）。
4. 解析 ToUnicode：读取 /Resources/Font/F5(/BAAAAA+OpenSans-Regular) 的 /ToUnicode CMap，得到 bfrange <0054> <005B> <0072>，即 0x54='r'…0x59='w'；因此 0x0058='v'。FLAG 片段 0052 0058 0058 0050 0047 0054 精确对应 p,v,v,n,e,r，说明 PDF 内确实写的是两个 v（leet 写法 pvvner，与 1earn 一致），而非提取错误。
5. 可视化复核：pdftoppm -r 600 -f 3 -l 3 渲染第 3 页并用 PIL 裁出 'D1no{a_g00d_' 前段放大到 2520x300（crop2.png），肉眼可见 p v v n e r 两个 v 字形。
6. 脚本化验证：编写 /challenge/workspace/extract_flag.py，同时打印文本层结果和内容流解码结果，两者都输出 [redacted]（日志 evidence_extract.log）。
7. 提交：调用 submit_flag 提交该 flag（前几次因浏览器 recipe 选择器超时报错，重试后返回 SUBMISSION_PENDING 且无失败标记），再以页面证据调用 confirm_submission，系统返回 CORRECT，确认 flag 正确。
