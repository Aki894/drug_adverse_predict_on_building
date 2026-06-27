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
    drug_ids = data.get("drug_id")
    side_ids = data.get("side_id")
    sample_ids = None
    if drug_ids is not None and side_ids is not None:
        sample_ids = np.stack(
            [np.asarray(drug_ids, dtype=np.int64), np.asarray(side_ids, dtype=np.int64)],
            axis=1,
        )
    return labels, scores, sample_ids


def align_loaded_folds(loaded_a, loaded_b, fold):
    labels_a, scores_a, sample_ids_a = loaded_a
    labels_b, scores_b, sample_ids_b = loaded_b

    if sample_ids_a is not None and sample_ids_b is not None:
        order_a = np.lexsort((sample_ids_a[:, 1], sample_ids_a[:, 0]))
        order_b = np.lexsort((sample_ids_b[:, 1], sample_ids_b[:, 0]))
        sorted_ids_a = sample_ids_a[order_a]
        sorted_ids_b = sample_ids_b[order_b]
        if sorted_ids_a.shape != sorted_ids_b.shape or not np.array_equal(sorted_ids_a, sorted_ids_b):
            raise ValueError(f"Fold {fold} sample IDs do not match between outputs")

        labels_a = labels_a[order_a]
        labels_b = labels_b[order_b]
        scores_a = scores_a[order_a]
        scores_b = scores_b[order_b]

    if labels_a.shape != labels_b.shape or not np.array_equal(labels_a, labels_b):
        raise ValueError(f"Fold {fold} labels do not match between outputs")

    return labels_a, scores_a, scores_b


def rank_percentile(scores):
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty_like(order, dtype=np.float32)
    ranks[order] = np.arange(len(scores), dtype=np.float32)
    if len(scores) <= 1:
        return np.zeros_like(scores, dtype=np.float32)
    return ranks / float(len(scores) - 1)


def transform_scores(scores, transform):
    scores = np.asarray(scores, dtype=np.float32)
    if transform == "none":
        return scores
    if transform == "minmax":
        score_min = float(np.min(scores))
        score_max = float(np.max(scores))
        return (scores - score_min) / (score_max - score_min + 1e-12)
    if transform == "zscore":
        return (scores - float(np.mean(scores))) / (float(np.std(scores)) + 1e-12)
    if transform == "rank":
        return rank_percentile(scores)
    raise ValueError(f"Unknown score transform: {transform}")


def fuse_scores(scores_a, scores_b, weight_a, score_transform):
    transformed_a = transform_scores(scores_a, score_transform)
    transformed_b = transform_scores(scores_b, score_transform)
    return weight_a * transformed_a + (1.0 - weight_a) * transformed_b


def metrics_at_threshold(labels, scores, threshold):
    pred = scores >= threshold
    return {
        "auc": metrics.roc_auc_score(labels, scores),
        "aupr": metrics.average_precision_score(labels, scores),
        "acc": metrics.accuracy_score(labels, pred),
        "mcc": metrics.matthews_corrcoef(labels, pred),
    }


def binary_score_at_threshold(labels, scores, threshold, metric):
    pred = scores >= threshold
    if metric == "mcc":
        return metrics.matthews_corrcoef(labels, pred)
    return metrics.accuracy_score(labels, pred)


def select_threshold(labels, scores, metric, threshold_min, threshold_max, threshold_steps):
    thresholds = np.linspace(threshold_min, threshold_max, threshold_steps)
    best_threshold = 0.5
    best_score = -np.inf

    for threshold in thresholds:
        score = binary_score_at_threshold(labels, scores, threshold, metric)
        if (score > best_score) or (
            np.isclose(score, best_score)
            and abs(threshold - 0.5) < abs(best_threshold - 0.5)
        ):
            best_threshold = float(threshold)
            best_score = float(score)

    return best_threshold, metrics_at_threshold(labels, scores, best_threshold)


def evaluate_weight(output_a, output_b, weight_a, threshold, folds, calibrate_args=None, score_transform="none"):
    rows = []
    for fold in range(1, folds + 1):
        loaded_a = load_fold(output_a, fold)
        loaded_b = load_fold(output_b, fold)
        if loaded_a is None or loaded_b is None:
            continue

        labels_a, scores_a, scores_b = align_loaded_folds(loaded_a, loaded_b, fold)

        scores = fuse_scores(scores_a, scores_b, weight_a, score_transform)
        if calibrate_args is None:
            fold_threshold = threshold
            fold_metrics = metrics_at_threshold(labels_a, scores, fold_threshold)
        else:
            fold_threshold, fold_metrics = select_threshold(
                labels_a,
                scores,
                metric=calibrate_args["metric"],
                threshold_min=calibrate_args["min"],
                threshold_max=calibrate_args["max"],
                threshold_steps=calibrate_args["steps"],
            )
        rows.append((fold, fold_threshold, fold_metrics))

    if not rows:
        raise SystemExit("No matching fold prediction files were found")

    mean_metrics = {
        key: float(np.mean([metrics_row[key] for _, _, metrics_row in rows]))
        for key in ["auc", "aupr", "acc", "mcc"]
    }
    mean_threshold = float(np.mean([threshold_row for _, threshold_row, _ in rows]))
    return rows, mean_metrics, mean_threshold


