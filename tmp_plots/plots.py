import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np
from upsetplot import UpSet, from_memberships
import seaborn as sns


def _ensure_dir(output_dir: str) -> None:
    import os
    os.makedirs(output_dir, exist_ok=True)


def plot_violin(df: pd.DataFrame, output_dir: str = "output") -> None:
    """Generate violin + box plots for state and transition counts."""
    _ensure_dir(output_dir)

    state_col = "stats.spot.buchi_analysis.state_count"
    transition_col = "stats.spot.buchi_analysis.transition_count"
    states_count = df[state_col].dropna()
    states_count = states_count[~states_count.astype(str).str.lower().eq("error")].to_numpy()
    transitions_count = df[transition_col].dropna()
    transitions_count = transitions_count[~transitions_count.astype(str).str.lower().eq("error")].to_numpy()

    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(9, 4), sharey=False)
    colors = sns.color_palette("turbo", 2)

    # First plot for states count
    sns.violinplot(
        y=states_count,
        color=colors[0],
        saturation=0.4,
        bw_method=0.5,
        edgecolor="black",
        linewidth=1,
        linecolor="k",
        ax=ax1,
        inner=None,
        legend=False,
    )
    sns.boxplot(
        y=states_count,
        color=colors[0],
        width=0.12,
        boxprops={'zorder': 2},
        ax=ax1,
        showcaps=True,
        showbox=True,
        whiskerprops={"linewidth": 1.2, "color": "black"},
        medianprops={"linewidth": 1.2, "color": "black"},
        fliersize=5,
    )
    ax1.set_title("states_count")
    ax1.set_ylabel("Count")
    ax1.set_ylim(bottom=None, top=states_count.max() * 1.8)
    major_ticks = ax1.get_yticks()
    spacing = major_ticks[1] - major_ticks[0]
    ax1.yaxis.set_minor_locator(mticker.MultipleLocator(spacing / 5))
    ax1.text(
        0,
        states_count.max() + 0.52 * (states_count.max() - states_count.min()),
        f"Mean: {states_count.mean():.2f}\nMedian: {pd.Series(states_count).median():.2f}\nStd: {states_count.std():.2f}",
        ha="center",
        va="bottom",
        fontsize=9,
        weight="bold",
    )

    # Second plot for transitions count
    sns.violinplot(
        y=transitions_count,
        color=colors[1],
        saturation=0.4,
        bw_method=0.5,
        edgecolor="black",
        linewidth=1,
        linecolor="k",
        ax=ax2,
        inner=None,
        legend=False,
    )
    sns.boxplot(
        y=transitions_count,
        color=colors[1],
        width=0.12,
        boxprops={'zorder': 2},
        ax=ax2,
        showcaps=True,
        showbox=True,
        whiskerprops={"linewidth": 1.2, "color": "black"},
        medianprops={"linewidth": 1.2, "color": "black"},
        fliersize=5,
    )
    ax2.set_title("transition_counts")
    ax2.set_ylabel("Count")
    ax2.set_ylim(bottom=None, top=transitions_count.max() * 1.8)
    major_ticks = ax2.get_yticks()
    spacing = major_ticks[1] - major_ticks[0]
    ax2.yaxis.set_minor_locator(mticker.MultipleLocator(spacing / 5))
    ax2.text(
        0,
        transitions_count.max() + 0.52 * (transitions_count.max() - transitions_count.min()),
        f"Mean: {transitions_count.mean():.2f}\nMedian: {pd.Series(transitions_count).median():.2f}\nStd: {transitions_count.std():.2f}",
        ha="center",
        va="bottom",
        fontsize=9,
        weight="bold",
    )

    plt.tight_layout()
    plt.savefig(f"{output_dir}/Violin_plots.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)


def plot_scatter(df: pd.DataFrame, output_dir: str = "output") -> None:
    """Generate log-log scatter plot of states vs transitions."""
    _ensure_dir(output_dir)
    state_col = "stats.spot.buchi_analysis.state_count"
    transition_col = "stats.spot.buchi_analysis.transition_count"
    states_count = df[state_col].dropna()
    states_count = states_count[~states_count.astype(str).str.lower().eq("error")].to_numpy()
    transitions_count = df[transition_col].dropna()
    transitions_count = transitions_count[~transitions_count.astype(str).str.lower().eq("error")].to_numpy()

    fig = plt.figure(figsize=(6, 5))
    plt.scatter(states_count, transitions_count, alpha=0.7, c="green", edgecolor="k")
    plt.xlabel("state_count")
    plt.ylabel("transition_count")
    plt.grid(True, which="both", ls="--")
    plt.xscale("log")
    plt.yscale("log")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/Scatter_plot.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)


