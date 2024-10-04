def idea_parser(subparser):
    # create the parser for the "geneviz" command
    parser_idea = subparser.add_parser(
        "idea",
        help="Perform Gene Set Enrichment using Enrichr and visualize as an IDEA plot",
    )
    parser_idea.add_argument("-i", "--input", help="Input file", required=True)
    parser_idea.add_argument(
        "-o",
        "--output",
        help="Output file (default = '<prefix>.<geneset>.html')",
        required=False,
        default="network",
    )
    parser_idea.add_argument(
        "-s",
        "--geneset",
        help="Gene set to perform enrichment against (BP, MF, CC, or any name in Enrichr)",
        required=False,
        default="BP",
    )
    parser_idea.add_argument(
        "-g",
        "--gene_column",
        help="Column name of gene names (default = 'gene')",
        required=False,
        default="gene",
    )
    parser_idea.add_argument(
        "-f",
        "--fc_column",
        help="Column name of fold change values (default = 'log_fold_change')",
        required=False,
        default="log_fold_change",
    )
    parser_idea.add_argument(
        "-p",
        "--pval_column",
        help="Column name of score column (default = 'fdr')",
        required=False,
        default="fdr",
    )
    parser_idea.add_argument(
        "-t",
        "--threshold_column",
        help="Column name of threshold column (default = 'fdr')",
        required=False,
        default="fdr",
    )
    parser_idea.add_argument(
        "-th",
        "--threshold",
        type=float,
        help="Threshold value (default = 0.1) to use for differentially expressed genes",
        required=False,
        default=0.1,
    )
    parser_idea.add_argument(
        "-tth",
        "--term_threshold",
        type=float,
        help="Threshold value (default = 0.1) to use for enriched terms",
        required=False,
        default=0.1,
    )
    parser_idea.add_argument(
        "--sided",
        type=str,
        help="One-sided enrichment, choose either 'up' or 'down'",
        required=False,
    )
    parser_idea.add_argument(
        "--top",
        type=int,
        help="Number of top terms to show (default = 30)",
        required=False,
        default=30,
    )
    parser_idea.add_argument(
        "--term_palette",
        type=str,
        help="Color palette for term nodes",
        required=False,
        default="Greens",
    )
    parser_idea.add_argument(
        "--gene_palette",
        type=str,
        help="Color palette for gene nodes",
        required=False,
    )
    parser_idea.add_argument(
        "--up_color",
        type=str,
        help="Color palette for up-regulated genes",
        required=False,
    )
    parser_idea.add_argument(
        "--down_color",
        type=str,
        help="Color palette for down-regulated genes",
        required=False,
    )
