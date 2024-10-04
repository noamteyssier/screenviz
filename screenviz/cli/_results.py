def results_parser(subparser):
    parser_results = subparser.add_parser(
        "results", help="Visualize CRISPR screen results interactively"
    )
    parser_results.add_argument(
        "-s", "--sgrna-file", help="Input file for sgRNA-level results", required=False
    )
    parser_results.add_argument(
        "-g", "--gene-file", help="Input file for gene-level results", required=False
    )
    parser_results.add_argument(
        "-n",
        "--prefix",
        help="Prefix for the input files. Will match {prefix}.sgrna_results.tsv and {prefix}.gene_results.tsv",
        required=False,
    )
    parser_results.add_argument(
        "-p",
        "--port",
        help="Port number to run the visualization on (default = 8050)",
        type=int,
        default=8050,
    )
