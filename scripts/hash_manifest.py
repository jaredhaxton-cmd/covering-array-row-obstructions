#!/usr/bin/env python3
"""Regenerate repository integrity manifest (only after deliberate content changes)."""
import hashlib,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
paths=[]
for p in root.rglob('*'):
    if not p.is_file() or p.name=='SHA256SUMS.txt':continue
    rel=p.relative_to(root)
    if any(part in ('.git','__pycache__','build') for part in rel.parts) or p.suffix in ('.pyc','.bin','.exe'):continue
    paths.append(rel)
(root/'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256((root/p).read_bytes()).hexdigest()}  {p.as_posix()}\n' for p in sorted(paths,key=lambda p:p.as_posix())))
