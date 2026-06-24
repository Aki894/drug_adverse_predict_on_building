# Evidence Bank

## Remote Experiment Summary

| Experiment | Output | Epochs | Mean AUC | Mean AUPR | Mean ACC | Mean MCC | Interpretation |
|---|---|---:|---:|---:|---:|---:|---|
| Fold-local base | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_084455_solo5_foldlocal_base/results.txt` | 5 | 0.91102 | 0.90658 | 0.82887 | 0.66108 | Baseline after fold-local negative sampling cleanup. |
| D4 similarity negative weighting | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_090556_solo5_d4_neg_nopin/results.txt` | 5 | 0.91138 | 0.90698 | 0.82806 | 0.66116 | Tiny AUC/AUPR gain, no useful ACC/MCC gain. Not strong enough as the main method. |
| Fold-local threshold calibration | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_092120_solo5_calibrated_threshold/results.txt` | 5 | 0.91262 | 0.90820 | 0.83518 | 0.67062 | Best current signal: all four means improve, with strongest gains on ACC/MCC. |
| PU-style negative BCE + threshold calibration | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_115459_solo5_pu_weighted_fixed/results.txt` | 5 | 0.91042 | 0.90573 | 0.83285 | 0.66598 | Negative ablation: below calibrated-threshold screen, so do not promote as the main direction. |
| Support-aware ADR weighting | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_133135_solo5_support_weighted/results.txt` | 5 | 0.91005 | 0.90612 | 0.82697 | 0.65855 | Negative ablation: below 5-epoch fold-local base. Current weighting is too weak/noisy to promote. |
| Fold-local threshold calibration | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_102434_e30_calibrated_threshold_quiet_u/results.txt` | 30 | 0.93023 | 0.92643 | 0.85587 | 0.71201 | Completed five-fold long-training candidate. Must be compared against the same-epoch base before being promoted. |
| Fold-local base comparator | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_121030_e30_base_quiet_u/results.txt` | 30 | 0.92965 | 0.92597 | 0.85550 | 0.71140 | Completed five-fold same-epoch comparator. Calibrated threshold is only slightly higher: +0.00058 AUC, +0.00046 AUPR, +0.00037 ACC, +0.00061 MCC. |

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

The 30-epoch calibrated-threshold run is a real but very small improvement over the same-epoch fold-local base: AUC +0.00058, AUPR +0.00046, ACC +0.00037, and MCC +0.00061. Treat it as a useful decision-layer component, not a sufficient standalone paper contribution. Continue with support-aware ADR weighting and graph/side-risk directions to seek a stronger ranking-metric contribution.

## 30-Epoch Fold-Local Base Comparator Progress

| Fold | AUC | AUPR | ACC | MCC | Threshold |
|---|---:|---:|---:|---:|---:|
| 1 | 0.92779 | 0.92238 | 0.85435 | 0.70882 | 0.500 |
| 2 | 0.93009 | 0.92735 | 0.85873 | 0.71754 | 0.500 |
| 3 | 0.93056 | 0.92596 | 0.85649 | 0.71329 | 0.500 |
| 4 | 0.92714 | 0.92456 | 0.84997 | 0.69996 | 0.500 |
| 5 | 0.93268 | 0.92958 | 0.85798 | 0.71741 | 0.500 |

Final five-fold mean: AUC 0.92965, AUPR 0.92597, ACC 0.85550, MCC 0.71140.

## 30-Epoch Calibrated Threshold Progress

| Fold | AUC | AUPR | ACC | MCC | Selected Threshold |
|---|---:|---:|---:|---:|---:|
| 1 | 0.92582 | 0.92032 | 0.85157 | 0.70317 | 0.510 |
| 2 | 0.92957 | 0.92745 | 0.85574 | 0.71240 | 0.420 |
| 3 | 0.93004 | 0.92620 | 0.85403 | 0.70837 | 0.450 |
| 4 | 0.93180 | 0.92668 | 0.85948 | 0.71898 | 0.480 |
| 5 | 0.93393 | 0.93148 | 0.85852 | 0.71712 | 0.530 |

Final five-fold mean: AUC 0.93023, AUPR 0.92643, ACC 0.85587, MCC 0.71201.

## Implemented Follow-Up Direction

PU-style negative BCE weighting has been implemented as a switchable follow-up experiment in `pythonPredict/DGAPred(Compare)/src/main.py`.

- Switch: `--use_pu_negative_weighting`
- Default behavior: off, so existing baseline/calibrated-threshold runs are unchanged.
- Mechanism: positive samples keep weight 1.0; negative samples receive a BCE weight based on drug-side combined pseudo-negative risk.
- Risk sources: drug similarity evidence plus optional ADR similarity evidence from MESH/GDA matrices.
- First queued remote screen exposed a calibration-path batch shape bug and was replaced by `solo5_pu_weighted_fixed`.
- Fixed remote screen: `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_115459_solo5_pu_weighted_fixed/`.
- Final fixed screen: AUC 0.91042, AUPR 0.90573, ACC 0.83285, MCC 0.66598.
- Interpretation: below the 5-epoch threshold-calibration screen (AUC 0.91262, AUPR 0.90820, ACC 0.83518, MCC 0.67062), so this is a negative ablation rather than a publishable main direction.
