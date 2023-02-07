import sys
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio

pio.templates.default = "plotly_white"

def classify(x, lfc: str):
    if x.is_significant and x[lfc]> 0:
        return "Enriched"
    elif x.is_significant and x[lfc]< 0:
        return "Depleted"
    else:
        return "Not significant"

class VisualizeGenes:
    def __init__(
            self, 
            filename: str,
            gene_column: str = "gene",
            fc_column: str = "log_fold_change",
            pval_column: str = "pvalue",
            threshold_column: str = "fdr",
            threshold: float = 0.1,
        ):
        self.filename = filename
        self.gene_column = gene_column
        self.fc_column = fc_column
        self.pval_column = pval_column
        self.threshold_column = threshold_column
        self.threshold = threshold

        self.df = self.load_dataframe(filename)

    def load_dataframe(self, filename: str) -> pd.DataFrame:
        df = pd.read_csv(self.filename, sep="\t")
        assert self.gene_column in df.columns, f"The input file must have a column named {self.gene_column}"
        assert self.fc_column in df.columns, f"The input file must have a column named {self.fc_column}"
        assert self.pval_column in df.columns, f"The input file must have a column named {self.pval_column}"
        assert self.threshold_column in df.columns, f"The input file must have a column named {self.threshold_column}"
        return df

    def plot_volcano(self, output: str = "volcano.html"):
        self.df[f"log_{self.pval_column}"] = -np.log10(self.df[self.pval_column])
        self.df["is_significant"] = self.df[self.threshold_column] < self.threshold
        self.df["classification"] = self.df.apply(lambda x: classify(x, self.fc_column), axis=1)
        self.df["sizing"] = self.df.is_significant.apply(lambda x: 10 if x else 5)
        
        xmax = self.df[self.fc_column].abs().max()
        xmax_adj = xmax + xmax * 0.1

        fig = px.scatter(
            self.df,
            x=self.fc_column,
            y=f"log_{self.pval_column}",
            hover_name=self.gene_column,
            color="classification",
            size="sizing",
            color_discrete_map={
                "Enriched": "#801a00",
                "Depleted": "#002966",
                "Not significant": "#808080",
            }
        )
        if self.threshold_column == self.pval_column:
            fig.add_hline(y=-np.log10(self.threshold), line_dash="dash", line_color="black", name="Threshold")
        fig.update_xaxes(range=[-xmax_adj, xmax_adj])
        fig.update_layout(
            height=1400,
            width=1400,
            title="Volcano plot of gene enrichment analysis",
        )

        print(f"Saving volcano plot to: {output}", file=sys.stderr)
        fig.write_html(output)
