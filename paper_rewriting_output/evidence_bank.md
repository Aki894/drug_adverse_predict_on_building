# Evidence Bank

## Remote Experiment Summary

| Experiment | Output | Epochs | Mean AUC | Mean AUPR | Mean ACC | Mean MCC | Interpretation |
|---|---|---:|---:|---:|---:|---:|---|
| Fold-local base | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_084455_solo5_foldlocal_base/results.txt` | 5 | 0.91102 | 0.90658 | 0.82887 | 0.66108 | Baseline after fold-local negative sampling cleanup. |
| D4 similarity negative weighting | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_090556_solo5_d4_neg_nopin/results.txt` | 5 | 0.91138 | 0.90698 | 0.82806 | 0.66116 | Tiny AUC/AUPR gain, no useful ACC/MCC gain. Not strong enough as the main method. |
| Fold-local threshold calibration | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_092120_solo5_calibrated_threshold/results.txt` | 5 | 0.91262 | 0.90820 | 0.83518 | 0.67062 | Best current signal: all four means improve, with strongest gains on ACC/MCC. |
| Fold-local threshold calibration | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_102434_e30_calibrated_threshold_quiet_u/results.txt` | 30 | 0.92848 | 0.92466 | 0.85378 | 0.70798 | In-progress three-fold mean; strong long-training confirmation so far. |

## Fold-Level Calibrated Thresholds

| Fold | AUC | AUPR | ACC | MCC | Selected Threshold |
|---|---:|---:|---:|---:|---:|
| 1 | 0.90952 | 0.90269 | 0.83490 | 0.67019 | 0.600 |
| 2 | 0.91314 | 0.90939 | 0.83426 | 0.66867 | 0.500 |
| 3 | 0.91187 | 0.90557 | 0.83287 | 0.66599 | 0.430 |
| 4 | 0.91158 | 0.90947 | 0.83501 | 0.67026 | 0.400 |
| 5 | 0.91700 | 0.91390 | 0.83885 | 0.67801 | 0.450 |

## Literature Anchors

- Reliable-negative drug side-effect prediction is a direct precedent for treating unlabeled zeros carefully: Zheng et al., BMC Bioinformatics 2019, "Inverse similarity and reliable negative samples for drug side-effect prediction" (`https://link.springer.com/article/10.1186/s12859-018-2563-x`).
- MCC-oriented threshold search is a reasonable procedure for imbalanced classification decisions: the PLOS ONE MCC classifier paper notes grid search can be used to determine an MCC-oriented threshold (`https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0177678`).

## Next Validation Gate

Finish the 30-epoch calibrated-threshold five-fold run and compare against a 30-epoch fold-local base under identical batch/thread/pin-memory settings. The current three-fold mean is already substantially above the 5-epoch screening result, but the five-fold mean is required before finalizing the claim.

## 30-Epoch Calibrated Threshold Progress

| Fold | AUC | AUPR | ACC | MCC | Selected Threshold |
|---|---:|---:|---:|---:|---:|
| 1 | 0.92582 | 0.92032 | 0.85157 | 0.70317 | 0.510 |
| 2 | 0.92957 | 0.92745 | 0.85574 | 0.71240 | 0.420 |
| 3 | 0.93004 | 0.92620 | 0.85403 | 0.70837 | 0.450 |

Current three-fold mean: AUC 0.92848, AUPR 0.92466, ACC 0.85378, MCC 0.70798.

## Implemented Follow-Up Direction

PU-style negative BCE weighting has been implemented as a switchable follow-up experiment in `pythonPredict/DGAPred(Compare)/src/main.py`.

- Switch: `--use_pu_negative_weighting`
- Default behavior: off, so existing baseline/calibrated-threshold runs are unchanged.
- Mechanism: positive samples keep weight 1.0; negative samples receive a BCE weight based on drug-side combined pseudo-negative risk.
- Risk sources: drug similarity evidence plus optional ADR similarity evidence from MESH/GDA matrices.
- First queued remote screen: `/data/ccc/ADR/logs/solo5_pu_weighted_wait_*.log`, configured to wait for the current 30-epoch calibrated-threshold run before starting.
