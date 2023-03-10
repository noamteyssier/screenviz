import argparse
from screenviz.gene import VisualizeGenes
from screenviz.sgrna import VisualizeSGRNAs
from screenviz.compare import CompareScreens

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="subcommand", required=True)

    # create the parser for the "geneviz" command
    parser_geneviz = subparser.add_parser("gene", help="Visualize the volcano plot of the gene enrichment analysis")
    parser_geneviz.add_argument(
            "-i", 
            "--input", 
            help="Input file", 
            required=True)
    parser_geneviz.add_argument(
            "-o", 
            "--output", 
            help="Output file (default = 'gene_volcano.html')",
            required=False, 
            default="gene_volcano.html")
    parser_geneviz.add_argument(
            "-g", 
            "--gene_column", 
            help="Column name of gene names (default = 'gene')",
            required=False, 
            default="gene")
    parser_geneviz.add_argument(
            "-f", 
            "--fc_column", 
            help="Column name of fold change values (default = 'log_fold_change')",
            required=False, 
            default="log_fold_change")
    parser_geneviz.add_argument(
            "-p", 
            "--pval_column", 
            help="Column name of score column (default = 'pvalue')",
            required=False, 
            default="pvalue")
    parser_geneviz.add_argument(
            "-t", 
            "--threshold_column", 
            help="Column name of threshold column (default = 'fdr')",
            required=False, 
            default="fdr")
    parser_geneviz.add_argument(
            "-th",
            "--threshold",
            type=float,
            help="Threshold value (default = 0.1)",
            required=False,
            default=0.1)

    # create the parser for the "sgrnaviz" command
    parser_sgrnaviz = subparser.add_parser("sgrna", help="Visualize the volcano plot of the sgRNA enrichment analysis")
    parser_sgrnaviz.add_argument(
            "-i", 
            "--input", 
            help="Input file", 
            required=True)
    parser_sgrnaviz.add_argument(
            "-o", 
            "--output", 
            help="Output file (default = 'sgrna_volcano.html')",
            required=False, 
            default="sgrna_volcano.html")
    parser_sgrnaviz.add_argument(
            "-s",
            "--sgrna_column",
            help="Column name of sgRNA names (default = 'sgrna')",
            required=False,
            default="sgrna")
    parser_sgrnaviz.add_argument(
            "-g", 
            "--gene_column", 
            help="Column name of gene names (default = 'gene')",
            required=False, 
            default="gene")
    parser_sgrnaviz.add_argument(
            "-f", 
            "--fc_column", 
            help="Column name of fold change values (default = 'log2_fold_change')",
            required=False, 
            default="log2_fold_change")
    parser_sgrnaviz.add_argument(
            "-p", 
            "--pval_column", 
            help="Column name of score column (default = 'pvalue')",
            required=False, 
            default="pvalue_twosided")
    parser_sgrnaviz.add_argument(
            "-t", 
            "--threshold_column", 
            help="Column name of threshold column (default = 'fdr')",
            required=False, 
            default="fdr")
    parser_sgrnaviz.add_argument(
            "-th",
            "--threshold",
            type=float,
            help="Threshold value (default = 0.1)",
            required=False,
            default=0.1)

    parser_compare_gene = subparser.add_parser("compare", help="Compare the gene enrichments between two analyses of the same screen")
    parser_compare_gene.add_argument(
            "-i", 
            "--screen_a", 
            help="Input file to use as the first screen", 
            required=True)
    parser_compare_gene.add_argument(
            "-I", 
            "--screen_b", 
            help="Input file to use as the second screen", 
            required=True)
    parser_compare_gene.add_argument(
            "-x",
            "--variable_column_a",
            help="Column name to plot for the first screen",
            required=False,
            default="pvalue")
    parser_compare_gene.add_argument(
            "-X",
            "--variable_column_b",
            help="Column name to plot for the second screen",
            required=False,
            default="pvalue")
    parser_compare_gene.add_argument(
            "-t",
            "--threshold_column_a",
            help="Column name to use as the threshold for the first screen",
            required=False,
            default="fdr")
    parser_compare_gene.add_argument(
            "-T",
            "--threshold_column_b",
            help="Column name to use as the threshold for the second screen",
            required=False,
            default="fdr")
    parser_compare_gene.add_argument(
            "-th",
            "--threshold",
            type=float,
            help="Threshold value (default = 0.1)",
            required=False,
            default=0.1)
    parser_compare_gene.add_argument(
            "-m",
            "--merge_column_a",
            help="Column to merge on the first screen",
            required=False,
            default="gene")
    parser_compare_gene.add_argument(
            "-M",
            "--merge_column_b",
            help="Column to merge on the second screen",
            required=False,
            default="gene")
    parser_compare_gene.add_argument(
            "-n",
            "--no_log_transform_a",
            help="Do not log transform the first screen",
            required=False,
            action="store_false")
    parser_compare_gene.add_argument(
            "-N",
            "--no_log_transform_b",
            help="Do not log transform the second screen",
            required=False,
            action="store_false")

    return parser.parse_args()

def main_cli():
    args = get_args()
    if args.subcommand == "gene":
        vg = VisualizeGenes(
            filename=args.input,
            gene_column=args.gene_column,
            fc_column=args.fc_column,
            pval_column=args.pval_column,
            threshold_column=args.threshold_column,
            threshold=args.threshold,
        )
        vg.plot_volcano(output=args.output)
    elif args.subcommand == "sgrna":
        sg = VisualizeSGRNAs(
            filename=args.input,
            sgrna_column=args.sgrna_column,
            gene_column=args.gene_column,
            fc_column=args.fc_column,
            pval_column=args.pval_column,
            threshold_column=args.threshold_column,
            threshold=args.threshold,
        )
        sg.plot_volcano(output=args.output)
    elif args.subcommand == "compare":
        cs = CompareScreens(
            filename_a=args.screen_a,
            filename_b=args.screen_b,
            variable_column_a=args.variable_column_a,
            variable_column_b=args.variable_column_b,
            threshold_column_a=args.threshold_column_a,
            threshold_column_b=args.threshold_column_b,
            threshold=args.threshold,
            merge_column_a=args.merge_column_a,
            merge_column_b=args.merge_column_b,
            log_transform_a=~args.no_log_transform_a,
            log_transform_b=~args.no_log_transform_b,
        )
        cs.plot_volcano()

if __name__ == "__main__":
    main_cli()