def plot_upset(df: pd.DataFrame, output_dir: str = "output") -> None:
    """Generate UpSet plot for Manna-Pnueli class combinations."""
    _ensure_dir(output_dir)

    col = "stats.spot.manna_pnueli_class"
    tmp = df.copy()
    if col in tmp.columns:
        tmp = tmp[tmp[col].astype(str).str.lower() != "error"]
        combinations = tmp[col].dropna().astype(str).apply(lambda x: x.split())
        if not combinations.empty:
            comb_counts = combinations.value_counts()
            data = from_memberships(comb_counts.index, data=comb_counts.values)
            up = UpSet(data, show_counts=True, facecolor="darkblue", sort_by="degree")
            up.plot()
            plt.savefig(f"{output_dir}/Upset_plot.pdf", format="pdf", bbox_inches="tight")
            plt.close('all')


def plot_stacked_barchart(df: pd.DataFrame, output_dir: str = "output") -> None:
    """Stacked bar chart of boolean features across Manna-Pnueli classes."""
    _ensure_dir(output_dir)

    bool_cols = {
        "stats.spot.syntactic_safety": "syntactic_safety",
        "stats.spot.is_stutter_invariant_formula": "stutter_invariant",
        "stats.spot.tgba_analysis.is_complete": "tgba_analysis_complete",
        "stats.spot.tgba_analysis.is_deterministic": "tgba_analysis_deterministic",
    }
    categories = [
        "safety",
        "obligation",
        "persistence",
        "recurrence",
        "reactivity",
        "guarantee",
    ]

    counts = {}
    for col, display_name in bool_cols.items():
        if col not in df.columns:
            continue
        # Treat various truthy encodings as True (strings, booleans)
        col_vals = df[col]
        truthy = (
            (col_vals == True) |
            col_vals.astype(str).str.lower().isin(["true", "wahr", "1", "yes"])
        )
        subset = df.loc[truthy, "stats.spot.manna_pnueli_class"].astype(str)
        cat_counts = {cat: subset.str.contains(cat, case=False).sum() for cat in categories}
        counts[display_name] = cat_counts

    if not counts:
        return

    count_df = pd.DataFrame(counts).T
    colors = ["#6EA68A", "#3E9388", "#24687C", "#E18330", "#E5AE1F", "#0F3866"]
    ax = count_df.plot(kind="bar", stacked=True, figsize=(10, 6), color=colors)

    plt.title("Stacked counts by boolean semantic feature for each Manna-Pnueli class")
    plt.ylabel("Count")
    plt.xticks(rotation=20, ha="right")
    plt.legend(title="Manna-Pnueli class", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/Stacked_barchart.pdf", format="pdf", bbox_inches="tight")
    plt.close(ax.figure)


def plot_correlation_matrix(df: pd.DataFrame, output_dir: str = "output") -> None:
    """Correlation matrix of boolean semantic features."""
    _ensure_dir(output_dir)

    bool_cols = {
        "stats.spot.syntactic_safety": "syntactic_safety",
        "stats.spot.is_stutter_invariant_formula": "stutter_invariant",
        "stats.spot.tgba_analysis.is_complete": "tgba_analysis_complete",
        "stats.spot.tgba_analysis.is_deterministic": "tgba_analysis_deterministic",
    }

    data = df[list(bool_cols.keys())].rename(columns=bool_cols).copy()
    data = data.replace({
        "TRUE": 1, "FALSE": 0,
        "WAHR": 1, "FALSCH": 0,
        True: 1, False: 0,
        "Error": pd.NA, "error": pd.NA,
    })
    for c in data.columns:
        data[c] = pd.to_numeric(data[c], errors="coerce")
    corr_matrix = data.corr()

    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)

    fig = plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1, mask=mask)
    plt.title("Correlation matrix of boolean semantic features")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/CorrelationMatrix.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)


