# Evidence Bank

## Remote Experiment Summary

| Experiment | Output | Epochs | Mean AUC | Mean AUPR | Mean ACC | Mean MCC | Interpretation |
|---|---|---:|---:|---:|---:|---:|---|
| Fold-local base | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_084455_solo5_foldlocal_base/results.txt` | 5 | 0.91102 | 0.90658 | 0.82887 | 0.66108 | Baseline after fold-local negative sampling cleanup. |
| D4 similarity negative weighting | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_090556_solo5_d4_neg_nopin/results.txt` | 5 | 0.91138 | 0.90698 | 0.82806 | 0.66116 | Tiny AUC/AUPR gain, no useful ACC/MCC gain. Not strong enough as the main method. |
| Fold-local threshold calibration | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_092120_solo5_calibrated_threshold/results.txt` | 5 | 0.91262 | 0.90820 | 0.83518 | 0.67062 | Best current signal: all four means improve, with strongest gains on ACC/MCC. |

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

Run the same calibrated-threshold setting for 30 epochs and compare against a 30-epoch fold-local base under identical batch/thread/pin-memory settings. Treat the 5-epoch result as screening evidence only.

