#!/usr/bin/env python3
"""Normalize a separately obtained upstream array ONLY if the pinned SHA-256 matches."""
import argparse, hashlib, json, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('target',choices=['Q9','Q10'])
p.add_argument('source',type=pathlib.Path)
p.add_argument('output_dir',type=pathlib.Path)
args=p.parse_args()
m=next(x for x in json.loads((ROOT/'data/inputs.json').read_text()) if x['id']==args.target)
lines=[line.strip() for line in args.source.read_text(encoding='utf-8-sig').splitlines() if line.strip()]
n,k,v=m['n'],m['k'],m['v']
for skip in (0,1):
    try:
        rows=[[int(x) for x in re.split(r'[\s,]+',line)] for line in lines[skip:]]
    except ValueError:continue
    if len(rows)!=n or any(len(r)!=k for r in rows):continue
    for offset in (0,1):
        if any(not 0<=s-offset<v for r in rows for s in r):continue
        # Canonical archived form: one space between entries, one LF after every row.
        data=''.join(' '.join(str(s-offset) for s in r)+'\n' for r in rows).encode()
        if hashlib.sha256(data).hexdigest()!=m['sha256']:continue
        args.output_dir.mkdir(parents=True,exist_ok=True)
        path=args.output_dir/m['filename']
        if path.exists() and path.read_bytes()!=data: raise SystemExit(f'Refusing to overwrite different file {path}')
        path.write_bytes(data)
        print(f'Exact pinned input reproduced: {path}')
        raise SystemExit(0)
raise SystemExit('No exact SHA-256 match; no file written. Check source/version and ordering.')
