# Experiment Log

## 2026-06-24 Remote Screening

Remote host: `server-NER`

Remote project root: `/data/ccc/ADR`

Conda environment: `/root/miniconda3/envs/adr`

### Base 5-Epoch Fold-Local Sampling

Command family:

```bash
python pythonPredict/DGAPred\(Compare\)/src/main.py --run_name solo5_foldlocal_base --epochs 5 --batch_size 256 --test_batch_size 512 --torch_threads 4 --torch_interop_threads 1
```

Mean metrics: AUC 0.91102, AUPR 0.90658, ACC 0.82887, MCC 0.66108.

### D4 Similarity Negative Weighting

Command family:

```bash
python pythonPredict/DGAPred\(Compare\)/src/main.py --run_name solo5_d4_neg_nopin --epochs 5 --batch_size 256 --test_batch_size 512 --torch_threads 4 --torch_interop_threads 1 --no-pin_memory --use_d4_similarity_negative_weighting
```

Mean metrics: AUC 0.91138, AUPR 0.90698, ACC 0.82806, MCC 0.66116.

Conclusion: not enough gain for the main improvement direction.

### Fold-Local Threshold Calibration

Command:

```bash
python pythonPredict/DGAPred\(Compare\)/src/main.py --run_name solo5_calibrated_threshold --epochs 5 --batch_size 256 --test_batch_size 512 --torch_threads 4 --torch_interop_threads 1 --no-pin_memory --use_calibrated_threshold --threshold_metric mcc --threshold_min 0.1 --threshold_max 0.9 --threshold_steps 81
```

Mean metrics: AUC 0.91262, AUPR 0.90820, ACC 0.83518, MCC 0.67062.

Conclusion: strongest current signal. Needs a 30-epoch confirmation run.

30-epoch in-progress evidence:

- Remote output: `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_102434_e30_calibrated_threshold_quiet_u/results.txt`
- Fold 1: AUC 0.92582, AUPR 0.92032, ACC 0.85157, MCC 0.70317, threshold 0.510.
- Fold 2: AUC 0.92957, AUPR 0.92745, ACC 0.85574, MCC 0.71240, threshold 0.420.
- Fold 3: AUC 0.93004, AUPR 0.92620, ACC 0.85403, MCC 0.70837, threshold 0.450.
- Fold 4: AUC 0.93180, AUPR 0.92668, ACC 0.85948, MCC 0.71898, threshold 0.480.
- Fold 5: AUC 0.93393, AUPR 0.93148, ACC 0.85852, MCC 0.71712, threshold 0.530.
- Five-fold mean: AUC 0.93023, AUPR 0.92643, ACC 0.85587, MCC 0.71201.

### PU-Style Negative BCE Weighting

Implementation commit: `b0545a1 Add PU-style negative BCE weighting`

Planned queued command:

```bash
python -u pythonPredict/DGAPred\(Compare\)/src/main.py --run_name solo5_pu_weighted --epochs 5 --batch_size 256 --test_batch_size 512 --torch_threads 4 --torch_interop_threads 1 --no-pin_memory --disable_tqdm --use_pu_negative_weighting --use_calibrated_threshold --threshold_metric mcc --threshold_min 0.1 --threshold_max 0.9 --threshold_steps 81
```

Purpose: test whether treating suspicious unobserved negatives as lower-confidence negatives improves ranking metrics beyond threshold calibration alone.

Status update:

- The first queued PU run exposed a calibration-path bug: enabling PU adds a fourth `sample_weight` tensor to the training loader, while `test()` still assumed three tensors when reused for training-fold threshold calibration.
- Fix commit: `503fab3 Record final DGAPred threshold run`; `test()` now accepts both three-column and four-column batches.
- Restarted remote screen: `solo5_pu_weighted_fixed`, output directory `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_115459_solo5_pu_weighted_fixed/`.
- Final fixed five-fold result: AUC 0.91042, AUPR 0.90573, ACC 0.83285, MCC 0.66598.
- Conclusion: negative ablation. It is below the 5-epoch calibrated-threshold run (AUC 0.91262, AUPR 0.90820, ACC 0.83518, MCC 0.67062), so PU-style negative BCE should not be promoted without redesign.

