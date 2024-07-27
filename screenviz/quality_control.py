import dash
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output, State


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
        self.df = pd.read_csv(filename, sep="\t")

        self.guide_column = guide_column
        self.gene_column = gene_column
        self.sample_columns = [
            col for col in self.df.columns if col not in [guide_column, gene_column]
        ]
        self.gene_list = sorted(self.df[gene_column].unique())

        # Store both normal and log-transformed data
        self.df_normal = self.df.copy()
        self.df_log = self.df.copy()
        self.df_log[self.sample_columns] = self.log_transform(
            self.df_log[self.sample_columns]
        )

        self.app.layout = self.create_layout()
        self.register_callbacks()

    def generate_histogram_data(self, selected_sample=None):
        if selected_sample is None or selected_sample == "All Samples":
            non_zero_counts = (self.df[self.sample_columns] > 0).sum(axis=1)
        else:
            non_zero_counts = (self.df[selected_sample] > 0).astype(int)

        mask = non_zero_counts > 0
        masked_df = self.df[mask]
        sgrna_counts = masked_df[self.gene_column].value_counts().sort_index()
        membership_counts = sgrna_counts.value_counts().sort_index()
        return membership_counts

    def generate_gene_membership_data(self):
        gene_counts = self.df[self.gene_column].value_counts().reset_index()
        gene_counts.columns = ["Gene", "Number of sgRNAs"]
        return gene_counts.to_dict("records")

    def create_histogram(self, selected_sample=None):
        sgrna_counts = self.generate_histogram_data(selected_sample)

        # Calculate the range for y-axis ticks
        y_values = np.log10(sgrna_counts.values + 1)
        y_min = int(np.floor(min(y_values)))
        y_max = int(np.ceil(max(y_values)))

        fig = go.Figure(data=[go.Bar(x=sgrna_counts.index.astype(str), y=y_values)])
        fig.update_layout(
            title=f"Distribution of Gene Membership Size ({selected_sample or 'All Samples'})",
            xaxis_title="Number of sgRNAs",
            bargap=0.2,
            yaxis=dict(
                tickmode="array",
                tickvals=list(range(y_min, y_max + 1)),
                ticktext=[f"10<sup>{i}</sup>" for i in range(y_min, y_max + 1)],
                title="Number of Genes",
            ),
            height=555,  # Set height to 555px to match the data table
        )
        return fig

    def log_transform(self, matrix: pd.DataFrame):
        mat = matrix.values
        mat = np.clip(a=mat, a_min=0, a_max=None)
        return np.log10(mat + 1)

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
                html.Div(
                    [
                        # First card: Scatter plot and main data table
                        self.create_scatter_and_data_card(self.CARD_STYLE),
                        # Second card: Histogram and gene membership table
                        self.create_histogram_and_gene_membership_card(self.CARD_STYLE),
                    ]
                ),
            ],
            style={"fontFamily": "Arial, sans-serif", "padding": "20px"},
        )

    def create_scatter_and_data_card(self, card_style):
        return html.Div(
            [
                html.H3("Scatter Plot and Data Table"),
                html.Div(
                    [
                        # Scatter plot
                        html.Div(
                            [
                                self._create_axis_dropdown("x"),
                                self._create_axis_dropdown("y"),
                                self._create_gene_dropdown(),
                                self._create_log_transform_switch(),
                                self._create_scatter_plot(),
                            ],
                            style={
                                "width": "50%",
                                "display": "inline-block",
                                "vertical-align": "top",
                            },
                        ),
                        # Data table
                        html.Div(
                            [
                                self._create_scatter_plot_data_table(),
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

    def create_histogram_and_gene_membership_card(self, card_style):
        return html.Div(
            [
                html.H3("Gene Membership Distribution and Table"),
                html.Div(
                    [
                        # Histogram
                        html.Div(
                            [
                                self._create_histogram_dropdown(),
                                self._create_histogram_plot(),
                            ],
                            style={
                                "width": "50%",
                                "display": "inline-block",
                                "vertical-align": "top",
                            },
                        ),
                        # Gene membership table
                        html.Div(
                            [
                                self._create_gene_membership_table(),
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

    def _create_histogram_dropdown(self):
        return html.Div(
            [
                dcc.Dropdown(
                    id="histogram-sample-dropdown",
                    options=[{"label": "All Samples", "value": "All Samples"}]
                    + [{"label": col, "value": col} for col in self.sample_columns],
                    value="All Samples",
                    style={"width": "100%", "marginBottom": "10px"},
                ),
            ]
        )

    def _create_histogram_plot(self):
        return dcc.Graph(
            id="histogram-plot",
            figure=self.create_histogram(),
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
        )

    def _create_gene_membership_table(self):
        return dash_table.DataTable(
            id="gene-membership-table",
            columns=[
                {"name": "Gene", "id": "Gene"},
                {"name": "Number of sgRNAs", "id": "Number of sgRNAs"},
            ],
            data=self.generate_gene_membership_data(),
            page_size=20,
            style_table={
                "height": "600px",
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
            sort_action="native",
            sort_mode="multi",
        )

    def _create_axis_dropdown(self, axis):
        return html.Div(
            [
                html.Label(f"Select {axis.upper()}-axis Sample:"),
                dcc.Dropdown(
                    id=f"{axis}-axis-dropdown",
                    options=[
                        {"label": col, "value": col} for col in self.sample_columns
                    ],
                    value=self.sample_columns[0]
                    if axis == "x"
                    else self.sample_columns[1]
                    if len(self.sample_columns) > 1
                    else self.sample_columns[0],
                ),
            ],
            style={"margin-bottom": "10px"},
        )

    def _create_gene_dropdown(self):
        return html.Div(
            [
                html.Label("Highlight Gene:"),
                dcc.Dropdown(
                    id="gene-dropdown",
                    options=[{"label": gene, "value": gene} for gene in self.gene_list],
                    value="non-targeting"
                    if "non-targeting" in self.gene_list
                    else self.gene_list[0],
                    placeholder="Select a gene to highlight",
                ),
            ],
            style={"margin-bottom": "10px"},
        )

    def _create_log_transform_switch(self):
        return html.Div(
            [
                dcc.Checklist(
                    id="log-transform-switch",
                    options=[{"label": "Log10-transform counts", "value": "log"}],
                    value=["log"],
                    style={"display": "inline-block", "margin-left": "10px"},
                ),
            ],
            style={"margin-bottom": "10px"},
        )

    def _create_scatter_plot(self):
        return html.Div(
            [
                dcc.Graph(
                    id="scatter-plot",
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
            ]
        )

    def _create_scatter_plot_data_table(self):
        return html.Div(
            [
                html.Button("Export TSV", id="export-button"),
                dcc.Download(id="download-dataframe-tsv"),
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
                        "height": "600px",
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
                ),
            ]
        )

    def get_figure(
        self,
        x_col,
        y_col,
        selection_range,
        highlighted_gene,
        selected_points,
        log_transform,
        current_layout=None,
    ):
        df = self.df_log if log_transform else self.df_normal

        if highlighted_gene:
            colors = [
                "selected_gene" if gene == highlighted_gene else "unselected_gene"
                for gene in df[self.gene_column]
            ]
            df["color_by_gene"] = colors
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                hover_data=[self.guide_column, self.gene_column],
                color="color_by_gene",
                color_discrete_map={
                    "selected_gene": self.DEFAULT_HIGHLIGHT_COLOR,
                    "unselected_gene": self.DEFAULT_MARKER_COLOR,
                },
            )
        else:
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                hover_data=[self.guide_column, self.gene_column],
            )

        if selected_points:
            opacity_list = [
                self.SELECTED_OPACITY
                if i in selected_points
                else self.UNSELECTED_OPACITY
                for i in range(len(df))
            ]
        else:
            opacity_list = [self.DEFAULT_OPACITY] * len(df)

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
        x_range = fig.layout.xaxis.range or [df[x_col].min(), df[x_col].max()]
        y_range = fig.layout.yaxis.range or [df[y_col].min(), df[y_col].max()]
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

        new_layout = {
            "title": "Scatter Plot",
            "xaxis_title": f"Log10p[ {x_col} ]" if log_transform else x_col,
            "yaxis_title": f"Log10p[ {y_col} ]" if log_transform else y_col,
        }

        if current_layout:
            new_layout.update(
                {
                    "xaxis": {
                        "range": current_layout["xaxis"]["range"],
                        "autorange": current_layout["xaxis"]["autorange"],
                    },
                    "yaxis": {
                        "range": current_layout["yaxis"]["range"],
                        "autorange": current_layout["yaxis"]["autorange"],
                    },
                }
            )

        fig.update_layout(new_layout)

        return fig

    def register_callbacks(self):
        @self.app.callback(
            Output("scatter-plot", "figure"),
            [
                Input("scatter-plot", "selectedData"),
                Input("x-axis-dropdown", "value"),
                Input("y-axis-dropdown", "value"),
                Input("gene-dropdown", "value"),
                Input("log-transform-switch", "value"),
            ],
            [State("scatter-plot", "figure")],
        )
        def update_graph(
            selectedData, x_col, y_col, highlighted_gene, log_transform, current_figure
        ):
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

            current_layout = current_figure["layout"] if current_figure else None

            fig = self.get_figure(
                x_col,
                y_col,
                selection_range,
                highlighted_gene,
                selected_points,
                "log" in log_transform,
                current_layout,
            )
            return fig

        @self.app.callback(
            Output("data-table", "data"),
            [
                Input("scatter-plot", "selectedData"),
                Input("x-axis-dropdown", "value"),
                Input("y-axis-dropdown", "value"),
                Input("log-transform-switch", "value"),
            ],
        )
        def update_table(selecteddata, x_col, y_col, log_transform):
            df = self.df_log if "log" in log_transform else self.df_normal
            if selecteddata and "range" in selecteddata:
                selection_range = selecteddata["range"]
                filtered_df = df[
                    (df[x_col] >= selection_range["x"][0])
                    & (df[x_col] <= selection_range["x"][1])
                    & (df[y_col] >= selection_range["y"][0])
                    & (df[y_col] <= selection_range["y"][1])
                ]
                return filtered_df.to_dict("records")
            return df.to_dict("records")

        @self.app.callback(
            Output("download-dataframe-tsv", "data"),
            Input("export-button", "n_clicks"),
            State("data-table", "data"),
            prevent_initial_call=True,
        )
        def export_table_to_tsv(n_clicks, table_data):
            if n_clicks is None:
                return dash.no_update
            df = pd.DataFrame(table_data)
            return dcc.send_data_frame(
                df.to_csv, "exported_data.tsv", sep="\t", index=False
            )

        @self.app.callback(
            Output("histogram-plot", "figure"),
            [Input("histogram-sample-dropdown", "value")],
        )
        def update_histogram(selected_sample):
            return self.create_histogram(selected_sample)

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