def plot_extended_correlation_matrix(df: pd.DataFrame, output_dir: str = "output") -> None:
    """Correlation matrix including Manna-Pnueli one-hot features."""
    _ensure_dir(output_dir)

    bool_cols = {
        "stats.spot.syntactic_safety": "syntactic_safety",
        "stats.spot.is_stutter_invariant_formula": "stutter_invariant",
        "stats.spot.tgba_analysis.is_complete": "tgba_analysis_complete",
        "stats.spot.tgba_analysis.is_deterministic": "tgba_analysis_deterministic",
    }
    keywords = ["safety", "obligation", "persistence", "recurrence", "reactivity", "guarantee"]

    data = df[list(bool_cols.keys())].rename(columns=bool_cols).copy()
    data = data.replace({
        "TRUE": 1, "FALSE": 0,
        "WAHR": 1, "FALSCH": 0,
        True: 1, False: 0,
        "Error": pd.NA, "error": pd.NA,
    })
    for c in data.columns:
        data[c] = pd.to_numeric(data[c], errors="coerce")
    data = data.dropna()

    for kw in keywords:
        data[kw] = df["stats.spot.manna_pnueli_class"].apply(
            lambda x: 1 if pd.notna(x) and isinstance(x, str) and kw in x.lower() else 0
        )

    corr_matrix = data.corr()
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)

    fig = plt.figure(figsize=(10, 8))
    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap="coolwarm",
        center=0,
        vmin=-1,
        vmax=1,
        mask=mask,
        linecolor='gray',
    )
    plt.title("Correlation matrix of all semantic features")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/CorrelationMatrixExtended.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)


# This is produced and in the Confidence of the FrequentItemSetMining
def plot_extended_conditional_probability_matrix(df: pd.DataFrame, output_dir: str = "output") -> None:
    """Extended conditional probability matrix across semantic features."""
    _ensure_dir(output_dir)
    bool_cols = {
        "stats.spot.syntactic_safety": "syntactic_safety",
        "stats.spot.is_stutter_invariant_formula": "stutter_invariant",
        "stats.spot.tgba_analysis.is_complete": "tgba_analysis_complete",
        "stats.spot.tgba_analysis.is_deterministic": "tgba_analysis_deterministic",
    }
    keywords = ["safety", "obligation", "persistence", "recurrence", "reactivity", "guarantee"]

    data = df[list(bool_cols.keys())].rename(columns=bool_cols).copy()
    data = data.replace({
        "TRUE": 1, "FALSE": 0,
        "WAHR": 1, "FALSCH": 0,
        True: 1, False: 0,
        "Error": pd.NA, "error": pd.NA,
    })
    for c in data.columns:
        data[c] = pd.to_numeric(data[c], errors="coerce")
    data = data.dropna()

    for kw in keywords:
        data[kw] = df["stats.spot.manna_pnueli_class"].apply(
            lambda x: 1 if pd.notna(x) and isinstance(x, str) and kw in x.lower() else 0
        )

    cond_prob_matrix = pd.DataFrame(index=data.columns, columns=data.columns, dtype=float)
    for col_A in data.columns:
        for col_B in data.columns:
            A_positive = data[col_A] == 1
            if A_positive.sum() > 0:
                cond_prob_matrix.loc[col_A, col_B] = data.loc[A_positive, col_B].mean()
            else:
                cond_prob_matrix.loc[col_A, col_B] = np.nan

    fig = plt.figure(figsize=(10, 8))
    sns.heatmap(
        cond_prob_matrix,
        annot=True,
        cmap="coolwarm",
        center=0.5,
        vmin=0,
        vmax=1,
        linecolor='gray',
    )
    plt.title("Conditional probability matrix of semantic features")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/ConditionalProbabilityExtended.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)



