import os
from typing import Optional

import pandas as pd
import seaborn as sns
from matplotlib.colors import to_hex
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage


def _ensure_dir(output_dir: str) -> None:
    os.makedirs(output_dir, exist_ok=True)


def plot_agglomerative_clustering_and_pca(
    df: pd.DataFrame,
    output_dir: str = "output",
    manual_n_clusters: Optional[int] = 5,
) -> None:
    """Run agglomerative clustering, save dendrogram and PCA cluster scatter.

    Outputs:
    - Clustering_Dendrogram.pdf
    - AgglomerativeClusters_PCA.pdf
    - cluster_assignments.csv
    """
    _ensure_dir(output_dir)

    bool_cols = {
        "stats.spot.syntactic_safety": "syntactic_safety",
        "stats.spot.is_stutter_invariant_formula": "stutter_invariant",
        "stats.spot.tgba_analysis.is_complete": "tgba_complete",
        "stats.spot.tgba_analysis.is_deterministic": "tgba_deterministic",
        "stats.spot.buchi_analysis.is_complete": "buchi_complete",
        "stats.spot.buchi_analysis.is_deterministic": "buchi_deterministic",
        "stats.spot.deterministic_attempt.automaton_analysis.is_complete": "det_complete",
        "stats.spot.deterministic_attempt.automaton_analysis.is_deterministic": "det_deterministic",
    }
    num_cols = [
        "stats.spot.tgba_analysis.state_count",
        "stats.spot.tgba_analysis.transition_count",
        "stats.spot.buchi_analysis.state_count",
        "stats.spot.buchi_analysis.transition_count",
        "stats.spot.deterministic_attempt.automaton_analysis.state_count",
        "stats.spot.deterministic_attempt.automaton_analysis.transition_count",
        "stats.spot.tgba_analysis.acceptance_sets",
        "stats.spot.buchi_analysis.acceptance_sets",
        "stats.spot.deterministic_attempt.automaton_analysis.acceptance_sets",
    ]

    existing_bool_cols = {k: v for k, v in bool_cols.items() if k in df.columns}
    existing_num_cols = [c for c in num_cols if c in df.columns]
    if not existing_bool_cols and not existing_num_cols:
        print("[clustering] Skipped: no relevant columns found.")
        return

    clu_df = df[list(existing_bool_cols.keys()) + existing_num_cols].copy()
    clu_df = clu_df.replace({
        "WAHR": 1, "FALSCH": 0,
        "TRUE": 1, "FALSE": 0,
        True: 1, False: 0,
        "Error": pd.NA,
    })
    for c in clu_df.columns:
        clu_df[c] = pd.to_numeric(clu_df[c], errors="coerce")

    keywords = ["safety", "obligation", "persistence", "recurrence", "reactivity", "guarantee"]
    if "stats.spot.manna_pnueli_class" in df.columns:
        for kw in keywords:
            clu_df[kw] = df["stats.spot.manna_pnueli_class"].apply(
                lambda x: 1 if pd.notna(x) and isinstance(x, str) and kw in x.lower() else 0
            )

    clu_df = clu_df.dropna()
    if clu_df.empty or clu_df.shape[0] <= 1:
        print("[clustering] Skipped: not enough clean data to cluster.")
        return

    if "stats.spot.spot_formula" in df.columns:
        labels_series = df.loc[clu_df.index, "stats.spot.spot_formula"].astype(str)
    elif "stats.spot.formula" in df.columns:
        labels_series = df.loc[clu_df.index, "stats.spot.formula"].astype(str)
    else:
        labels_series = pd.Series([f"row_{i}" for i in clu_df.index], index=clu_df.index)

    if "id" in df.columns:
        id_series = df.loc[clu_df.index, "id"].astype(str)
    else:
        id_series = pd.Series(clu_df.index.astype(str), index=clu_df.index)

    def _fmt_label(formula, id_):
        s = str(formula) if pd.notna(formula) else ""
        s = s.strip()
        if len(s) > 60:
            s = s[:60] + "..."
        return f"{s} [{id_}]"

    labels_list = [_fmt_label(labels_series.loc[i], id_series.loc[i]) for i in clu_df.index]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(clu_df.values)
    Z = linkage(X_scaled, method="ward")

    if manual_n_clusters is not None:
        n_clusters = int(manual_n_clusters)
    else:
        n_clusters = 5 if clu_df.shape[0] >= 5 else max(2, clu_df.shape[0] // 2)

    agg = AgglomerativeClustering(n_clusters=n_clusters, linkage="ward")
    labels = agg.fit_predict(X_scaled)
    palette = sns.color_palette("tab10", n_clusters)
    palette_hex = [to_hex(c) for c in palette]

    def _make_link_color_func(Z, leaf_cluster_labels, palette_hex):
        n = len(leaf_cluster_labels)
        children = {i + n: (int(left), int(right)) for i, (left, right, _, _) in enumerate(Z)}

        from functools import lru_cache
        @lru_cache(maxsize=None)
        def subtree_clusters(node_id):
            if node_id < n:
                return {int(leaf_cluster_labels[node_id])}
            l, r = children[node_id]
            return subtree_clusters(l) | subtree_clusters(r)

        def link_color_func(node_id):
            clusters = subtree_clusters(int(node_id))
            if len(clusters) == 1:
                k = next(iter(clusters))
                return palette_hex[k % len(palette_hex)]
            return "#BBBBBB"
        return link_color_func

    if n_clusters > 1:
        d_high = Z[-(n_clusters - 1), 2]
        d_low = Z[-(n_clusters), 2] if n_clusters <= Z.shape[0] else d_high * 0.5
        cut_height = (d_high + d_low) / 2.0
    else:
        cut_height = 0.0

    # Dendrogram
    n_leaves = len(labels_list)
    fig_height = max(6, 0.28 * n_leaves + 2)
    fig = plt.figure(figsize=(12, fig_height))
    link_color_func = _make_link_color_func(Z, labels, palette_hex)
    dobj = dendrogram(
        Z,
        labels=labels_list,
        orientation="right",
        leaf_rotation=0,
        leaf_font_size=8,
        link_color_func=link_color_func,
    )
    if n_clusters > 1:
        plt.axvline(cut_height, linestyle="--", color="#444444", linewidth=1)
    ax = plt.gca()
    for tick, row_idx in zip(ax.get_yticklabels(), dobj['leaves']):
        k = int(labels[row_idx])
        tick.set_color(palette_hex[k % len(palette_hex)])
    plt.title("Agglomerative clustering dendrogram (Ward linkage)")
    plt.xlabel("Distance")
    plt.ylabel("")
    plt.tight_layout()
    plt.subplots_adjust(left=0.35)
    fig.savefig(f"{output_dir}/Clustering_Dendrogram.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)

    # PCA projection
    pca = PCA(n_components=2)
    coords = pca.fit_transform(X_scaled)
    fig2 = plt.figure(figsize=(12, 8))
    for k in sorted(set(labels)):
        idx = labels == k
        plt.scatter(
            coords[idx, 0], coords[idx, 1], alpha=0.8, edgecolor="k",
            label=f"Cluster {k}", color=palette_hex[k % len(palette_hex)]
        )
    ids_for_plot = id_series.loc[clu_df.index].astype(str).values
    for (x, y, lab) in zip(coords[:, 0], coords[:, 1], ids_for_plot):
        plt.text(x + 0.06, y + 0.06, lab, fontsize=7, alpha=0.9)
    plt.xlabel("PCA 1")
    plt.ylabel("PCA 2")
    plt.title("Agglomerative clusters (PCA projection)")
    plt.legend(loc="best", fontsize=8)
    plt.tight_layout()
    fig2.savefig(f"{output_dir}/AgglomerativeClusters_PCA.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig2)

    cluster_out = pd.DataFrame({
        "label": labels_series.values,
        "cluster": labels,
    }, index=clu_df.index)
    cluster_out.to_csv(os.path.join(output_dir, "cluster_assignments.csv"))

