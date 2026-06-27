"""Evaluate fold-local ADR label-correlation residual scores.

This script reconstructs DGAPred's balanced five-fold sample split and tests
whether a drug's training-fold ADR profile supports held-out ADR labels through
ADR co-occurrence or side-effect similarity. It does not use model predictions.
"""

import argparse
import os
import pickle
import random

import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.model_selection import StratifiedKFold


SEED = 42


def build_balanced_samples(label_matrix):
    random.seed(SEED)
    np.random.seed(SEED)

    n_samples = label_matrix.shape[0] * label_matrix.shape[1]
    interaction_target = np.zeros((n_samples, 3), dtype=np.int64)

    row = 0
    for drug_idx in range(label_matrix.shape[0]):
        for side_idx in range(label_matrix.shape[1]):
            interaction_target[row] = [drug_idx, side_idx, label_matrix[drug_idx, side_idx]]
            row += 1

    data_shuffle = interaction_target[interaction_target[:, 2].argsort()]
    n_positive = int(np.count_nonzero(data_shuffle[:, 2]))
    n_negative = int(n_samples - n_positive)

    positive_samples = data_shuffle[n_negative:]
    negative_samples = data_shuffle[:n_negative]
    sampled_indices = random.sample(list(range(n_negative)), n_negative)
    balanced_negative = negative_samples[sampled_indices[:n_positive]]
    final_sample = np.vstack((positive_samples, balanced_negative))

    data_x = [(int(row[0]), int(row[1])) for row in final_sample]
    data_y = [int(row[2]) for row in final_sample]
    return final_sample, data_x, data_y


def safe_minmax(matrix):
    matrix = np.asarray(matrix, dtype=np.float32)
    matrix = np.nan_to_num(matrix, nan=0.0, posinf=0.0, neginf=0.0)
    min_value = float(np.min(matrix))
    max_value = float(np.max(matrix))
    return (matrix - min_value) / (max_value - min_value + 1e-12)


def cosine_label_correlation(train_positive, n_drugs, n_sides, smooth):
    profile = np.zeros((n_drugs, n_sides), dtype=np.float32)
    if len(train_positive) > 0:
        profile[train_positive[:, 0].astype(int), train_positive[:, 1].astype(int)] = 1.0

    counts = profile.T @ profile
    support = np.sqrt(np.diag(counts) + smooth)
    corr = counts / (support[:, None] * support[None, :] + 1e-12)
    np.fill_diagonal(corr, 0.0)
    return safe_minmax(corr), profile


def jaccard_label_correlation(train_positive, n_drugs, n_sides, smooth):
    profile = np.zeros((n_drugs, n_sides), dtype=np.float32)
    if len(train_positive) > 0:
        profile[train_positive[:, 0].astype(int), train_positive[:, 1].astype(int)] = 1.0

    intersect = profile.T @ profile
    side_support = np.diag(intersect)
    union = side_support[:, None] + side_support[None, :] - intersect
    corr = (intersect + smooth) / (union + smooth + 1e-12)
    np.fill_diagonal(corr, 0.0)
    return safe_minmax(corr), profile


def conditional_label_correlation(train_positive, n_drugs, n_sides, smooth):
    profile = np.zeros((n_drugs, n_sides), dtype=np.float32)
    if len(train_positive) > 0:
        profile[train_positive[:, 0].astype(int), train_positive[:, 1].astype(int)] = 1.0

    counts = profile.T @ profile
    known_support = profile.sum(axis=0)
    corr = (counts + smooth) / (known_support[None, :] + smooth * n_sides + 1e-12)
    np.fill_diagonal(corr, 0.0)
    return safe_minmax(corr), profile


def bidirectional_conditional_label_correlation(train_positive, n_drugs, n_sides, smooth, mode):
    forward, profile = conditional_label_correlation(train_positive, n_drugs, n_sides, smooth)
    reverse = forward.T
    if mode == "product":
        corr = np.sqrt(np.clip(forward * reverse, 0.0, None))
    elif mode == "hmean":
        corr = (2.0 * forward * reverse) / (forward + reverse + 1e-12)
    else:
        raise ValueError(f"Unknown bidirectional conditional mode: {mode}")
    np.fill_diagonal(corr, 0.0)
    return safe_minmax(corr), profile