### 30-Epoch Fold-Local Base Comparator

Command:

```bash
python -u pythonPredict/DGAPred\(Compare\)/src/main.py --run_name e30_base_quiet_u --epochs 30 --batch_size 256 --test_batch_size 512 --torch_threads 4 --torch_interop_threads 1 --no-pin_memory --disable_tqdm
```

Purpose: compare against the completed 30-epoch calibrated-threshold run under the same batch/thread/pin-memory settings, isolating the contribution of fold-local MCC threshold calibration to ACC/MCC.

Status: running on `server-NER`.

- Remote output: `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_121030_e30_base_quiet_u/results.txt`
- Fold 1: AUC 0.92779, AUPR 0.92238, ACC 0.85435, MCC 0.70882, threshold 0.500.
- Fold 2: AUC 0.93009, AUPR 0.92735, ACC 0.85873, MCC 0.71754, threshold 0.500.
- Fold 3: AUC 0.93056, AUPR 0.92596, ACC 0.85649, MCC 0.71329, threshold 0.500.
- Fold 4: AUC 0.92714, AUPR 0.92456, ACC 0.84997, MCC 0.69996, threshold 0.500.
- Fold 5: AUC 0.93268, AUPR 0.92958, ACC 0.85798, MCC 0.71741, threshold 0.500.
- Five-fold mean: AUC 0.92965, AUPR 0.92597, ACC 0.85550, MCC 0.71140.

Interpretation: compared with the completed 30-epoch calibrated-threshold run (AUC 0.93023, AUPR 0.92643, ACC 0.85587, MCC 0.71201), calibrated threshold is only slightly higher: +0.00058 AUC, +0.00046 AUPR, +0.00037 ACC, and +0.00061 MCC. Keep it as a useful decision-layer component, but continue searching for a stronger method-level contribution that improves ranking metrics.

### Support-Aware ADR Weighting

Implementation status: locally implemented as a switchable follow-up in `pythonPredict/DGAPred(Compare)/src/main.py`.

Planned 5-epoch screening command:

```bash
python -u pythonPredict/DGAPred\(Compare\)/src/main.py --run_name solo5_support_weighted --epochs 5 --batch_size 256 --test_batch_size 512 --torch_threads 4 --torch_interop_threads 1 --no-pin_memory --disable_tqdm --use_support_aware_weighting
```

Purpose: test whether fold-local ADR support statistics improve sparse-ADR learning. Low-support ADR positives receive a conservative BCE weight boost; unobserved negatives under low- or zero-support ADRs receive a conservative confidence discount. The default parameters are intentionally mild: `support_threshold=5`, `support_positive_boost=0.25`, `support_negative_discount=0.15`, and `support_negative_min_weight=0.3`.

Validation status: syntax check passed locally with `PYTHONPYCACHEPREFIX=/tmp/dgapred_pycache python3 -m py_compile pythonPredict/DGAPred\(Compare\)/src/main.py`. Remote screen `solo5_support_weighted` started after the base comparator finished.

Remote run:

- Log: `/data/ccc/ADR/logs/solo5_support_weighted_20260624_133132.log`
- Output: `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_133135_solo5_support_weighted/`
- Fold 1 startup weight diagnostics: low-support ADR count 508, zero-support negative samples 913, mean weights all/positive/negative 0.9764/1.0060/0.9469.
- Final five-fold screen: AUC 0.91005, AUPR 0.90612, ACC 0.82697, MCC 0.65855.
- Interpretation: negative ablation. It is below the 5-epoch fold-local base (AUC 0.91102, AUPR 0.90658, ACC 0.82887, MCC 0.66108), so the current conservative support-aware weighting should not be promoted.

### Fold-Local Graph Prior

Implementation status: locally implemented as a switchable follow-up in `pythonPredict/DGAPred(Compare)/src/main.py`.

Planned 5-epoch screening command:

```bash
python -u pythonPredict/DGAPred\(Compare\)/src/main.py --run_name solo5_graph_prior --epochs 5 --batch_size 256 --test_batch_size 512 --torch_threads 4 --torch_interop_threads 1 --no-pin_memory --disable_tqdm --use_graph_prior --graph_prior_weight 0.5 --graph_prior_combine max
```

