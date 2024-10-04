def results_parser(subparser):
    parser_results = subparser.add_parser(
        "results", help="Visualize CRISPR screen results interactively"
    )
    parser_results.add_argument(
        "-s", "--sgrna-file", help="Input file for sgRNA-level results", required=True
    )
    parser_results.add_argument(
        "-g", "--gene-file", help="Input file for gene-level results", required=True
    )
    parser_results.add_argument(
        "-p",
        "--port",
        help="Port number to run the visualization on (default = 8050)",
        type=int,
        default=8050,
    )
