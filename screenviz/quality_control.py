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

    def generate_histogram_data(self):
        gene_counts = self.df[self.gene_column].value_counts()
        sgrna_counts = gene_counts.value_counts().sort_index()
        return sgrna_counts

    def generate_gene_membership_data(self):
        gene_counts = self.df[self.gene_column].value_counts().reset_index()
        gene_counts.columns = ["Gene", "Number of sgRNAs"]
        return gene_counts.to_dict("records")

    def create_histogram(self):
        sgrna_counts = self.generate_histogram_data()

        # Calculate the range for y-axis ticks
        y_values = np.log10(sgrna_counts.values + 1)
        y_min = int(np.floor(min(y_values)))
        y_max = int(np.ceil(max(y_values)))

        fig = go.Figure(data=[go.Bar(x=sgrna_counts.index.astype(str), y=y_values)])
        fig.update_layout(
            title="Distribution of Gene Membership Size",
            xaxis_title="Number of sgRNAs",
            bargap=0.2,
            yaxis=dict(
                tickmode="array",
                tickvals=list(range(y_min, y_max + 1)),
                ticktext=[f"10<sup>{i}</sup>" for i in range(y_min, y_max + 1)],
                title="Number of Genes",
            ),
        )
        return fig

    def log_transform(self, matrix: pd.DataFrame):
        mat = matrix.values
        mat = np.clip(a=mat, a_min=0, a_max=None)
        return np.log10(mat + 1)

    def _add_x_axis_dropdown(self, components: list):
        title = html.Label("Select X-axis Sample:")
        dropdown = dcc.Dropdown(
            id="x-axis-dropdown",
            options=[{"label": col, "value": col} for col in self.sample_columns],
            value=self.sample_columns[0],
        )
        components.extend([title, dropdown])

    def _add_y_axis_dropdown(self, components: list):
        title = html.Label("Select Y-axis Sample:")
        dropdown = dcc.Dropdown(
            id="y-axis-dropdown",
            options=[{"label": col, "value": col} for col in self.sample_columns],
            value=self.sample_columns[1]
            if len(self.sample_columns) > 1
            else self.sample_columns[0],
        )
        components.append(html.Br())
        components.extend([title, dropdown])

    def _build_gene_dropdown(self, components: list):
        title = html.Label("Highlight Gene:")
        dropdown = dcc.Dropdown(
            id="gene-dropdown",
            options=[{"label": gene, "value": gene} for gene in self.gene_list],
            value="non-targeting"
            if "non-targeting" in self.gene_list
            else self.gene_list[0],
            placeholder="Select a gene to highlight",
        )
        components.append(html.Br())
        components.extend([title, dropdown])

    def _build_log_transform_switch(self, components: list):
        switch = dcc.Checklist(
            id="log-transform-switch",
            options=[{"label": "", "value": "log"}],
            value=["log"],
            style={
                "display": "inline-block",
                "margin-left": "10px",
            },
        )
        components.append(html.Br())
        components.append(switch)
        components.append(
            html.Label("Log10-transform counts", style={"display": "inline"})
        )
        components.append(html.Br())

    def _build_scatter_plot(self, components: list):
        components.append(html.Br())
        components.append(html.Label("Scatter Plot:", style={"font-weight": "bold"}))
        components.append(html.Br())
        components.append(
            html.Label("Drag to select points, double click to clear selection")
        )
        components.append(
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
            )
        )

    def _build_export_button(self, components: list):
        button = html.Button("Export TSV", id="export-button")
        components.append(button)
        components.append(dcc.Download(id="download-dataframe-tsv"))

    def _build_data_table(self, components: list):
        components.append(html.Br())
        components.append(
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
                style_table={"height": "800px", "overflowY": "auto"},
                style_header={"fontWeight": "bold", "textAlign": "center"},
                style_cell={"textAlign": "center"},
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "rgb(230, 230, 230)",
                    }
                ],
            )
        )

    def _build_histogram(self, components: list):
        components.append(html.Br())
        components.append(
            html.Label(
                "Non-Zero Gene Membership Distribution:", style={"font-weight": "bold"}
            )
        )
        components.append(html.Br())
        components.append(
            dcc.Graph(
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
        )

    def _build_gene_membership_table(self, components: list):
        components.append(html.Br())
        components.append(
            html.Label("Gene Membership Table:", style={"font-weight": "bold"})
        )
        components.append(html.Br())
        components.append(
            dash_table.DataTable(
                id="gene-membership-table",
                columns=[
                    {"name": "Gene", "id": "Gene"},
                    {"name": "Number of sgRNAs", "id": "Number of sgRNAs"},
                ],
                data=self.generate_gene_membership_data(),
                page_size=10,
                style_table={"height": "400px", "overflowY": "auto"},
                style_header={"fontWeight": "bold", "textAlign": "center"},
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
        )

    def _build_left_panel(self, components: list):
        self._add_x_axis_dropdown(components)
        self._add_y_axis_dropdown(components)
        self._build_gene_dropdown(components)
        self._build_log_transform_switch(components)
        self._build_scatter_plot(components)
        self._build_histogram(components)

    def _build_right_panel(self, components: list):
        self._build_export_button(components)
        self._build_data_table(components)
        self._build_gene_membership_table(components)

    def create_layout(self):
        left_panel_components = []
        right_panel_components = []

        # Left panel components
        self._build_left_panel(left_panel_components)

        # Right panel components
        self._build_right_panel(right_panel_components)

        return html.Div(
            [
                html.H1("CRISPR Screen Quality Control Visualization Suite"),
                html.Div(
                    [
                        # Left panel: Scatter plot and controls
                        html.Div(
                            left_panel_components,
                            style={"width": "48%", "display": "inline-block"},
                        ),
                        # Right panel: Data table
                        html.Div(
                            right_panel_components,
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
