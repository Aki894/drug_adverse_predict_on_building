"""Evaluate score-level ensembles from saved DGAPred fold prediction files."""

import argparse
import os
import pickle

import numpy as np
from sklearn import metrics


def load_fold(output_dir, fold):
    path = os.path.join(output_dir, f"testdata_fold{fold}.pkl")
    if not os.path.exists(path):
        return None
    with open(path, "rb") as handle:
        data = pickle.load(handle)
    labels = (np.asarray(data["ground_truth"]) > 0).astype(np.int32)
    scores = np.asarray(data["pred_value"], dtype=np.float32)
    return labels, scores


def metrics_at_threshold(labels, scores, threshold):
    pred = scores >= threshold
    return {
        "auc": metrics.roc_auc_score(labels, scores),
        "aupr": metrics.average_precision_score(labels, scores),
        "acc": metrics.accuracy_score(labels, pred),
        "mcc": metrics.matthews_corrcoef(labels, pred),
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate weighted prediction ensembles across DGAPred folds.")
    parser.add_argument("--output_a", required=True, help="First DGAPred output directory")
    parser.add_argument("--output_b", required=True, help="Second DGAPred output directory")
    parser.add_argument("--weight_a", type=float, default=0.5, help="Score weight for output_a; output_b gets 1-weight_a")
    parser.add_argument("--threshold", type=float, default=0.5, help="Decision threshold for ACC/MCC")
    parser.add_argument("--folds", type=int, default=5, help="Maximum number of folds to inspect")
    args = parser.parse_args()

    rows = []
    for fold in range(1, args.folds + 1):
        loaded_a = load_fold(args.output_a, fold)
        loaded_b = load_fold(args.output_b, fold)
        if loaded_a is None or loaded_b is None:
            continue

        labels_a, scores_a = loaded_a
        labels_b, scores_b = loaded_b
        if labels_a.shape != labels_b.shape or not np.array_equal(labels_a, labels_b):
            raise ValueError(f"Fold {fold} labels do not match between outputs")

        scores = args.weight_a * scores_a + (1.0 - args.weight_a) * scores_b
        fold_metrics = metrics_at_threshold(labels_a, scores, args.threshold)
        rows.append(fold_metrics)
        print(
            f"Fold {fold}: AUC: {fold_metrics['auc']:.5f}, "
            f"AUPR: {fold_metrics['aupr']:.5f}, ACC: {fold_metrics['acc']:.5f}, "
            f"MCC: {fold_metrics['mcc']:.5f}, threshold: {args.threshold:.3f}"
        )

    if not rows:
        raise SystemExit("No matching fold prediction files were found")

    print(
        "Mean: "
        f"AUC: {np.mean([r['auc'] for r in rows]):.5f}, "
        f"AUPR: {np.mean([r['aupr'] for r in rows]):.5f}, "
        f"ACC: {np.mean([r['acc'] for r in rows]):.5f}, "
        f"MCC: {np.mean([r['mcc'] for r in rows]):.5f}, "
        f"n_folds: {len(rows)}"
    )


if __name__ == "__main__":
    main()
