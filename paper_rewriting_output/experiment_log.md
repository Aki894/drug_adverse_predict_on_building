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
- Four-fold mean: AUC 0.92890, AUPR 0.92506, ACC 0.85489, MCC 0.70990.

Interim interpretation: the first four base folds are extremely close to the corresponding calibrated-threshold folds, with calibrated threshold now slightly higher on all four means. Do not finalize threshold calibration as the paper's main contribution until the base comparator completes all five folds. If the five-fold base remains comparable or better, move the main experimental effort toward support-aware ADR weighting, side-aware pseudo-negative risk, or a fold-local graph-propagation prior that can affect ranking metrics as well as decision metrics.

### Support-Aware ADR Weighting

Implementation status: locally implemented as a switchable follow-up in `pythonPredict/DGAPred(Compare)/src/main.py`.

Planned 5-epoch screening command:

```bash
python -u pythonPredict/DGAPred\(Compare\)/src/main.py --run_name solo5_support_weighted --epochs 5 --batch_size 256 --test_batch_size 512 --torch_threads 4 --torch_interop_threads 1 --no-pin_memory --disable_tqdm --use_support_aware_weighting
```

Purpose: test whether fold-local ADR support statistics improve sparse-ADR learning. Low-support ADR positives receive a conservative BCE weight boost; unobserved negatives under low- or zero-support ADRs receive a conservative confidence discount. The default parameters are intentionally mild: `support_threshold=5`, `support_positive_boost=0.25`, `support_negative_discount=0.15`, and `support_negative_min_weight=0.3`.

Validation status: syntax check passed locally with `PYTHONPYCACHEPREFIX=/tmp/dgapred_pycache python3 -m py_compile pythonPredict/DGAPred\(Compare\)/src/main.py`. Remote run should wait until the 30-epoch base comparator finishes or be launched only if spare GPU capacity is available.
