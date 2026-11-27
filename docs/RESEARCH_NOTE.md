# Research note: three-interaction certificates of local irreducibility

**Research direction:** Jared Haxton, Projects Lattice & Forge  
**Date:** 2026-11-26, America/Phoenix  
**Status:** computational result; independently adjudicated by Project Forge (Muse) on 2026-11-26 — all claims confirmed; published with owner authorization

## Abstract

We study exact row-replacement neighborhoods of two previously constructed covering arrays, CA(351;5,7,3) and CA(340;4,6,4). For each unordered triple of removed rows, we exhibit a triangle in the incompatibility graph of residual uncovered interactions, using only interactions that were covered exactly once in the source array. This triangle is a certificate that two replacement rows cannot restore coverage. Exhaustive enumeration produces 7,145,775 and 6,492,980 certificates, respectively, with no unresolved triple. We also verify that every source row's singleton interactions collectively involve every column, proving impossibility of 1-to-0 and 2-to-1 reductions. These are local irreducibility results for exact, hash-pinned arrays, not global lower bounds. A deterministic producer and separate certificate checker are provided.

## Definitions and prior literature

A homogeneous CA(N;t,k,v) is an N-by-k array over symbols 0,...,v-1 such that for every t-element column subset, every v^t assignment occurs in at least one row.

An interaction specifies a t-element column set and one symbol in each of those columns. Two interactions conflict when their column sets intersect at a position where they require different symbols. A set of interactions with no conflicting pair can be extended to one full row: for every mentioned column, all required symbols agree, and unmentioned columns can be filled arbitrarily.

The incompatibility graph of interactions not covered by a fixed row set therefore has chromatic number equal to the minimum number of additional rows needed to cover those interactions (the empty graph needs zero). The forward direction assigns each missing interaction to a row that covers it; the reverse direction merges each independent color class into a consistent row. This established formulation is explicitly described in Sarkar and Colbourn (2019), §3.3 of its preprint arXiv:1606.06730. It is not a novelty claim of this work.

A singleton witness of row r is an interaction exhibited by r and no other row of the original array. The use of only singleton witnesses gives a sufficient obstruction test: removing a set of rows may also uncover interactions with multiple original occurrences, but ignoring them can only weaken, not invalidate, a certificate of impossibility.

## Proposition 1: singleton triangle obstruction

Let A be any covering array. Let x, y and z be distinct row indices. Suppose there exist interactions I_x, I_y and I_z, each uniquely exhibited by its designated row in A, and suppose all three pairs conflict.

Then no array obtained by removing x, y and z and inserting two arbitrary full rows can cover all the required interactions.

**Proof.** Removing the three rows uncovers all three designated interactions, because each has exactly one original occurrence. No remaining row covers any of them. A replacement row cannot exhibit any conflicting pair. Since the three interactions conflict pairwise, one replacement row covers at most one. Two replacement rows cover at most two of the three. At least one required interaction remains missing. QED.

The certificate stores the one column-subset index needed to reconstruct each interaction from its original row. The three interactions, their uniqueness, and the three conflict edges can all be checked directly without searching replacement rows.

### Shared-column certificate

A sufficient special case occurs when the three rows have different symbols at one column j and each has a singleton interaction involving j. Selecting those three interactions gives a triangle. The generator checks this explicitly, then searches other three-witness combinations when no such shared-column certificate is found. The checker does not trust which path the generator took and verifies the actual three interaction pairs.

## Proposition 2: 1-to-0 and 2-to-1 obstruction

If each row in A has some singleton witness then deleting any one row without replacement uncovers an interaction.

More strongly, assume the union of the column sets of the singleton witnesses of each row covers all k columns, and the rows of A are distinct. Any one replacement row covering all singleton witnesses of a deleted row r must equal r coordinate-by-coordinate. If two distinct rows x and y are removed, a replacement row has to cover every singleton witness of both x and y, so it must equal both rows, a contradiction.

Therefore no pair of rows can be replaced by one. QED.

The checker directly counts distinct rows and the number of rows whose singleton-witness column union equals the full column set. Both predicates hold for the exact source arrays.

## Computational method

1. Preserve the input arrays from the Lattice D0007 archives, including row/column ordering, zero-based symbols and SHA-256.
2. Enumerate all t-column selections and count every interaction. Verify full coverage and record the column-set indices of interactions with one original occurrence for each row.
3. Iterate lexicographically over all unordered triples x < y < z. First attempt a shared-column certificate; otherwise look for pairwise incompatibility among one singleton witness per row. Emit three witness indices, or an explicit unresolved marker. The latter is **not** evidence of repairability.
4. In a separate C++ implementation, read the source rows, enumerate column selections recursively, compute multiplicities using base-v integer encoding, recheck full coverage, and reconstruct the singleton witness membership matrix.
5. Read exactly three bytes for each required deletion triple in order. Reject out-of-range IDs, non-singleton witnesses, missing conflict edges, truncation, trailing bytes, or unresolved markers in strict mode.
6. Recheck single- and two-row irreducibility conditions; require that the number of verified certificates equals the binomial coefficient N choose 3.
7. Independently regenerate and compare certificate bytes. The verification path never calls the generator.

## Results

