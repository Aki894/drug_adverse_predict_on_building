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

### PU-Style Negative BCE Weighting

Implementation commit: `b0545a1 Add PU-style negative BCE weighting`

Planned queued command:

```bash
python -u pythonPredict/DGAPred\(Compare\)/src/main.py --run_name solo5_pu_weighted --epochs 5 --batch_size 256 --test_batch_size 512 --torch_threads 4 --torch_interop_threads 1 --no-pin_memory --disable_tqdm --use_pu_negative_weighting --use_calibrated_threshold --threshold_metric mcc --threshold_min 0.1 --threshold_max 0.9 --threshold_steps 81
```

Purpose: test whether treating suspicious unobserved negatives as lower-confidence negatives improves ranking metrics beyond threshold calibration alone.
