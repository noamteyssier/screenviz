# screenviz.results.gene_card

import numpy as np
import plotly.express as px
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output
from dash_daq import ToggleSwitch

from .._constants import (
    DEPLETION_COLOR,
    ENRICHMENT_COLOR,
    NON_TARGETING_COLOR,
    NOT_SIGNIFICANT_COLOR,
)
from ._utils import load_gene_dataframe, load_sgrna_dataframe


class GeneCard:
    PVALUE_COLUMN = "pvalue"
    LFC_COLUMN = "log2fc"
    COLOR_MAP = {
        "Enriched": ENRICHMENT_COLOR,
        "Depleted": DEPLETION_COLOR,
        "Not significant": NOT_SIGNIFICANT_COLOR,
        "Amalgam": NON_TARGETING_COLOR,
    }
    SYMBOL_MAP = {
        True: "circle-open",
        False: "circle",
    }

    def __init__(self, gene_file: str, sgrna_file: str, amalgam_token: str = "amalgam"):
        self.gene_filename = gene_file
        self.sgrna_filename = sgrna_file
        self.amalgam_token = amalgam_token
        self.gene_frame = load_gene_dataframe(gene_file)
        self.sgrna_frame = load_sgrna_dataframe(sgrna_file)
        self.build_sgrna_fdr_lookup()
        self.layout = self.create_layout()

    def build_sgrna_fdr_lookup(self):
        """
        Create a lookup table to easily pull out sgRNA FDRs for each gene.
        """
        self.sgrna_fdr_lookup = dict()
        genes = self.gene_frame["gene"].unique()
        for gene in genes:
            gene_sgrnas = self.sgrna_frame[self.sgrna_frame["gene"] == gene]
            self.sgrna_fdr_lookup[gene] = gene_sgrnas["fdr"].values

    def create_layout(self):
        return html.Div(
            [
                html.H2("Gene Differential Abundance"),
                dcc.Graph(id="gene-volcano-plot"),
                html.Div(
                    [
                        html.Br(),
                        html.Label("Toggle FDR/p-value:"),
                        ToggleSwitch(
                            id="gene-toggle-fdr-pvalue",
                            value=True,
                            label=["p-value", "FDR"],
                            style={
                                "width": "250px",
                                "margin": "left: auto; right: auto;",
                            },
                        ),
                        html.Br(),
                        html.Label("P-value clamping threshold:"),
                        dcc.Slider(
                            id="gene-clamp-slider",
                            min=1,
                            max=100,
                            step=1,
                            value=30,
                            marks={i: str(i) for i in range(0, 101, 10)},
                        ),
                        html.Label("Gene FDR Threshold:"),
                        dcc.Input(
                            id="gene-threshold-input",
                            type="number",
                            value=0.1,
                            step=0.01,
                        ),
                        html.Br(),
                        html.Label("sgRNA FDR Threshold:"),
                        dcc.Input(
                            id="sgrna-threshold-input",
                            type="number",
                            value=0.1,
                            step=0.01,
                        ),
                    ]
                ),
                html.Br(),
                html.H3("Data Table, Filtered by Threshold"),
                dash_table.DataTable(
                    id="gene-data-table",
                    columns=[{"name": i, "id": i} for i in self.gene_frame.columns],
                    data=self.gene_frame.to_dict("records"),
                    page_size=10,
                    sort_action="native",
                    filter_action="native",
                ),
            ]
        )

    def register_callbacks(self, app):
        @app.callback(
            Output("gene-volcano-plot", "figure"),
            [
                Input("gene-threshold-input", "value"),
                Input("sgrna-threshold-input", "value"),
                Input("gene-clamp-slider", "value"),
                Input("gene-toggle-fdr-pvalue", "value"),
            ],
        )
        def update_plot(gene_threshold, sgrna_threshold, clamp_threshold, use_fdr):
            return self.create_volcano_plot(
                gene_threshold, sgrna_threshold, clamp_threshold, use_fdr
            )

        @app.callback(
            Output("gene-data-table", "data"), [Input("gene-threshold-input", "value")]
        )
        def update_data_table(threshold):
            filtered_df = self.gene_frame[self.gene_frame["fdr"] < threshold]
            return filtered_df.to_dict("records")

    def classify(self, x, lfc):
        if self.amalgam_token in x.gene:
            return "Amalgam"
        elif x.is_significant and x[lfc] > 0:
            return "Enriched"
        elif x.is_significant and x[lfc] < 0:
            return "Depleted"
        else:
            return "Not significant"

    def count_significant_sgrnas(self, gene: str, sgrna_threshold: str) -> int:
        """
        Count the number of significant sgRNAs for a given gene (lookups the FDR array in a precalculated table).
        """
        return (self.sgrna_fdr_lookup[gene] < sgrna_threshold).sum()

    def create_volcano_plot(
        self, gene_threshold=0.1, sgrna_threshold=0.1, clamp_threshold=30, use_fdr=True
    ):
        df = self.gene_frame.copy()
        df["log_pvalue"] = -np.log10(df[self.PVALUE_COLUMN])
        df["log_fdr"] = -np.log10(df["fdr"])
        df["clamped_log_pvalue"] = df["log_pvalue"].clip(upper=clamp_threshold)
        df["clamped_log_fdr"] = df["log_fdr"].clip(upper=clamp_threshold)
        df["is_significant"] = df["fdr"] < gene_threshold
        df["classification"] = df.apply(
            lambda x: self.classify(x, self.LFC_COLUMN), axis=1
        )
        df["magnitude"] = df[self.LFC_COLUMN].abs().clip(lower=0.3)
        df["significant_sgrnas"] = df["gene"].apply(
            lambda x: self.count_significant_sgrnas(x, sgrna_threshold)
        )
        df["Single-Significant-SGRNA"] = df.apply(
            lambda x: x["is_significant"] & (x["significant_sgrnas"] == 1), axis=1
        )

        y_col = "clamped_log_fdr" if use_fdr else "clamped_log_pvalue"
        y_title = (
            f"-log10({'FDR' if use_fdr else 'p-value'}) [clamped at {clamp_threshold}]"
        )

        fig = px.scatter(
            df,
            x=self.LFC_COLUMN,
            y=y_col,
            color="classification",
            hover_name="gene",
            hover_data=[
                self.LFC_COLUMN,
                self.PVALUE_COLUMN,
                "fdr",
                "significant_sgrnas",
            ],
            symbol="Single-Significant-SGRNA",
            color_discrete_map=self.COLOR_MAP,
            symbol_map=self.SYMBOL_MAP,
            size="magnitude",
        )

        fig.add_hline(
            y=min(-np.log10(gene_threshold), clamp_threshold),
            line_dash="dash",
            line_color="black",
            name="Threshold",
        )

        fig.update_layout(
            height=600,
            width=1000,
            title_text="Gene Differential Abundance Analysis",
            xaxis_title="log Fold Change",
            yaxis_title=y_title,
            showlegend=True,
        )

        return fig
