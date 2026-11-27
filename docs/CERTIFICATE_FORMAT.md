# TRI3 v1 certificate format

The manifest in `data/inputs.json` pins the required source array. All indices are zero-based. No solver-specific proof format is needed.

For an N-row input and specified strength t, enumerate all t-element subsets of the k columns lexicographically, and number them 0 through C(k,t)-1. TRI3 v1 supports at most 255 such subsets, so 255 is not a valid column-subset index.

For every triple of row indices (x,y,z), x<y<z, in lexicographic order, the raw stream stores exactly three unsigned bytes:

- byte 0: column-subset index of a singleton interaction in row x
- byte 1: column-subset index of a singleton interaction in row y
- byte 2: column-subset index of a singleton interaction in row z

The symbols are recovered from the respective rows of the pinned source array. The triple of bytes 255,255,255 is reserved for **unresolved**; it is forbidden in strict verification. Partial use of 255 is invalid. A triangle-free instance may still be impossible to repair; an unresolved marker simply means this producer did not find a singleton triangle.

The index order is equivalent to three nested loops:

```python
for x in range(N):
    for y in range(x+1,N):
        for z in range(y+1,N):
            # read exactly three bytes
```

Raw length must be exactly 3*C(N,3). The gzip files contain no application-specific metadata and are compressed versions of the raw byte streams. All certificate content is independently checked, not merely checksummed.

| Target | Raw bytes | Gzip bytes |
|---|---:|---:|
| Q9 | 21,437,325 | 2,718,561 |
| Q10 | 19,478,940 | 1,758,218 |
| Total | 40,916,265 | 4,476,779 |

The checker computes full array coverage, reconstructs the exact occurrence count for every interaction, confirms that each designated interaction occurs exactly once in the source, and tests each of the three conflict edges. It handles stream exhaustion and rejects trailing data. It does not run the producer or assume its counters are correct.

A witness is independently checkable by hand: identify its row and chosen t columns, count matching source rows (must be one), then compare each pair of patterns for a shared column with different required symbols.
