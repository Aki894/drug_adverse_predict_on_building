# Evidence Bank

## Remote Experiment Summary

| Experiment | Output | Epochs | Mean AUC | Mean AUPR | Mean ACC | Mean MCC | Interpretation |
|---|---|---:|---:|---:|---:|---:|---|
| Fold-local base | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_084455_solo5_foldlocal_base/results.txt` | 5 | 0.91102 | 0.90658 | 0.82887 | 0.66108 | Baseline after fold-local negative sampling cleanup. |
| D4 similarity negative weighting | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_090556_solo5_d4_neg_nopin/results.txt` | 5 | 0.91138 | 0.90698 | 0.82806 | 0.66116 | Tiny AUC/AUPR gain, no useful ACC/MCC gain. Not strong enough as the main method. |
| Fold-local threshold calibration | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_092120_solo5_calibrated_threshold/results.txt` | 5 | 0.91262 | 0.90820 | 0.83518 | 0.67062 | Best current signal: all four means improve, with strongest gains on ACC/MCC. |
| PU-style negative BCE + threshold calibration | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_115459_solo5_pu_weighted_fixed/results.txt` | 5 | 0.91042 | 0.90573 | 0.83285 | 0.66598 | Negative ablation: below calibrated-threshold screen, so do not promote as the main direction. |
| Support-aware ADR weighting | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_133135_solo5_support_weighted/results.txt` | 5 | 0.91005 | 0.90612 | 0.82697 | 0.65855 | Negative ablation: below 5-epoch fold-local base. Current weighting is too weak/noisy to promote. |
| Fold-local graph prior | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_134911_solo5_graph_prior/results.txt` | 5 | 0.91357 | 0.90903 | 0.82870 | 0.66187 | Best current short-run method direction for ranking metrics: +0.00255 AUC and +0.00245 AUPR over 5-epoch base. |
| Fold-local graph prior + threshold calibration | `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_141045_solo5_graph_prior_calibrated_fixed/results.txt` | 5 | 0.91188 | 0.90772 | 0.83296 | 0.66644 | Above 5-epoch base on all four metrics, but sacrifices AUC/AUPR compared with graph prior alone. |
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

The 30-epoch calibrated-threshold run is a real but very small improvement over the same-epoch fold-local base: AUC +0.00058, AUPR +0.00046, ACC +0.00037, and MCC +0.00061. Treat it as a useful decision-layer component, not a sufficient standalone paper contribution.

The current best short-run method-level candidate is fold-local graph prior. Its 5-epoch run improves ranking metrics over the 5-epoch base (AUC +0.00255, AUPR +0.00245), while the graph-prior-plus-calibration variant improves ACC/MCC but weakens ranking. The 30-epoch validation run `e30_graph_prior_quiet_u` is still active on `server-NER` (PID `721883`, log `/data/ccc/ADR/logs/e30_graph_prior_quiet_u_20260624_142522.log`). As of the latest check, it has completed 3/5 folds with mean AUC 0.92915, AUPR 0.92474, ACC 0.85478, and MCC 0.70963, which is below the 30-epoch base comparator so far. Keep waiting for the full 5-fold result, but prepare the next candidate rather than assuming graph prior will win.

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

## Fold-Local Graph Prior Evidence

| Variant | Epochs | AUC | AUPR | ACC | MCC | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| Graph prior, max combine, weight 0.5 | 5 | 0.91357 | 0.90903 | 0.82870 | 0.66187 | Best short-run ranking signal so far. Promote to 30-epoch validation. |
| Graph prior + calibrated threshold | 5 | 0.91188 | 0.90772 | 0.83296 | 0.66644 | Useful if ACC/MCC are prioritized, but not as strong for AUC/AUPR. |

Active validation run:

```bash
python -u pythonPredict/DGAPred\(Compare\)/src/main.py --run_name e30_graph_prior_quiet_u --epochs 30 --batch_size 256 --test_batch_size 512 --torch_threads 4 --torch_interop_threads 1 --no-pin_memory --disable_tqdm --use_graph_prior --graph_prior_weight 0.5 --graph_prior_combine max
```

Remote status checked on 2026-06-24: PID `721883` is still running. The log reached fold 1 epoch 3 with interim test AUC 0.90641 and AUPR 0.89956; no final fold result is available yet.

Updated remote status checked on 2026-06-24:

| Completed Fold | AUC | AUPR | ACC | MCC | Threshold |
|---|---:|---:|---:|---:|---:|
| 1 | 0.92722 | 0.92071 | 0.85275 | 0.70562 | 0.500 |
| 2 | 0.92939 | 0.92772 | 0.85691 | 0.71385 | 0.500 |
| 3 | 0.93083 | 0.92578 | 0.85467 | 0.70942 | 0.500 |