Purpose: test whether a fold-local prior propagated over drug and ADR similarity graphs can improve ranking metrics. The prior is computed only from the current training fold positives, then added as a small centered logit residual (`weight * (prior - 0.5)`) during training and testing.

First graph-prior calibrated attempt:

- Command used `--use_graph_prior --use_calibrated_threshold`.
- It failed after fold 1 training because training-fold threshold calibration passes the 5-column graph-prior training loader into `test()`, while `test()` handled only 3-column test batches and 4-column prior/weight batches.
- Fix: `test()` now accepts 5-column batches as `(drug, side, label, sample_weight, graph_prior)` and uses the final column as the graph prior.
- Remote GitHub pull temporarily hung at commit `adc4b7d`, so the fixed `main.py` was backed up and uploaded to `server-NER` by `scp`; remote syntax check passed with `python -m py_compile`.
- Restarted fixed screen: log `/data/ccc/ADR/logs/solo5_graph_prior_calibrated_fixed_20260624_141041.log`.

Five-epoch graph-prior screen:

- Output: `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_134911_solo5_graph_prior/results.txt`
- Final five-fold result: AUC 0.91357, AUPR 0.90903, ACC 0.82870, MCC 0.66187.
- Interpretation: best current short-run method-level direction for ranking metrics. Compared with 5-epoch base (AUC 0.91102, AUPR 0.90658, ACC 0.82887, MCC 0.66108), it improves AUC by 0.00255 and AUPR by 0.00245, with nearly unchanged ACC and a small MCC gain.

Five-epoch graph-prior-plus-calibration screen:

- Output: `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_141045_solo5_graph_prior_calibrated_fixed/results.txt`
- Final five-fold result: AUC 0.91188, AUPR 0.90772, ACC 0.83296, MCC 0.66644.
- Interpretation: above 5-epoch base on all four metrics, but weaker than graph prior alone on AUC/AUPR. Keep it as a possible threshold-metric variant, not the first mainline.

Thirty-epoch graph-prior validation:

```bash
python -u pythonPredict/DGAPred\(Compare\)/src/main.py --run_name e30_graph_prior_quiet_u --epochs 30 --batch_size 256 --test_batch_size 512 --torch_threads 4 --torch_interop_threads 1 --no-pin_memory --disable_tqdm --use_graph_prior --graph_prior_weight 0.5 --graph_prior_combine max
```

- Remote PID: `721883`
- Log: `/data/ccc/ADR/logs/e30_graph_prior_quiet_u_20260624_142522.log`
- Output: `/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_142525_e30_graph_prior_quiet_u/`
- Status check on 2026-06-24: still running. The log reached fold 1 epoch 3 with interim test AUC 0.90641, AUPR 0.89956, ACC 0.82892, MCC 0.65783.

Later status check on 2026-06-24:

- Remote PID `721883` is still running.
- Completed fold 1: AUC 0.92722, AUPR 0.92071, ACC 0.85275, MCC 0.70562.
- Completed fold 2: AUC 0.92939, AUPR 0.92772, ACC 0.85691, MCC 0.71385.
- Completed fold 3: AUC 0.93083, AUPR 0.92578, ACC 0.85467, MCC 0.70942.
- Partial 3-fold mean: AUC 0.92915, AUPR 0.92474, ACC 0.85478, MCC 0.70963.
- Interpretation: weaker than the 30-epoch base comparator so far. Continue the run to 5/5 folds, but prepare a new reliable-negative filtering experiment.

### Reliable Negative Filtering

Implementation status: locally implemented as a switchable follow-up in `pythonPredict/DGAPred(Compare)/src/main.py`.

Mechanism:

- Use only current fold training candidates.
- Compute combined pseudo-negative risk from drug-side and ADR-side similarity evidence.
- Remove candidate negatives above `--reliable_negative_filter_percentile`.
- Sample from the remaining pool to match the number of training positives.
- Keep test fold unchanged.

Planned 5-epoch screening command:

