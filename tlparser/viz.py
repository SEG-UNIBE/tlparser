import os

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

pio.kaleido.scope.mathjax = None

import seaborn as sns
from d3blocks import D3Blocks

from tlparser.config import Configuration
from tlparser.utils import Utils


class Viz:
    title_map = {
        "stats.agg.aps": "Atomic Propositions",
        "stats.agg.cops": "Comparison Operators",
        "stats.agg.lops": "Logical Operators",
        "stats.agg.tops": "Temporal Operators",
    }

    def __init__(self, config: Configuration, file):
        self.config = config
        self.data = pd.read_excel(file)

    def __get_file_name(self, prefix, suffix=".pdf"):
        os.makedirs(self.config.folder_data_out, exist_ok=True)
        return os.path.join(
            self.config.folder_data_out,
            f"{prefix}_{Utils.get_unique_filename()}{suffix}",
        )

    def __get_reduced_logic_order(self):
        return [
            item
            for item in self.config.logic_order
            if item in self.data["type"].unique()
        ]

    def plot_histogram(self):
        reduced_order = self.__get_reduced_logic_order()
        type_palette = self.config.color_palette
        df = self.data.copy()
        df["type"] = pd.Categorical(df["type"], categories=reduced_order, ordered=True)
        _, axes = plt.subplots(2, 2, figsize=(8, 4), sharex=True, sharey=True)
        axes = axes.flatten()
        titles = {
            "self": "(a) Naturally Chosen Formalization",
            "yes": "(b) Translation Possible",
            "no": "(c) Translation Not Possible",
            "unknown": "(d) Translation Status Uncertain",
        }

        max_count = df["type"].value_counts().max() + 5

        for ax, translation in zip(axes, ["self", "yes", "no", "unknown"]):
            sns.histplot(
                data=df[df["translation"] == translation],
                x="type",
                ax=ax,
                shrink=0.8,
                discrete=True,
                hue="type",
                multiple="stack",
                palette=type_palette,
                legend=False,
            )
            ax.set_title(titles.get(translation, f"Translatable: {translation}"))
            ax.set_xlabel("")
            ax.set_ylabel("Count")
            ax.set_ylim(0, max_count)
            ax.yaxis.set_minor_locator(ticker.MultipleLocator(5))

            for bar in ax.patches:
                height = bar.get_height()
                if height > 0:
                    y = height / 2 if height > 14 else height + 8
                    ax.annotate(
                        f"{int(height)}",
                        xy=(bar.get_x() + bar.get_width() / 2, y),
                        xytext=(0, 0),
                        textcoords="offset points",
                        ha="center",
                        va="center",
                        fontsize=8,
                        color="black",
                        bbox=dict(
                            boxstyle="round,pad=0.2",
                            facecolor="white",
                            edgecolor="black",
                        ),
                    )

        plt.tight_layout()
        out = self.__get_file_name("hist")
        plt.savefig(out)
        plt.close()
        return out

    def plot_violin(self, include_strip=False):
        type_palette = self.config.color_palette
        df_filtered = self.data[self.data["translation"] == "self"]
        agg_columns = df_filtered.filter(like=".agg.").columns.tolist()
        df_long = pd.melt(
            df_filtered,
            id_vars=["id", "type"],
            value_vars=agg_columns,
            var_name="aggregation",
            value_name="value",
        )

        stats_values = (
            df_long.groupby(["type", "aggregation"])["value"]
            .agg(["mean", "median", "count", "std"])
            .reset_index()
        )

        y_min = df_long["value"].min()
        y_max = df_long["value"].max() + 4.5

        fig, axes = plt.subplots(
            nrows=2, ncols=2, figsize=(8, 7), sharex=True, sharey=True
        )
        axes = axes.flatten()
        plt.subplots_adjust(hspace=0.05, wspace=0.05)
        i = 1

        for ax, agg in zip(axes, agg_columns):
            violin = sns.violinplot(
                x="type",
                y="value",
                data=df_long[df_long["aggregation"] == agg],
                hue="type",
                palette=type_palette,
                bw_method=0.5,
                edgecolor="black",
                linewidth=1,
                linecolor="k",
                ax=ax,
                inner=None,
                legend=False,
            )
            sns.boxplot(
                x="type",
                y="value",
                hue="type",
                palette=type_palette,
                data=df_long[df_long["aggregation"] == agg],
                width=0.12,
                showcaps=True,
                showbox=True,
                whiskerprops={"linewidth": 1.2, "color": "black"},
                medianprops={"linewidth": 1.2, "color": "black"},
                ax=ax,
                fliersize=5,
            )

            for violin_part in violin.collections:
                violin_part.set_alpha(0.6)

            if include_strip:
                sns.stripplot(
                    x="type",
                    y="value",
                    hue="type",
                    data=df_long[df_long["aggregation"] == agg],
                    alpha=0.3,
                    palette=type_palette,
                    size=3,
                    marker="d",
                    edgecolor="black",
                    linewidth=1,
                    ax=ax,
                    dodge=False,
                )

            ax.set_xlabel("")
            ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))

            for _, row in stats_values[stats_values["aggregation"] == agg].iterrows():
                annotation_y = y_max - 0.5
                annotation_text = (
                    f"μ={row['mean']:.1f}\n"
                    f"M={row['median']:.1f}\n"
                    f"σ={row['std']:.1f}"
                )
                ax.text(
                    row["type"],
                    annotation_y,
                    annotation_text,
                    color="black",
                    ha="center",
                    va="bottom",
                )

            if i > 2:
                for x_category in df_long["type"].unique():
                    filtered_values = stats_values.loc[
                        (stats_values["aggregation"] == agg)
                        & (stats_values["type"] == x_category),
                        "count",
                    ]
                    n_value = (
                        int(filtered_values.iloc[0]) if not filtered_values.empty else 0
                    )
                    x_position = list(df_long["type"].unique()).index(x_category)
                    ax.text(
                        x_position,
                        y_min - 8,
                        f"n={n_value}",
                        color="black",
                        ha="center",
                        va="top",
                    )

            i += 1
            ax.set_title(self.title_map.get(agg, agg))
            ax.set_ylabel("Count")
            ax.set_ylim(y_min - 5, y_max + 5)

        for i in range(len(agg_columns), len(axes)):
            axes[i].set_visible(False)

        fig.tight_layout()
        out = self.__get_file_name("viol")
        plt.savefig(out)
        plt.close()
        return out

    def plot_pairplot(self):
        type_palette = self.config.color_palette
        df = self.data[self.data["translation"] == "self"]
        agg_columns = df.filter(like=".agg.").columns.tolist()
        df_pairplot = df[agg_columns + ["type"]]

        unique_types = df_pairplot["type"].nunique()
        markers = ["o", "s", "D", "^", "v", "P"][:unique_types]

        g = sns.pairplot(
            df_pairplot,
            hue="type",
            palette=type_palette,
            diag_kind="kde",
            markers=markers,
        )

        for i, ax in enumerate(g.axes.flat):
            row_var = g.x_vars[i % len(g.x_vars)]
            col_var = g.y_vars[i // len(g.x_vars)]
            ax.set_xlabel(self.title_map.get(row_var, row_var))
            ax.set_ylabel(self.title_map.get(col_var, col_var))
            for artist in ax.collections:
                artist.set_edgecolor("black")
                artist.set_alpha(0.6)

        g._legend.set_title("")
        out = self.__get_file_name("pairp")
        plt.savefig(out)
        plt.close()
        return out

    def plot_sankey(self):
        df = self.data.copy()
        flow_counts = {"yes": {}, "no": {}, "unknown": {}}
        for id_value, group in df.groupby("id"):
            source_type = group[group["translation"] == "self"]["type"].values[0]
            for _, row in group.iterrows():
                target_type = row["type"]
                translation_type = row["translation"]
                if translation_type in ["yes", "no", "unknown"]:
                    if (source_type, target_type) not in flow_counts[translation_type]:
                        flow_counts[translation_type][
                            (source_type, target_type)
                        ] = set()
                    flow_counts[translation_type][(source_type, target_type)].add(
                        id_value
                    )

        labels = df["type"].unique().tolist()
        source = []
        target = []
        value = []
        link_labels = []
        link_colors = []

        translation_colors = {
            "yes": "rgba(0, 128, 0, 0.7)",
            "no": "rgba(255, 0, 0, 0.7)",
            "unknown": "rgba(128, 128, 128, 0.7)",
        }

        label_to_index = {label: idx for idx, label in enumerate(labels)}
        for translation_type, flows in flow_counts.items():
            for (src, tgt), ids_set in flows.items():
                source.append(label_to_index[src])
                target.append(label_to_index[tgt])
                value.append(len(ids_set))
                link_labels.append(f"{len(ids_set)} ids ({translation_type})")
                link_colors.append(translation_colors[translation_type])

        fig = go.Figure(
            data=[
                go.Sankey(
                    arrangement="freeform",
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(color="black", width=0.5),
                        label=labels,
                    ),
                    link=dict(
                        arrowlen=15,
                        source=source,
                        target=target,
                        value=value,
                        label=link_labels,
                        color=link_colors,
                    ),
                )
            ]
        )

        fig.update_layout(
            title_text="Sankey Diagram of Translations",
            font_size=10,
        )
        out = self.__get_file_name("sankey")
        pio.write_image(fig, out, format="pdf")
        return out

    def plot_chord(self):
        outs = []
        for target in ["yes", "no", "unknown"]:
            df = self.data.copy()
            d3 = D3Blocks(chart="chord", frame=True, verbose=50)
            links = []

            for _, group in df.groupby("id"):
                source_type_row = group[group["translation"] == "self"]
                if not source_type_row.empty:
                    source_type = source_type_row["type"].values[0]
                    yes_targets = group[
                        (group["translation"] == target)
                        & (group["type"] != source_type)
                    ]
                    for _, row in yes_targets.iterrows():
                        target_type = row["type"]
                        links.append(
                            {
                                "source": source_type,
                                "target": target_type,
                                "weight": 1,
                                "color": self.config.color_palette.get(source_type),
                            }
                        )
            if len(links) > 0:
                links_df = pd.DataFrame(links)
                links_df = (
                    links_df.groupby(["source", "target"])
                    .size()
                    .reset_index(name="weight")
                )

                d3.chord(
                    links_df,
                    ordering=self.__get_reduced_logic_order(),
                    reset_properties=False,
                )

                for label, color in self.config.color_palette.items():
                    if label in d3.node_properties.index:
                        d3.node_properties.loc[label, "color"] = color

                out = self.__get_file_name(f"chord_{target}", ".html")
                d3.chord(
                    links_df,
                    title=f"Chord Diagram (self -> {target})",
                    save_button=True,
                    filepath=out,
                    ordering=self.__get_reduced_logic_order(),
                    figsize=(550, 550),
                    reset_properties=False,
                    arrowhead=26,
                    fontsize=13,
                )
                outs.append(out)

        return "\n".join(outs)
