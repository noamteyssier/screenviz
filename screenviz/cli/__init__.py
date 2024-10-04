import argparse as ap

from ._compare import compare_parser
from ._gene import gene_parser
from ._idea import idea_parser
from ._quality_control import quality_control_parser
from ._results import results_parser
from ._sgrna import sgrna_parser


def get_args() -> ap.Namespace:
    parser = ap.ArgumentParser()
    subparser = parser.add_subparsers(dest="subcommand", required=True)
    gene_parser(subparser)
    sgrna_parser(subparser)
    compare_parser(subparser)
    idea_parser(subparser)
    quality_control_parser(subparser)
    results_parser(subparser)
    return parser.parse_args()