```bash
python -u pythonPredict/DGAPred\(Compare\)/src/main.py --run_name solo5_reliable_neg_p90 --epochs 5 --batch_size 256 --test_batch_size 512 --torch_threads 4 --torch_interop_threads 1 --no-pin_memory --disable_tqdm --use_reliable_negative_filter --reliable_negative_filter_percentile 90
```

Purpose: test whether filtering only the highest-risk unlabeled negatives is more effective than the failed PU-style global BCE weighting.

Remote queue status:

- Queued after active graph-prior PID `721883` finishes, to avoid GPU contention.
- Queue wrapper PID: `842959`.
- Log: `/data/ccc/ADR/logs/solo5_reliable_neg_p90_20260624_151900.log`.

Early-stop status:

- The preceding 30-epoch graph-prior process stalled during fold 4 after completing 3/5 folds; the partial mean was AUC 0.92915, AUPR 0.92474, ACC 0.85478, MCC 0.70963, below the 30-epoch base comparator. It was terminated to unblock the queued experiment.
- Reliable negative filtering started and completed fold 1 with AUC 0.90739, AUPR 0.89877, ACC 0.83031, MCC 0.66253. This is clearly below the 5-epoch base on AUC/AUPR, so the run was terminated as a negative early-stop screen.

### Low-Weight Graph Prior Follow-Up

Rationale: graph prior with weight 0.5 improved 5-epoch AUC/AUPR but underperformed the 30-epoch base in the partial long run. A smaller residual may keep the short-run ranking benefit while reducing over-regularization.

Remote run:

```bash
python -u pythonPredict/DGAPred\(Compare\)/src/main.py --run_name solo5_graph_prior_w02 --epochs 5 --batch_size 256 --test_batch_size 512 --torch_threads 4 --torch_interop_threads 1 --no-pin_memory --disable_tqdm --use_graph_prior --graph_prior_weight 0.2 --graph_prior_combine max
```

- PID: `869136` wrapper / `869141` python.
- Log: `/data/ccc/ADR/logs/solo5_graph_prior_w02_20260624_152739.log`.

Early-stop status:

- Fold 1 finished with AUC 0.90755, AUPR 0.90026, ACC 0.83020, MCC 0.66051.
- This is below the 5-epoch base and below the original graph-prior weight 0.5 screen, so the run was terminated.

### Mean-Aggregated Graph Prior Follow-Up

Rationale: reducing the graph-prior weight weakened the signal. The next test keeps weight 0.5 but changes aggregation from `max` to `mean`, checking whether a smoother prior is more stable than a weaker prior.

Remote run:

```bash
python -u pythonPredict/DGAPred\(Compare\)/src/main.py --run_name solo5_graph_prior_mean --epochs 5 --batch_size 256 --test_batch_size 512 --torch_threads 4 --torch_interop_threads 1 --no-pin_memory --disable_tqdm --use_graph_prior --graph_prior_weight 0.5 --graph_prior_combine mean
```

- PID: `885892` wrapper / `885897` python.
- Log: `/data/ccc/ADR/logs/solo5_graph_prior_mean_20260624_153337.log`.

Early-stop status:

- Fold 1 finished with AUC 0.90724, AUPR 0.90023, ACC 0.82657, MCC 0.65638.
- This is below the 5-epoch base. Mean aggregation was terminated as a negative screen.

### Score-Level Ensemble Evaluation

Implementation status: added `pythonPredict/DGAPred(Compare)/src/evaluate_prediction_ensemble.py` to evaluate fixed-weight score averages from saved `testdata_fold*.pkl` files.

Remote exploratory evaluation:

- 5-epoch base + graph-prior max, 0.5/0.5 score average, 5 folds: AUC 0.91368, AUPR 0.90930, ACC 0.83054, MCC 0.66465.
- 30-epoch base + graph-prior max, 0.5/0.5 score average, 3 available folds: AUC 0.93019, AUPR 0.92598, ACC 0.85695, MCC 0.71393.

Interpretation: score averaging is the most promising new evidence in this turn. It improves the 5-epoch base on all metrics and turns the weak partial 30-epoch graph-prior standalone run into a positive complementary signal over the available folds. It needs full-fold validation before being promoted as the final method.
