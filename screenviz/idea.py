# screenviz.idea

import sys
from typing import Optional
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
    term_threshold: float,
    sided: Optional[str],
    top: int,
    gene_palette: Optional[str] = None,
    term_palette: Optional[str] = None,
    up_color: Optional[str] = "Reds",
    down_color: Optional[str] = "Blues",
):
    """Run IDEA analysis."""
    frame = pd.read_csv(filename, sep="\t")
    frame["padj"] = frame[pval_column].values
    frame["gene_column"] = frame[gene_column].values
    sig = frame[frame[threshold_column] < threshold].copy()
    if sided:
        if sided == "up":
            sig = sig[sig[fc_column] > 0]
            gene_palette = up_color
        elif sided == "down":
            sig = sig[sig[fc_column] < 0]
            sig[fc_column] = -sig[fc_column]
            gene_palette = down_color

    gsea = run_gsea(
        genes=sig[gene_column].values,
        library=geneset,
        background=frame[gene_column].values,
    )
    if gsea.shape[0] == 0:
        sys.exit(f"No gene sets were enriched for provided geneset: {geneset}")
    idea = IDEA(
        sig,
        gsea.head(top),
        deg_color_name=fc_column,
        gene_palette=gene_palette,
        term_palette=term_palette,
    )
    idea.visualize(f"{output}.{geneset}.html")