Partial mean over 3 folds: AUC 0.92915, AUPR 0.92474, ACC 0.85478, MCC 0.70963. This interim result is weaker than the 30-epoch base comparator (AUC 0.92965, AUPR 0.92597, ACC 0.85550, MCC 0.71140), so graph prior may need lower weight or a different aggregation if the final 5-fold result stays below base.

## Next Candidate: Reliable Negative Filtering

Implemented a new switchable candidate in `pythonPredict/DGAPred(Compare)/src/main.py`.

- Switch: `--use_reliable_negative_filter`
- Main parameter: `--reliable_negative_filter_percentile`, default `90.0`.
- Mechanism: compute fold-local pseudo-negative risk for every training candidate negative from both drug-neighbor positive evidence and ADR-neighbor positive evidence, remove only candidates above the chosen risk percentile, then sample the remaining pool to match the number of training positives.
- Scope: training fold only. Test fold remains unchanged.
- Rationale: the earlier PU-style BCE reduced all suspicious negatives continuously and failed. This version is sharper and more local: it only removes the highest-risk tail from the training negative pool.

Planned first screen:

```bash
python -u pythonPredict/DGAPred\(Compare\)/src/main.py --run_name solo5_reliable_neg_p90 --epochs 5 --batch_size 256 --test_batch_size 512 --torch_threads 4 --torch_interop_threads 1 --no-pin_memory --disable_tqdm --use_reliable_negative_filter --reliable_negative_filter_percentile 90
```

Remote status: queued on `server-NER` behind the active graph-prior run to avoid resource contention. Queue wrapper PID is `842959`; log is `/data/ccc/ADR/logs/solo5_reliable_neg_p90_20260624_151900.log`.

Early-stop result: fold 1 finished with AUC 0.90739, AUPR 0.89877, ACC 0.83031, MCC 0.66253, below the 5-epoch base. The run was terminated as a negative screen.

## Low-Weight Graph Prior Follow-Up

Because graph prior weight 0.5 was positive in 5-epoch screening but weak in the partial 30-epoch run, the next active test reduces the logit residual weight to 0.2 while keeping max aggregation.

```bash
python -u pythonPredict/DGAPred\(Compare\)/src/main.py --run_name solo5_graph_prior_w02 --epochs 5 --batch_size 256 --test_batch_size 512 --torch_threads 4 --torch_interop_threads 1 --no-pin_memory --disable_tqdm --use_graph_prior --graph_prior_weight 0.2 --graph_prior_combine max
```

Remote status: running on `server-NER`; log `/data/ccc/ADR/logs/solo5_graph_prior_w02_20260624_152739.log`.

Early-stop result: fold 1 finished with AUC 0.90755, AUPR 0.90026, ACC 0.83020, MCC 0.66051, below the 5-epoch base. Lowering the residual weight to 0.2 appears to weaken rather than stabilize the graph-prior signal.

## Mean-Aggregated Graph Prior Follow-Up

Next active test: keep graph-prior weight 0.5 but switch aggregation from `max` to `mean`.

```bash
python -u pythonPredict/DGAPred\(Compare\)/src/main.py --run_name solo5_graph_prior_mean --epochs 5 --batch_size 256 --test_batch_size 512 --torch_threads 4 --torch_interop_threads 1 --no-pin_memory --disable_tqdm --use_graph_prior --graph_prior_weight 0.5 --graph_prior_combine mean
```

Remote status: running on `server-NER`; log `/data/ccc/ADR/logs/solo5_graph_prior_mean_20260624_153337.log`.

Early-stop result: fold 1 finished with AUC 0.90724, AUPR 0.90023, ACC 0.82657, MCC 0.65638, below the 5-epoch base. Mean aggregation is a negative screen.

## Score-Level Ensemble Evidence

Added reusable evaluator: `pythonPredict/DGAPred(Compare)/src/evaluate_prediction_ensemble.py`.

Exploratory result from saved prediction files:

| Ensemble | Folds | Weight | AUC | AUPR | ACC | MCC | Interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| 5-epoch base + graph-prior max | 5 | 0.5 / 0.5 | 0.91368 | 0.90930 | 0.83054 | 0.66465 | Improves over 5-epoch base on all metrics and is more balanced than graph-prior alone. |
| 30-epoch base + graph-prior max | 3 | 0.5 / 0.5 | 0.93019 | 0.92598 | 0.85695 | 0.71393 | Partial 3-fold evidence; improves over both available partial base and partial graph-prior means. Needs full graph-prior folds or a rerun to verify. |

This suggests the graph prior may be most useful as a complementary score signal rather than as a standalone long-training replacement.
