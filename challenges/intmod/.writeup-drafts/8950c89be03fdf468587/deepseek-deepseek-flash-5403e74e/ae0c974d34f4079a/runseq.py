import subprocess, os, re
M=(1<<64)-1
def rol(v,c):
    c%=64; return ((v<<c)|(v>>(64-c)))&M if c else v&M
def get_states(inpbytes):
    open('/tmp/in.bin','wb').write(inpbytes)
    subprocess.run(['./tracer'],timeout=120)
    lines=open('/tmp/ptrace.log').read().splitlines()
    stops=[]
    for l in lines:
        if 'EXIT' in l or 'KILLED' in l or 'LIMIT' in l: continue
        m=re.match(r'(\d+) RIP=([0-9a-f]+) sig=(\d+)',l)
        rip=int(m.group(2),16)
        if 0x400000<=rip<0x405000:
            d=dict(re.findall(r'(\w+)=([0-9a-f]+)',l))
            regs=[int(d['r8'],16),int(d['r9'],16),int(d['r10'],16),int(d['r11'],16),int(d['r12'],16),int(d['r13'],16),int(d['r14'],16)]
            stops.append((rip,regs))
    return stops
def allfits(s,t,n=7):
    res=set()
    for a in range(n):
        for b in range(n):
            if a==b: continue
            for c in range(64):
                r=rol(s[b],c)
                if (s[a]+r)&M==t[a]:
                    tt=list(s); tt[a]=(tt[a]+r)&M
                    if tt==t: res.add(('addrol',a,b,c))
                if (s[a]^r)==t[a]:
                    tt=list(s); tt[a]^=r
                    if tt==t: res.add(('xorrol',a,b,c))
    for a in range(n):
        for c in range(64):
            if rol(s[a],c)==t[a]:
                tt=list(s); tt[a]=rol(tt[a],c)
                if tt==t: res.add(('rol',a,c))
    for a in range(n):
        for b in range(n):
            if a!=b:
                tt=list(s); tt[a],tt[b]=tt[b],tt[a]
                if tt==t: res.add(('swap',a,b))
    for a in range(n):
        if s[a]&1:
            K=(t[a]*pow(s[a],-1,1<<64))&M
            tt=list(s); tt[a]=(tt[a]*K)&M
            if tt==t: res.add(('mul',a,K))
    return res
inputs=[b'A'*33, b'B'*33, b'\xff'*33, bytes(range(33))]
seqs=[]
for inp in inputs:
    st=get_states(inp)
    seqs.append(st)
    print("input",inp[:4],"stops",len(st), "first RIPs", [hex(s[0]) for s in st[:6]])
import pickle
pickle.dump(seqs,open('/tmp/seqs.pkl','wb'))
