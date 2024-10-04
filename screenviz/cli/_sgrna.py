def sgrna_parser(subparser):
    # create the parser for the "sgrna" command
    parser_sgrna = subparser.add_parser(
        "sgrna", help="Visualize the volcano plot of the sgRNA enrichment analysis"
    )
    parser_sgrna.add_argument("-i", "--input", help="Input file", required=True)
    parser_sgrna.add_argument(
        "-o",
        "--output",
        help="Output file (default = 'sgrna_volcano.html')",
        required=False,
        default="sgrna_volcano.html",
    )
    parser_sgrna.add_argument(
        "-s",
        "--sgrna_column",
        help="Column name of sgRNA names (default = 'sgrna')",
        required=False,
        default="sgrna",
    )
    parser_sgrna.add_argument(
        "-g",
        "--gene_column",
        help="Column name of gene names (default = 'gene')",
        required=False,
        default="gene",
    )
    parser_sgrna.add_argument(
        "-f",
        "--fc_column",
        help="Column name of fold change values (default = 'log2_fold_change')",
        required=False,
        default="log2_fold_change",
    )
    parser_sgrna.add_argument(
        "-p",
        "--pval_column",
        help="Column name of score column (default = 'pvalue')",
        required=False,
        default="pvalue_twosided",
    )
    parser_sgrna.add_argument(
        "-t",
        "--threshold_column",
        help="Column name of threshold column (default = 'fdr')",
        required=False,
        default="fdr",
    )
    parser_sgrna.add_argument(
        "-th",
        "--threshold",
        type=float,
        help="Threshold value (default = 0.1)",
        required=False,
        default=0.1,
    )
