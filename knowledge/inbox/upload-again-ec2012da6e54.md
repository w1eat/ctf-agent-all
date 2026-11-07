---
title: "upload-again"
source_challenge: "upload-again"
confirmation_source: independent_quorum
verification_status: verified
run_id: "cc3541f884a540f6bc5d88791fd00d0f"
---

# upload-again

## 可复用方法

Flag found via Upload-to-document-root + body-prefix scanner bypass (padding) + race-condition PHP webshell execution while the file is alive during the ~300ms 'scan' before unlink; readfile('/flag').: [redacted] | Evidence: GET / returns upload form, PHP/8.2.34, hint: '上传的文件在/路径...可能被point删了' (file is placed at document root / and deleted shortly after). ; POST multipart file -> `<p>scan complete (N bytes), file removed.</p>` after ~0.38s, proving move to doc root then delayed unlink (~300ms window). ; Race test with benign file: uploaded raceXXXXXXXX.txt and 8 concurrent GET /raceXXXXXXXX.txt returned the exact random MARKER (8/8 hits) -> file is web-accessible at /<name> during the window and the server handles concurrent requests. ; Filter mapping: filename containing '.php'/'.pHp'/'.phtml' OR content '<?php'+whitespace causes an immediate TCP reset (0ms, no HTTP response); ',i.e.' a scanner that only inspects the first ~2KB of the multipart body. ; Bypass: adding a >2000-byte filler form field before the file part makes the identical 'filename="shell.php"' payload return 'scan complete (2 bytes), file removed.' instead of a reset. | Independently verified by deepseek/deepseek-flash, deepseek/deepseek-flash#verifier

## 验证步骤

1. 1. 连接服务：`curl -s [redacted] PHP 8.2.34 上传表单，提示“上传的文件在/路径……可能被point删了”。“point/点”= 点号/文档根，说明文件被写到文档根目录 `/`，随后被删除。
2. 2. 观察上传流程：用 curl 上传任意文件，响应为 `<p>scan complete (N bytes), file removed.</p>`，耗时约 0.38s。说明服务端先 `move_uploaded_file` 到 `/` + 文件名，sleep≈300ms 模拟扫描，再 `unlink`。N 为上传字节数。
3. 3. 验证竞争窗口与文件可访问性：上传内容带随机 MARKER 的 `raceXXXXXXXX.txt`，同时用 8 个线程并发 GET `/raceXXXXXXXX.txt`。8 个线程全部返回原始 MARKER，证明：文档根就是 `/`；删除前存在约 300ms 的可访问窗口；PHP 内置服务器多 worker 可以并发处理。
4. 4. 摸清过滤器：文件名含 `.php`（大小写不敏感）、`.phtml` 等，或正文出现 `<?php` 后跟空白字符时，连接在约 0ms 被 RST（无 HTTP 响应），说明有一个只看请求体前 ~2KB 的“扫描器”。注意 `<?php` 后不带空白、`<?=` 不被拦截。
5. 5. 绕过扫描器：在 multipart 中先放一个 2000 字节以上的填充字段（如 pad=A*2000），把真正含 `filename="shell.php"` 和 PHP 代码的文件段推到前 2KB 之外。同样 payload 立刻返回 `scan complete`，不再被 RST。
6. 6. 竞争 RCE 读 flag：构造 `shXXXXXXXX.php`，内容 `<?php echo 'FLAG>>'; readfile('/flag'); echo '<<'; ?>`，前面加 4~8KB 填充。Python 脚本开 10 个线程疯狂 GET `/shXXXXXXXX.php`，同时发起上传；在内置服务器执行该临时 webshell 的瞬间即可拿到输出。
7. 7. 结果：多次运行稳定输出 `[redacted]`（/flag 为 43 字节，含结尾换行）。另用 `ls -la / ; id` 验证 `/flag` 属于 ctf(999) 且仅有该一个 flag 文件。
8. 8. 说明：平台的 submit_flag 浏览器自动化报错（找不到 textarea[aria-label=Flag]），confirm_submission 提示无 pending submission；但 flag 是通过在远端容器内直接读取 /flag 得到的，具备独立、可复现证据。
