import dash
import pandas as pd
import plotly.express as px
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output


class CRISPRQCDashApp:
    DEFAULT_MARKER_COLOR = "#124559"
    DEFAULT_HIGHLIGHT_COLOR = "#aec3b0"
    SELECT_FILL_COLOR = "#adb5bd"

    def __init__(self, filename: str, guide_column: str, gene_column: str):
        self.app = dash.Dash(__name__)
        self.df = pd.read_csv(filename, sep="\t")
        self.guide_column = guide_column
        self.gene_column = gene_column
        self.sample_columns = [
            col for col in self.df.columns if col not in [guide_column, gene_column]
        ]
        self.gene_list = sorted(self.df[gene_column].unique())

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
                                html.Label("Select X-axis Sample:"),
                                dcc.Dropdown(
                                    id="x-axis-dropdown",
                                    options=[
                                        {"label": col, "value": col}
                                        for col in self.sample_columns
                                    ],
                                    value=self.sample_columns[0],
                                ),
                                html.Label("Select Y-axis Sample:"),
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
                                html.Label("Highlight Gene:"),
                                dcc.Dropdown(
                                    id="gene-dropdown",
                                    options=[
                                        {"label": gene, "value": gene}
                                        for gene in self.gene_list
                                    ],
                                    value="non-targeting"
                                    if "non-targeting" in self.gene_list
                                    else self.gene_list[0],
                                    placeholder="Select a gene to highlight",
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

    def get_figure(self, x_col, y_col, selection_range, highlighted_gene):
        if highlighted_gene:
            colors = [
                "in_guide" if gene == highlighted_gene else "out_guide"
                for gene in self.df[self.gene_column]
            ]
            self.df["color_by_gene"] = colors
            fig = px.scatter(
                self.df,
                x=x_col,
                y=y_col,
                hover_data=[self.guide_column, self.gene_column],
                color=self.df["color_by_gene"],
                color_discrete_map={
                    "in_guide": self.DEFAULT_HIGHLIGHT_COLOR,
                    "out_guide": self.DEFAULT_MARKER_COLOR,
                },
            )
        else:
            fig = px.scatter(
                self.df,
                x=x_col,
                y=y_col,
                hover_data=[self.guide_column, self.gene_column],
            )

        if highlighted_gene:
            fig.update_traces(
                mode="markers",
                marker={
                    "size": 10,
                    "line": {"width": 1.0, "color": "black"},
                    "opacity": 0.8,
                },
            )
        else:
            fig.update_traces(
                marker={
                    "color": self.DEFAULT_MARKER_COLOR,
                },
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
                line=dict(color="black", width=3),
                fillcolor=self.SELECT_FILL_COLOR,
                opacity=0.2,
            )

        return fig

    def register_callbacks(self):
        @self.app.callback(
            Output("scatter-plot", "figure"),
            [
                Input("scatter-plot", "selectedData"),
                Input("x-axis-dropdown", "value"),
                Input("y-axis-dropdown", "value"),
                Input("gene-dropdown", "value"),
            ],
        )
        def update_graph(selectedData, x_col, y_col, highlighted_gene):
            selection_range = (
                selectedData["range"]
                if selectedData and "range" in selectedData
                else None
            )
            fig = self.get_figure(x_col, y_col, selection_range, highlighted_gene)
            return fig

        @self.app.callback(
            Output("data-table", "data"),
            [
                Input("scatter-plot", "selectedData"),
                Input("x-axis-dropdown", "value"),
                Input("y-axis-dropdown", "value"),
            ],
        )
        def update_table(selectedData, x_col, y_col):
            if selectedData and "range" in selectedData:
                selection_range = selectedData["range"]
                filtered_df = self.df[
                    (self.df[x_col] >= selection_range["x"][0])
                    & (self.df[x_col] <= selection_range["x"][1])
                    & (self.df[y_col] >= selection_range["y"][0])
                    & (self.df[y_col] <= selection_range["y"][1])
                ]
                return filtered_df.to_dict("records")
            return self.df.to_dict("records")

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
