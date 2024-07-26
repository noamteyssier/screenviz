import dash
import numpy as np
import pandas as pd
import plotly.express as px
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output


class CRISPRQCDashApp:
    DEFAULT_MARKER_COLOR = "#124559"
    DEFAULT_HIGHLIGHT_COLOR = "#aec3b0"
    SELECT_FILL_COLOR = "#adb5bd"
    AB_LINE_COLOR = "#ff6b6b"
    DEFAULT_OPACITY = 0.8
    SELECTED_OPACITY = 1.0
    UNSELECTED_OPACITY = 0.25

    def __init__(
        self, filename: str, guide_column: str, gene_column: str, log_transform=True
    ):
        self.app = dash.Dash(__name__)
        self.df = pd.read_csv(filename, sep="\t")

        self.guide_column = guide_column
        self.gene_column = gene_column
        self.sample_columns = [
            col for col in self.df.columns if col not in [guide_column, gene_column]
        ]
        self.gene_list = sorted(self.df[gene_column].unique())

        # Log-transform the data
        if log_transform:
            self.df[self.sample_columns] = self.log_transform(
                self.df[self.sample_columns]
            )
        self.log_transform = log_transform

        self.app.layout = self.create_layout()
        self.register_callbacks()

    def log_transform(self, matrix: pd.DataFrame):
        mat = matrix.values
        mat = np.clip(a=mat, a_min=0, a_max=None)
        return np.log10(mat + 1)

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
                                html.Br(),
                                html.Label(
                                    "Scatter Plot:", style={"font-weight": "bold"}
                                ),
                                html.Br(),
                                html.Label(
                                    "Drag to select points, double click to clear selection"
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
                                        {
                                            "name": i,
                                            "id": i,
                                            "type": "numeric",
                                            "format": {"specifier": ".4f"},
                                        }
                                        if self.df[i].dtype in ["float64", "float32"]
                                        else {"name": i, "id": i}
                                        for i in self.df.columns
                                    ],
                                    data=self.df.to_dict("records"),
                                    page_size=20,
                                    style_table={
                                        "height": "800px",
                                        "overflowY": "auto",
                                    },
                                    style_header={
                                        "fontWeight": "bold",
                                        "textAlign": "center",
                                    },
                                    style_cell={"textAlign": "center"},
                                    style_data_conditional=[
                                        {
                                            "if": {"row_index": "odd"},
                                            "backgroundColor": "rgb(230, 230, 230)",
                                        }
                                    ],
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

    def get_figure(
        self, x_col, y_col, selection_range, highlighted_gene, selected_points
    ):
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

        if selected_points:
            opacity_list = [
                self.SELECTED_OPACITY
                if i in selected_points
                else self.UNSELECTED_OPACITY
                for i in range(len(self.df))
            ]
        else:
            opacity_list = [self.DEFAULT_OPACITY] * len(self.df)

        if highlighted_gene:
            fig.update_traces(
                mode="markers",
                marker={
                    "size": 10,
                    "line": {"width": 1.0, "color": "black"},
                    "opacity": opacity_list,
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

        # Add A/B line (diagonal line)
        x_range = fig.layout.xaxis.range or [self.df[x_col].min(), self.df[x_col].max()]
        y_range = fig.layout.yaxis.range or [self.df[y_col].min(), self.df[y_col].max()]
        overall_min = min(x_range[0], y_range[0])
        overall_max = max(x_range[1], y_range[1])

        fig.add_trace(
            {
                "type": "scatter",
                "x": [overall_min, overall_max],
                "y": [overall_min, overall_max],
                "mode": "lines",
                "line": {"color": self.AB_LINE_COLOR, "dash": "dash"},
                "name": "A/B Line",
            }
        )

        fig.update_layout(
            title="Scatter Plot",
            xaxis_title=f"Log10p[ {x_col} ]" if self.log_transform else x_col,
            yaxis_title=f"Log10p[ {y_col} ]" if self.log_transform else y_col,
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
            selected_points = []
            if selectedData and "points" in selectedData:
                selected_points = [
                    point["pointIndex"] for point in selectedData["points"]
                ]
            fig = self.get_figure(
                x_col, y_col, selection_range, highlighted_gene, selected_points
            )
            return fig

        @self.app.callback(
            Output("data-table", "data"),
            [
                Input("scatter-plot", "selectedData"),
                Input("x-axis-dropdown", "value"),
                Input("y-axis-dropdown", "value"),
            ],
        )
        def update_table(selecteddata, x_col, y_col):
            if selecteddata and "range" in selecteddata:
                selection_range = selecteddata["range"]
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
