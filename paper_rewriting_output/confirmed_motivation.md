# Confirmed Working Motivation

Improve DGAPred's threshold-dependent ADR decision quality by adding fold-local MCC-oriented probability threshold calibration, while preserving the existing ADR cross-validation convention and leaving test folds untouched.

This is the current working motivation, not the final paper claim. The evidence is strongest for ACC/MCC improvement after a 5-epoch screen and remains strong in the completed 30-epoch five-fold validation, with final means of AUC 0.93023, AUPR 0.92643, ACC 0.85587, and MCC 0.71201. A same-epoch fold-local base comparison is still useful before treating it as the final contribution.
