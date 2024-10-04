# screenviz.results.app

import dash
from dash import dcc, html

from .gene_card import GeneCard
from .sgrna_card import SGRNACard


class ResultsDashApp:
    def __init__(
        self,
        sgrna_file: str,
        gene_file: str,
        ntc_token: str = "non-targeting",
        amalgam_token="amalgam",
    ):
        self.app = dash.Dash(__name__)

        # Initialize the cards
        self.sgrna_card = SGRNACard(sgrna_file, ntc_token=ntc_token)
        self.gene_card = GeneCard(gene_file, amalgam_token=amalgam_token)
        # self.idea_card = IDEACard(idea_file)

        self.app.layout = self.create_layout()
        self.register_callbacks()

    def create_layout(self):
        return html.Div(
            [
                html.H1("CRISPR Screen Results Dashboard"),
                dcc.Tabs(
                    [
                        dcc.Tab(
                            label="sgRNA Results", children=[self.sgrna_card.layout]
                        ),
                        dcc.Tab(label="Gene Results", children=[self.gene_card.layout]),
                        # dcc.Tab(
                        #     label="Pathway Results", children=[self.idea_card.layout]
                        # ),
                    ]
                ),
            ]
        )

    def register_callbacks(self):
        self.sgrna_card.register_callbacks(self.app)
        self.gene_card.register_callbacks(self.app)
        # self.idea_card.register_callbacks(self.app)

    def run_server(self, debug=True, port=8050):
        self.app.run_server(debug=debug, port=port)


def results_app_entry(sgrna_file, gene_file, port=8050):
    app = ResultsDashApp(sgrna_file, gene_file)
    app.run_server(debug=True, port=port)
