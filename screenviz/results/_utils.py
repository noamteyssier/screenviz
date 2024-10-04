from typing import List

import pandas as pd

REQ_SGRNA = ["sgrna", "gene", "log2fc", "pvalue_twosided", "fdr", "base"]
REQ_GENES = ["gene", "log2fc", "pvalue", "fdr"]


def load_dataframe(filename: str, required_columns: List[str]) -> pd.DataFrame:
    """
    Load a dataframe from a file and check that it has the required columns.
    """
    df = pd.read_csv(filename, sep="\t")
    for col in required_columns:
        assert col in df.columns, f"The input file must have a column named {col}"
    return df


def load_gene_dataframe(
    filename: str,
) -> pd.DataFrame:
    """
    Load a gene dataframe from a file and check that it has the required columns.
    """
    return load_dataframe(filename, required_columns=REQ_GENES)


def load_sgrna_dataframe(
    filename: str,
) -> pd.DataFrame:
    """
    Load an sgRNA dataframe from a file and check that it has the required columns.
    """
    return load_dataframe(filename, required_columns=REQ_SGRNA)
