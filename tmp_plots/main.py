import os
import pandas as pd

from plots import (
    plot_violin,
    plot_scatter,
    plot_upset,
    plot_stacked_barchart,
    plot_correlation_matrix,
    plot_extended_correlation_matrix,
    plot_extended_conditional_probability_matrix,
    plot_extended_jaccard_similarity_matrix,
    plot_frequent_itemset_mining,
    plot_semantic_features_frequency,
)
from clustering import plot_agglomerative_clustering_and_pca


DATA_FILE = "spacewire_250919215922.xlsx"
OUTPUT_DIR = "output"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_excel(DATA_FILE)

    # Call any plots you want to generate. Comment out lines to skip.
    plot_violin(df, OUTPUT_DIR)
    plot_scatter(df, OUTPUT_DIR)
    plot_upset(df, OUTPUT_DIR)
    plot_stacked_barchart(df, OUTPUT_DIR)
    plot_correlation_matrix(df, OUTPUT_DIR)
    plot_extended_correlation_matrix(df, OUTPUT_DIR)
    plot_extended_conditional_probability_matrix(df, OUTPUT_DIR)
    plot_extended_jaccard_similarity_matrix(df, OUTPUT_DIR)
    plot_frequent_itemset_mining(df, OUTPUT_DIR)
    plot_semantic_features_frequency(df, OUTPUT_DIR)

    # Clustering and PCA plots are in a separate module
    plot_agglomerative_clustering_and_pca(df, OUTPUT_DIR, manual_n_clusters=5)


if __name__ == "__main__":
    main()
