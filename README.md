# Three-interaction obstruction certificates for covering-array row replacement

**Jared Haxton — Project Lattice / Project Forge**  
**Version 0.1.0 (verification and publication candidate), 2026-11-26**

This repository records an exhaustive computational result about two existing covering arrays. It does not introduce those arrays, improve their sizes, or claim a global covering-array lower bound.

## Main result

Neither of the two pinned arrays can be made smaller by removing any three distinct row indices and inserting any two rows, with all other rows unchanged. Each of the 13,638,755 unordered deletion triples has an explicit obstruction consisting of three pairwise incompatible interactions that occur uniquely in the three deleted rows.

| Array | Required interactions | Deletion triples | Shared-column certificates | Additional triangle certificates | Verified |
|---|---:|---:|---:|---:|---:|
| CA(351;5,7,3) | 5,103 | 7,145,775 | 5,962,743 | 1,183,032 | 7,145,775 |
| CA(340;4,6,4) | 3,840 | 6,492,980 | 6,151,082 | 341,898 | 6,492,980 |
| **Total** | — | **13,638,755** | **12,113,825** | **1,524,930** | **13,638,755** |

The generator emits three column-subset identifiers per deletion triple. The separate certificate checker reconstructs interaction multiplicities directly from each source array and validates every witness. No SAT/SMT solver or third-party Python library is required.

The source arrays also have distinct rows, and every row has singleton interactions whose union covers every column. Consequently every one-row deletion loses coverage, and no two rows can be replaced by one. Together these results establish local irreducibility under shrinking replacements involving at most three deleted rows.

## Reproduce

Requirements: Python 3.9+, a C++17 compiler such as g++ or clang++, and about 50 MB of temporary disk space; no package installation or internet connection required after obtaining the input arrays.

From the repository root:

```sh
python3 scripts/run.py test
python3 scripts/run.py verify --inputs ../verification-inputs
python3 scripts/run.py regenerate --inputs ../verification-inputs
```

For a public checkout, place the exact archived arrays in a directory and pass `--inputs /path/to/arrays`; see [data/README.md](data/README.md) for provenance, expected SHA-256 hashes and the redistribution note. The private handoff already contains those files in the sibling directory shown above. The tool defaults to that directory when available, otherwise to `data/`.

Use `--target Q9` or `--target Q10` for one instance. If necessary, set the environment variable `CXX=clang++`. The `verify` command does not run the generator; it compiles the separate verifier and checks each bundled certificate. The `regenerate` command independently reconstructs the generator's inputs and compares the resulting uncompressed certificate stream byte-for-byte with the bundled baseline before also verifying it. The test command includes tiny brute-force repair controls and intentionally broken inputs/certificates.

Expected result: Q9 verified 7,145,775, Q10 verified 6,492,980, both unresolved 0. See [results](evidence/results.json) and the captured logs for full detail.

## What is included

- [Research note and proof](docs/RESEARCH_NOTE.md)
- [Certificate format](docs/CERTIFICATE_FORMAT.md) and [worked original examples](docs/WORKED_CERTIFICATES.md)
- [Source provenance](data/README.md) and immutable input manifest
- `src/generate.cpp` — triangle-certificate production
- `scripts/generate.py` — interaction witness preparation
- `src/verify.cpp` — independent validation implementation
- `scripts/run.py` — offline reproducibility and tests
- `certificates/` — gzip-compressed records, one for every deletion triple (4,476,779 bytes total)
- `evidence/` — exact counts, raw results and test logs
- `CITATION.cff` — suggested attribution
- GitHub Actions smoke tests and full verification when pinned input files are available

## Prior work and scope

The general equivalence between completing uncovered covering-array interactions and coloring their incompatibility graph is established prior art: Sarkar & Colbourn, *Two-stage algorithms for covering array construction*, J. Combinatorial Designs (2019), [DOI 10.1002/jcd.21657](https://doi.org/10.1002/jcd.21657), [arXiv:1606.06730 §3.3](https://arxiv.org/abs/1606.06730). This work applies the known framework to a specific exhaustive local-replacement census with small, independently verifiable certificates. No priority for the general graph formulation is asserted.

The arrays are third-party constructions; the archived attribution is Dwyer / CKRS cross-sum for Q9 and CKRS simulated annealing for Q10. They were obtained via the ca-tools table. See the [data provenance](data/README.md). This package does not claim authorship of the input constructions.

The exact empirical claim is limited to the pinned row lists. Neither a global optimum nor an improved CAN(t,k,v) bound follows. A different array, a broader neighborhood, or a different construction could succeed.

## Status and citation

This is a reproducible research release. The complete certificate streams and controls were checked by the package's authoring environment and independently adjudicated by Project Forge (Muse) on 2026-11-26: all seven adjudicated claims were confirmed, including an exhaustive independent validation of all 13,638,755 certificates and a false-positive test battery. Publication was authorized by the owner. This is not a refereed publication and is not an assertion of scientific priority over all prior research.

Research directed by Jared Haxton (Project Lattice and Project Forge), using AI-assisted computational research (ChatGPT; Muse supplied the underlying Lattice research drops). The algorithms, proof details and code here are provided for scrutiny rather than relying on the authority of either AI system.

Suggested citation: Jared Haxton, *Three-interaction obstruction certificates for covering-array row replacement*, Projects Lattice & Forge, v0.1.0, 2026. Released at https://github.com/jaredhaxton-cmd/covering-array-row-obstructions (v0.1.0); no DOI is claimed.
