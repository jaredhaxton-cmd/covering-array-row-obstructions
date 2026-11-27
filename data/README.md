# Input provenance

The two exact arrays were extracted byte-for-byte from the supplied Lattice D0007 delivery (2026-11-26 22:00 Arizona time), whose SHA-256 and nested member paths are pinned in [inputs.json](inputs.json). They contain plain, whitespace-delimited, zero-based symbols without a header. Row and column ordering matters for these certificates.

The archived pass 38 and 39 programs record the upstream source paths in the ca-tools repository:

| Target | Original array attribution in archive | Recorded upstream path |
|---|---|---|
| Q9 | S5 Dwyer database; CKRS cross-sum construction | table/arrays/CA_351_5_7_3.txt |
| Q10 | S7 CKRS; simulated annealing | table/arrays/CA_340_4_6_4.txt |

- Registry: <https://github.com/chrispbsmolen/ca-tools>
- Table DOI (all versions): <https://doi.org/10.5281/zenodo.24168008>
- CKRS: Colbourn, Kéri, Rivas Soriano and Schlage-Puchta (2010), <https://doi.org/10.1016/j.dam.2010.03.008>. See also the CAs project (<https://github.com/ugroempi/CAs>), which exposes ckrsCA and dwyerCA retrieval functions. Neither a freshly retrieved array nor a reconstructed one should be substituted unless the pinned SHA-256 matches.
- Dwyer database: <https://github.com/aadwyer/CA_Database>
- Registry's data-license text: <https://github.com/chrispbsmolen/ca-tools/blob/main/LICENSE-DATA>

The archived source arrays themselves are the exact inputs of the claims; the upstream commit and original source-specific redistribution terms were not captured in the delivery, and the two live upstream files could not be fetched during release preparation. The public registry's data license distinguishes its own CC BY 4.0 data from third-party data, which retains its source-specific terms. Do not assume all upstream arrays are covered by the registry's general license.

For independent verification, the outer handoff contains the original arrays in `verification-inputs/`, and an audit-only copy of the original delivery. These are separate from the proposed GitHub repository. The owner should confirm attribution, upstream version/link and redistribution terms before publicly copying those third-party input files into this repo. Alternatively, publish exact acquisition instructions and SHA-256 hashes while users supply the input files.

If an upstream download includes a size header or uses different whitespace or one-based symbols, normalize only those formatting differences; do not reorder rows/columns. Use `python3 scripts/normalize_input.py Q9 SOURCE OUTPUT_DIR` (or Q10) to try only formatting/zero-base conversions and accept a match to the manifest. The SHA-256 of the normalized file must match inputs.json. If it does not, do not present it as the pinned instance or use it with the bundled certificates.

Verification command:

```sh
python3 scripts/run.py verify --inputs /path/to/exact/arrays
```

All required evidence is fully available offline in the private handoff. This note makes no ownership claim over the underlying arrays.
