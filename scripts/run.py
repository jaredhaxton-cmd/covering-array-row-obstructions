#!/usr/bin/env python3
"""Offline reproduction and certificate verification, Python >=3.9 and C++17."""
import argparse, gzip, hashlib, itertools, json, os, pathlib, shlex, shutil, subprocess, sys, tempfile

from generate import prepare
ROOT=pathlib.Path(__file__).resolve().parents[1]
MANIFEST=json.loads((ROOT/'data/inputs.json').read_text())
DEFAULT_INPUTS=ROOT.parent/'verification-inputs'
if not DEFAULT_INPUTS.is_dir(): DEFAULT_INPUTS=ROOT/'data'

def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def compile_code(folder, name):
    exe=folder/(name+('.exe' if os.name=='nt' else ''))
    command=shlex.split(os.environ.get('CXX','g++'))+['-std=c++17','-O3','-Wall','-Wextra','-Wpedantic',str(ROOT/'src'/f'{name}.cpp'),'-o',str(exe)]
    subprocess.run(command,check=True)
    return exe

def read_rows(path,n,k,v):
    rows=[list(map(int,l.split())) for l in path.read_text().splitlines() if l.strip()]
    if len(rows)!=n or any(len(r)!=k or any(not 0<=s<v for s in r) for r in rows):
        raise ValueError(f'invalid array shape/symbols: {path}')
    return rows

def headered(folder, rows,t,v):
    p=folder/'array.txt'
    p.write_text(f'{len(rows)} {len(rows[0])} {t} {v}\n'+''.join(' '.join(map(str,r))+'\n' for r in rows))
    return p

def invoke(exe,*args,input=None,success=True):
    res=subprocess.run([str(exe),*map(str,args)],input=input,text=True,capture_output=True)
    if (res.returncode==0)!=success:
        raise RuntimeError(f'unexpected process exit={res.returncode}\n{res.stdout}{res.stderr}')
    return res.stdout+res.stderr

def fields(log):
    return {line.split('=')[0]:line.split('=')[1] for line in log.split() if '=' in line}

def gen(exe,rows,t,v,raw):
    print(invoke(exe,raw,input=prepare(rows,t,v)),end='',flush=True)

def check(exe,hdr,raw,expected,strict=True):
    result=invoke(exe,hdr,raw,*([] if strict else ['--allow-unresolved']))
    print(result,end='',flush=True)
    f=fields(result)
    if int(f['triples'])!=expected: raise ValueError('wrong deletion-triple census')
    if strict and (int(f['verified'])!=expected or int(f['unresolved'])!=0): raise ValueError('incomplete strict verification')
    return f

def full(args,folder,gen_exe,verify_exe):
    for item in MANIFEST:
        if args.target and item['id']!=args.target:continue
        print(f"\n{item['id']} {item['filename']}",flush=True)
        p=args.inputs/item['filename']
        if not p.is_file(): raise FileNotFoundError(f"Missing pinned input: {p}. See data/README.md.")
        if digest(p)!=item['sha256']: raise ValueError(f"SHA-256 mismatch for {p}; exact archived row order and bytes required")
        rows=read_rows(p,item['n'],item['k'],item['v'])
        hdr=headered(folder,rows,item['t'],item['v'])
        raw=folder/'certificate.bin'; expected=item['expected_triples']
        gz=ROOT/'certificates'/f"{item['id']}.tri3.gz"
        if args.command=='regenerate':
            gen(gen_exe,rows,item['t'],item['v'],raw)
            if args.write_baseline:
                with open(raw,'rb') as src, open(gz,'wb') as out, gzip.GzipFile(filename='',fileobj=out,mode='wb',mtime=0,compresslevel=9) as dest:
                    shutil.copyfileobj(src,dest)
            else:
                with gzip.open(gz,'rb') as src, open(raw,'rb') as actual:
                    while True:
                        x,y=src.read(1024*1024),actual.read(1024*1024)
                        if x!=y:raise ValueError("regenerated witnesses differ from baseline")
                        if not x:break
                print('regenerated certificate matches bundled bytes',flush=True)
        else:
            if not gz.exists():raise FileNotFoundError(gz)
            with gzip.open(gz,'rb') as src,open(raw,'wb') as dest:shutil.copyfileobj(src,dest)
        if raw.stat().st_size!=3*expected:raise ValueError('wrong certificate length')
        result=check(verify_exe,hdr,raw,expected)
        if int(result['distinct_rows'])!=item['n'] or int(result['all_columns_rows'])!=item['n']: raise ValueError('2-to-1 corollary conditions failed')
        print(f"2-to-1 corollary: all {item['n']*(item['n']-1)//2} pairs excluded")
        print(f"raw SHA256 {digest(raw)}; gzip SHA256 {digest(gz)}; gzip bytes {gz.stat().st_size}",flush=True)

