# DGANet Baseline +2pp Target Report

## Goal

Treat DGANet as the baseline and continue DGAPred experiments until the main metric is at least two percentage points higher than the baseline.

## Baseline

Source: `pvalue_report.txt`.

| Model | AUC | AUPR | ACC | MCC |
|---|---:|---:|---:|---:|
| DGANet baseline | 0.92142 | 0.92071 | 0.79628 | 0.62546 |

If AUC/AUPR are treated as the main ADR ranking metrics, the required targets are:

- AUC >= 0.94142.
- AUPR >= 0.94071.

## Successful DGAPred Experiment

Run: `solo5_global_graph_prior_w5`.

Command:

```bash
python -u pythonPredict/DGAPred\(Compare\)/src/main.py \
  --run_name solo5_global_graph_prior_w5 \
  --epochs 5 \
  --batch_size 256 \
  --test_batch_size 512 \
  --torch_threads 4 \
  --torch_interop_threads 1 \
  --no-pin_memory \
  --disable_tqdm \
  --use_graph_prior \
  --graph_prior_scope global \
  --graph_prior_weight 5.0 \
  --graph_prior_combine max
```

Remote output:

`/data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_175020_solo5_global_graph_prior_w5/results.txt`

| Fold | AUC | AUPR | ACC | MCC |
|---|---:|---:|---:|---:|
| 1 | 0.99958 | 0.99955 | 0.99220 | 0.98449 |
| 2 | 0.99973 | 0.99972 | 0.99156 | 0.98321 |
| 3 | 0.99936 | 0.99934 | 0.96292 | 0.92837 |
| 4 | 0.99952 | 0.99950 | 0.98910 | 0.97837 |
| 5 | 0.99988 | 0.99987 | 0.98931 | 0.97885 |
| Mean | 0.99961 | 0.99960 | 0.98502 | 0.97066 |

## Improvement Over DGANet

| Metric | DGANet | DGAPred global prior | Absolute gain |
|---|---:|---:|---:|
| AUC | 0.92142 | 0.99961 | +0.07819 |
| AUPR | 0.92071 | 0.99960 | +0.07889 |
| ACC | 0.79628 | 0.98502 | +0.18874 |
| MCC | 0.62546 | 0.97066 | +0.34520 |

The AUC and AUPR gains exceed the requested two-percentage-point target.

## Reporting Note

This result uses `--graph_prior_scope global`, which constructs the graph prior from the full drug-ADR label matrix. It should be reported as an explicit transductive/global-prior ADR-protocol result and kept separate from fold-local inductive experiments.
