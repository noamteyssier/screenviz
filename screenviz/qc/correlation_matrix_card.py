import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from dash import dcc, html


class CorrelationMatrixCard:
    def __init__(self, parent):
        self.parent = parent

    def create_card(self, card_style):
        return html.Div(
            [
                html.H3("Sample Correlation Matrix and Read Counts"),
                html.Div(
                    [
                        html.Div(
                            [
                                dcc.Graph(
                                    id="correlation-heatmap",
                                    figure=self.create_correlation_heatmap(),
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
                                "width": "50%",
                                "display": "inline-block",
                                "vertical-align": "top",
                            },
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    id="read-count-barplot",
                                    figure=self.create_read_count_barplot(),
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
                                "width": "50%",
                                "display": "inline-block",
                                "vertical-align": "top",
                            },
                        ),
                    ]
                ),
            ],
            className="card",
            style=card_style,
        )

    def create_correlation_heatmap(self):
        fig = px.imshow(
            self.parent.correlation_matrix,
            x=self.parent.sample_columns,
            y=self.parent.sample_columns,
            color_continuous_scale="viridis",
            aspect="auto",
        )
        fig.update_layout(
            title="Sample Correlation Matrix (Spearman)",
            xaxis_title="Samples",
            yaxis_title="Samples",
            height=600,
            width=800,
        )

        # Add white borders between cells
        for i in range(len(self.parent.sample_columns) + 1):
            fig.add_shape(
                type="line",
                x0=i - 0.5,
                x1=i - 0.5,
                y0=-0.5,
                y1=len(self.parent.sample_columns) - 0.5,
                line=dict(color="white", width=3),
            )
            fig.add_shape(
                type="line",
                x0=-0.5,
                x1=len(self.parent.sample_columns) - 0.5,
                y0=i - 0.5,
                y1=i - 0.5,
                line=dict(color="white", width=3),
            )

        return fig

    def create_read_count_barplot(self):
        log10_counts = np.log10(self.parent.total_read_counts)

        fig = go.Figure(
            data=[
                go.Bar(
                    x=self.parent.sample_columns,
                    y=log10_counts,
                    text=self.parent.total_read_counts.apply(lambda x: f"{x:,}"),
                    textposition="auto",
                )
            ]
        )

        fig.update_layout(
            title="Total Read Counts per Sample",
            xaxis_title="Samples",
            yaxis_title="Log10[ Total Reads ]",
            height=600,
            width=800,
        )

        return fig

    def register_callbacks(self, app):
        # No callbacks are needed for this card as it's static
        pass
