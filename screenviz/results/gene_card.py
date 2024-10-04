# screenviz.results.gene_card

import numpy as np
import pandas as pd
import plotly.express as px
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output
from dash_daq import ToggleSwitch


class GeneCard:
    PVALUE_COLUMN = "pvalue"
    LFC_COLUMN = "log2fc"
    COLOR_MAP = {
        "Enriched": "#801a00",
        "Depleted": "#002966",
        "Not significant": "#808080",
    }

    def __init__(self, gene_file):
        self.filename = gene_file
        self.df = self.load_dataframe(gene_file)
        self.layout = self.create_layout()

    def load_dataframe(self, filename):
        df = pd.read_csv(filename, sep="\t")
        required_columns = [
            "gene",
            self.LFC_COLUMN,
            self.PVALUE_COLUMN,
            "fdr",
        ]
        for col in required_columns:
            assert col in df.columns, f"The input file must have a column named {col}"
        return df

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
                        html.Label("FDR Threshold:"),
                        dcc.Input(
                            id="gene-threshold-input",
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
                    columns=[{"name": i, "id": i} for i in self.df.columns],
                    data=self.df.to_dict("records"),
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
                Input("gene-clamp-slider", "value"),
                Input("gene-toggle-fdr-pvalue", "value"),
            ],
        )
        def update_plot(threshold, clamp_threshold, use_fdr):
            return self.create_volcano_plot(threshold, clamp_threshold, use_fdr)

        @app.callback(
            Output("gene-data-table", "data"), [Input("gene-threshold-input", "value")]
        )
        def update_data_table(threshold):
            filtered_df = self.df[self.df["fdr"] < threshold]
            return filtered_df.to_dict("records")

    def classify(self, x, lfc):
        if x.is_significant and x[lfc] > 0:
            return "Enriched"
        elif x.is_significant and x[lfc] < 0:
            return "Depleted"
        else:
            return "Not significant"

    def create_volcano_plot(self, threshold=0.1, clamp_threshold=30, use_fdr=True):
        df = self.df.copy()
        df["log_pvalue"] = -np.log10(df[self.PVALUE_COLUMN])
        df["log_fdr"] = -np.log10(df["fdr"])
        df["clamped_log_pvalue"] = df["log_pvalue"].clip(upper=clamp_threshold)
        df["clamped_log_fdr"] = df["log_fdr"].clip(upper=clamp_threshold)
        df["is_significant"] = df["fdr"] < threshold
        df["classification"] = df.apply(
            lambda x: self.classify(x, self.LFC_COLUMN), axis=1
        )
        df["magnitude"] = df[self.LFC_COLUMN].abs().clip(lower=0.3)

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
            hover_data=[self.LFC_COLUMN, self.PVALUE_COLUMN, "fdr"],
            color_discrete_map=self.COLOR_MAP,
            size="magnitude",
        )

        fig.add_hline(
            y=min(-np.log10(threshold), clamp_threshold),
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
