# screenviz.qc.scatter_data_card

import warnings

import dash
import pandas as pd
import plotly.express as px
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output, State


class ScatterDataCard:
    def __init__(self, parent):
        self.parent = parent

    def create_card(self, card_style):
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

    def _create_axis_dropdown(self, axis):
        return html.Div(
            [
                html.Label(f"Select {axis.upper()}-axis Sample:"),
                dcc.Dropdown(
                    id=f"{axis}-axis-dropdown",
                    options=[
                        {"label": col, "value": col}
                        for col in self.parent.sample_columns
                    ],
                    value=self.parent.sample_columns[0]
                    if axis == "x"
                    else (
                        self.parent.sample_columns[1]
                        if len(self.parent.sample_columns) > 1
                        else self.parent.sample_columns[0]
                    ),
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
                    options=[
                        {"label": gene, "value": gene} for gene in self.parent.gene_list
                    ],
                    value="non-targeting"
                    if "non-targeting" in self.parent.gene_list
                    else self.parent.gene_list[0],
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
                        if self.parent.df[i].dtype in ["float64", "float32"]
                        else {"name": i, "id": i}
                        for i in self.parent.df.columns
                    ],
                    data=self.parent.df.to_dict("records"),
                    page_size=21,
                    style_table={"height": "750px", "overflowY": "auto"},
                    style_header={"fontWeight": "bold", "textAlign": "center"},
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
        df = self.parent.df_log if log_transform else self.parent.df_normal

        if highlighted_gene:
            df["color_by_gene"] = df[self.parent.gene_column].map(
                lambda x: "selected_gene"
                if x == highlighted_gene
                else "unselected_gene"
            )
            # Suppress warning about get_group() deprecation
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore", category=FutureWarning, module="plotly.express._core"
                )
                fig = px.scatter(
                    df,
                    x=x_col,
                    y=y_col,
                    hover_data=[self.parent.guide_column, self.parent.gene_column],
                    color="color_by_gene",
                    color_discrete_map={
                        "selected_gene": self.parent.DEFAULT_HIGHLIGHT_COLOR,
                        "unselected_gene": self.parent.DEFAULT_MARKER_COLOR,
                    },
                )
        else:
            fig = px.scatter(
                df,
                x=x_col,
                y=y_col,
                hover_data=[self.parent.guide_column, self.parent.gene_column],
            )

        if selected_points:
            opacity_list = [
                self.parent.SELECTED_OPACITY
                if i in selected_points
                else self.parent.UNSELECTED_OPACITY
                for i in range(len(df))
            ]
        else:
            opacity_list = [self.parent.DEFAULT_OPACITY] * len(df)

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
            fig.update_traces(marker={"color": self.parent.DEFAULT_MARKER_COLOR})

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
                fillcolor=self.parent.SELECT_FILL_COLOR,
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
                "line": {"color": self.parent.AB_LINE_COLOR, "dash": "dash"},
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

    def register_callbacks(self, app):
        @app.callback(
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

        @app.callback(
            Output("data-table", "data"),
            [
                Input("scatter-plot", "selectedData"),
                Input("x-axis-dropdown", "value"),
                Input("y-axis-dropdown", "value"),
                Input("log-transform-switch", "value"),
            ],
        )
        def update_table(selecteddata, x_col, y_col, log_transform):
            df = self.parent.df_log if "log" in log_transform else self.parent.df_normal
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

        @app.callback(
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