def lift_label_correlation(train_positive, n_drugs, n_sides, smooth):
    profile = np.zeros((n_drugs, n_sides), dtype=np.float32)
    if len(train_positive) > 0:
        profile[train_positive[:, 0].astype(int), train_positive[:, 1].astype(int)] = 1.0

    counts = profile.T @ profile
    support = profile.sum(axis=0)
    expected = (support[:, None] * support[None, :]) / max(float(n_drugs), 1.0)
    lift = (counts + smooth) / (expected + smooth + 1e-12)
    corr = np.log1p(lift)
    np.fill_diagonal(corr, 0.0)
    return safe_minmax(corr), profile


def load_external_similarity(similarity_path, source):
    if source == "mesh":
        return safe_minmax(pd.read_csv(f"{similarity_path}/side_mesh_sim.csv", header=0, index_col=0).values)
    if source == "gda":
        return safe_minmax(pd.read_csv(f"{similarity_path}/adr_GDisease_sim.csv", header=0, index_col=0).values)
    raise ValueError(f"Unsupported external similarity source: {source}")


def build_drug_similarity(similarity_path):
    matrices = []
    for filename in ("drug_rdkit.csv", "drug_DGen_sim.csv", "drug_ge_sim.csv"):
        matrix = pd.read_csv(f"{similarity_path}/{filename}", header=0, index_col=0).values
        matrices.append(safe_minmax(matrix))
    return safe_minmax(np.mean(matrices, axis=0))


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
        return safe_minmax(scores)
    if transform == "rank":
        return rank_percentile(scores)
    raise ValueError(f"Unknown transform: {transform}")


def score_samples(samples, profile, corr, aggregation, topk):
    scores = np.zeros(len(samples), dtype=np.float32)
    for idx, (drug_idx, side_idx, _) in enumerate(samples):
        known_sides = np.flatnonzero(profile[int(drug_idx)] > 0)
        if len(known_sides) == 0:
            continue
        values = corr[int(side_idx), known_sides]
        if aggregation == "max":
            scores[idx] = float(np.max(values))
        elif aggregation == "mean":
            scores[idx] = float(np.mean(values))
        elif aggregation == "topk_mean":
            k = min(max(1, int(topk)), len(values))
            scores[idx] = float(np.mean(np.sort(values)[-k:]))
        elif aggregation == "noisy_or":
            probs = np.clip(values, 0.0, 1.0)
            scores[idx] = float(1.0 - np.prod(1.0 - probs))
        elif aggregation == "topk_noisy_or":
            k = min(max(1, int(topk)), len(values))
            probs = np.clip(np.sort(values)[-k:], 0.0, 1.0)
            scores[idx] = float(1.0 - np.prod(1.0 - probs))
        else:
            raise ValueError(f"Unknown aggregation: {aggregation}")
    return scores


def score_drug_neighbor_samples(samples, train_positive, drug_sim, aggregation, topk):
    scores = np.zeros(len(samples), dtype=np.float32)
    if len(train_positive) == 0:
        return scores

    side_ids = samples[:, 1].astype(int)
    drug_ids = samples[:, 0].astype(int)
    for side_idx in np.unique(side_ids):
        positive_drugs = train_positive[train_positive[:, 1].astype(int) == side_idx, 0].astype(int)
        if len(positive_drugs) == 0:
            continue
        sample_idx = np.flatnonzero(side_ids == side_idx)
        values = drug_sim[drug_ids[sample_idx]][:, positive_drugs]
        if aggregation == "max":
            scores[sample_idx] = values.max(axis=1)
        elif aggregation == "mean":
            scores[sample_idx] = values.mean(axis=1)
        elif aggregation == "topk_mean":
            k = min(max(1, int(topk)), values.shape[1])
            scores[sample_idx] = np.sort(values, axis=1)[:, -k:].mean(axis=1)
        elif aggregation == "noisy_or":
            probs = np.clip(values, 0.0, 1.0)
            scores[sample_idx] = 1.0 - np.prod(1.0 - probs, axis=1)
        elif aggregation == "topk_noisy_or":
            k = min(max(1, int(topk)), values.shape[1])
            probs = np.clip(np.sort(values, axis=1)[:, -k:], 0.0, 1.0)
            scores[sample_idx] = 1.0 - np.prod(1.0 - probs, axis=1)
        else:
            raise ValueError(f"Unknown aggregation: {aggregation}")
    return scores


def fuse_scores(label_scores, drug_scores, weight_label):
    return weight_label * label_scores + (1.0 - weight_label) * drug_scores


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
    best_threshold = 0.5
    best_score = -np.inf
    for threshold in np.linspace(threshold_min, threshold_max, threshold_steps):
        score = binary_score_at_threshold(labels, scores, float(threshold), metric)
        if (score > best_score) or (
            np.isclose(score, best_score)
            and abs(float(threshold) - 0.5) < abs(best_threshold - 0.5)
        ):
            best_threshold = float(threshold)
            best_score = float(score)
    return best_threshold