| Quantity | Q9 | Q10 |
|---|---:|---:|
| (N,t,k,v) | (351,5,7,3) | (340,4,6,4) |
| Column subsets | 21 | 15 |
| Required interactions | 5,103 | 3,840 |
| Globally singleton interactions | 2,943 | 2,681 |
| Minimum / maximum per-row singleton count | 7 / 9 | 4 / 11 |
| Rows whose singleton column union is complete | 351 | 340 |
| Distinct source rows | 351 | 340 |
| Single deletions excluded | 351 | 340 |
| 2-to-1 pairs excluded | 61,425 | 57,630 |
| Three-deletion triples | 7,145,775 | 6,492,980 |
| Certificates from shared-column fast path | 5,962,743 | 6,151,082 |
| Certificates from subsequent triangle search | 1,183,032 | 341,898 |
| Valid triangle certificates (strict checker) | 7,145,775 | 6,492,980 |
| Unresolved triples | 0 | 0 |

Total: 13,638,755 verified triple certificates, 119,055 excluded pair neighborhoods, and 691 excluded singleton deletions. These are labeled row-index neighborhoods of two fixed arrays, not a count of distinct arrays modulo isomorphism.

The original prototype used a distinct-symbol test followed by bipartiteness testing on the singleton conflict graph. It excluded all triples. A follow-up identified triangles in every residual graph, strengthening the result to a compact certificate per triple. The publication candidate uses direct triangle construction and a separate verification implementation. A general non-bipartite graph need not have a triangle, so the empirical all-triangle result is not a logical consequence of the original bipartite test. It has been verified explicitly here.

The captured test includes both repairable and unrepairable small covering arrays with brute-force enumeration of all pairs of possible replacement rows, plus deliberately corrupt, truncated, and overlong certificate streams, a noncovering input, strict rejection of an unresolved case, invalid singleton/edge checks, and a deliberately unresolved but brute-force-unrepairable deletion triple in a binary CA(6;2,4,2). This last control demonstrates that failure to find a singleton triangle must never be treated as a proof of feasibility.

## Why this is useful

The result demonstrates a strong and inexpensive structural barrier against a common local search move. Rather than asking an exact solver to inspect millions of replacement neighborhoods individually, we can screen them using small mathematical certificates. A future constructive search can use the certificates to choose a neighborhood that breaks or avoids the conflict structure.

All triples in these two arrays admit an obstruction of size three. That is an empirical statement about these instances; it is not asserted for all covering arrays. A failed triangle search does not prove repairability. A full incompatibility graph can contain larger odd cycles or other coloring obstructions, and interactions with multiplicity greater than one may matter.

Promising research: test more arrays (including known repairable instances), compare local-obstruction distributions across construction families, study larger deletions and replacement budgets via clique/coloring certificates, exploit symmetry for compact certificate families, and use small obstructions to guide search moves that can genuinely improve existing arrays.

## Limits

- No new array is constructed and no upper bound is improved.
- No global nonexistence claim is made for CA(350;5,7,3) or CA(339;4,6,4).
- No conclusion about 4-to-3 or equally sized preparatory edits follows from this result.
- No originality claim for graph coloring, incompatibility graphs, or reduction via a clique.
- The result is tied to the exact archived inputs and is not a claim about all constructions with the same parameters.
- The timings logged here pertain to one execution environment and the measured code phases. They are not a controlled speedup comparison.
- Authorship of the original arrays remains with their constructors. Independent adjudication was completed by Project Forge (Muse) on 2026-11-26 (all claims confirmed); a bounded prior-art search found no prior documentation of these specific certificates, which is not a proof of worldwide novelty. Publication was authorized by the owner.

## References

1. K. Sarkar and C. J. Colbourn, “Two-stage algorithms for covering array construction,” Journal of Combinatorial Designs 27(8), 2019. DOI: [10.1002/jcd.21657](https://doi.org/10.1002/jcd.21657). Preprint [arXiv:1606.06730](https://arxiv.org/abs/1606.06730), §3.3 (incompatibility graph and chromatic-number completion).
2. C. Smolen, [ca-tools: a maintained table of covering arrays, with checked arrays and tools that verify them](https://github.com/chrispbsmolen/ca-tools), dataset DOI [10.5281/zenodo.24168008](https://doi.org/10.5281/zenodo.24168008). Archive provenance and source IDs are recorded in [data/README.md](../data/README.md); the exact upstream commit was not retained in the provided source snapshot.
3. A. Dwyer, [CA Database](https://github.com/aadwyer/CA_Database), indicated source for Q9 in the Lattice archive. The construction itself is attributed by the archive to CKRS (cross-sum).
4. C. J. Colbourn, G. Kéri, P. P. Rivas Soriano and J.-C. Schlage-Puchta, “Covering and radius-covering arrays: Constructions and classification,” Discrete Applied Mathematics 158(11), 2010. DOI: [10.1016/j.dam.2010.03.008](https://doi.org/10.1016/j.dam.2010.03.008). The Lattice archive attributes the Q9 cross-sum and Q10 simulated-annealing constructions to CKRS; the exact upstream file provenance should still be rechecked before publication.
5. J. Torres-Jimenez and A. Rodriguez-Cristerna, “Metaheuristic post-optimization of the NIST repository of covering arrays,” 2017, [DOI 10.1016/j.trit.2016.12.006](https://doi.org/10.1016/j.trit.2016.12.006), relevant prior art on row reduction and repair.

The present document is a pre-release research note, not a comprehensive novelty survey.
