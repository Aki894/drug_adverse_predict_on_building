# Source Map

| Source ID | Path / URL | Type | Used For | Notes |
|---|---|---|---|---|
| S1 | pythonPredict/DGAPred(Compare)/src/main.py | code | Training pipeline, sampling, metrics | Contains D4 contrastive and negative sampling hooks. |
| S2 | pythonPredict/DGAPred(Compare)/src/model/model.py | code | Model architecture | Feature interaction attention, ARConv, contrastive learning. |
| S3 | pythonPredict/drug_side.csv | dataset cache | Label matrix | 453 drugs x 1019 ADRs, sparse observed positives. |
| S4 | pythonPredict/drug_rdkit.csv, drug_DGen_sim.csv, drug_ge_sim.csv | feature matrices | Drug similarity evidence | Used for false-negative risk scoring. |
| S5 | pythonPredict/side_mesh_sim.csv, adr_GDisease_sim.csv | feature matrices | ADR similarity evidence | Available for later ADR-side risk scoring. |
| S6 | pythonPredict/DGAPred(Compare)/dataset_analysis_report.txt | local analysis | Dataset risks | Documents unlabeled-zero pseudo-negative risk and low-support ADRs. |
| W1 | Web search: reliable negative samples adverse drug reaction prediction PU learning | web evidence | SOTA direction | Supports PU/reliable-negative framing for unlabeled drug-ADR pairs. |
| W2 | Web search: positive unlabeled learning drug side effect prediction negative samples | web evidence | SOTA direction | Supports treating unknown interactions differently from verified negatives. |
| W3 | https://link.springer.com/article/10.1186/s12859-018-2563-x | paper | Reliable negative samples for drug side-effect prediction | Directly supports using similarity evidence to address unlabeled negative noise. |
| W4 | https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0177678 | paper | MCC-aware thresholding | Supports grid-search threshold selection for MCC-oriented imbalanced classification. |
| E1 | Remote output: /data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_092120_solo5_calibrated_threshold/results.txt | experiment | 5-epoch calibrated-threshold screen | Mean AUC 0.91262, AUPR 0.90820, ACC 0.83518, MCC 0.67062. |
| E2 | Remote output: /data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_084455_solo5_foldlocal_base/results.txt | experiment | 5-epoch fold-local base screen | Mean AUC 0.91102, AUPR 0.90658, ACC 0.82887, MCC 0.66108. |
| E3 | Remote output: /data/ccc/ADR/pythonPredict/DGAPred(Compare)/2drug-2side/DGAPred/data/output_20260624_090556_solo5_d4_neg_nopin/results.txt | experiment | 5-epoch D4 negative weighting screen | Mean AUC 0.91138, AUPR 0.90698, ACC 0.82806, MCC 0.66116. |
