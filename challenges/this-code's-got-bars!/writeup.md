# This Code's Got Bars! 题解

- 分类：BSides Orlando
- 确认方式：平台确认
- 复现状态：人工复现


## 题目信息

1-Dimensional and Patented! (barcode challenge). HARDWARE/on-site challenge: likely a 1-D barcode printed on the BSides Orlando 2026 badge or at the venue. REMOTE-ATTEMPT GUIDANCE: search for published badge artwork/design files or high-resolution photos of the badge and any barcode on it, then decode with zbarimg/dcode (try Code39, Code128, UPC, POSTNET, ITF). Also try the badge's PCB silkscreen. Flag format sun{...}.

## 解题原理

本题是一道线下/硬件向的 1-D 条码（barcode）题，题名 "This Code's Got Bars!" 与 "1-Dimensional" 暗示 flag 被编码为一条一维条码，而不是藏在二进制程序或网页逻辑里。官方预期是在 BSides Orlando 2026 徽章本体或现场印刷物上找到条码再扫描解码；由于徽章的硬件设计文件被公开发布，可以改用 OSINT 路线：从公开仓库取得徽章设计文件，定位其中的条码图层并做条码解码，从而在不接触实物徽章的情况下得到明文 flag。

## 关键步骤

1. 在 GitHub 上搜索 BSides Orlando 2026 徽章（badge），发现公开仓库 badge-gallery/bsidesorlando-2026，其中包含徽章硬件设计文件（KiCad / PSD）。
2. 克隆该仓库，并按 flag 格式对全仓库做 grep（如 `grep -rao 'sun{[^}]*}' .`），在 hardware/uv_art.psd 中命中字符串 sun{ctf_r_4_h00m4n5}。
3. 用 psd-tools 枚举 uv_art.psd 的图层，得到 'bsbadgeE'、'sun{ctf_r_4_h00m4n5}.png'、'Copper Layer'、'LED Locations' 等图层；其中目标图层包围盒为 1191,1153–1856,1281，宽而扁，符合一维条码的形状特征。
4. 导出该图层（665x128）为 layer_bars.png，并把透明底合成到白底，得到 layer_bars_flat.png，以便条码解码器正确识别前景/背景对比。
5. 用 zbarimg 解码：`zbarimg -q --raw layer_bars_flat.png` 输出 sun{ctf_r_4_h00m4n5}；`zbarimg layer_bars_flat.png` 明确报告符号类型为 CODE-128，即一维条码，与题目 "1-Dimensional / got bars" 的描述吻合。
6. 解码结果与图层文件名中的 flag 字符串一致，提交后平台确认该题为正确（Solved）。

## EXP 与运行方法

文件：无

本题未保存任何 EXP 脚本（exp_files 为空），replay.status 为 manual，因此无法自动复现，只能按上述步骤人工复现：git clone 公开徽章仓库 badge-gallery/bsidesorlando-2026 → 全仓库 grep 提取 sun{...} 字符串 → 用 psd-tools 列出 uv_art.psd 图层并导出条码图层 → 将透明图层合成到白底 → 运行 zbarimg 对该 PNG 做 CODE-128 解码读取 flag。所需工具为 git、grep、psd-tools（Python）、zbarimg（zbar 工具集）。

## 验证结果

没有可自动运行的 EXP；请按题解步骤人工复现。

证据：

- Browser evidence shows modal alert "Correct" for This Code's Got Bars! (challenge id 21), card now marked "✦ Solved" with solve count 44, and overall counter advanced to 23/37 SOLVED. Flag was independently derived by the solver from the public BSides Orlando 2026 badge repo (zbarimg CODE-128 decode of the uv_art.psd barcode layer).

## Flag

`sun{ctf_r_4_h00m4n5}`

## 限制与备注

复现高度依赖两个外部前提：其一，徽章设计仓库 badge-gallery/bsidesorlando-2026 必须保持公开可访问，若仓库被删除或转为私有则 OSINT 路线失效；其二，需要可用的 psd-tools 与 zbarimg 环境，且 PSD 图层必须正确导出并做白底合成才能被 zbarimg 稳定识别。此外，拿到的 flag 来自公开设计文件而非现场实物徽章，属于对官方意图的非预期等价路径；本材料中该 flag 已经平台确认（confirmation_source 为 platform_confirmed），故可视为已验证答案，但如果没有平台该确认信息，单凭 zbarimg 输出不足以断言提交会被接受。本材料未提供 EXP 脚本，也未给出任何自动复现记录，因此不能声称 EXP 已自动复现。
