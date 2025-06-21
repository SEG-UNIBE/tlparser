import os
import math

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

pio.kaleido.scope.mathjax = None

import networkx as nx
from pyvis.network import Network
import seaborn as sns
from d3blocks import D3Blocks

from tlparser.config import Configuration
from tlparser.utils import Utils


class Viz:
    title_map = {
        "stats.agg.aps": ["Atomic Propositions (APs)", "Count"],
        "stats.agg.cops": ["Comparison Operators (COPs)", "Count"],
        "stats.agg.lops": ["Logical Operators (LOPs)", "Count"],
        "stats.agg.tops": ["Temporal Operators (TOPs)", "Count"],
        "stats.asth": ["Abstract Syntrax Tree Height (ASTH)", "Height"],
        "stats.entropy.lops_tops": ["Entropy (LOPs & TOPs)", "Entropy (base 2)"],
        "stats.req_len": ["Requirement Text Length", "Character Count"],
        "stats.req_sentence_count": ["Requirement Sentences", "Sentence Count"],
        "stats.req_word_count": ["Requirement Words", "Word Count"],
    }
    translatability = ["yes", "no", "depends"]

    def __init__(self, config: Configuration, file, selfonly=False):
        self.config = config
        self.data = pd.read_excel(file)
        if selfonly:
            selftypes = self.data[self.data["translation"] == "self"]["type"].unique()
            self.data = self.data[self.data["type"].isin(selftypes)]

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
        _, axes = plt.subplots(2, 2, figsize=(7, 4), sharex=True, sharey=True)
        axes = axes.flatten()
        titles = {
            "self": {"title": "(a) Natural Formalization", "var": "n"},
            "yes": {"title": "(b) Possible", "var": "t_1"},
            "no": {"title": "(c) Not Possible", "var": "t_2"},
            "depends": {"title": "(d) Conditional", "var": "t_3"},
        }
        max_count = df["type"].value_counts().max() + 5
        translations_ordered = sorted(
            df["translation"].unique(), key=lambda x: list(titles.keys()).index(x)
        )

        for ax, translation in zip(axes, translations_ordered):
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
            n = df[df["translation"] == translation].shape[0]
            title_info = titles.get(
                translation, {"title": f"Translatable: {translation}", "var": ""}
            )
            ax.set_title(f"{title_info['title']} (${title_info['var']}={n}$)")
            ax.set_xlabel("")
            ax.set_ylabel("Count")
            ax.set_ylim(0, max_count)
            major_locs = ax.yaxis.get_majorticklocs()
            if len(major_locs) > 1:
                major_interval = major_locs[1] - major_locs[0]
                minor_tick_interval = major_interval / 5
                ax.yaxis.set_minor_locator(ticker.MultipleLocator(minor_tick_interval))

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

    def _plot_violin(
        self, df_long, stats_values, metrics, title_map, out_prefix, include_strip=False
    ):
        type_palette = self.config.color_palette
        number_of_types = df_long["type"].unique().size

        fig, axes = plt.subplots(
            nrows=2 if len(metrics) > 3 else 1,
            ncols=3,
            figsize=(11, 8) if len(metrics) > 3 else (11, 4),
            sharex=False,
            sharey=False,
        )
        axes = axes.flatten()
        plt.subplots_adjust(hspace=0.05, wspace=0.05)
        i = 1

        for ax, agg in zip(axes, metrics):
            y_max = df_long[df_long["aggregation"] == agg]["value"].max() * 1.8
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

            x_shift = 1 / number_of_types / 2
            for _, row in stats_values[stats_values["aggregation"] == agg].iterrows():
                annotation_text = (
                    f"$\mu={row['mean']:.1f}$\n"
                    f"$M={row['median']:.1f}$\n"
                    f"$\sigma={row['std']:.1f}$"
                )
                ax.text(
                    x_shift,
                    0.83,
                    annotation_text,
                    color="black",
                    ha="center",
                    va="bottom",
                    transform=ax.transAxes,
                )
                x_shift += 1 / number_of_types

            if i > 0:  # increase to print 'n=...' more sparsly
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
                        -0.18 * y_max,
                        f"$n={n_value}$",
                        color="black",
                        ha="center",
                        va="top",
                    )

            i += 1
            ax.set_title(title_map.get(agg, agg)[0])
            ax.set_ylabel(title_map.get(agg, agg)[1])
            ax.set_ylim(-0.09 * y_max, y_max)
            major_locs = ax.yaxis.get_majorticklocs()
            if len(major_locs) > 1:
                major_interval = major_locs[1] - major_locs[0]
                minor_tick_interval = major_interval / 5
                ax.yaxis.set_minor_locator(ticker.MultipleLocator(minor_tick_interval))

        for j in range(len(metrics), len(axes)):
            axes[j].set_visible(False)

        fig.tight_layout()
        out = self.__get_file_name(out_prefix)
        plt.savefig(out)
        plt.close()
        return out

    def plot_violin_engcompl(self, include_strip=False):
        df_filtered = self.data[self.data["translation"] == "self"]
        metrics = df_filtered.filter(like=".agg.").columns.tolist()
        metrics = metrics + ["stats.asth", "stats.entropy.lops_tops"]
        df_long = pd.melt(
            df_filtered,
            id_vars=["id", "type"],
            value_vars=metrics,
            var_name="aggregation",
            value_name="value",
        )

        stats_values = (
            df_long.groupby(["type", "aggregation"])["value"]
            .agg(["mean", "median", "count", "std"])
            .reset_index()
        )
        return self._plot_violin(
            df_long,
            stats_values,
            metrics,
            self.title_map,
            "viol_engcompl",
            include_strip,
        )

    def plot_violin_reqtext(self, include_strip=False):
        df_filtered = self.data[self.data["translation"] == "self"]
        metrics = df_filtered.filter(like=".req_").columns.tolist()
        df_long = pd.melt(
            df_filtered,
            id_vars=["id", "type"],
            value_vars=metrics,
            var_name="aggregation",
            value_name="value",
        )

        stats_values = (
            df_long.groupby(["type", "aggregation"])["value"]
            .agg(["mean", "median", "count", "std"])
            .reset_index()
        )
        return self._plot_violin(
            df_long, stats_values, metrics, self.title_map, "viol_req", include_strip
        )

    def plot_pairplot(self):
        type_palette = self.config.color_palette
        df = self.data[self.data["translation"] == "self"]
        metrics = df.filter(like=".agg.").columns.tolist()
        df_pairplot = df[metrics + ["type", "stats.asth", "stats.entropy.lops_tops"]]

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
            ax.set_xlabel(self.title_map.get(row_var, row_var)[0])
            ax.set_ylabel(self.title_map.get(col_var, col_var)[0])
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
        flow_counts = {"yes": {}, "no": {}, "depends": {}}
        for id_value, group in df.groupby("id"):
            source_type = group[group["translation"] == "self"]["type"].values[0]
            for _, row in group.iterrows():
                target_type = row["type"]
                translation_type = row["translation"]
                if translation_type in self.translatability:
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
            "depends": "rgba(128, 128, 128, 0.7)",
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
        for target in self.translatability:
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
                    arrowhead=38,
                    fontsize=13,
                )
                outs.append(out)

        return "\n".join(outs)

    def plot_dag_interactive(self):
        outs = []
        for target in self.translatability:
            df = self.data.copy()
            G = nx.DiGraph()

            # constructing the directed graph
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
                        if G.has_edge(source_type, target_type):
                            G[source_type][target_type]["weight"] += 1
                        else:
                            G.add_edge(
                                source_type,
                                target_type,
                                weight=1,
                                color=Utils.lighten_color(
                                    hex_color=self.config.color_palette.get(
                                        source_type, "black"
                                    ),
                                    opacity=0.8,
                                ),
                            )

            if G.number_of_edges() > 0:
                # using PyVis for interactive plotting
                net = Network(
                    notebook=True,
                    directed=True,
                    height="600px",
                    width="100%",
                    cdn_resources="in_line",
                )
                net.from_nx(G)
                net.show_buttons(filter_=["physics"])

                for node in net.nodes:
                    node["color"] = Utils.lighten_color(
                        hex_color=self.config.color_palette.get(node["label"], "black"),
                        opacity=0.8,
                    )
                    # node['opacity'] = 0.6
                    node["font"] = {"color": "black", "size": 28}
                    node["borderWidth"] = 2
                    node["shape"] = "box"

                for edge in net.edges:
                    weight = G[edge["from"]][edge["to"]].get("width", 1)
                    color = G[edge["from"]][edge["to"]].get("color", "black")
                    edge["value"] = math.log10(weight)
                    edge["title"] = f"Weight: {weight}"
                    edge["arrowStrikethrough"] = True
                    edge["color"] = color
                    edge["label"] = str(weight)
                    edge["font"] = {
                        "color": "black",
                        "size": 10,
                        "background": "rgba(255, 255, 255, 0)",
                        "strokeWidth": 0,
                    }
                    edge["arrows"] = {"to": {"enabled": True, "scaleFactor": 1.5}}

                net.set_edge_smooth("dynamic")
                net.repulsion(
                    node_distance=100,
                    central_gravity=0.05,
                    spring_length=80,
                    spring_strength=0.005,
                )

                # save as HTML
                out = self.__get_file_name(f"dag_{target}", ".html")
                net.show(out)
                outs.append(out)

        return outs
