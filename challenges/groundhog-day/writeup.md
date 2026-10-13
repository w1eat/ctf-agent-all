# Groundhog Day 题解

- 分类：web
- 确认方式：平台确认
- 复现状态：人工复现


## 题目信息

The Punxsutawney Orbital Weather Authority has been broadcasting the same forecast since 1993. Every reading is fresh. Every date is always the same.

## 解题原理

这是一个服务端 URL 抓取（SSRF）与内部报告生成器组合利用的场景。控制台页面提供 feed=<url> 参数，服务端会代替用户去抓取该 URL（/feed 的 JSON debug 注释回显 source=http://127.0.0.1:8000/feed bytes=351，说明抓取发生在服务端），因此该参数构成 SSRF 入口。借助 gopher:// 协议可以把任意原始 TCP 字节流（这里是完整的 HTTP 请求）发往内网 127.0.0.1:8000，从而访问外部不可达的内部 /report 报告生成端点。该端点接收 content/title 并生成 PDF，渲染过程会执行注入的 HTML/JS：脚本用 XHR 读取本地文件，把内容 base64 编码后以 ZB64START...ZB64END 标记写入 PDF。最后从 JSON 响应中取回 base64 的 PDF，用 pdftotext 提取文本并解码标记，即得到 Flag。题目名“土拨鼠日/每天都是同一天”与 gopher、日复一日不变的日期意象呼应。

## 关键步骤

1. 确认 SSRF 入口：向控制台页面传入 feed=<url> 参数，观察服务端替用户抓取该 URL（/feed 的 JSON debug 注释回显 source 与 bytes，表明抓取发生在服务端）。
2. 构造 gopher://127.0.0.1:8000/_<URL 编码的原始 HTTP 请求>，把请求经 SSRF 转发到内网 8000 端口，绕过外层 URL 抓取器的协议与目标限制。
3. 向内网 POST /report 提交 content 与 title，content 为一段 HTML/JS 载荷：脚本用同步 XMLHttpRequest 读取目标本地文件，把内容 base64 编码后以 ZB64START...ZB64END 包裹写入页面。
4. 服务端生成 PDF 并以 base64 放在 JSON 的 data 字段返回；脚本解码写出 out.pdf，再运行 pdftotext 得到文本。
5. 从文本中匹配 ZB64START(.*?)ZB64END，去掉非 base64 字符并补齐 padding 后解码，得到 Flag（如 out.txt 中 ZB64STARTc3Vue3MxeF9tMHIzX3czM2tzXzBmX2cwcGgzcl9zc3JmfQoAZB64END 解码为 sun{s1x_m0r3_w33ks_0f_g0ph3r_ssrf}）。
6. 提交该 Flag，平台返回 Correct，确认解答成功。

## EXP 与运行方法

文件：`exp/fileread.py`, `exp/wk.py`, `exp/out.txt`

附件包含三个文件：exp/fileread.py 可在命令行传入文件路径，内部通过 gopher() 把原始 HTTP 请求编码后作为 feed 参数发给目标站，再由 post_report() 向 127.0.0.1:8000/report 提交读文件的 HTML/JS 载荷，解码返回的 PDF base64 并调用 pdftotext，最后从 ZB64START/ZB64END 中解码出文件内容；exp/wk.py 封装了 build_post()/gen_pdf()/pdftext() 等函数，可把 stdin 的内容作为报告正文生成 PDF 并打印文本，用于调试渲染与提取；exp/out.txt 是已提取的输出，内含 ZB64STARTc3Vue3MxeF9tMHIzX3czM2tzXzBmX2cwcGgzcl9zc3JmfQoAZB64END。由于 replay.status 为 manual，这些脚本只能由人工按上述方式运行（例如先运行 fileread.py 读取目标路径，或先运行 wk.py 验证渲染），未由平台自动复现。

## 验证结果

提供的 EXP 运行命令不符合安全的单脚本格式，需人工复现。

证据：

- Console page exposes a feed=<url> parameter that the server fetches server-side (feed-debug comment echoed source=http://127.0.0.1:8000/feed bytes=351).
- gopher:// SSRF reached the internal report generator on 127.0.0.1:8000 POST /report and returned JSON with base64 PDF data.
- The rendered PDF embedded ZB64START...ZB64END containing c3Vue3MxeF9tMHIzX3czM2tzXzBmX2cwcGgzcl9zc3JmfQoA which decodes to sun{s1x_m0r3_w33ks_0f_g0ph3r_ssrf}.
- Submission of sun{s1x_m0r3_w33ks_0f_g0ph3r_ssrf} returned Correct on the SunshineCTF challenge page.

## Flag

`sun{s1x_m0r3_w33ks_0f_g0ph3r_ssrf}`

## 限制与备注

replay.status 为 manual，材料中 replay.command 为空、无 exit_code/stdout，因此不能声称 EXP 已自动复现，只能给出人工执行方式。脚本依赖多个外部条件：目标站 https://odyssey.web.2026.sunshinectf.games 可达、内网 127.0.0.1:8000 存在 /report 且在 PDF 渲染时执行 JS、系统安装 pdftotext（wk.py 还用到 pdfinfo）、脚本中写的 /challenge/workspace 输出目录存在且可写。文件读取依赖渲染环境的 JS/XHR 能力与目标路径，具体读取的本地文件路径在材料中未给出，需人工确定。confirmation_source 为 platform_confirmed 且证据显示提交返回 Correct，故 Flag 可视为已确认；但若更换环境，端口、路径与渲染行为可能不同，需要重新验证。
