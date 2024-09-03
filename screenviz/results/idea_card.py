# screenviz.results.idea_card

import pandas as pd
import plotly.graph_objects as go
from dash import dash_table, dcc, html
from dash.dependencies import Input, Output


class IDEACard:
    def __init__(self, idea_file):
        self.df = pd.read_csv(idea_file, sep="\t")
        self.layout = self.create_layout()

    def create_layout(self):
        return html.Div(
            [
                html.H2("Pathway Enrichment (IDEA Plot)"),
                dcc.Graph(id="idea-plot"),
                html.Div(
                    [
                        html.Label("Select Pathway:"),
                        dcc.Dropdown(
                            id="pathway-dropdown",
                            options=[
                                {"label": pathway, "value": pathway}
                                for pathway in self.df["Pathway"].unique()
                            ],
                            value=self.df["Pathway"].iloc[0],
                        ),
                    ]
                ),
                dash_table.DataTable(
                    id="idea-data-table",
                    columns=[{"name": i, "id": i} for i in self.df.columns],
                    data=self.df.to_dict("records"),
                    page_size=10,
                    sort_action="native",
                    filter_action="native",
                ),
            ]
        )

    def register_callbacks(self, app):
        @app.callback(Output("idea-plot", "figure"), Input("pathway-dropdown", "value"))
        def update_idea_plot(selected_pathway):
            pathway_data = self.df[self.df["Pathway"] == selected_pathway]

            fig = go.Figure()

            # Add nodes for genes
            fig.add_trace(
                go.Scatter(
                    x=pathway_data["Gene_X"],
                    y=pathway_data["Gene_Y"],
                    mode="markers",
                    marker=dict(size=10, color=pathway_data["Gene_Color"]),
                    text=pathway_data["Gene"],
                    hoverinfo="text",
                )
            )

            # Add nodes for terms
            fig.add_trace(
                go.Scatter(
                    x=pathway_data["Term_X"],
                    y=pathway_data["Term_Y"],
                    mode="markers",
                    marker=dict(size=20, color=pathway_data["Term_Color"]),
                    text=pathway_data["Term"],
                    hoverinfo="text",
                )
            )

            # Add edges
            for _, row in pathway_data.iterrows():
                fig.add_trace(
                    go.Scatter(
                        x=[row["Gene_X"], row["Term_X"]],
                        y=[row["Gene_Y"], row["Term_Y"]],
                        mode="lines",
                        line=dict(color="gray", width=1),
                        hoverinfo="none",
                    )
                )

            fig.update_layout(
                title=f"IDEA Plot for {selected_pathway}",
                showlegend=False,
                hovermode="closest",
            )

            return fig

        @app.callback(
            Output("idea-data-table", "data"), Input("pathway-dropdown", "value")
        )
        def update_data_table(selected_pathway):
            filtered_df = self.df[self.df["Pathway"] == selected_pathway]
            return filtered_df.to_dict("records")