def fit_threshold_from_rows(rows, metric, threshold_min, threshold_max, threshold_steps):
    labels = np.concatenate([row[0] for row in rows], axis=0)
    scores = np.concatenate([row[1] for row in rows], axis=0)
    return select_threshold(labels, scores, metric, threshold_min, threshold_max, threshold_steps)


def evaluate_leave_one_fold_cv(
    output_a,
    output_b,
    weights,
    threshold,
    folds,
    calibrate_args=None,
    selection_metric="aupr",
    score_transform="none",
):
    fold_rows = []
    for heldout_fold in range(1, folds + 1):
        train_rows = []
        test_row = None
        for fold in range(1, folds + 1):
            loaded_a = load_fold(output_a, fold)
            loaded_b = load_fold(output_b, fold)
            if loaded_a is None or loaded_b is None:
                continue
            labels_a, scores_a, scores_b = align_loaded_folds(loaded_a, loaded_b, fold)
            weight_metrics = []
            for weight in weights:
                scores = fuse_scores(scores_a, scores_b, float(weight), score_transform)
                if calibrate_args is None:
                    metrics_row = metrics_at_threshold(labels_a, scores, threshold)
                else:
                    _, metrics_row = select_threshold(
                        labels_a,
                        scores,
                        metric=calibrate_args["metric"],
                        threshold_min=calibrate_args["min"],
                        threshold_max=calibrate_args["max"],
                        threshold_steps=calibrate_args["steps"],
                    )
                weight_metrics.append((float(weight), labels_a, scores, metrics_row))
            if fold == heldout_fold:
                test_row = weight_metrics
            else:
                train_rows.append(weight_metrics)

        if not train_rows or test_row is None:
            continue

        best_weight = None
        best_score = -np.inf
        for weight in weights:
            weight = float(weight)
            scores = []
            for fold_metrics in train_rows:
                for candidate_weight, labels_a, candidate_scores, metrics_row in fold_metrics:
                    if np.isclose(candidate_weight, weight):
                        scores.append(metrics_row[selection_metric])
                        break
            mean_score = float(np.mean(scores))
            if mean_score > best_score:
                best_score = mean_score
                best_weight = weight

        chosen_test = None
        for candidate_weight, labels_a, candidate_scores, metrics_row in test_row:
            if np.isclose(candidate_weight, best_weight):
                if calibrate_args is None:
                    chosen_test = (labels_a, candidate_scores, metrics_row, threshold)
                else:
                    train_pairs = []
                    for fold_metrics in train_rows:
                        for cw, tr_labels, tr_scores, tr_metrics in fold_metrics:
                            if np.isclose(cw, best_weight):
                                train_pairs.append((tr_labels, tr_scores))
                    fold_threshold, _ = fit_threshold_from_rows(
                        train_pairs,
                        metric=calibrate_args["metric"],
                        threshold_min=calibrate_args["min"],
                        threshold_max=calibrate_args["max"],
                        threshold_steps=calibrate_args["steps"],
                    )
                    chosen_test = (labels_a, candidate_scores, metrics_row, fold_threshold)
                break

        if chosen_test is None:
            continue

        labels, scores, _, fold_threshold = chosen_test
        fold_metrics = metrics_at_threshold(labels, scores, fold_threshold)
        fold_rows.append((heldout_fold, best_weight, fold_threshold, fold_metrics))

    if not fold_rows:
        raise SystemExit("No fold results were produced for leave-one-fold CV")

    mean_metrics = {
        key: float(np.mean([fold_metrics[key] for _, _, _, fold_metrics in fold_rows]))
        for key in ["auc", "aupr", "acc", "mcc"]
    }
    mean_weight = float(np.mean([weight for _, weight, _, _ in fold_rows]))
    mean_threshold = float(np.mean([threshold_row for _, _, threshold_row, _ in fold_rows]))
    return fold_rows, mean_metrics, mean_weight, mean_threshold


