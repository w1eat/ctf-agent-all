---
title: "PWN 0x01: Insight"
source_challenge: "PWN 0x01: Insight"
confirmation_source: independent_quorum
verification_status: verified
run_id: "0cd56e959b7841faa43f9a9202044946"
---

# PWN 0x01: Insight

## 可复用方法

Flag found via 附件并非二进制而是 Typora 导出的教学 PDF（IDA Pro.pdf）。用 pdftotext/pypdf 提取第 3 页文本层得到末行 flag，并用 PDF 内容流 CID + 内嵌 OpenSans 子集的 TrueType 字形名逐字符复核（'vv' 为 GID 0x58 名为 v 的 12 点单轮廓字形，'w' 是 GID 0x59；'1' 为 GID 0x14 名为 one），确认不是 OCR/字体 cmap 造成的错觉。: [redacted] | Evidence: pdfinfo: 3 页, Producer Typora/Electron, 无 JavaScript/OpenAction, %%EOF 后无附加数据 ; pdftotext -layout 第 3 页最后一行: [redacted] ; pypdf visitor_text 在页面 3 (字体 /F5 = BAAAAA+OpenSans-Regular, tm=(62,2682)) 输出完全相同的字符串 ; 页面 3 内容流中该行是单个 Tj: <0027 0014 0050 0051 005D 0043 0041 0049 0013 0013 0046 0041 0052 0058 0058 0050 0047 ...>，CIDToGIDMap /Identity ; 内嵌子集 glyph 名序列: D one n o braceleft a underscore g zero zero d underscore p v v n e r underscore ... t o underscore one e a r n ...（GID 0x58='v' 12点单轮廓, GID 0x59='w' 29点, GID 0x14='one'） | Independently verified by deepseek/deepseek-flash, deepseek/deepseek-flash#verifier

## 验证步骤

1. 识别附件: file 显示为 PDF 1.7（Typora/Electron 生成），不是 ELF/PE，所以本关是读文档而非反汇编二进制。
2. 提取文本层: 运行 pdftotext -layout "/challenge/distfiles/IDA Pro.pdf" -，在第 3 页末尾出现 [redacted]。
3. 交叉验证提取器: 用 pypdf 的 extract_text(visitor_text=...) 逐 text-show 回调，确认同一字符串位于 /F5 (BAAAAA+OpenSans-Regular) 且在 tm=(62,2682)，排除了 pdftotext 单点错误。
4. 抗字体欺骗复核: 解压页面 3 的 Contents 流，取该行 <...> Tj 的 CID 列表；因 CIDToGIDMap 为 /Identity，CID 即 GID。再解析 /FontFile2 内嵌 OpenSans 子集（fontTools），得到该行 glyph 名为 D one n o braceleft a underscore g zero zero d underscore p v v n e r ... t o underscore one e a r n ...；'vv' 对应 GID 0x58（12 点单轮廓 v），真正 'w' 是 GID 0x59（29 点），'1earn' 首字符是 GID 0x14 'one' 而非 'l'。因此 PDF 字面值就是 pvvner / 1earn，flag 为首尾匹配该字面值的字符串。
5. 排查其它隐藏面: pdftotext -bbox 只有页面可见文字；pypdf 显示注释仅 /URI [redacted] /JavaScript、无 /OpenAction；二进制尾部无附加数据；内嵌截图 X23 只是 IDA 界面（main -> init_sandbox/init_io/vuln），无 flag，排除隐写/附加载荷。
6. 尝试在线验证: 连续调用 submit_flag 均因浏览器配方找不到 textarea[aria-label="Flag"] 而报错；手动 Playwright 打开 challenge_url 在未登录状态返回 'The requested resource does not exist'，/api/v1/auth/register|login 返回 403 HumanVerificationRequired，无法建立会话，因此平台确认不可得，结论基于附件字面证据。
