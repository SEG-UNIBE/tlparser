import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from tlparser.utils import Utils
from tlparser.config import Configuration


class Viz:

    type_order = ["INV", "LTL", "MTLb", "MITL", "TPTL", "STL"]

    title_map = {
        "stats.agg.aps": "Atomic Propositions",
        "stats.agg.cops": "Comparison Operators",
        "stats.agg.lops": "Logical Operators",
        "stats.agg.tops": "Temporal Operators",
    }

    def __init__(self, config: Configuration, file):
        self.config = config
        self.data = pd.read_excel(file)

    def plot_distribution_natural(self):
        empty_counts = (
            self.data[self.data["projection"] == "self"]
            .groupby("type")
            .size()
            .reindex(self.type_order, fill_value=0)
        )

        plt.figure(figsize=(8, 6))
        empty_counts.plot(kind="bar")

        plt.xlabel("Logic")
        plt.ylabel("Requirements")
        plt.title("Histogram of Natural Fomalizations by Logic")
        plt.xticks(rotation=0)

        os.makedirs(self.config.folder_data_out, exist_ok=True)
        prefix = Utils.extract_filename_without_suffix(self.config.file_data_in)
        out = os.path.join(
            self.config.folder_data_out,
            f"dist_nat_{prefix}_{Utils.get_unique_filename()}_dist.pdf",
        )
        plt.savefig(out)
        plt.close()

        return out

    def plot_distribution_combined(self):
        projection_counts = (
            self.data.groupby(["type", "projection"])
            .size()
            .unstack(fill_value=0)
            .reindex(self.type_order, fill_value=0)
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

        os.makedirs(self.config.folder_data_out, exist_ok=True)
        prefix = Utils.extract_filename_without_suffix(self.config.file_data_in)
        out = os.path.join(
            self.config.folder_data_out,
            f"dist_comb_{prefix}_{Utils.get_unique_filename()}_dist.pdf",
        )
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
            .agg(["mean", "median", "count"])
            .reset_index()
        )

        y_min = df_long["value"].min()
        y_max = df_long["value"].max() + 5

        # Create a 2x2 grid of subplots
        fig, axes = plt.subplots(
            nrows=2, ncols=2, figsize=(11, 7), sharex=True, sharey=True
        )
        axes = axes.flatten()  # Flatten the axes array for easier iteration
        plt.subplots_adjust(hspace=0.2, wspace=0.2)

        # Plot each aggregation in a separate subplot
        for ax, agg in zip(axes, agg_columns):
            violin = sns.violinplot(
                x="type",
                y="value",
                data=df_long[df_long["aggregation"] == agg],
                palette="colorblind",
                bw_method=0.5,
                ax=ax,
            )
            # Make violins slightly transparent
            for violin_part in violin.collections:
                violin_part.set_alpha(0.6)

            sns.swarmplot(
                x="type",
                y="value",
                data=df_long[df_long["aggregation"] == agg],
                color="black",
                alpha=0.5,
                size=4,
                marker="o",
                edgecolor="white",
                ax=ax,
            )
            ax.set_xlabel("")

            # Annotate mean and median values on the plot above each violin
            for _, row in stats_values[stats_values["aggregation"] == agg].iterrows():
                # Position the annotations above the maximum data point with some padding
                annotation_y = y_max - 0.5

                # Prepare formatted string for annotation
                annotation_text = (
                    f"n: {row['count']:<5}\n"
                    f"μ:  {row['mean']:<4.1f}\n"
                    f"M:  {row['median']:<4.1f}"
                )

                ax.text(
                    row["type"],
                    annotation_y,
                    annotation_text,
                    color="black",
                    ha="center",
                    va="bottom",
                    fontfamily="monospace",
                    # size=8,
                )

            ax.set_title(self.title_map.get(agg, agg))
            ax.set_ylabel("Count")
            ax.set_ylim(y_min - 5, y_max + 5)

        # Hide any unused subplots if number of agg_columns is less than 4
        for i in range(len(agg_columns), len(axes)):
            axes[i].set_visible(False)

        # plt.suptitle(
        #     'Violin and Swarm Plot of Aggregation Values by Type (Filtered by projection = "self")'
        # )
        fig.tight_layout()

        out = self.get_file_name("violine")
        plt.savefig(out)
        plt.close()
        return out

    def get_file_name(self, prefix):
        os.makedirs(self.config.folder_data_out, exist_ok=True)
        return os.path.join(
            self.config.folder_data_out,
            f"{prefix}_{Utils.get_unique_filename()}_dist.pdf",
        )