def mean_metric(rows, metric):
    return float(np.mean([row[metric] for row in rows]))


def build_correlation(train_positive, label_matrix, args):
    n_drugs, n_sides = label_matrix.shape
    if args.source == "cosine":
        corr, profile = cosine_label_correlation(train_positive, n_drugs, n_sides, args.smooth)
    elif args.source == "jaccard":
        corr, profile = jaccard_label_correlation(train_positive, n_drugs, n_sides, args.smooth)
    elif args.source == "conditional":
        corr, profile = conditional_label_correlation(train_positive, n_drugs, n_sides, args.smooth)
    elif args.source == "conditional_product":
        corr, profile = bidirectional_conditional_label_correlation(
            train_positive, n_drugs, n_sides, args.smooth, mode="product"
        )
    elif args.source == "conditional_hmean":
        corr, profile = bidirectional_conditional_label_correlation(
            train_positive, n_drugs, n_sides, args.smooth, mode="hmean"
        )
    elif args.source == "lift":
        corr, profile = lift_label_correlation(train_positive, n_drugs, n_sides, args.smooth)
    elif args.source in ("mesh", "gda"):
        corr = load_external_similarity(args.similarity_path, args.source)
        profile = np.zeros((n_drugs, n_sides), dtype=np.float32)
        profile[train_positive[:, 0].astype(int), train_positive[:, 1].astype(int)] = 1.0
    elif args.source == "hybrid":
        cooccur, profile = cosine_label_correlation(train_positive, n_drugs, n_sides, args.smooth)
        mesh = load_external_similarity(args.similarity_path, "mesh")
        gda = load_external_similarity(args.similarity_path, "gda")
        corr = safe_minmax(args.cooccur_weight * cooccur + args.mesh_weight * mesh + args.gda_weight * gda)
    elif args.source == "conditional_hybrid":
        cooccur, profile = conditional_label_correlation(train_positive, n_drugs, n_sides, args.smooth)
        mesh = load_external_similarity(args.similarity_path, "mesh")
        gda = load_external_similarity(args.similarity_path, "gda")
        corr = safe_minmax(args.cooccur_weight * cooccur + args.mesh_weight * mesh + args.gda_weight * gda)
    else:
        raise ValueError(f"Unknown source: {args.source}")
    np.fill_diagonal(corr, 0.0)
    return corr, profile


