# screenviz.qc.app

import dash
from dash import html

from .correlation_matrix_card import CorrelationMatrixCard
from .histogram_membership_card import HistogramMembershipCard
from .scatter_data_card import ScatterDataCard
from .utils import calculate_correlation_matrix, load_data


class CRISPRQCDashApp:
    DEFAULT_MARKER_COLOR = "#ABABAB"
    DEFAULT_HIGHLIGHT_COLOR = "#F68E5F"
    SELECT_FILL_COLOR = "#adb5bd"
    AB_LINE_COLOR = "#ff6b6b"
    DEFAULT_OPACITY = 0.8
    SELECTED_OPACITY = 1.0
    UNSELECTED_OPACITY = 0.25
    THEME_COLOR = "#007bff"
    CARD_STYLE = {
        "backgroundColor": "#f6f6f6",
        "borderRadius": "10px",
        "boxShadow": "0 4px 8px 0 rgba(0,0,0,0.2)",
        "padding": "20px",
        "margin": "20px 0",
    }

    def __init__(self, filename: str, guide_column: str, gene_column: str):
        self.app = dash.Dash(__name__)
        self.df, self.df_normal, self.df_log, self.sample_columns, self.gene_list = (
            load_data(filename, guide_column, gene_column)
        )
        self.guide_column = guide_column
        self.gene_column = gene_column
        self.correlation_matrix = calculate_correlation_matrix(
            self.df, self.sample_columns
        )
        self.total_read_counts = self.df_normal[self.sample_columns].sum()

        self.scatter_data_card = ScatterDataCard(self)
        self.histogram_membership_card = HistogramMembershipCard(self)
        self.correlation_matrix_card = CorrelationMatrixCard(self)

        self.app.layout = self.create_layout()
        self.register_callbacks()

    def create_layout(self):
        return html.Div(
            [
                html.H1(
                    "CRISPR Screen Quality Control Visualization Suite",
                    style={
                        "textAlign": "center",
                        "color": self.THEME_COLOR,
                        "marginBottom": "30px",
                    },
                ),
                self.create_table_of_contents(),
                html.Div(
                    [
                        html.Div(
                            id="scatter-and-data",
                            children=[
                                self.scatter_data_card.create_card(self.CARD_STYLE)
                            ],
                        ),
                        html.Div(
                            id="histogram-and-membership",
                            children=[
                                self.histogram_membership_card.create_card(
                                    self.CARD_STYLE
                                )
                            ],
                        ),
                        html.Div(
                            id="correlation-and-readcounts",
                            children=[
                                self.correlation_matrix_card.create_card(
                                    self.CARD_STYLE
                                )
                            ],
                        ),
                    ]
                ),
            ],
            style={"fontFamily": "Arial, sans-serif", "padding": "20px"},
        )

    def create_table_of_contents(self):
        return html.Div(
            [
                html.H2("Table of Contents", style={"color": self.THEME_COLOR}),
                html.Ul(
                    [
                        html.Li(
                            html.A(
                                "Scatter Plot and Data Table",
                                href="#scatter-and-data",
                            )
                        ),
                        html.Li(
                            html.A(
                                "Gene Membership Distribution and Table",
                                href="#histogram-and-membership",
                            )
                        ),
                        html.Li(
                            html.A(
                                "Sample Correlation Matrix and Read Counts",
                                href="#correlation-and-readcounts",
                            )
                        ),
                    ]
                ),
            ],
            style={"marginBottom": "30px"},
        )

    def register_callbacks(self):
        self.scatter_data_card.register_callbacks(self.app)
        self.histogram_membership_card.register_callbacks(self.app)
        self.correlation_matrix_card.register_callbacks(self.app)

    def run_server(self, debug=True, port=8050):
        self.app.run_server(debug=debug, port=port)
