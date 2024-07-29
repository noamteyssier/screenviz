from .app import CRISPRQCDashApp


def quality_control_app_entry(
    filename: str,
    port: int,
    guide_column: str,
    gene_column: str,
):
    app = CRISPRQCDashApp(filename, guide_column, gene_column)
    app.run_server(debug=True, port=port)
