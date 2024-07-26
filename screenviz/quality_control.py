import dash
import pandas as pd
import plotly.express as px
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output


class CRISPRQCDashApp:
    def __init__(self, filename: str, guide_column: str, gene_column: str):
        self.app = dash.Dash(__name__)
        self.df = pd.read_csv(filename, sep="\t")
        self.guide_column = guide_column
        self.gene_column = gene_column
        self.sample_columns = [
            col for col in self.df.columns if col not in [guide_column, gene_column]
        ]

        self.app.layout = self.create_layout()
        self.register_callbacks()

    def create_layout(self):
        return html.Div(
            [
                html.H1("CRISPR Screen Quality Control Visualization Suite"),
                html.Div(
                    [
                        # Left panel: Scatter plot
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id="x-axis-dropdown",
                                    options=[
                                        {"label": col, "value": col}
                                        for col in self.sample_columns
                                    ],
                                    value=self.sample_columns[0],
                                ),
                                dcc.Dropdown(
                                    id="y-axis-dropdown",
                                    options=[
                                        {"label": col, "value": col}
                                        for col in self.sample_columns
                                    ],
                                    value=self.sample_columns[1]
                                    if len(self.sample_columns) > 1
                                    else self.sample_columns[0],
                                ),
                                dcc.Graph(
                                    id="scatter-plot", config={"displayModeBar": False}
                                ),
                            ],
                            style={"width": "48%", "display": "inline-block"},
                        ),
                        # Right panel: Data table
                        html.Div(
                            [
                                dash_table.DataTable(
                                    id="data-table",
                                    columns=[
                                        {"name": i, "id": i} for i in self.df.columns
                                    ],
                                    data=self.df.to_dict("records"),
                                    page_size=10,
                                    style_table={
                                        "height": "500px",
                                        "overflowY": "auto",
                                    },
                                )
                            ],
                            style={
                                "width": "48%",
                                "float": "right",
                                "display": "inline-block",
                            },
                        ),
                    ]
                ),
            ]
        )

    def get_figure(self, x_col, y_col, selection_range):
        fig = px.scatter(
            self.df, x=x_col, y=y_col, hover_data=[self.guide_column, self.gene_column]
        )

        fig.update_traces(
            mode="markers",
            marker={"color": "rgba(0, 116, 217, 0.7)", "size": 10},
        )

        fig.update_layout(
            dragmode="select",
            hovermode="closest",
            newselection_mode="gradual",
        )

        if selection_range:
            fig.add_shape(
                type="rect",
                x0=selection_range["x"][0],
                x1=selection_range["x"][1],
                y0=selection_range["y"][0],
                y1=selection_range["y"][1],
                line=dict(color="red", width=2),
                fillcolor="red",
                opacity=0.2,
            )

        return fig

    def register_callbacks(self):
        @self.app.callback(
            [Output("scatter-plot", "figure"), Output("data-table", "data")],
            [
                Input("scatter-plot", "selectedData"),
                Input("x-axis-dropdown", "value"),
                Input("y-axis-dropdown", "value"),
            ],
        )
        def update_graph_and_table(selectedData, x_col, y_col):
            selection_range = (
                selectedData["range"]
                if selectedData and "range" in selectedData
                else None
            )
            fig = self.get_figure(x_col, y_col, selection_range)

            if selection_range:
                filtered_df = self.df[
                    (self.df[x_col] >= selection_range["x"][0])
                    & (self.df[x_col] <= selection_range["x"][1])
                    & (self.df[y_col] >= selection_range["y"][0])
                    & (self.df[y_col] <= selection_range["y"][1])
                ]
                table_data = filtered_df.to_dict("records")
            else:
                table_data = self.df.to_dict("records")

            return fig, table_data

    def run_server(self, debug=True, port=8050):
        self.app.run_server(debug=debug, port=port)


def quality_control_app_entry(
    filename: str,
    port: int,
    guide_column: str,
    gene_column: str,
):
    app = CRISPRQCDashApp(filename, guide_column, gene_column)
    app.run_server(debug=True, port=port)
