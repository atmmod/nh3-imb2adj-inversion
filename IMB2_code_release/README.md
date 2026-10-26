# IMB2 code

IMB2 (iterative moving-box mass balance) is the mass-balance step of the hybrid IMB2 + 4D-Var NH₃ emissions inversion. In the code it is called "MB" or "mb" (`mb_scal()`, `MB_no`, `run_model_mb`). It is implemented in a modified version of the py4dvar framework (https://github.com/steven-thomas/py4dvar); the files here come from the working copy used for the April 2017 production run with CrIS v1.6.3 NH₃ retrievals (36US2 domain, γ = 5000).

| File | Contents |
|---|---|
| `imb2_mb_scal.py` | `mb_scal()`, the IMB2 routine, extracted from `py4dvar/fourdvar/_main_driver.py` (lines 1–694: license header, imports, `gama`, `mb_scal()`). The 4D-Var routines in that file are left out. |
| `imb2_supporting_code.py` | Excerpts of the IMB2-specific helpers that `mb_scal()` calls in other py4dvar modules, each labelled with its source file and line numbers. A reference copy, not an importable module. |
| `run_imb2_then_4dvar.py` | The driver for the production run (`py4dvar/tests/cris_obs_run_mb_4dvar.py`): IMB2 first, then 4D-Var starting from the IMB2 posterior. |

## What `mb_scal()` does

1. Defines a 13 × 13-cell moving box (about 470 km across) around each 36 km grid cell (`trans_rad = 6`), truncated at the domain edges.
2. Averages the observed CrIS total columns (already averaged within each grid cell) over the box.
3. Runs CMAQ forward with the current emission scaling factors, applies the CrIS observation operator, converts the result to total columns, and averages it within grid cells and then over the box.
4. Takes the relative difference (observed − simulated) / simulated, averages it over the box again and clips it to [−0.99, 99]. The scaling factor is α = 1 + this value.
5. Fills cells with no valid α (no observations in their box) by inverse-distance weighting over the surrounding 13 × 13 cells (power 1, geodesic distance). Data-void neighbours enter at α = 1 in the first iteration and at their previous interpolated value after that.
6. Multiplies the emission scaling factors by α in every emission layer and limits them to 0.1–10.
7. Repeats steps 3–6 while the normalized mean difference between successive scaling fields (Σ|σ_t − σ_t−1| / Σσ_t−1) is at least 0.05 and the observation term of the 4D-Var cost function, J_o, has not increased. If the loop stops because J_o increased, the previous iteration's field is returned, unless the increase came on the first update.

`gama` (5000) weights the background term of the 4D-Var cost function. In `mb_scal()` it only enters a cost value written to the log, so it does not affect the IMB2 update or when IMB2 stops.

## Requirements

The code is written for Python 2.7 (for example, `user_driver.py` imports `cPickle`, and the IDW loops pass floats to `range()`, which Python 3 rejects). It uses NumPy, SciPy, netCDF4, geopy and Matplotlib, and runs inside the modified py4dvar framework with a CMAQ forward-model build.

## License

py4dvar is Copyright 2016 University of Melbourne and is licensed under the Apache License 2.0. The files here are derived from a modified copy of py4dvar; `imb2_mb_scal.py` keeps the original license header and states that it was modified.
