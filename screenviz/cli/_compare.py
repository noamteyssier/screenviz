def compare_parser(subparser):
    parser_compare_gene = subparser.add_parser(
        "compare",
        help="Compare the gene enrichments between two analyses of the same screen",
    )
    parser_compare_gene.add_argument(
        "-i", "--screen_a", help="Input file to use as the first screen", required=True
    )
    parser_compare_gene.add_argument(
        "-I", "--screen_b", help="Input file to use as the second screen", required=True
    )
    parser_compare_gene.add_argument(
        "-x",
        "--variable_column_a",
        help="Column name to plot for the first screen",
        required=False,
        default="pvalue",
    )
    parser_compare_gene.add_argument(
        "-X",
        "--variable_column_b",
        help="Column name to plot for the second screen",
        required=False,
        default="pvalue",
    )
    parser_compare_gene.add_argument(
        "-t",
        "--threshold_column_a",
        help="Column name to use as the threshold for the first screen",
        required=False,
        default="fdr",
    )
    parser_compare_gene.add_argument(
        "-T",
        "--threshold_column_b",
        help="Column name to use as the threshold for the second screen",
        required=False,
        default="fdr",
    )
    parser_compare_gene.add_argument(
        "-th",
        "--threshold",
        type=float,
        help="Threshold value (default = 0.1)",
        required=False,
        default=0.1,
    )
    parser_compare_gene.add_argument(
        "-m",
        "--merge_column_a",
        help="Column to merge on the first screen",
        required=False,
        default="gene",
    )
    parser_compare_gene.add_argument(
        "-M",
        "--merge_column_b",
        help="Column to merge on the second screen",
        required=False,
        default="gene",
    )
    parser_compare_gene.add_argument(
        "-n",
        "--no_log_transform_a",
        help="Do not log transform the first screen",
        required=False,
        action="store_false",
    )
    parser_compare_gene.add_argument(
        "-N",
        "--no_log_transform_b",
        help="Do not log transform the second screen",
        required=False,
        action="store_false",
    )