def main():
    parser = argparse.ArgumentParser(description="Evaluate weighted prediction ensembles across DGAPred folds.")
    parser.add_argument("--output_a", required=True, help="First DGAPred output directory")
    parser.add_argument("--output_b", required=True, help="Second DGAPred output directory")
    parser.add_argument("--weight_a", type=float, default=0.5, help="Score weight for output_a; output_b gets 1-weight_a")
    parser.add_argument("--sweep_weights", action="store_true", help="Evaluate a grid of weight_a values")
    parser.add_argument("--leave_one_fold_cv", action="store_true", help="Select weight per held-out fold using the other folds")
    parser.add_argument("--weight_min", type=float, default=0.0, help="Minimum weight_a when sweeping")
    parser.add_argument("--weight_max", type=float, default=1.0, help="Maximum weight_a when sweeping")
    parser.add_argument("--weight_steps", type=int, default=11, help="Number of weight_a values when sweeping")
    parser.add_argument("--threshold", type=float, default=0.5, help="Decision threshold for ACC/MCC")
    parser.add_argument("--score_transform", choices=["none", "minmax", "zscore", "rank"], default="none",
                        help="Per-fold score transform before weighted fusion")
    parser.add_argument("--calibrate_threshold", action="store_true", help="Select threshold per fold on provided labels")
    parser.add_argument("--threshold_metric", choices=["acc", "mcc"], default="mcc", help="Metric for threshold selection")
    parser.add_argument("--threshold_min", type=float, default=0.1, help="Minimum threshold for calibration")
    parser.add_argument("--threshold_max", type=float, default=0.9, help="Maximum threshold for calibration")
    parser.add_argument("--threshold_steps", type=int, default=81, help="Number of threshold grid points")
    parser.add_argument("--folds", type=int, default=5, help="Maximum number of folds to inspect")
    args = parser.parse_args()

    calibrate_args = None
    if args.calibrate_threshold:
        calibrate_args = {
            "metric": args.threshold_metric,
            "min": args.threshold_min,
            "max": args.threshold_max,
            "steps": args.threshold_steps,
        }

    if args.sweep_weights:
        weights = np.linspace(args.weight_min, args.weight_max, args.weight_steps)
    else:
        weights = np.asarray([args.weight_a], dtype=np.float32)

    if args.leave_one_fold_cv:
        rows, mean_metrics, mean_weight, mean_threshold = evaluate_leave_one_fold_cv(
            output_a=args.output_a,
            output_b=args.output_b,
            weights=weights,
            threshold=args.threshold,
            folds=args.folds,
            calibrate_args=calibrate_args,
            selection_metric=args.threshold_metric if calibrate_args is not None else "aupr",
            score_transform=args.score_transform,
        )
        for fold, weight, fold_threshold, fold_metrics in rows:
            print(
                f"Fold {fold}: selected_weight={weight:.4f}, "
                f"AUC: {fold_metrics['auc']:.5f}, AUPR: {fold_metrics['aupr']:.5f}, "
                f"ACC: {fold_metrics['acc']:.5f}, MCC: {fold_metrics['mcc']:.5f}, "
                f"threshold: {fold_threshold:.3f}"
            )
        print(
            "LeaveOneFoldCV Mean: "
            f"AUC: {mean_metrics['auc']:.5f}, "
            f"AUPR: {mean_metrics['aupr']:.5f}, "
            f"ACC: {mean_metrics['acc']:.5f}, "
            f"MCC: {mean_metrics['mcc']:.5f}, "
            f"mean_weight: {mean_weight:.4f}, "
            f"threshold_mean: {mean_threshold:.3f}, "
            f"n_folds: {len(rows)}"
        )
        return

    summaries = []
    for weight in weights:
        rows, mean_metrics, mean_threshold = evaluate_weight(
            output_a=args.output_a,
            output_b=args.output_b,
            weight_a=float(weight),
            threshold=args.threshold,
            folds=args.folds,
            calibrate_args=calibrate_args,
            score_transform=args.score_transform,
        )
        summaries.append((float(weight), mean_metrics, mean_threshold, len(rows)))

        if not args.sweep_weights:
            for fold, fold_threshold, fold_metrics in rows:
                print(
                    f"Fold {fold}: AUC: {fold_metrics['auc']:.5f}, "
                    f"AUPR: {fold_metrics['aupr']:.5f}, ACC: {fold_metrics['acc']:.5f}, "
                    f"MCC: {fold_metrics['mcc']:.5f}, threshold: {fold_threshold:.3f}"
                )

        print(
            f"WeightA {float(weight):.4f}: "
            f"AUC: {mean_metrics['auc']:.5f}, "
            f"AUPR: {mean_metrics['aupr']:.5f}, "
            f"ACC: {mean_metrics['acc']:.5f}, "
            f"MCC: {mean_metrics['mcc']:.5f}, "
            f"threshold_mean: {mean_threshold:.3f}, "
            f"n_folds: {len(rows)}"
        )

    best_auc = max(summaries, key=lambda item: item[1]["auc"])
    best_aupr = max(summaries, key=lambda item: item[1]["aupr"])
    best_mcc = max(summaries, key=lambda item: item[1]["mcc"])
    print(
        "BestByAUC: "
        f"weight_a={best_auc[0]:.4f}, AUC={best_auc[1]['auc']:.5f}, "
        f"AUPR={best_auc[1]['aupr']:.5f}, ACC={best_auc[1]['acc']:.5f}, MCC={best_auc[1]['mcc']:.5f}"
    )
    print(
        "BestByAUPR: "
        f"weight_a={best_aupr[0]:.4f}, AUC={best_aupr[1]['auc']:.5f}, "
        f"AUPR={best_aupr[1]['aupr']:.5f}, ACC={best_aupr[1]['acc']:.5f}, MCC={best_aupr[1]['mcc']:.5f}"
    )
    print(
        "BestByMCC: "
        f"weight_a={best_mcc[0]:.4f}, AUC={best_mcc[1]['auc']:.5f}, "
        f"AUPR={best_mcc[1]['aupr']:.5f}, ACC={best_mcc[1]['acc']:.5f}, MCC={best_mcc[1]['mcc']:.5f}"
    )


if __name__ == "__main__":
    main()
