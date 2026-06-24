# Research Dossier

## Target Scene

The immediate target is an experimental ML/biomedical paper around DGAPred-style adverse drug reaction prediction. The code predicts drug-ADR associations from multi-view drug similarities and ADR similarities.

## Problem Constraints

The available label matrix is sparse and positive-observed: zeros mostly mean unobserved pairs, not clinically verified non-associations. This makes random negative sampling noisy. Existing local analysis reports 453 drugs, 1019 ADRs, 23,395 positives, 438,212 zeros, and explicit pseudo-negative risk.

## Accepted Paper Pattern

A strong paper framing should combine a domain-specific data issue with a model-side improvement: (1) identify unlabeled-zero false-negative risk in ADR prediction; (2) introduce reliability-aware negative sampling or weighting; (3) keep the evaluation protocol comparable to DGAPred; (4) show gains through fold-wise AUC/AUPR/ACC/MCC and ablations.

## Constraints for This Project

The first implementation must be practical: no new external databases, no expensive preprocessing, no change to test-set construction requested by the user. The safest first move is to alter training negative sampling only, keep test folds intact, and preserve command-line switches for ablation.
