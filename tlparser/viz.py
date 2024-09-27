import os
import pandas as pd
import matplotlib.pyplot as plt

from tlparser.utils import Utils
from tlparser.config import Configuration


class Viz:

    type_order = ["INV", "LTL", "MTLb", "MITL", "TPTL", "STL"]

    def __init__(self, config: Configuration, file):
        self.config = config
        self.data = pd.read_excel(file)

    def plot_distribution(self):
        empty_counts = (
            self.data[self.data["projection"] == "self"]
            .groupby("type")
            .size()
            .reindex(self.type_order, fill_value=0)
        )

        plt.figure(figsize=(8, 6))
        empty_counts.plot(kind="bar")

        plt.xlabel("Type")
        plt.ylabel("Requirements")
        plt.title("Histogram of Natural Fomalizations by Logic")
        plt.xticks(rotation=0)

        os.makedirs(self.config.folder_data_out, exist_ok=True)
        prefix = Utils.extract_filename_without_suffix(self.config.file_data_in)
        out = os.path.join(
            self.config.folder_data_out,
            f"{prefix}_{Utils.get_unique_filename()}_dist.pdf",
        )
        plt.savefig(out)
        plt.close()

        return out