def covered(rows,t,v):
    k=len(rows[0])
    return all(len({tuple(r[c] for c in cs) for r in rows})==v**t for cs in itertools.combinations(range(k),t))

def brute_repair(rows,t,v,triple):
    remaining=[r for i,r in enumerate(rows) if i not in triple]
    candidates=list(itertools.product(range(v),repeat=len(rows[0])))
    return any(covered(remaining+[a,b],t,v) for a,b in itertools.combinations_with_replacement(candidates,2))

def tests(folder,producer,checker):
    raw=folder/'test.bin'
    # All triples are genuinely unrepairable: 4 rows, 2 columns, binary strength 2.
    cases=[('unrepairable',[[0,0],[0,1],[1,0],[1,1]],2,2,4),
           ('repairable',[[0,0],[1,1],[0,1]],1,2,0),
           ('redundant',[[0,0],[0,1],[1,1],[1,0]],1,2,0)]
    for label,rows,t,v,expect in cases:
        print('control:',label,flush=True)
        hdr=headered(folder,rows,t,v)
        gen(producer,rows,t,v,raw)
        tr=list(itertools.combinations(range(len(rows)),3))
        r=check(checker,hdr,raw,len(tr),False)
        assert int(r['verified'])==expect
        for i,triple in enumerate(tr):
            witness=raw.read_bytes()[i*3:(i+1)*3]
            feasible=brute_repair(rows,t,v,triple)
            assert feasible==(witness==b'\xff'*3), (label,triple,feasible,witness)
        if expect:
            orig=raw.read_bytes()
            raw.write_bytes(bytes([254,orig[1],orig[2]])+orig[3:])
            invoke(checker,hdr,raw,success=False)
            raw.write_bytes(orig[:-1]);invoke(checker,hdr,raw,success=False)
            raw.write_bytes(orig+b'\0');invoke(checker,hdr,raw,success=False)
        else:
            invoke(checker,hdr,raw,success=False)
    # Three genuine singleton witnesses that do NOT conflict. Reject both a
    # correct singleton ID with a missing conflict edge and an in-range non-singleton ID.
    rows=[[1,0,0],[0,1,0],[0,0,1]]
    hdr=headered(folder,rows,1,2)
    raw.write_bytes(bytes([0,1,2]))
    assert 'missing conflict edge' in invoke(checker,hdr,raw,success=False)
    raw.write_bytes(bytes([1,1,2]))
    assert 'invalid singleton witness' in invoke(checker,hdr,raw,success=False)

    # Independently found counterexample to an unsafe completeness assumption:
    # a covering array and deletion triple with no singleton triangle but no
    # two-row repair either. Check every triple against direct enumeration.
    rows=[[0,0,0,0],[0,0,0,1],[0,0,1,0],[0,1,1,1],[1,0,1,1],[1,1,0,0]]
    hdr=headered(folder,rows,2,2)
    gen(producer,rows,2,2,raw)
    tr=list(itertools.combinations(range(len(rows)),3))
    check(checker,hdr,raw,len(tr),False)
    cert=raw.read_bytes()
    for i,tri in enumerate(tr):
        if cert[3*i:3*i+3]!=b'\xff'*3:
            assert not brute_repair(rows,2,2,tri)
    i=tr.index((1,3,4))
    assert cert[3*i:3*i+3]==b'\xff'*3
    assert not brute_repair(rows,2,2,(1,3,4))
    print('Incompleteness control passed: unresolved triple (1,3,4) is independently brute-force UNSAT.')
    bad=[[0,0],[0,1],[1,0]]
    hdr=headered(folder,bad,2,2)
    raw.write_bytes(b'\xff'*3);invoke(checker,hdr,raw,'--allow-unresolved',success=False)
    try: prepare(bad,2,2)
    except ValueError: pass
    else: raise AssertionError('producer failed to reject non-covering input')
    # Triangle-free obstruction possible in general; a marker means unproven,
    # not repairable. The tiny cases above happen to have exact decisions.
    print('All controls passed (brute-force repair, invalid witness IDs, missing edges, corrupt/truncated/extra certificate, unresolved strict rejection, invalid source, unresolved-but-UNSAT example).')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['verify','regenerate','test'])
    parser.add_argument('--inputs',type=pathlib.Path,default=DEFAULT_INPUTS)
    parser.add_argument('--target',choices=['Q9','Q10'])
    parser.add_argument('--write-baseline',action='store_true',help='maintainer only: replace checked-in certificate files instead of comparing')
    args=parser.parse_args()
    if args.write_baseline and args.command!='regenerate':parser.error('--write-baseline requires regenerate')
    with tempfile.TemporaryDirectory(prefix='lattice-forge-') as tmp:
        folder=pathlib.Path(tmp); checker=compile_code(folder,'verify')
        producer=compile_code(folder,'generate') if args.command in ('regenerate','test') else None
        if args.command=='test': tests(folder,producer,checker)
        else: full(args,folder,producer,checker)

if __name__=='__main__': main()
