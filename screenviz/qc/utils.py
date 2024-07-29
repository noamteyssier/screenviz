from typing import List, Tuple

import numpy as np
import pandas as pd


def load_data(
    filename: str, guide_column: str, gene_column: str
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, List[str], List[str]]:
    frame = pd.read_csv(filename, sep="\t")
    sample_columns = [
        col for col in frame.columns if col not in [guide_column, gene_column]
    ]
    df = frame.copy()
    df_normal = df.copy()
    df_log = df.copy()
    df_log[sample_columns] = np.log10(df[sample_columns] + 1)
    gene_list = sorted(df[gene_column].unique())
    return (df, df_normal, df_log, sample_columns, gene_list)


def calculate_correlation_matrix(
    df: pd.DataFrame, sample_columns: List[str], method: str = "spearman"
) -> pd.DataFrame:
    return df[sample_columns].corr(method=method)
