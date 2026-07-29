# TOMS Algorithm-paper software component

Package: **quadratic_diagonal 1.1.0**  
Purpose: exact constructive diagonal representability over maximal real quadratic orders.

The article PDF and software component are supplied as separate submission files. The
software ZIP produced by `scripts/make_submission_archive.py` contains exactly one
top-level directory, the source package, a universal wheel, tests, examples,
reproduction drivers, deterministic validation summaries, documentation, an executed
notebook, licence and citation metadata, and per-file SHA-256 checksums.

## Offline core check

```bash
python -m pip install --no-index dist/*.whl
quadratic-diagonal represent --D 21 --alpha 30,0 \
  --coeff 2,1 --coeff 1,0 --coeff 1,0 --coeff 1,0 \
  --method mitm --compact
```

The JSON result contains an explicit root tuple and `"certified": true`.

## Referee workflow

```bash
python -m pip install --no-build-isolation -e .[repro]
python scripts/run_all_checks.py
```

The complete validation and notebook path is:

```bash
python scripts/run_all_checks.py --full --with-notebook
```

## Independent validation supplied

The full bounded corpus covers 26 squarefree fields through `D = 41` and records:

- 2,998 weighted-search comparisons against independent sharp-box enumeration;
- 2,512 DP/MITM/direct-sumset representability comparisons;
- 2,452 independently verified constructive certificates;
- 104 batched bounded-search comparisons;
- zero discrepancies.

The machine-readable summary is `data/validation_summary.json`.

## Portability

The core package has no runtime dependency outside the Python standard library and
uses arbitrary-precision integers. Python 3.10--3.13 is supported. CI is configured
for Linux, macOS and Windows. Optional reproduction dependencies are confined to
pytest, Matplotlib, Jupyter and nbconvert. See `docs/PORTABILITY.md`.

Timing values depend on hardware and interpreter state. All mathematical certificates,
state counts and validation totals are deterministic.
