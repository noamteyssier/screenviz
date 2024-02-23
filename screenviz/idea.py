import sys
from typing import Optional
import numpy as np
import pandas as pd
from idea import run_gsea, IDEA


def RunIDEA(
    filename: str,
    geneset: str,
    output: str,
    gene_column: str,
    fc_column: str,
    pval_column: str,
    threshold_column: str,
    threshold: float,
    sided: Optional[str],
    top: int,
):
    """Run IDEA analysis."""
    frame = pd.read_csv(filename, sep="\t")
    frame["padj"] = frame[pval_column].values
    frame["gene_column"] = frame[gene_column].values
    sig = frame[frame[threshold_column] < threshold].copy()
    if sided:
        if sided == "up":
            sig = sig[sig[fc_column] > 0]
            palette = "Reds"
        elif sided == "down":
            sig = sig[sig[fc_column] < 0]
            sig[fc_column] = -sig[fc_column]
            palette = "Blues"
    else:
        palette = None

    gsea = run_gsea(
        sig[gene_column].values, geneset, background=frame[gene_column].values
    )
    if gsea.shape[0] == 0:
        sys.exit(f"No gene sets were enriched for provided geneset: {geneset}")
    idea = IDEA(
        sig,
        gsea.head(top),
        deg_color_name=fc_column,
        gene_palette=palette,
        term_palette="Greens",
    )
    idea.visualize(f"{output}.{geneset}.html")
