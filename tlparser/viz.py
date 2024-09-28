import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns

from tlparser.utils import Utils
from tlparser.config import Configuration


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

    def __get_file_name(self, prefix):
        os.makedirs(self.config.folder_data_out, exist_ok=True)
        return os.path.join(
            self.config.folder_data_out,
            f"{prefix}_{Utils.get_unique_filename()}.pdf",
        )

    def plot_distribution_natural(self):
        empty_counts = (
            self.data[self.data["projection"] == "self"]
            .groupby("type")
            .size()
            .reindex(self.config.logic_order, fill_value=0)
        )

        plt.figure(figsize=(8, 6))
        empty_counts.plot(kind="bar")

        plt.xlabel("Logic")
        plt.ylabel("Requirements")
        plt.title("Histogram of Natural Fomalizations by Logic")
        plt.xticks(rotation=0)

        out = self.__get_file_name("distnat")
        plt.savefig(out)
        plt.close()

        return out

    def plot_distribution_combined(self):
        projection_counts = (
            self.data.groupby(["type", "projection"])
            .size()
            .unstack(fill_value=0)
            .reindex(self.config.logic_order, fill_value=0)
        )

        projection_colors = {
            "self": "blue",
            "yes": "green",
            "no": "red",
            "unknown": "gray",
        }

        plt.figure(figsize=(10, 6))
        projection_counts.plot(
            kind="bar",
            stacked=False,  # grouped bars
            color=[
                projection_colors.get(col, "black") for col in projection_counts.columns
            ],
        )

        plt.xlabel("Logic")
        plt.ylabel("Requirements")
        plt.title("Histogram of Natural Formalizations by Logic and Projection Status")
        plt.xticks(rotation=0)
        plt.legend(title="Projection Status")

        out = self.__get_file_name("distcomb")
        plt.savefig(out)
        plt.close()

        return out

    def plot_complexity(self):

        df_filtered = self.data[self.data["projection"] == "self"]
        agg_columns = df_filtered.filter(like=".agg.").columns.tolist()
        df_long = pd.melt(
            df_filtered,
            id_vars=["id", "type"],
            value_vars=agg_columns,
            var_name="aggregation",
            value_name="value",
        )

        # Calculate mean and median values for annotations
        stats_values = (
            df_long.groupby(["type", "aggregation"])["value"]
            .agg(["mean", "median", "count", "std"])
            .reset_index()
        )

        y_min = df_long["value"].min()
        y_max = df_long["value"].max() + 4.5

        # Create a 2x2 grid of subplots
        fig, axes = plt.subplots(
            nrows=2, ncols=2, figsize=(9, 7), sharex=True, sharey=True
        )
        axes = axes.flatten()  # Flatten the axes array for easier iteration
        plt.subplots_adjust(hspace=0.1, wspace=0.1)
        i = 1
        # Plot each aggregation in a separate subplot
        for ax, agg in zip(axes, agg_columns):
            violin = sns.violinplot(
                x="type",
                y="value",
                data=df_long[df_long["aggregation"] == agg],
                hue="type",
                palette="colorblind",
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
                palette="colorblind",
                data=df_long[df_long["aggregation"] == agg],
                width=0.12,  # Adjust the box width
                showcaps=True,
                showbox=True,
                whiskerprops={"linewidth": 1.2, "color": "black"},
                medianprops={"linewidth": 1.2, "color": "black"},
                ax=ax,
                fliersize=5,
            )
            # Make violins slightly transparent
            for violin_part in violin.collections:
                violin_part.set_alpha(0.5)

            # sns.stripplot(
            #     x="type",
            #     y="value",
            #     hue="type",
            #     data=df_long[df_long["aggregation"] == agg],
            #     alpha=0.4,
            #     size=5,
            #     marker="o",
            #     edgecolor="black",
            #     linewidth=1,
            #     ax=ax,
            #     dodge=False,
            # )
            ax.set_xlabel("")
            ax.yaxis.set_minor_locator(ticker.MultipleLocator(1))

            # Annotate mean and median values on the plot above each violin
            for _, row in stats_values[stats_values["aggregation"] == agg].iterrows():
                # Position the annotations above the maximum data point with some padding
                annotation_y = y_max - 0.5

                # Prepare formatted string for annotation
                annotation_text = (
                    # f"n={row['count']}\n"
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
                    # fontfamily="monospace",
                    # size=8,
                )

            # Place the count 'n' below the x-axis tick marks
            if i > 2:
                for x_category in df_long["type"].unique():
                    # Get the specific count 'n' for this aggregation and type
                    n_value = int(
                        stats_values[
                            (stats_values["aggregation"] == agg)
                            & (stats_values["type"] == x_category)
                        ]["count"].iloc[0]
                    )

                    # Find the x position of the category
                    x_position = list(df_long["type"].unique()).index(x_category)

                    # Annotate n value below the x-tick
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

        # Hide any unused subplots if number of agg_columns is less than 4
        for i in range(len(agg_columns), len(axes)):
            axes[i].set_visible(False)

        fig.tight_layout()

        out = self.__get_file_name("violine")
        plt.savefig(out)
        plt.close()
        return out

    def plot_pairplot(self):

        df = self.data[self.data["projection"] == "self"]
        agg_columns = df.filter(like=".agg.").columns.tolist()
        df_pairplot = df[agg_columns + ["type"]]

        unique_types = df_pairplot["type"].nunique()
        markers = ["o", "s", "D", "^", "v", "P"][:unique_types]

        g = sns.pairplot(
            df_pairplot,
            hue="type",
            palette="colorblind",
            diag_kind="kde",
            markers=markers,
        )

        for ax in g.axes.flat:
            for artist in ax.collections:
                artist.set_edgecolor("black")
                artist.set_alpha(0.6)
        g._legend.set_title("Logic")

        out = self.__get_file_name("pairplot")
        plt.savefig(out)
        plt.close()
        return out

    def plot_projection_classes(self):

        df = self.data[self.data["projection"] == "self"]

        projection_key_counts = df["projclass"].value_counts().reset_index()
        projection_key_counts.columns = ["projclass", "count"]

        # Plot a seaborn histogram for counts per key
        plt.figure(figsize=(10, 6))
        sns.barplot(data=projection_key_counts, x="projclass", y="count")
        plt.xlabel("Projection Key")
        plt.ylabel("Count")
        plt.title("Counts per Projection Class")
        plt.tight_layout()

        out = self.__get_file_name("projclass")
        plt.savefig(out)
        plt.close()
        return out
