# you cut me off 题解

- 分类：Forensics
- 确认方式：平台确认
- 复现状态：待检查


## 题目信息

Here's a flag! It's uhhh ....... .............. .....................uhhhhhhhhh......................... hmm..

## 解题原理

本题为 Forensics 中的 PNG 结构篡改题。PNG 文件 IHDR 中声明图像高为 382 行，但全部 IDAT 数据拼接后经 zlib 解压得到 823042 字节，按每行步长 (宽度492 × 4通道 + 1 滤波字节) = 1969 字节计算，实际包含 418 行像素数据（823042 == 418 × 1969），即比声明高度多出 36 行。正常解码器只按 IHDR 声明的 382 行渲染，裁掉的下方 36 行因此不可见（呼应题名 you cut me off）。需要绕过解码器的裁剪，手动重建全部 418 行才能看到隐藏在底部的 Discord 输入框及其中的 flag。

## 关键步骤

1. 用 file/pngcheck 检查附件：其为 492x382 RGBA PNG，仅含 IHDR/sRGB/gAMA/pHYs/IDAT/IEND 等标准 chunk，没有文本块，alpha 全为 255，LSB 位平面为空，排除常见隐写方向。
2. 解析 PNG chunk，收集全部 IDAT 数据并拼接后做 zlib 解压，得到 823042 字节原始滤波数据。
3. 按行宽 (492*4+1)=1969 计算真实行数：823042 / 1969 = 418 行，而 IHDR 只声明 382 行，说明图片下方 36 行被截掉隐藏。
4. 按 PNG 滤波规则 0..4 对全部 418 行逐行反滤波，重建 492x418 的完整 RGBA 图像；用已声明高度之前的行作为 Filter 2/3/4 所需的 prev 行参考。
5. 导出完整重建图 full.png，并裁出被隐藏的底部 36 行放大（2 倍）保存为 hidden_rows.png。
6. 在放大后的隐藏区域中可看到 Discord 输入框，其中显示 flag：sun{totallyoriginalchallengeidea}（材料记录为 8x 放大确认）。
7. 解题脚本为 /challenge/workspace/solve.py，输出 /challenge/workspace/full.png 与 /challenge/workspace/hidden_rows.png。

## EXP 与运行方法

文件：`exp/solve.py`

已保存的 EXP 为 exp/solve.py，运行方式为 cd /challenge/workspace && python3 solve.py。脚本硬编码 SRC=/challenge/distfiles/hereyougo.png、W=492、DECLARED_H=382、STRIDE=492*4+1，流程为：遍历 PNG chunk 拼接全部 IDAT → zlib.decompress → 用 raw 长度整除 STRIDE 得到真实高度 418 → 对 418 行按滤波类型 0/1/2/3/4 依次反滤波（Filter 3/4 用纯 Python 循环实现）→ 用 PIL 保存 /challenge/workspace/full.png，并裁剪 y=382..418 的区域放大 2 倍保存为 hidden_rows.png。需注意 replay 状态为 needs_review：脚本退出码为 0，stdout 仅打印 "declared height: 382  true height: 418" 和 "hidden rows rendered -> hidden_rows.png ; flag shown in bottom chat box"，并未直接输出 flag，因此不能声称该 EXP 已自动复现出 flag；flag 值由平台确认（confirmation_source 为 platform_confirmed），EXP 的实际作用是把隐藏行渲染成图片，flag 仍需人工查看 hidden_rows.png 读出。

## 验证结果

EXP 运行失败或未输出记录的 Flag。

运行命令：`cd /challenge/workspace && python3 solve.py`

证据：

- file/pngcheck report 492x382 RGBA PNG with only IHDR/sRGB/gAMA/pHYs/IDAT/IEND chunks; no text chunks, alpha all 255, LSB bit planes empty.
- Decompressed IDAT length 823042 vs expected 382*(492*4+1)=752158; 823042 == 418*(492*4+1), so true height is 418px.
- Unfiltering all 418 scanlines and viewing hidden bottom 36 rows shows the Discord input box: sun{totallyoriginalchallengeidea} (confirmed at 8x zoom).
- Reconstructions saved: /challenge/workspace/full.png and /challenge/workspace/hidden_rows.png.

## Flag

`sun{totallyoriginalchallengeidea}`

## 限制与备注

1) EXP 依赖原题环境：需要 /challenge/distfiles/hereyougo.png 存在，并需要 numpy、Pillow 及可写目录 /challenge/workspace。2) 脚本硬编码宽度 492 与声明高度 382，换一份文件即失效。3) 脚本不做 OCR，不会自动打印 flag，只能生成 full.png 和 hidden_rows.png，flag 的读取依赖人工视觉确认，材料中的 "8x zoom 确认" 无法在本说明中独立复核。4) replay 状态为 needs_review，依据材料不能断言 EXP 已自动复现出记录的 flag；脚本虽退出码为 0，但 stdout 未包含 flag 字符串。5) Filter 3/4 的实现为逐字节 Python 循环，效率较低，若滤波数据或 prev 行参考有误，重建图像可能出错，脚本本身没有内置正确性校验。6) 依据现有证据无法确认隐藏内容之外的额外信息（如是否存在其他未声明的裁剪或更深层隐写）。
