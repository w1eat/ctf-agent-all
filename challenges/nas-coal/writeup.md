# NAS coal 题解

- 分类：Forensics
- 确认方式：平台确认
- 复现状态：自动复现通过


## 题目信息

someone put coal in my gem collection :^(

## 解题原理

该题是 Forensics 类文档分析题：题目分发的 gem-collection.pptm 是带宏的 PowerPoint（OOXML/ZIP 容器），其中 ppt/vbaProject.bin 是一个 OLE 复合文档，内含名为 MediaCache 的 VBA 模块（Sub RefreshCache）。宏把一段硬编码的 Base64 字符串拼接成 powershell.exe -NoProfile -EncodedCommand 命令行（属于典型的 VBA 宏投递 PowerShell 载荷手法，即题面所说的“coal”——混入宝石收藏中的煤块）。该 Base64 按 UTF-16LE 解码后即为 PowerShell 脚本，脚本中 $campaign 字段的值就是 flag。Slide 5 的文字提示 '>mfw olevba oneshot chall' 也印证了预期解法是用 olevba 一步提取解码。

## 关键步骤

1. 将 gem-collection.pptm 按 OOXML/ZIP 解析，定位到 ppt/vbaProject.bin，即题目描述中“混入的煤”对应的高危宏对象。
2. 对 ppt/vbaProject.bin 运行 olevba（或按 OLE 流手工提取），得到 VBA 宏 MediaCache.RefreshCache：其中 encoded 变量为一段 Base64，随后被拼接为 commandLine = "powershell.exe -NoProfile -EncodedCommand " & encoded 并 Debug.Print。
3. 取出该 Base64 字符串进行解码，解码结果需按 UTF-16LE 解释为 PowerShell 文本（宏中保存的正是 UTF-16LE 编码的 PowerShell）。
4. 在解码出的 PowerShell 中读取 $campaign 的赋值；该值 sun{yup_issa_gem} 即为 flag。脚本中另有 $source='https://gem-cache.example.invalid/coal.bin' 与 $destination='coal.bin'，属于诱饵/载荷下载路径，不是 flag。
5. 将 sun{yup_issa_gem} 提交至平台，提交页面返回 'Correct'，确认 flag 正确。

## EXP 与运行方法

文件：`exp/solve.py`

已保存的 EXP 为 exp/solve.py，用 Python 标准库 zipfile 直接读取 pptm 内的 ppt/vbaProject.bin，再用正则匹配长度 ≥100 的可打印 Base64 串，逐个 base64 解码并按 UTF-16LE 转字符串输出，最后用 re.search(r"sun\{[^}]+\}") 提取 flag。replay.status 为 verified：在全新沙箱中以 `cd /challenge/workspace && python3 solve.py` 运行，退出码 0，stdout 打印出解码后的 PowerShell（含 $campaign = 'sun{yup_issa_gem}'）以及 `FLAG: sun{yup_issa_gem}`，与记录一致；因此该 EXP 已自动复现成功。若不便运行 Python，也可用等价的人工方式：解压 pptm，对 ppt/vbaProject.bin 执行 olevba，再手工 Base64 解码并按 UTF-16LE 转码读取 $campaign。

## 验证结果

全新沙箱运行成功，输出与记录的 Flag 一致。

运行命令：`cd /challenge/workspace && python3 solve.py`

证据：

- ppt/vbaProject.bin is an OLE with a single VBA module 'MediaCache' (Sub RefreshCache) containing a Base64 blob.
- olevba decoded macro: encoded = "JABj..." ; commandLine = "powershell.exe -NoProfile -EncodedCommand " & encoded ; Debug.Print commandLine
- Base64 decoded (UTF-16LE) => $campaign = 'sun{yup_issa_gem}' / $source = 'https://gem-cache.example.invalid/coal.bin' / $destination = 'coal.bin'
- Slide 5 text hint reads '>mfw olevba oneshot chall' confirming the intended olevba one-shot path.
- Platform submission page (2026.sunshinectf.org) returned alert 'Correct' for sun{yup_issa_gem}.

## Flag

`sun{yup_issa_gem}`

## 限制与备注

该解法依赖目标文件为 OOXML/ZIP 结构且宏位于 ppt/vbaProject.bin，且 Base64 串足够长（EXP 以 ≥100 字符为筛选阈值）并可按 UTF-16LE 成功解码；若宏被混淆、Base64 分片存储或改用其他编码/压缩方式，正则与直接解码可能失效，需要改用 olevba 等工具或人工分析。EXP 中写死了路径 /challenge/distfiles/gem-collection.pptm，换环境需修改路径。脚本仅提取第一个匹配 sun{...} 的字符串，若样本中存在多个诱饵 flag 可能误报。此外，本说明仅依据给定材料与已记录的回放结果，平台确认信息来自提供的提交记录，未在本次写作过程中重新联网验证。
