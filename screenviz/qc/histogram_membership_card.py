import numpy as np
import plotly.graph_objects as go
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output


class HistogramMembershipCard:
    def __init__(self, parent):
        self.parent = parent

    def create_card(self, card_style):
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
                    + [
                        {"label": col, "value": col}
                        for col in self.parent.sample_columns
                    ],
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
            style_table={"height": "600px", "overflowY": "auto"},
            style_header={"fontWeight": "bold", "textAlign": "center"},
            style_cell={"textAlign": "center"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "rgb(230, 230, 230)"}
            ],
            sort_action="native",
            sort_mode="multi",
        )

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

    def generate_histogram_data(self, selected_sample=None):
        if selected_sample is None or selected_sample == "All Samples":
            non_zero_counts = (self.parent.df[self.parent.sample_columns] > 0).sum(
                axis=1
            )
        else:
            non_zero_counts = (self.parent.df[selected_sample] > 0).astype(int)

        mask = non_zero_counts > 0
        masked_df = self.parent.df[mask]
        sgrna_counts = masked_df[self.parent.gene_column].value_counts().sort_index()
        membership_counts = sgrna_counts.value_counts().sort_index()
        return membership_counts

    def generate_gene_membership_data(self):
        gene_counts = (
            self.parent.df[self.parent.gene_column].value_counts().reset_index()
        )
        gene_counts.columns = ["Gene", "Number of sgRNAs"]
        return gene_counts.to_dict("records")

    def register_callbacks(self, app):
        @app.callback(
            Output("histogram-plot", "figure"),
            [Input("histogram-sample-dropdown", "value")],
        )
        def update_histogram(selected_sample):
            return self.create_histogram(selected_sample)

        @app.callback(
            Output("gene-membership-table", "data"),
            [Input("histogram-sample-dropdown", "value")],
        )
        def update_gene_membership_table(selected_sample):
            # This callback updates the gene membership table based on the selected sample
            if selected_sample is None or selected_sample == "All Samples":
                return self.generate_gene_membership_data()
            else:
                # Filter the dataframe based on the selected sample
                mask = self.parent.df[selected_sample] > 0
                filtered_df = self.parent.df[mask]
                gene_counts = (
                    filtered_df[self.parent.gene_column].value_counts().reset_index()
                )
                gene_counts.columns = ["Gene", "Number of sgRNAs"]
                return gene_counts.to_dict("records")
