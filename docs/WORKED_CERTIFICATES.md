# Worked certificates

Each example is a real record from the corresponding compressed certificate stream. The row and column indices are zero-based.

## Q9: non-shared-column example
Triple (0, 1, 3); record index 1; record bytes [4, 4, 4].

| Row | Column subset | Required symbols | Occurrences in source |
|---:|---|---|---:|
| 0 | (0, 1, 2, 4, 6) | (0, 0, 0, 0, 0) | 1 |
| 1 | (0, 1, 2, 4, 6) | (1, 1, 1, 1, 1) | 1 |
| 3 | (0, 1, 2, 4, 6) | (0, 0, 0, 1, 1) | 1 |

Conflict edges:
- Rows 0 and 1: column 0, symbols 0 vs 1.
- Rows 0 and 3: column 4, symbols 0 vs 1.
- Rows 1 and 3: column 0, symbols 1 vs 0.

These three missing interactions require at least three replacement rows. No column has three distinct symbols across the deleted rows, so the easy shared-column filter alone would miss this witness.

## Q10: non-shared-column example
Triple (0, 1, 4); record index 2; record bytes [0, 0, 10].

| Row | Column subset | Required symbols | Occurrences in source |
|---:|---|---|---:|
| 0 | (0, 1, 2, 3) | (0, 0, 0, 0) | 1 |
| 1 | (0, 1, 2, 3) | (0, 0, 0, 1) | 1 |
| 4 | (1, 2, 3, 4) | (0, 1, 0, 0) | 1 |

Conflict edges:
- Rows 0 and 1: column 3, symbols 0 vs 1.
- Rows 0 and 4: column 2, symbols 0 vs 1.
- Rows 1 and 4: column 2, symbols 0 vs 1.

These three missing interactions require at least three replacement rows. No column has three distinct symbols across the deleted rows, so the easy shared-column filter alone would miss this witness.

