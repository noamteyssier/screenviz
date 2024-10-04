def quality_control_parser(subparser):
    parser_quality_control = subparser.add_parser(
        "qc",
        help="Visualize quality control metrics interactively on the input data",
    )
    parser_quality_control.add_argument(
        "-i",
        "--input",
        help="Input file (this should be a count-matrix from the output of sgcount)",
        required=True,
    )
    parser_quality_control.add_argument(
        "-p",
        "--port",
        help="Port number to run the visualization on (default = 8050)",
        required=False,
        default=8050,
    )
    parser_quality_control.add_argument(
        "-s",
        "--guide-column",
        help="Column name of sgRNA names (default = 'Guide')",
        required=False,
        default="Guide",
    )
    parser_quality_control.add_argument(
        "-g",
        "--gene-column",
        help="Column name of gene names (default = 'Gene')",
        required=False,
        default="Gene",
    )
