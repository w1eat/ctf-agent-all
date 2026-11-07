---
title: "PWN 0x02: Interaction"
source_challenge: "PWN 0x02: Interaction"
confirmation_source: independent_quorum
verification_status: verified
run_id: "0cd56e959b7841faa43f9a9202044946"
---

# PWN 0x02: Interaction

## 可复用方法

Flag found via PDF attachment content extraction: the only attachment pwntools.pdf explicitly ends with a FLAG section containing the flag; verified by two independent extractors (pdftotext, pypdf) and by visually rendering page 7.: [redacted] | Evidence: ls /challenge/distfiles -> only pwntools.pdf (251251 bytes, PDF 1.7, 7 pages). metadata.yml: challenge_mode: attachment, connection_info: '', environment_required: false -> no remote service and no ELF binary are supplied. ; pdftotext -layout /challenge/distfiles/pwntools.pdf out.txt: final lines of page 7 are 'FLAG' then '[redacted]'. ; pypdf PdfReader page 7 extract_text gives exactly '[redacted]'; codepoints are pure ASCII 44 31 4e 4f 7b 79 30 75 5f 6e 30 77 5f 68 30 77 5f 74 30 5f 75 35 33 5f 70 77 6e 74 30 30 6c 73 7d. ; pdftoppm -f 7 -l 7 -r 100 -png rendered page7-7.png; view_image shows the FLAG heading and the same [redacted] string visibly, ruling out white/hidden text or extraction artifacts. ; pdfdetach -list reports 0 embedded files; exiftool shows no custom metadata; all FlateDecode streams decompressed and regex-searched for flag-like tokens found only this one real text flag (font data noise excluded). | Independently verified by deepseek/deepseek-flash, deepseek/deepseek-flash#verifier

## 验证步骤

1. 侦察附件：执行 ls -la /challenge/distfiles 与 file，确认本关唯一附件是 pwntools.pdf，没有 ELF 程序、libc 或远程地址。
2. 核对元数据：读取 /challenge/metadata.yml，看到 challenge_mode: attachment、connection_info: ''、environment_required: false，说明题目不提供远程交互服务，本题的“交互”知识点仅体现在教程 PDF 中，真正可解的入口是附件本身。
3. 提取文本：运行 pdftotext -layout /challenge/distfiles/pwntools.pdf out.txt，查看 out.txt 末尾，第 7 页章节 'FLAG' 下方就是 [redacted]。
4. 交叉验证：用 pypdf 独立解析第 7 页并提取 D1NO 开头的 token，得到完全相同字符串；打印每个字符十六进制码点，确认全部是 ASCII，没有同形字或零宽字符。
5. 视觉复核：用 pdftoppm -f 7 -l 7 -r 100 -png 渲染第 7 页为 page7-7.png，再 view_image 查看，页面上明确显示 FLAG 标题及相同 flag，排除隐藏/白色文字导致的误读。
6. 排除其他载体：pdfdetach -list 显示 0 个嵌入文件；exiftool 无自定义元数据；脚本解压全部 FlateDecode 流并正则搜索，除该 token 外没有第二个真实 flag（其余匹配均为压缩字体数据的随机字节）。
7. 排除隐藏服务：metadata 无连接信息；nmap 172.17.0.1 常用 pwn 端口全部 closed；平台 flag-submissions 接口需 [redacted]
8. 尝试平台提交：submit_flag 三次均在浏览器自动化阶段报 textarea[aria-label="Flag"] 选择器不存在，属于提交工具与平台前端 DOM 不匹配的基础设施错误，未返回 INCORRECT。
9. 结论：附件 PDF 是本题唯一且完整的信息源，其页码 7 明示的 [redacted] 即为题目 flag；因平台提交工具故障，标记为待平台确认的候选 flag。
