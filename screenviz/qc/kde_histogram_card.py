# screenviz.qc.kde_histogram_card

import numpy as np
import plotly.graph_objects as go
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output
from scipy import stats


class KDEHistogramCard:
    def __init__(self, parent):
        self.parent = parent

    def create_card(self, card_style):
        return html.Div(
            [
                html.H3("sgRNA Count Distribution"),
                html.Div(
                    [
                        # KDE Histogram plot
                        html.Div(
                            [
                                dcc.Graph(
                                    id="kde-histogram-plot",
                                    config={
                                        "displayModeBar": True,
                                        "modeBarButtonsToRemove": [
                                            "lasso2d",
                                            "autoScale2d",
                                            "hoverClosestCartesian",
                                            "hoverCompareCartesian",
                                            "toggleSpikelines",
                                        ],
                                        "displaylogo": False,
                                    },
                                ),
                            ],
                            style={
                                "width": "70%",
                                "display": "inline-block",
                                "vertical-align": "top",
                            },
                        ),
                        # Sample selection table
                        html.Div(
                            [
                                html.Label("Select Samples:"),
                                dash_table.DataTable(
                                    id="sample-selection-table",
                                    columns=[
                                        {"name": "Sample", "id": "sample"},
                                        {
                                            "name": "Include",
                                            "id": "include",
                                            "presentation": "dropdown",
                                        },
                                    ],
                                    data=[
                                        {"sample": col, "include": "Yes"}
                                        for col in self.parent.sample_columns
                                    ],
                                    editable=True,
                                    row_selectable=False,
                                    style_table={
                                        "height": "400px",
                                        "overflowY": "auto",
                                    },
                                    style_cell={"textAlign": "left"},
                                    style_data_conditional=[
                                        {"if": {"column_id": "include"}, "width": "30%"}
                                    ],
                                    dropdown={
                                        "include": {
                                            "options": [
                                                {"label": "Yes", "value": "Yes"},
                                                {"label": "No", "value": "No"},
                                            ]
                                        }
                                    },
                                ),
                            ],
                            style={
                                "width": "28%",
                                "display": "inline-block",
                                "vertical-align": "top",
                                "marginLeft": "2%",
                            },
                        ),
                    ]
                ),
            ],
            className="card",
            style=card_style,
        )

    def create_kde_histogram(self, selected_samples):
        fig = go.Figure()

        for sample in selected_samples:
            kde = self.calculate_kde(self.parent.df_log[sample])
            fig.add_trace(go.Scatter(x=kde[0], y=kde[1], mode="lines", name=sample))

        x_min = self.parent.df_log[selected_samples].values.min()
        x_max = self.parent.df_log[selected_samples].values.max()
        tick_values = np.arange(np.floor(x_min), np.ceil(x_max) + 1)

        # Include 10^x label on the x-axis

        fig.update_layout(
            title="Distribution of Log10 sgRNA Counts",
            xaxis=dict(
                title="Counts",
                tickmode="array",
                tickvals=tick_values,
                ticktext=[f"10<sup>{int(val)}</sup>" for val in tick_values],
                tickangle=0,
            ),
            yaxis_title="Density",
            barmode="overlay",
            height=600,
        )

        return fig

    def calculate_kde(self, data, bandwidth=0.05):
        x_range = np.linspace(data.min(), data.max(), 1000)
        kde = stats.gaussian_kde(data, bw_method=bandwidth)
        return x_range, kde(x_range)

    def register_callbacks(self, app):
        @app.callback(
            Output("kde-histogram-plot", "figure"),
            [
                Input("sample-selection-table", "data"),
                Input("sample-selection-table", "columns"),
            ],
        )
        def update_kde_histogram(rows, columns):
            selected_samples = [
                row["sample"] for row in rows if row["include"] == "Yes"
            ]
            return self.create_kde_histogram(selected_samples)
