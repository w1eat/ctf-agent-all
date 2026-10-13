# You Are Kidding Me 题解

- 分类：web
- 确认方式：平台确认
- 复现状态：自动复现通过


## 题目信息

Ever wanted to read up on the cars of the future? We got a blog for that!

## 解题原理

题目是一个 Flask 博客站点，其鉴权使用 HS256 签名的 JWT。服务端在处理 /admin 请求时，会把 JWT header 中的 `kid` 字段当作密钥文件名，使用 os.path.join('/app/keys', kid) 拼接路径加载该文件；由于未对 kid 做路径穿越过滤，攻击者可以把 kid 设为任意路径（如 /etc/passwd、/app/app.py），只要解析后的路径不在保护名单内，服务端就会把文件内容回显在 /admin 的调试 “Pass Inspector” 面板中，形成路径穿越导致的信息泄露。进一步地，泄露的 /app/app.py 源码中硬编码了编辑器签名密钥 EDITOR_KEY，而 is_protected() 只屏蔽 reader.key、editor.key 和 flag.txt 三个文件，因此攻击者可以拿到该密钥后自行伪造 role=editor 的 JWT，通过 /admin 的权限校验读取 flag。

## 关键步骤

1. 访问 /login，以 name=reader 登录，获取服务端签发的 HS256 JWT，观察其 header 中携带 kid=reader.key。
2. 构造伪造 token 请求 /admin，把 JWT header 的 kid 改为路径穿越值来读取文件：kid=/etc/passwd 验证穿越可行，kid=/app/app.py 读取 Flask 源码。服务端通过 os.path.join('/app/keys', kid) 解析路径，未受保护的路径会把文件内容回显到 “Pass Inspector” 调试面板（kid=/app/app.py 时返回 HTTP 401，但响应体中已泄露源码）。
3. 从泄露的 /app/app.py 中提取硬编码的编辑器签名密钥 EDITOR_KEY = b'ch-pr0t0type-edit0r-s1gn1ng-k3y-d0-n0t-sh1p'，并确认 is_protected() 只屏蔽 reader.key、editor.key 和 flag.txt。
4. 使用泄露的密钥自行签发 HS256 JWT：header 为 {alg:HS256, kid:editor.key, typ:JWT}，payload 为 {sub:reader, role:editor}，按 HMAC-SHA256 计算签名。
5. 携带该伪造 token 请求 GET /admin，服务端校验签名通过且认定 role=editor，返回 HTTP 200，响应体包含 flag：sun{h0tw1r3d_4dm1n_jwt}。

## EXP 与运行方法

文件：`exp/solve.py`

已保存 EXP 为 exp/solve.py，可直接执行：cd /challenge/workspace && python3 solve.py。脚本自身完成全部利用逻辑：用硬编码的编辑器密钥对 header {alg:HS256, kid:editor.key, typ:JWT} 和 payload {sub:reader, role:editor} 做 base64url 编码并计算 HMAC-SHA256 签名，拼接成 JWT；随后以该 token 作为 cookie 请求 https://kidding.web.2026.sunshinectf.games/admin，打印 HTTP 状态码并用正则从响应体中提取 sun{...} 形式的 flag。该 EXP 已在新沙箱中运行成功（replay.status=verified，退出码 0，输出 200 与 ['sun{h0tw1r3d_4dm1n_jwt}']），确认可自动复现。

## 验证结果

全新沙箱运行成功，输出与记录的 Flag 一致。

运行命令：`cd /challenge/workspace && python3 solve.py`

证据：

- /login issues a JWT with header kid=reader.key, HS256 (observed Set-Cookie token=[已脱敏]]
- /admin loads the file named in the JWT `kid` header via os.path.join('/app/keys', kid) and, when the resolved path is not protected, dumps the file contents in the debug 'Pass Inspector' panel.
- GET /admin with kid=/etc/passwd dumped /etc/passwd contents; kid=/app/app.py dumped the Flask source (confirmed reachable at GET /admin, HTTP 401 with disclosed body).
- The dumped /app/app.py hardcodes EDITOR_KEY = b'ch-pr0t0type-edit0r-s1gn1ng-k3y-d0-n0t-sh1p' and reveals is_protected() only withholds the two key files and flag.txt.
- Forged HS256 JWT: header {alg:HS256,kid:editor.key}, payload {sub:reader,role:editor}, signed with the leaked editor key -> GET /admin returns HTTP 200 with body containing sun{h0tw1r3d_4dm1n_jwt}.
- Platform submission page displayed alert 'Correct'.

## Flag

`sun{h0tw1r3d_4dm1n_jwt}`

## 限制与备注

利用依赖以下几个条件同时成立：服务端确实把 JWT header 的 kid 字段拼接到 /app/keys 下做文件读取，且路径穿越未被过滤；被读取的文件解析后不在 is_protected() 保护名单内；/app/app.py 中硬编码了可用的 EDITOR_KEY；服务端接受自行签发的 HS256 token 且 payload 中的 role=editor 能通过 /admin 权限校验。若目标部署改变了密钥管理方式（如改为从环境变量读取密钥）、修补了 kid 路径穿越、或调整了 is_protected() 与角色校验逻辑，该 EXP 将失效。EXP 中硬编码了目标域名与签名密钥，换环境需相应修改。Flag 已由平台确认（confirmation_source=platform_confirmed，提交页面显示 Correct），不属于未验证候选值。
