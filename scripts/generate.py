"""Independent Python preparation for the certificate producer (not the checker)."""
import itertools
from collections import Counter

def prepare(rows,t,v):
    k=len(rows[0])
    columns=list(itertools.combinations(range(k),t))
    if len(columns)>255: raise ValueError("certificate v1 supports <=255 column sets")
    unique=[[] for _ in rows]
    for i,cs in enumerate(columns):
        patterns=[tuple(r[c] for c in cs) for r in rows]
        counts=Counter(patterns)
        if len(counts)!=v**t:
            raise ValueError("input not a covering array")
        for r,p in enumerate(patterns):
            if counts[p]==1:unique[r].append(i)
    lines=[[len(rows),k,len(columns)],*rows,
           *([len(cs),*cs] for cs in columns),*([len(w),*w] for w in unique)]
    return "".join(" ".join(map(str,r))+"\n" for r in lines)
