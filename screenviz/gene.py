import sys
from typing import Optional
import numpy as np
import pandas as pd
import yaml
import plotly.express as px
import plotly.io as pio

pio.templates.default = "plotly_white"


def classify(x, lfc: str, ntc: Optional[str] = None):
    if ntc and ntc in x.gene:
        return "NTC"
    elif x.is_significant and x[lfc] > 0:
        return "Enriched"
    elif x.is_significant and x[lfc] < 0:
        return "Depleted"
    else:
        return "Not significant"


def signify(
    x,
    lfc_column: str,
    threshold_column: str,
    threshold: Optional[float] = None,
    threshold_low: Optional[float] = None,
    threshold_high: Optional[float] = None,
    method: Optional[str] = None,
):
    if threshold_low is not None and threshold_high is not None and method is not None:
        if method == "inc-product":
            return (
                x[threshold_column] < threshold_low
                or x[threshold_column] > threshold_high
            )
        elif method == "inc-pvalue":
            if x[lfc_column] < 0:
                return x[threshold_column] < threshold_low
            else:
                return x[threshold_column] < threshold_high
    else:
        assert threshold, "Must provide a threshold value"
        return x[threshold_column] < threshold


class VisualizeGenes:
    def __init__(
        self,
        filename: str,
        config: Optional[str] = None,
        gene_column: Optional[str] = "gene",
        fc_column: Optional[str] = "log_fold_change",
        pval_column: Optional[str] = "pvalue",
        threshold_column: Optional[str] = "fdr",
        threshold: Optional[float] = 0.1,
        ntc_token: Optional[str] = None,
    ):
        self.filename = filename
        self.config = config

        if self.config:
            self.load_config(self.config)
        else:
            self.gene_column = gene_column
            self.fc_column = fc_column
            self.pval_column = pval_column
            self.threshold_column = threshold_column
            self.threshold = threshold
            self.threshold_low = None
            self.threshold_high = None
            self.ntc_token = ntc_token
            self.method = None

        self.df = self.load_dataframe(filename)

    def load_config(self, config: str):
        with open(config, "r") as f:
            y = yaml.safe_load(f)
            assert "method" in y, "The config file must have a 'method' key"
            assert y["method"] in [
                "rra",
                "inc-pvalue",
                "inc-product",
            ], "The method must be one of 'rra', 'inc-pvalue', or 'inc-product'"

            self.gene_column = y["gene"]
            self.fc_column = y["x"]
            self.pval_column = y["y"]
            self.threshold_column = y["z"]
            self.method = y["method"]

            if y["method"] == "rra":
                self.threshold = y["threshold"]
                self.threshold_low = None
                self.threshold_high = None
            else:
                self.threshold = None
                self.threshold_low = y["threshold_low"]
                self.threshold_high = y["threshold_high"]

            if "ntc_token" in y:
                self.ntc_token = y["ntc_token"]
            else:
                self.ntc_token = None

    def load_dataframe(self, filename: str) -> pd.DataFrame:
        df = pd.read_csv(self.filename, sep="\t")
        assert (
            self.gene_column in df.columns
        ), f"The input file must have a column named {self.gene_column}"
        assert (
            self.fc_column in df.columns
        ), f"The input file must have a column named {self.fc_column}"
        assert (
            self.pval_column in df.columns
        ), f"The input file must have a column named {self.pval_column}"
        assert (
            self.threshold_column in df.columns
        ), f"The input file must have a column named {self.threshold_column}"
        return df

    def add_split_hline(self, fig, xmax):
        x_low = np.linspace(-xmax, 0, 100)
        x_high = np.linspace(0, xmax, 100)
        fig.add_scatter(
            x=x_low,
            y=-np.log10(self.threshold_low) * np.ones(100),
            mode="lines",
            line_color="#002966",
            name="Threshold ({:.3E})".format(self.threshold_low),
            legendgroup="Threshold",
        )
        fig.add_scatter(
            x=x_high,
            y=-np.log10(self.threshold_high) * np.ones(100),
            mode="lines",
            line_color="#801a00",
            name="Threshold ({:.3E})".format(self.threshold_high),
            legendgroup="Threshold",
        )

    def add_split_hyperbolic(self, fig, xmax):
        x_low = -np.linspace(0.1, xmax, 100)
        x_high = np.linspace(0.1, xmax, 100)
        y_low = self.threshold_low / x_low
        y_high = self.threshold_high / x_high
        fig.add_scatter(
            x=x_low,
            y=y_low,
            mode="lines",
            line_color="#002966",
            name="Threshold ({:.3E})".format(self.threshold_low),
            legendgroup="Threshold",
        )
        fig.add_scatter(
            x=x_high,
            y=y_high,
            mode="lines",
            line_color="#801a00",
            name="Threshold ({:.3E})".format(self.threshold_high),
            legendgroup="Threshold",
        )

    def plot_volcano(self, output: str = "volcano.html"):
        self.df[f"log_{self.pval_column}"] = -np.log10(self.df[self.pval_column])
        self.df["is_significant"] = self.df.apply(
            lambda x: signify(
                x,
                self.fc_column,
                self.threshold_column,
                self.threshold,
                self.threshold_low,
                self.threshold_high,
                self.method,
            ),
            axis=1,
        )
        self.df["classification"] = self.df.apply(
            lambda x: classify(x, self.fc_column, self.ntc_token), axis=1
        )
        self.df["sizing"] = self.df.is_significant.apply(lambda x: 10 if x else 5)

        xmax = self.df[self.fc_column].abs().max()
        ymax = self.df[f"log_{self.pval_column}"].max()
        ymin = self.df[f"log_{self.pval_column}"].min()
        xmax_adj = xmax + xmax * 0.1
        ymax_adj = ymax + ymax * 0.1

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
                "Not significant": "#333333",
                "NTC": "#808080",
            },
        )
        if not self.threshold_low and not self.threshold_high:
            if self.threshold_column == self.pval_column:
                fig.add_hline(
                    y=-np.log10(self.threshold),
                    line_dash="dash",
                    line_color="black",
                    name="Threshold",
                )
        else:
            if self.method == "inc-pvalue":
                self.add_split_hline(fig, xmax)
            elif self.method == "inc-product":
                self.add_split_hyperbolic(fig, xmax)

        fig.update_xaxes(range=[-xmax_adj, xmax_adj])
        fig.update_yaxes(range=[max(0, ymin), ymax_adj])
        fig.update_layout(
            height=800,
            width=1200,
            title="Volcano plot of gene enrichment analysis",
        )

        print(f"Saving volcano plot to: {output}", file=sys.stderr)
        fig.write_html(output)
