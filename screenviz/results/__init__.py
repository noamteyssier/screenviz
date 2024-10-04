# screenviz.results.__init__

from .app import ResultsDashApp


def results_app_entry(sgrna_file, gene_file, port=8050, ntc_token="non-targeting"):
    app = ResultsDashApp(sgrna_file, gene_file, ntc_token=ntc_token)
    app.run_server(debug=True, port=port)