def plot_extended_jaccard_similarity_matrix(df: pd.DataFrame, output_dir: str = "output") -> None:
    """Extended Jaccard similarity matrix across semantic features."""
    _ensure_dir(output_dir)
    bool_cols = {
        "stats.spot.syntactic_safety": "syntactic_safety",
        "stats.spot.is_stutter_invariant_formula": "stutter_invariant",
        "stats.spot.tgba_analysis.is_complete": "tgba_analysis_complete",
        "stats.spot.tgba_analysis.is_deterministic": "tgba_analysis_deterministic",
    }
    keywords = ["safety", "obligation", "persistence", "recurrence", "reactivity", "guarantee"]

    data = df[list(bool_cols.keys())].rename(columns=bool_cols).copy()
    data = data.replace({
        "TRUE": 1, "FALSE": 0,
        "WAHR": 1, "FALSCH": 0,
        True: 1, False: 0,
        "Error": pd.NA, "error": pd.NA,
    })
    for c in data.columns:
        data[c] = pd.to_numeric(data[c], errors="coerce")
    data = data.dropna()

    for kw in keywords:
        data[kw] = df["stats.spot.manna_pnueli_class"].apply(
            lambda x: 1 if pd.notna(x) and isinstance(x, str) and kw in x.lower() else 0
        )

    jaccard_matrix = pd.DataFrame(index=data.columns, columns=data.columns, dtype=float)
    for col_A in data.columns:
        set_A = data.index[data[col_A] == 1]
        for col_B in data.columns:
            set_B = data.index[data[col_B] == 1]
            intersection = len(set_A.intersection(set_B))
            union = len(set_A.union(set_B))
            jaccard_matrix.loc[col_A, col_B] = (intersection / union) if union > 0 else np.nan

    mask = np.triu(np.ones_like(jaccard_matrix, dtype=bool), k=1)

    fig = plt.figure(figsize=(10, 8))
    sns.heatmap(
        jaccard_matrix,
        annot=True,
        cmap="coolwarm",
        center=0.5,
        vmin=0,
        vmax=1,
        mask=mask,
        linecolor='gray',
    )
    plt.title("Jaccard similarity matrix of semantic features")
    plt.tight_layout()
    plt.savefig(f"{output_dir}/JaccardSimilarityMatrixExtended.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)



def plot_frequent_itemset_mining(df: pd.DataFrame, output_dir: str = "output") -> None:
    """Frequent itemset mining and rule metrics heatmaps."""
    _ensure_dir(output_dir)
    bool_cols = {
        "stats.spot.syntactic_safety": "syntactic_safety",
        "stats.spot.is_stutter_invariant_formula": "stutter_invariant",
        "stats.spot.tgba_analysis.is_complete": "tgba_analysis_complete",
        "stats.spot.tgba_analysis.is_deterministic": "tgba_analysis_deterministic",
    }
    keywords = ["safety", "obligation", "persistence", "recurrence", "reactivity", "guarantee"]

    data = df[list(bool_cols.keys())].rename(columns=bool_cols).copy()
    data = data.replace({
        "TRUE": 1, "FALSE": 0,
        "WAHR": 1, "FALSCH": 0,
        True: 1, False: 0,
        "Error": pd.NA, "error": pd.NA,
    })
    for c in data.columns:
        data[c] = pd.to_numeric(data[c], errors="coerce")
    data = data.dropna()
    for kw in keywords:
        data[kw] = df["stats.spot.manna_pnueli_class"].apply(
            lambda x: 1 if pd.notna(x) and isinstance(x, str) and kw in x.lower() else 0
        )
    
    items = data.columns
    metrics = ["support", "confidence", "lift", "conviction"]
    matrices = {m: pd.DataFrame(0.0, index=items, columns=items) for m in metrics}

    for a in items:
        for b in items:
            A = data[a]
            B = data[b]

            support_A = A.mean()
            support_B = B.mean()
            support_AB = ((A == 1) & (B == 1)).mean()

            # Support = P(A ∩ B)
            matrices["support"].loc[a, b] = support_AB
            # Confidence = Conditional Probability = P(B|A) = P(A ∩ B) / P(A)
            matrices["confidence"].loc[a, b] = support_AB / support_A if support_A > 0 else np.nan
            # Lift = P(B|A) / P(B) = P(A ∩ B) / (P(A)*P(B))
            matrices["lift"].loc[a, b] = support_AB / (support_A * support_B) if support_A > 0 and support_B > 0 else np.nan
            # Conviction = (1 - P(B)) / (1 - confidence)
            conf = matrices["confidence"].loc[a, b]
            matrices["conviction"].loc[a, b] = (1 - support_B) / (1 - conf) if conf < 1 else np.inf

    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    axes = axes.flatten()

    for ax, metric in zip(axes, metrics):
        matrix_to_plot = matrices[metric].copy()
        sns.heatmap(
            matrix_to_plot,
            annot=True,
            fmt=".2f",
            cmap="Blues",
            ax=ax,
            cbar=True
        )
        ax.set_title(metric.capitalize(), pad=12, fontsize=12)
        cbar = ax.collections[0].colorbar
        cbar.set_label("", rotation=0)

    plt.tight_layout()
    plt.savefig(f"{output_dir}/FrequentItemSetMining.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)



def plot_semantic_features_frequency(df: pd.DataFrame, output_dir: str = "output") -> None:
    """Table-style frequency of semantic features."""
    _ensure_dir(output_dir)
    bool_cols = {
        "stats.spot.syntactic_safety": "syntactic_safety",
        "stats.spot.is_stutter_invariant_formula": "stutter_invariant",
        "stats.spot.tgba_analysis.is_complete": "tgba_analysis_complete",
        "stats.spot.tgba_analysis.is_deterministic": "tgba_analysis_deterministic",
    }
    keywords = ["safety", "obligation", "persistence", "recurrence", "reactivity", "guarantee"]

    data = df[list(bool_cols.keys())].rename(columns=bool_cols).copy()
    data = data.replace({
        "TRUE": 1, "FALSE": 0,
        "WAHR": 1, "FALSCH": 0,
        True: 1, False: 0,
        "Error": pd.NA,
    })
    for c in data.columns:
        data[c] = pd.to_numeric(data[c], errors="coerce")
    data = data.dropna()
    for kw in keywords:
        data[kw] = df["stats.spot.manna_pnueli_class"].apply(
            lambda x: 1 if pd.notna(x) and isinstance(x, str) and kw in x.lower() else 0
        )

    freq = data.sum() / len(data)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.axis('off')
    table_data = [[feature, f"{value:.2f}"] for feature, value in freq.items()]

    table = ax.table(
        cellText=table_data,
        colLabels=["Semantic Feature", "Frequency"],
        cellLoc='center',
        colWidths=[0.6, 0.2],
        loc='center',
    )
    table.auto_set_font_size(False)
    table.set_fontsize(12)

    for key, cell in table.get_celld().items():
        cell.get_text().set_color('black')

    for col in range(len(table_data[0])):
        cell = table[(0, col)]
        cell.set_facecolor('#FFF8DC')

    plt.tight_layout()
    plt.savefig(f"{output_dir}/SemanticFeaturesFrequency.pdf", format="pdf", bbox_inches="tight")
    plt.close(fig)




# clustering-related plots are moved to clustering.py
