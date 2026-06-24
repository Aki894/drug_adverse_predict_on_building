# SOTA Gap Map

| Candidate Contribution | What SOTA Already Does | User Evidence | Real Gap | Claim Strength | Risk |
|---|---|---|---|---|---|
| Reliable negative sampling for ADR prediction | PU learning and reliable-negative selection are known for unlabeled biomedical links | dataset_analysis_report flags unlabeled zeros and high-risk negatives | Current DGAPred still samples random zeros | High | Need fold-wise ablation to prove gain |
| Debiased contrastive learning | DCL handles false negatives in contrastive batches | model.py already has standard/debiased InfoNCE switch | Current contrastive view is only noisy fused feature | Medium | May not improve if auxiliary loss dominates |
| Multi-view feature interaction attention | Cross-view attention is common in drug-target and multimodal learning | model.py has drug-to-side and side-to-drug attention | Need show which component helps ADR task | Medium | More modules can overfit |
| ADR-side risk scoring | Similar ADRs may transfer association evidence | side_mesh and GDA matrices are present | Current D4 negative risk uses only drug similarity | Medium | Extra scoring may overfilter hard negatives |
| Fold-local threshold calibration | MCC/threshold optimization is known for imbalanced binary classification | DGAPred reports ACC/MCC from a fixed 0.5 threshold | The probability scale is not calibrated for fold-specific ADR decisions | High for ACC/MCC, low for AUC/AUPR | Must avoid test-threshold tuning; calibrate only on training-fold predictions |

## Gap Summary

The first practical gap tested was negative sampling reliability under sparse positive-observed ADR labels. It produced only a very small ranking-metric gain in 5-epoch screening. The stronger current gap is that DGAPred converts probabilities to ACC/MCC decisions with a fixed 0.5 threshold, although fold-specific score calibration can improve threshold-dependent metrics without changing the ranking model or touching test labels.
