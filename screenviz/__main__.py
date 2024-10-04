# screenviz.__main__


from screenviz.cli import get_args
from screenviz.compare import CompareScreens
from screenviz.gene import VisualizeGenes
from screenviz.idea import RunIDEA
from screenviz.qc import quality_control_app_entry
from screenviz.results import results_app_entry
from screenviz.sgrna import VisualizeSGRNAs

from ._utils import find_free_port


def main_cli():
    args = get_args()
    if args.subcommand == "gene":
        vg = VisualizeGenes(
            filename=args.input,
            config=args.config,
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
    elif args.subcommand == "idea":
        RunIDEA(
            filename=args.input,
            geneset=args.geneset,
            output=args.output,
            gene_column=args.gene_column,
            fc_column=args.fc_column,
            pval_column=args.pval_column,
            threshold_column=args.threshold_column,
            threshold=args.threshold,
            sided=args.sided,
            top=args.top,
            gene_palette=args.gene_palette,
            term_palette=args.term_palette,
            up_color=args.up_color,
            down_color=args.down_color,
            term_threshold=args.term_threshold,
        )
    elif args.subcommand == "qc":
        port = find_free_port(args.port)
        quality_control_app_entry(
            filename=args.input,
            port=port,
            guide_column=args.guide_column,
            gene_column=args.gene_column,
        )
    elif args.subcommand == "results":
        if args.prefix is not None:
            sgrna_file = f"{args.prefix}.sgrna_results.tsv"
            gene_file = f"{args.prefix}.gene_results.tsv"
        else:
            if args.sgrna_file is None or args.gene_file is None:
                base_error = "Must provide either a prefix (-n) or both sgrna (-s) and gene (-g) files"
                if args.sgrna_file is None:
                    raise ValueError(base_error + " (sgrna file missing)")
                if args.gene_file is None:
                    raise ValueError(base_error + " (gene file missing)")
            sgrna_file = args.sgrna_file
            gene_file = args.gene_file
        port = find_free_port(args.port)
        results_app_entry(
            sgrna_file=sgrna_file,
            gene_file=gene_file,
            port=port,
            ntc_token=args.ntc_token,
        )


if __name__ == "__main__":
    main_cli()
