# screenviz.results.sgrna_card

import numpy as np
import pandas as pd
import plotly.express as px
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output
from dash_daq import ToggleSwitch
from plotly.subplots import make_subplots


class SGRNACard:
    PVALUE_COLUMN = "pvalue_twosided"
    COLOR_MAP = {
        "Enriched": "#801a00",
        "Depleted": "#002966",
        "Not significant": "#808080",
    }

    def __init__(self, sgrna_file):
        self.filename = sgrna_file
        self.df = self.load_dataframe(sgrna_file)
        self.layout = self.create_layout()

    def load_dataframe(self, filename):
        df = pd.read_csv(filename, sep="\t")
        required_columns = [
            "sgrna",
            "gene",
            "log2fc",
            self.PVALUE_COLUMN,
            "fdr",
            "base",
        ]
        for col in required_columns:
            assert col in df.columns, f"The input file must have a column named {col}"
        return df

    def create_layout(self):
        return html.Div(
            [
                html.H2("sgRNA Differential Abundance"),
                dcc.Graph(id="sgrna-plots"),
                html.Div(
                    [
                        html.Br(),
                        html.Label("Toggle FDR/p-value:"),
                        ToggleSwitch(
                            id="toggle-fdr-pvalue",
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
                            id="clamp-slider",
                            min=1,
                            max=100,
                            step=1,
                            value=30,
                            marks={i: str(i) for i in range(0, 101, 10)},
                        ),
                        html.Label("FDR Threshold:"),
                        dcc.Input(
                            id="threshold-input", type="number", value=0.1, step=0.01
                        ),
                    ]
                ),
                html.Br(),
                html.H3("Data Table, Filtered by Threshold"),
                dash_table.DataTable(
                    id="sgrna-data-table",
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
            Output("sgrna-plots", "figure"),
            [
                Input("threshold-input", "value"),
                Input("clamp-slider", "value"),
                Input("toggle-fdr-pvalue", "value"),
            ],
        )
        def update_plots(threshold, clamp_threshold, use_fdr):
            return self.create_plots(threshold, clamp_threshold, use_fdr)

        @app.callback(
            Output("sgrna-data-table", "data"), [Input("threshold-input", "value")]
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

    def create_plots(self, threshold=0.1, clamp_threshold=30, use_fdr=True):
        df = self.df.copy()
        df["log_pvalue"] = -np.log10(df[self.PVALUE_COLUMN])
        df["log_fdr"] = -np.log10(df["fdr"])
        df["clamped_log_pvalue"] = df["log_pvalue"].clip(upper=clamp_threshold)
        df["clamped_log_fdr"] = df["log_fdr"].clip(upper=clamp_threshold)
        df["is_significant"] = df["fdr"] < threshold
        df["classification"] = df.apply(lambda x: self.classify(x, "log2fc"), axis=1)
        df["magnitude"] = df["log2fc"].abs().clip(lower=0.3)

        fig = make_subplots(rows=1, cols=2, subplot_titles=("Volcano Plot", "MA Plot"))

        # Volcano Plot
        y_col = "clamped_log_fdr" if use_fdr else "clamped_log_pvalue"
        y_title = (
            f"-log10({'FDR' if use_fdr else 'p-value'}) [clamped at {clamp_threshold}]"
        )

        volcano_trace = px.scatter(
            df,
            x="log2fc",
            y=y_col,
            color="classification",
            hover_name="sgrna",
            hover_data=["gene", "log2fc", self.PVALUE_COLUMN, "fdr"],
            color_discrete_map=self.COLOR_MAP,
        )

        for trace in volcano_trace.data:
            fig.add_trace(trace, row=1, col=1)

        fig.add_hline(
            y=min(-np.log10(threshold), clamp_threshold),
            line_dash="dash",
            line_color="black",
            name="Threshold",
            row=1,
            col=1,
        )

        # MA Plot
        ma_trace = px.scatter(
            df,
            x=np.log10(df["base"] + 1),
            y="log2fc",
            color="classification",
            hover_name="sgrna",
            hover_data=["gene", "log2fc", self.PVALUE_COLUMN, "fdr"],
            color_discrete_map=self.COLOR_MAP,
            size="magnitude",
        )

        for trace in ma_trace.data:
            fig.add_trace(trace, row=1, col=2)

        # add a horizontal line at the zero-fold change threshold
        fig.add_hline(
            y=0,
            line_dash="solid",
            line_color="black",
            name="Origin",
            row=1,
            col=2,
        )

        fig.update_xaxes(title_text="log2 Fold Change", row=1, col=1)
        fig.update_yaxes(title_text=y_title, row=1, col=1)
        fig.update_xaxes(title_text="log10(Base Mean)", row=1, col=2)
        fig.update_yaxes(title_text="log2 Fold Change", row=1, col=2)

        fig.update_layout(
            height=600,
            width=1500,
            title_text="sgRNA Differential Abundance Analysis",
            showlegend=False,
        )

        return fig