def main():
    parser = argparse.ArgumentParser(description="Evaluate fold-local ADR label-correlation residual scores.")
    parser.add_argument("--similarity_path", default="pythonPredict", help="Directory containing drug_side and ADR similarity CSVs")
    parser.add_argument("--source", choices=["cosine", "jaccard", "conditional", "conditional_product", "conditional_hmean", "lift", "mesh", "gda", "hybrid", "conditional_hybrid"], default="cosine")
    parser.add_argument("--aggregation", choices=["max", "mean", "topk_mean", "noisy_or", "topk_noisy_or"], default="max")
    parser.add_argument("--label_topk", type=int, default=3,
                        help="Top-k related ADR labels used by label topk_mean aggregation")
    parser.add_argument("--mode", choices=["label", "drug", "fuse"], default="label",
                        help="Score source: ADR label residual, drug-neighbor residual, or weighted fusion")
    parser.add_argument("--drug_aggregation", choices=["max", "mean", "topk_mean", "noisy_or", "topk_noisy_or"], default="max")
    parser.add_argument("--drug_topk", type=int, default=3,
                        help="Top-k related drugs used by drug topk_mean aggregation")
    parser.add_argument("--weight_label", type=float, default=0.5,
                        help="Label residual weight when mode=fuse")
    parser.add_argument("--sweep_weights", action="store_true",
                        help="Sweep label residual weights from weight_min to weight_max when mode=fuse")
    parser.add_argument("--leave_one_fold_cv", action="store_true",
                        help="Select fusion weight on the other folds before evaluating each held-out fold")
    parser.add_argument("--weight_min", type=float, default=0.0)
    parser.add_argument("--weight_max", type=float, default=1.0)
    parser.add_argument("--weight_steps", type=int, default=21)
    parser.add_argument("--score_transform", choices=["none", "minmax", "rank"], default="rank")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--calibrate_threshold", action="store_true",
                        help="In leave-one-fold mode, select threshold on the other folds before evaluating held-out fold")
    parser.add_argument("--threshold_metric", choices=["acc", "mcc"], default="mcc")
    parser.add_argument("--threshold_min", type=float, default=0.1)
    parser.add_argument("--threshold_max", type=float, default=0.9)
    parser.add_argument("--threshold_steps", type=int, default=81)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--smooth", type=float, default=1e-3)
    parser.add_argument("--cooccur_weight", type=float, default=0.5)
    parser.add_argument("--mesh_weight", type=float, default=0.25)
    parser.add_argument("--gda_weight", type=float, default=0.25)
    parser.add_argument("--save_output_dir", default="", help="Optional DGAPred-style output directory for residual scores")
    args = parser.parse_args()

    label_matrix = pd.read_csv(f"{args.similarity_path}/drug_side.csv", header=0, index_col=0).values
    data, data_x, data_y = build_balanced_samples(label_matrix)
    if args.save_output_dir:
        os.makedirs(args.save_output_dir, exist_ok=True)
    drug_sim = build_drug_similarity(args.similarity_path) if args.mode in ("drug", "fuse") else None

    weights = [args.weight_label]
    if args.mode == "fuse" and args.sweep_weights:
        weights = np.linspace(args.weight_min, args.weight_max, args.weight_steps)

    best_summary = None
    summaries = []
    all_fold_metrics = {}
    all_fold_scores = {}

    for weight_label in weights:
        rows = []
        kfold = StratifiedKFold(args.folds, random_state=5, shuffle=True)
        for fold, (train_split, test_split) in enumerate(kfold.split(data_x, data_y), start=1):
            train_rows = data[train_split]
            test_rows = data[test_split]
            train_positive = train_rows[train_rows[:, 2] > 0]

            label_scores = None
            drug_scores = None
            if args.mode in ("label", "fuse"):
                corr, profile = build_correlation(train_positive, label_matrix, args)
                label_scores = score_samples(test_rows, profile, corr, args.aggregation, args.label_topk)
                label_scores = transform_scores(label_scores, args.score_transform)
            if args.mode in ("drug", "fuse"):
                drug_scores = score_drug_neighbor_samples(test_rows, train_positive, drug_sim, args.drug_aggregation, args.drug_topk)
                drug_scores = transform_scores(drug_scores, args.score_transform)

            if args.mode == "label":
                scores = label_scores
            elif args.mode == "drug":
                scores = drug_scores
            else:
                scores = fuse_scores(label_scores, drug_scores, float(weight_label))

            labels = (test_rows[:, 2] > 0).astype(np.int32)
            fold_metrics = metrics_at_threshold(labels, scores, args.threshold)
            all_fold_metrics[(float(weight_label), fold)] = fold_metrics
            all_fold_scores[(float(weight_label), fold)] = (labels, scores)
            nonzero_rate = float(np.mean(scores > 0))
            rows.append((fold, fold_metrics, nonzero_rate))
            if args.save_output_dir and len(weights) == 1:
                payload = {
                    "ground_truth": test_rows[:, 2].astype(np.float32),
                    "pred_value": scores.astype(np.float32),
                    "drug_id": test_rows[:, 0].astype(np.int64),
                    "side_id": test_rows[:, 1].astype(np.int64),
                }
                with open(os.path.join(args.save_output_dir, f"testdata_fold{fold}.pkl"), "wb") as handle:
                    pickle.dump(payload, handle)
            if len(weights) == 1:
                print(
                    f"Fold {fold}: AUC: {fold_metrics['auc']:.5f}, "
                    f"AUPR: {fold_metrics['aupr']:.5f}, ACC: {fold_metrics['acc']:.5f}, "
                    f"MCC: {fold_metrics['mcc']:.5f}, nonzero_rate: {nonzero_rate:.4f}"
                )

        mean_metrics = {
            key: float(np.mean([row[1][key] for row in rows]))
            for key in ["auc", "aupr", "acc", "mcc"]
        }
        summaries.append((float(weight_label), mean_metrics, len(rows)))
        if not args.leave_one_fold_cv:
            print(
                "Mean: "
                f"AUC: {mean_metrics['auc']:.5f}, "
                f"AUPR: {mean_metrics['aupr']:.5f}, "
                f"ACC: {mean_metrics['acc']:.5f}, "
                f"MCC: {mean_metrics['mcc']:.5f}, "
                f"mode: {args.mode}, source: {args.source}, aggregation: {args.aggregation}, "
                f"label_topk: {int(args.label_topk)}, "
                f"drug_aggregation: {args.drug_aggregation}, transform: {args.score_transform}, "
                f"drug_topk: {int(args.drug_topk)}, "
                f"weight_label: {float(weight_label):.4f}, n_folds: {len(rows)}"
            )

    if args.leave_one_fold_cv:
        fold_rows = []
        for heldout_fold in range(1, args.folds + 1):
            best_weight = None
            best_score = -np.inf
            best_threshold = float(args.threshold)
            for weight_label in weights:
                train_folds = [
                    fold for fold in range(1, args.folds + 1)
                    if fold != heldout_fold
                ]
                if args.calibrate_threshold:
                    train_labels = np.concatenate(
                        [all_fold_scores[(float(weight_label), fold)][0] for fold in train_folds],
                        axis=0,
                    )
                    train_scores = np.concatenate(
                        [all_fold_scores[(float(weight_label), fold)][1] for fold in train_folds],
                        axis=0,
                    )
                    candidate_threshold = select_threshold(
                        train_labels,
                        train_scores,
                        metric=args.threshold_metric,
                        threshold_min=args.threshold_min,
                        threshold_max=args.threshold_max,
                        threshold_steps=args.threshold_steps,
                    )
                    score = binary_score_at_threshold(
                        train_labels,
                        train_scores,
                        candidate_threshold,
                        args.threshold_metric,
                    )
                else:
                    candidate_threshold = float(args.threshold)
                    train_metrics = [
                        all_fold_metrics[(float(weight_label), fold)]
                        for fold in train_folds
                    ]
                    score = mean_metric(train_metrics, "aupr")
                if score > best_score:
                    best_score = score
                    best_weight = float(weight_label)
                    best_threshold = float(candidate_threshold)
            labels, scores = all_fold_scores[(best_weight, heldout_fold)]
            heldout_metrics = metrics_at_threshold(labels, scores, best_threshold)
            fold_rows.append((heldout_fold, best_weight, best_threshold, heldout_metrics))
            print(
                f"Fold {heldout_fold}: selected_weight={best_weight:.4f}, "
                f"AUC: {heldout_metrics['auc']:.5f}, "
                f"AUPR: {heldout_metrics['aupr']:.5f}, "
                f"ACC: {heldout_metrics['acc']:.5f}, "
                f"MCC: {heldout_metrics['mcc']:.5f}, "
                f"threshold: {best_threshold:.3f}"
            )
        mean_metrics = {
            key: float(np.mean([fold_metrics[key] for _, _, _, fold_metrics in fold_rows]))
            for key in ["auc", "aupr", "acc", "mcc"]
        }
        mean_weight = float(np.mean([weight for _, weight, _, _ in fold_rows]))
        mean_threshold = float(np.mean([threshold for _, _, threshold, _ in fold_rows]))
        print(
            "LeaveOneFoldCV Mean: "
            f"AUC: {mean_metrics['auc']:.5f}, "
            f"AUPR: {mean_metrics['aupr']:.5f}, "
            f"ACC: {mean_metrics['acc']:.5f}, "
            f"MCC: {mean_metrics['mcc']:.5f}, "
            f"mean_weight_label: {mean_weight:.4f}, "
            f"mean_threshold: {mean_threshold:.3f}, "
            f"n_folds: {len(fold_rows)}"
        )
        return

    if summaries:
        best_summary = max(summaries, key=lambda item: item[1]["aupr"])
        print(
            "BestByAUPR: "
            f"weight_label={best_summary[0]:.4f}, "
            f"AUC={best_summary[1]['auc']:.5f}, "
            f"AUPR={best_summary[1]['aupr']:.5f}, "
            f"ACC={best_summary[1]['acc']:.5f}, "
            f"MCC={best_summary[1]['mcc']:.5f}"
        )

    if args.save_output_dir and len(weights) == 1:
        with open(os.path.join(args.save_output_dir, "results.txt"), "w") as handle:
            handle.write(
                "Mean: "
                f"AUC: {mean_metrics['auc']:.5f}, "
                f"AUPR: {mean_metrics['aupr']:.5f}, "
                f"ACC: {mean_metrics['acc']:.5f}, "
                f"MCC: {mean_metrics['mcc']:.5f}, "
                f"mode: {args.mode}, source: {args.source}, aggregation: {args.aggregation}, "
                f"label_topk: {int(args.label_topk)}, "
                f"drug_aggregation: {args.drug_aggregation}, drug_topk: {int(args.drug_topk)}, "
                f"transform: {args.score_transform}, "
                f"weight_label: {float(weights[0]):.4f}, n_folds: {len(rows)}\n"
            )


if __name__ == "__main__":
    main()
