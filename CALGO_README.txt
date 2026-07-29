quadratic_diagonal 1.1.0
========================

Purpose
-------
Exact constructive representability by diagonal quadratic forms over maximal
real quadratic orders.

Requirements
------------
CPython 3.10--3.13. The core package has no third-party runtime dependency.
A universal wheel is supplied in dist/.

Offline core installation and certificate example
-------------------------------------------------
python -m pip install --no-index dist/*.whl
quadratic-diagonal represent --D 21 --alpha 30,0 --coeff 2,1 --coeff 1,0 --coeff 1,0 --coeff 1,0 --method mitm --compact

Source-tree smoke test
----------------------
Install the reproducibility requirements, then run:
python -m pip install --no-build-isolation -e .[repro]
python scripts/run_all_checks.py

Full reproduction
-----------------
python scripts/run_all_checks.py --full --with-notebook

The command-line example prints JSON containing a representation and an
independent certificate flag. The full workflow ends with OK.
