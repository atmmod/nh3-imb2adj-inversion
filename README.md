# Code for the hybrid IMB2 + 4D-Var CrIS NH₃ emissions inversion (ERL)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23889908.svg)](https://doi.org/10.5281/zenodo.23889908)

This repository archives the code behind the ERL paper on the hybrid IMB2 + 4D-Var inversion of NH₃ emissions with CrIS retrievals and the CMAQ adjoint.
[Paper citation and DOI: to be added after publication.]

## Citing this code

Lyu, C., Liu, J., Shephard, M. W., Sitwell, M., Henze, D. K., Lombardo, M., Zhao, S., Hakami, A., McDonald, B. C., Rasool, Q. Z., Silver, J. D., Thomas, S., Rayner, P., and Capps, S. L.: Code for the hybrid IMB2 + 4D-Var CrIS NH3 inversion, Zenodo [code], https://doi.org/10.5281/zenodo.23889908, 2026.

This DOI always resolves to the latest release. Version v1.0.0 is https://doi.org/10.5281/zenodo.23889909.

| Directory | Contents | Source |
|---|---|---|
| `cmaq_adj/` | CMAQ adjoint code (NH₃ version), with build directories and run scripts | `cmaq_adj`, commit `fe011566b801e69e4b83661c9d2c17e8c176b689` |
| `py4dvar/` | Unmodified snapshot of the py4dvar framework | https://github.com/steven-thomas/py4dvar, branch `CMAQ_emis_timestep` (the repository's default branch), commit `9e4bdf257e11ee4eb6f65407afc46e372c7990ce` (2020-07-12) |
| `IMB2_code_release/` | The IMB2 mass-balance code and the driver for the production run | See `IMB2_code_release/README.md` |

## Notes

- `py4dvar/` is the upstream code exactly as of the commit above, with the git history removed so that the archive is a single self-contained snapshot. The IMB2 files in `IMB2_code_release/` come from a modified working copy of py4dvar; they are not a patch against this snapshot.
- `cmaq_adj/` is the unpacked contents of the archive `cmaq_adj-CMAQ_adj_NH3_cl.zip`. One PBS job log, `scripts/run.adj.bwd.1day.l22.vf.base.proteus.o541383` (353 MB), is left out because it exceeds GitHub's file size limit.
- Each component carries its own license: py4dvar (Apache License 2.0, `py4dvar/LICENSE.txt`), IMB2 (`IMB2_code_release/LICENSE`), and the CMAQ adjoint (see `cmaq_adj/README.md`).

## Disclosure

This repository was assembled with Claude (Anthropic): Claude copied the three components from the authors' data folder and the upstream py4dvar repository, and drafted this README. The code in each component was written by its original authors.
