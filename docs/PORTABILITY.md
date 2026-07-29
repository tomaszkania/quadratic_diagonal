# Portability

The core `quadratic_diagonal` package uses only the Python standard library and arbitrary-precision integers.
It supports CPython 3.10--3.13 on Linux, macOS, and Windows.  Plotting, tests, and notebook
execution are optional reproducibility extras and are not imported by the mathematical library.
All mathematical outputs are deterministic; only wall-clock timings are machine-dependent.
