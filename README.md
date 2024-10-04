# screenviz

A CRISPR screen visualization toolkit.

## Installation

```bash
pip install screenviz
```

## Usage

This program is meant to be run from the commandline and will generate interactive visualizations for your CRISPR screen results.

### Gene Enrichment

To explore the gene-level enrichment of your analysis - specifically the classic volcano plot (log-fold-change on the x-axis and negative log p-value on the y-axis) -
you can use the `screenviz gene` subcommand:

```bash
screenviz gene -i results.gene_results.tsv
```

If your screen result is an output of `crispr_screen`, the defaults of the program will immediately generate a visualization which will be written to an `*.html` file
on your computer. You can open this file in your favorite browser and explore the results interactively there.

For a better visualization, pass in the `.yaml` configuration file produced from your `crispr_screen` run.
This will automatically determine if `RRA` or `INC` was used and show appropriate thresholds.

``` bash
screenviz gene -i results.gene_results.tsv -c results.screenviz.yaml
```

If your screen result is an output of a different program, you will need to tell `screenviz` what the names of the columns in your data represent.

If your result is from `MAGeCK` you can do the following:

```bash
# Left side of the volcano 
screenviz gene \
    -i sample1.gene_summary.txt \
    -g "id" \
    -f "neg|lfc" \
    -p "neg|fdr" \
    -t "neg|fdr"

# Right side of the volcano 
screenviz gene \
    -i sample1.gene_summary.txt \
    -g "id" \
    -f "pos|lfc" \
    -p "pos|fdr" \
    -t "pos|fdr"
```

Check out what the arguments are with the help command:

```bash
screenviz gene --help
```

### sgRNA Enrichment

To explore the sgrna-level enrichment of your analysis - specifically the classic volcano plot (log-fold-change on the x-axis and negative log p-value on the y-axis) -
you can use the `screenviz sgrna` subcommand:

```bash
screenviz sgrna -i results.sgrna_results.tsv
```

If your screen result is an output of `crispr_screen`, the defaults of the program will immediately generate a visualization which will be written to an `*.html` file
on your computer. You can open this file in your favorite browser and explore the results interactively there.

If your screen result is an output of a different program, you will need to tell `screenviz` what the names of the columns in your data represent.

If your result is from `MAGeCK` you can do the following:

```bash
screenviz sgrna \
    -i sample1.sgrna_summary.txt \
    -g "Gene" \
    -f "LFC" \
    -p "FDR" \
    -t "FDR"
```

### Comparison

To compare the results of two different analysis methods you can use the `screenviz compare` subcommand

```bash
screenviz compare \
    -i results_a.gene_results.tab \
    -I results_b.gene_results.tab
```

This will generate a scatter plot to compare the calculated FDR values of two different results.

To compare between `crispr_screen` and `MAGeCK` one can do:

```bash

# compare depleted genes
screenviz compare \
    -i results.gene_results.tsv \
    -I sample1.gene_summary.txt \
    -x fdr_low \
    -X "neg|fdr" \
    -m gene \
    -M id \
    -t fdr_low \
    -T "neg|fdr"

# compare enriched genes
screenviz compare \
    -i results.gene_results.tsv \
    -I sample1.gene_summary.txt \
    -x fdr_high \
    -X "pos|fdr" \
    -m gene \
    -M id \
    -t fdr_high \
    -T "pos|fdr"
```
